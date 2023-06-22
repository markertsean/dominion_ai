import random
import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

from decks import cards,dominion_cards


def validate_all_action_cards():
    kingdom_dict = dominion_cards.premade_kingdom_dict
    action_cards = dominion_cards.base_action_cards
    for key in kingdom_dict:
        kingdom = kingdom_dict[key]
        for card in kingdom:
            assert card in action_cards, key+'\'s '+card+' card is not recognized'

class DominionGame:
    def __init__(self,kingdom,n_players,):
        assert isinstance(n_players,int) and n_players > 0
        self.n_players = n_players

        assert kingdom in DominionGame.get_valid_kingdoms(), \
        'kingdom must be one of '+str(DominionGame.get_valid_kingdoms())
        self.kingdom_name = kingdom

        self.kingdom = self.generate_kingdom()
        self.trash = cards.CardPile('trash')

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
        if (
            (self.kingdom['province'].count() == 0) or
            (self.get_n_depleted_supply_piles() == 3)
        ):
            return True
        return False

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

        default_handsize = 5

        victory = False
        turn = 0
        while not victory:
            print("Turn: "+str(turn))
            for player in player_list:
                # Draw new hand, set things like turn_actions, buy, etc
                player.start_turn()
                print(player)
                # Action
                player.do_actions()

                # Spend treasure
                player.spend_treasure()

                # Buy
                player.do_buy(self.kingdom)

                # Cleanup
                player.cleanup()

                # Victory conditions
                if ( self.victory_condition_met() ):
                    victory = True
                    break

            turn += 1
            if ( turn > 100 ):
                break
