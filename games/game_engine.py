import random
import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

from decks import cards,dominion_cards
from util.logger import GameLogger

def validate_all_action_cards():
    kingdom_dict = dominion_cards.premade_kingdom_dict
    action_cards = dominion_cards.base_action_cards
    for key in kingdom_dict:
        kingdom = kingdom_dict[key]
        for card in kingdom:
            assert card in action_cards, key+'\'s '+card+' card is not recognized'

def opponent_gen(player,player_list):
    return [opp for opp in player_list if opp != player]

class DominionGame:
    def __init__(self,kingdom,n_players,max_turns=100,logger=None):
        assert (logger is None) or isinstance(logger,GameLogger)
        self.logger = logger

        assert isinstance(n_players,int) and n_players > 0
        self.n_players = n_players
        self.log("DG SETUP: set number of players to '{}'".format(self.n_players))

        assert kingdom in DominionGame.get_valid_kingdoms(), \
        'kingdom must be one of '+str(DominionGame.get_valid_kingdoms())
        self.kingdom_name = kingdom
        self.log("DG SETUP: set kingdom to '{}'".format(self.kingdom_name))

        self.kingdom = self.generate_kingdom()
        self.log("DG SETUP: created kingdom with cards = {}".format(
            ' '.join(sorted(["'{}'".format(str(card)) for card in self.kingdom.keys()]))
        ))
        self.trash = cards.CardPile('trash')

        assert isinstance(max_turns,int) and (max_turns>0)
        self.max_turns = max_turns

    def log(self,m,debug=False):
        if (self.logger is not None):
            self.logger.log(m,debug=debug)

    def get_premade_kingdom_dict():
        return dominion_cards.premade_kingdom_dict

    def get_premade_kingdoms():
        return list( DominionGame.get_premade_kingdom_dict().keys() )

    def get_valid_kingdoms():
        return ['random','random_premade']+DominionGame.get_premade_kingdoms()

    def get_non_vp_treasure_supply_card_dict():
        return dominion_cards.base_action_cards

    def get_n_depleted_supply_piles(self):
        n = 0
        for key in self.kingdom:
            if ( self.kingdom['province'].count() == 0 ):
                n += 1
        return n

    def victory_condition_met(self):
        n_depleted = self.get_n_depleted_supply_piles()
        n_province = self.kingdom['province'].count()
        victory = False
        if ( ( n_province == 0) or ( n_depleted == 3) ):
            victory = True
        self.log("DG STATUS: victory returns '{}' - n_provinces = '{}', n_depleted = '{}'".format(
            victory,n_province,n_depleted
        ))
        return victory

    def generate_kingdom(self):
        # Certain vp and treasure always present
        supply = [
            dominion_cards.copper_supply
            ,dominion_cards.silver_supply
            ,dominion_cards.gold_supply
            ,dominion_cards.estate_supply
            ,dominion_cards.duchy_supply
            ,dominion_cards.province_supply
        ]
        if (self.n_players == 2):
            supply.append(dominion_cards.curse_supply_2p)
        elif (self.n_players == 3):
            supply.append(dominion_cards.curse_supply_3p)
        else:
            supply.append(dominion_cards.curse_supply_4p)

        # Read which action cards to use from user input
        card_list = None
        card_dict = DominionGame.get_non_vp_treasure_supply_card_dict()
        if ( self.kingdom_name in DominionGame.get_premade_kingdoms() ):
            card_list = DominionGame.get_premade_kingdom_dict()[self.kingdom_name]
        elif ( self.kingdom_name == 'random_premade' ):
            rand_kingdom = random.choice(DominionGame.get_premade_kingdoms())
            card_list = DominionGame.get_premade_kingdom_dict()[rand_kingdom]
        elif (self.kingdom_name == 'random' ):
            all_cards = list( card_dict.keys() )
            card_list = random.sample(all_cards,10)

        # Add action cards to the supply
        for card in card_list:
            card_class = card_dict[card]
            supply.append( cards.CardSupply(card_class,10) )

        kingdom = {}
        for s in supply:
            kingdom[s.get_card().name] = s.copy()
        return kingdom

    def calc_vp(self,player_list):
        cards_with_vp_ability = ['gardens']

        if ( not isinstance(player_list,list) ):
            player_list = [player_list]

        vp_dict = {}
        for player in player_list:
            inp_params = {
                'player':player,
                'opponents':opponent_gen(player,player_list),
                'kingdom':self.kingdom,
                'trash':self.trash,
            }
            victory_points = 0
            for stack in [
                    player.hand.stack,
                    player.draw_pile.stack,
                    player.discard_pile.stack,
                    player.play_pile.stack
            ]:
                for card in stack:
                    if ( card.vp is not None ):
                        victory_points += card.vp
                    if ( card.name in cards_with_vp_ability ):
                        victory_points += card.ability(inp_params)

            player.victory_points = victory_points
            vp_dict[player.name] = victory_points
        return vp_dict

    def run_game(self,player_list):
        '''
        Deal out 3 estate + 7 copper to each player every standard game
        Loop over players
            Action phase
            Spend treasure
            Buy phase
            Clean up phase
            Check victory conditions
        '''
        # All players start with these
        for player in player_list:
            player.discard_pile.draw_from_supply( self.kingdom['copper'], 7 )
            player.discard_pile.draw_from_supply( self.kingdom['estate'], 3 )
            player.draw_to_hand()

        default_handsize = 5

        turn_dict = {}
        victory = False
        turn = 1
        while not victory:

            self.log("DG GAME: {}".format(30*'-'))
            self.log("DG GAME: turn '{}'".format(str(turn)))

            turn_dict[turn] = {}

            for player in player_list:

                self.log("DG GAME: {}".format('-'))
                self.log("DG GAME: player turn - '"+str(player.name)+"'")

                # Draw new hand, set things like turn_actions, buy, etc
                player.start_turn()
                starting_hand    = player.hand.count_cards()
                starting_discard = player.discard_pile.count_cards()
                starting_draw    = player.draw_pile.count_cards()

                # Action
                # TODO: Implement information on card action - IE gained, discarded, trashed...etc
                actions = player.do_actions(
                    opponent_gen(player,player_list),
                    self.kingdom,
                    self.trash
                )

                # Spend treasure
                treasure = player.spend_treasure()

                # Buy
                buy_card_list = player.do_buy(self.kingdom)
                buy_name_list = [ card.name for card in buy_card_list if card is not None ]

                # Cleanup
                player.cleanup()

                player_vp = self.calc_vp(player)[player.name]

                turn_dict[turn][player.name] = {
                    "hand_start":starting_hand,
                    "discard_start":starting_discard,
                    "draw_start":starting_draw,
                    "treasure_spent":treasure,
                    "cards_purchased":buy_name_list,
                    "victory_points_end":player_vp,
                    "actions":actions,
                }

                # Victory conditions
                if ( self.victory_condition_met() ):
                    victory = True
                    break

            turn += 1
            if ( turn > self.max_turns ):
                break

        point_dict = self.calc_vp(player_list)
        card_dict = {}
        for player in player_list:
            card_dict[player.name] = player.get_all_card_count()
            player.wipe_all_stacks()

        return point_dict, card_dict, turn_dict
