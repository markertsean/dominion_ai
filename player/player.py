import random
import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

from decks import cards,dominion_cards
from util.logger import GameLogger
from brains import buy_brains

class Player:
    def __init__(
        self,
        name,
        buy_brain=None,
        logger=None,
    ):
        self.name = name

        assert (logger is None) or isinstance(logger,GameLogger)
        self.logger = logger

        # TODO: add brain
        self.brain = None

        self.draw_pile    = cards.CardPile( 'draw' )
        self.hand         = cards.CardPile( 'hand' )
        self.discard_pile = cards.CardPile( 'discard' )
        self.play_pile    = cards.CardPile( 'play' )

        self.victory_points = 0

        self.n_default_action = 1
        self.n_default_buy    = 1
        self.n_default_coin   = 0
        self.n_default_draw   = 5

        self.turn_action = 0
        self.turn_buy = 0
        self.turn_coin = 0
        self.turn_draw = 0

        self.buy_brain = buy_brain
        if ( self.buy_brain is None ):
            self.buy_brain = buy_brains.buy_brain_dict['random']

        for key in self.__dict__.keys():
            if ( 'default' in key ):
                self.log("{} set to '{}'".format(key,self.__dict__[key]))

    def __repr__(self):
        ret_str  = "Player: "+self.name
        ret_str += "\n\tVP     : {}".format(self.victory_points)
        ret_str += "\n\tDraw   : {}".format(self.draw_pile.count_cards())
        ret_str += "\n\tHand   : {}".format(self.hand.count_cards())
        ret_str += "\n\tDiscard: {}".format(self.discard_pile.count_cards())
        return ret_str+"\n"

    def log(self,m,debug=False):
        if (self.logger is not None):
            self.logger.log("PLAYER {}: ".format(self.name)+m,debug=debug)

    def get_n_action(self):
        return self.n_default_action

    def get_n_buy(self):
        return self.n_default_buy

    def get_n_coin(self):
        return self.n_default_coin

    def get_n_draw(self):
        return self.n_default_draw

    def get_all_card_count(self):
        all_card_list = []
        for pile in [
            self.hand,
            self.draw_pile,
            self.discard_pile,
            self.play_pile,
        ]:
            for card in pile.stack:
                all_card_list.append(card)
        all_card_pile = cards.CardPile('all',all_card_list)
        return all_card_pile.count_cards()

    def discard_shuffle_to_draw(self):
        self.discard_pile.shuffle()
        return self.draw_pile.draw_from_pile(self.discard_pile,self.discard_pile.n_cards())

    # Currently only implemented for moat
    def defends(self):
        defended = 'moat' in [ card.name for card in self.hand.stack ]
        if defended:
            self.log("defends against attack by showing '{}'".format('moat'))
        return defended

    def wipe_all_stacks(self):
        for pile in [self.hand,self.draw_pile,self.discard_pile,self.play_pile]:
            pile.wipe_stack()

    # TODO: implement real decision algorithm
    def decide_discard(self,cards,n_max=None):
        if (n_max is None):
            n_max = cards.n_cards()

        index_list = []
        i = 0
        n = 0
        for card in cards.stack:
            if (
                ( n < n_max ) and
                (
                    ('curse' in card.type) or
                    ('victory' in card.type)
                )
            ):
                index_list.append(i)
                n += 1
            i += 1
        discard_list = []
        discard_str = "discarded with choice"
        any_discard = False
        for i in index_list[::-1]:
            any_discard=True
            discard_str += " '{}'".format(cards.stack[i].name)
            discard_list.append(cards.stack.pop(i))
        if (not any_discard):
            discard_str += " nothing"
        self.log(discard_str)
        return discard_list

    def force_discard(self,cards,n):
        discard_list = self.decide_discard(cards,n)
        if ( len(discard_list)<n ):
            discard_str = "forced to discard"
            # TODO: implement better logic
            while ( (cards.n_cards()>0) and (len(discard_list) < n) ):
                d = random.choice( cards.stack )
                discard_list.append( d )
                cards.stack.remove(d)
                discard_str += " '{}'".format(d.name)
            self.log(discard_str)
        return discard_list

    # TODO: implement real decision algorithm
    def decide_trash(self,cards,n_max=None):
        if (n_max is None):
            n_max = cards.n_cards()

        index_list = []
        i = 0
        n = 0
        for card in cards.stack:
            if (
                ( n < n_max ) and
                (
                    (
                        (
                            ('victory' in card.type) or
                            ('curse' in card.type)
                        ) and
                        (
                            (isinstance(card.vp,int)) and
                            ( card.vp <= 1 )
                        )
                    ) or
                    (
                        (card.name=='copper')
                    )
                )
            ):
                index_list.append(i)
                n += 1
            i += 1
        discard_list = []
        discard_str = "trashed"
        any_discard = False
        for i in index_list[::-1]:
            any_discard=True
            discard_str += " '{}'".format(cards.stack[i].name)
            discard_list.append(cards.stack.pop(i))
        if (not any_discard):
            discard_str += " nothing"
        self.log(discard_str)
        return discard_list

    def force_trash(self,cards,n):
        discard_list = self.decide_trash(cards,n)
        if ( len(discard_list)<n ):
            discard_str = "forced to trash"
            # TODO: implement better logic
            while ( (cards.n_cards()>0) and (len(discard_list) < n) ):
                d = random.choice( cards.stack )
                discard_list.append( d )
                cards.stack.remove(d)
                discard_str += " '{}'".format(d.name)
            self.log(discard_str)
        return discard_list

    def draw_to_hand(self,n_draw=None):
        '''
        Track n cards drawn
        Draw from pile
        If not enough cards, shuffle discard and transfer to draw pile
        Continue drawing
        '''
        if (n_draw==None):
            n_draw = self.get_n_draw()
        assert isinstance(n_draw,int)
        n_in_pile = self.draw_pile.n_cards()
        n_drawn = self.hand.draw_from_pile( self.draw_pile, n_draw )
        self.log("attempted to draw '{}' cards, drew '{}' from draw pile with '{}'".format(
            n_draw,n_drawn,n_in_pile
        ),debug=True)

        # Couldn't draw full hand from discard pile
        if ( n_drawn != n_draw ):
            # Shuffle discard to make new draw pile
            self.discard_shuffle_to_draw()
            n_remain = n_draw - n_drawn
            n_in_pile = self.draw_pile.n_cards()
            n_drawn_new = self.hand.draw_from_pile( self.draw_pile, n_remain )
            n_drawn += n_drawn_new

            self.log("shuffled discard, attempted to redraw '{}' cards, drew '{}' from draw pile with '{}'".format(
                n_remain, n_drawn_new, n_in_pile
            ),debug=True)

        self.log("drew {}, hand contains - {}".format(
            ' '.join(["'{}'".format(card.name) for card in self.hand.stack[-n_drawn:] ]),
            ' '.join(["'{}'".format(card.name) for card in self.hand.stack ])
        ),debug=True)

        return n_drawn

    def start_turn(self):
        self.turn_action = self.get_n_action()
        self.turn_buy    = self.get_n_buy()
        self.turn_coin   = self.get_n_coin()
        self.turn_draw   = self.get_n_draw()

        self.log("starting turn with '{}' actions, '{}' buy, '{}' coin, '{}' cards".format(
            self.turn_action,
            self.turn_buy,
            self.turn_coin,
            self.hand.n_cards()
        ),debug=True)

        self.log("starting turn with cards {}".format(
            " ".join(sorted([card.name for card in self.hand.stack]))
        ))

        return self.hand.n_cards()

    def play_card(self,card,inp_dict):

        for c, p in zip(
            [card.action,card.buy,card.coin,card.draw],
            [self.turn_action,self.turn_buy,self.turn_coin,self.turn_draw]
        ):
            if ( c is not None ):
                p += c
        if (
            (card.draw is not None) and
            (isinstance(card.draw,int))
        ):
            self.draw_to_hand(card.draw)
        # TODO: implement all the abilities, and draw properly
        if ( card.ability is not None ):
            card.ability( inp_dict )

    def do_actions(self,opponents,kingdom,trash):
        inp_params = {
            'player':self,
            'opponents':opponents,
            'kingdom':kingdom,
            'trash':trash,
        }
        new_card = True
        action_card_list = [None]
        while self.turn_action > 0:
            self.log("action phase with '{}' actions, '{}' buy, '{}' coin, '{}' cards".format(
                self.turn_action,
                self.turn_buy,
                self.turn_coin,
                self.turn_draw
            ),debug=True)

            # Will re-check when we gained a new card from our action
            if ( new_card ):
                action_card_list = [None]
                for card in self.hand.stack:
                    if ( 'action' in card.type ):
                        action_card_list.append( card )
                new_card = False

            self.log("action cards in hand - {}".format(
                ' '.join(["'{}'".format(
                        card.name if isinstance(card,cards.DominionCard) else None
                ) for card in action_card_list])
            ))

            # TODO: Implement brain and move...
            selected_card = random.choice( action_card_list )

            if (selected_card is not None):
                self.hand.stack.remove(selected_card)
                action_card_list.remove(selected_card)
                self.play_pile.topdeck( selected_card )
                new_card = self.play_card( selected_card, inp_params )

                self.log("played '{}'".format(selected_card.name),debug=True)
            else:
                self.log('plays nothing')

            self.turn_action -= 1

    def spend_treasure(self):
        coin = 0
        remaining_cards = self.hand.count_cards()
        for treasure in dominion_cards.treasure_reference:
            if ( treasure in remaining_cards ):
                self.log("spends '{}' '{}'".format(remaining_cards[treasure],treasure))
                coin += remaining_cards[treasure] * \
                dominion_cards.treasure_reference[treasure].coin
        self.turn_coin += coin
        self.log("has '{}' coin".format(self.turn_coin))
        return coin

    def do_buy(self,input_kingdom):
        self.log("has '{}' buy".format(self.turn_buy))
        for buy_i in range(0,self.turn_buy):

            self.log("has '{}' coin".format(self.turn_coin),debug=True)

            card_count_list = [(None,10,)]
            for supply in input_kingdom:
                card = input_kingdom[supply].get_card()
                if ( card.cost <= self.turn_coin ):
                    card_count_list.append(
                        ( card, input_kingdom[supply].count(), )
                    )

            brain_inputs = {
                'kingdom_counts':card_count_list
            }
            buy_card = self.buy_brain.choose_buy( brain_inputs )

            self.log("purchases '{}' for '{}'".format(
                buy_card.name if isinstance(buy_card,cards.DominionCard) else None,
                buy_card.cost if isinstance(buy_card,cards.DominionCard) else 0,
            ))
            if ( buy_card is not None ):
                self.turn_coin -= buy_card.cost

                self.discard_pile.draw_from_supply( input_kingdom[buy_card.name] )

    def cleanup(self):
        n_hand = self.hand.n_cards()
        n_play = self.play_pile.n_cards()
        n_returned = (
            self.discard_pile.draw_from_pile( self.hand, n_hand ) +
            self.discard_pile.draw_from_pile( self.play_pile, n_play )
        )
        self.log("cleanup '{}' cards in hand, '{}' cards in play, '{}' go into the discard".format(
            n_hand, n_play, n_returned
        ))
        n_draw = self.draw_to_hand( self.turn_draw )
        self.log("drew '{}' cards".format(
            n_draw
        ))
        return n_draw
