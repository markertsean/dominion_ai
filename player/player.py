import random
import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

from decks import cards,dominion_cards

class Player:
    def __init__(
        self,
        name
    ):
        self.name = name

        # TODO: add brain
        self.brain = None

        self.draw_pile    = cards.CardPile( 'draw' )
        self.hand         = cards.CardPile( 'hand' )
        self.discard_pile = cards.CardPile( 'discard' )

        self.victory_points = 0

        self.n_default_action = 1
        self.n_default_buy    = 1
        self.n_default_coin   = 0
        self.n_default_draw   = 5

        self.turn_actions = 0
        self.turn_buy = 0
        self.turn_coin = 0
        self.turn_draw = 0

    def __repr__(self):
        ret_str  = "Player: "+self.name
        ret_str += "\n\tVP     : {}".format(self.victory_points)
        ret_str += "\n\tDraw   : {}".format(self.draw_pile.count_cards())
        ret_str += "\n\tHand   : {}".format(self.hand.count_cards())
        ret_str += "\n\tDiscard: {}".format(self.discard_pile.count_cards())
        return ret_str+"\n"

    def get_n_action(self):
        return self.n_default_action

    def get_n_buy(self):
        return self.n_default_buy

    def get_n_coin(self):
        return self.n_default_coin

    def get_n_draw(self):
        return self.n_default_draw

    def discard_shuffle_to_draw(self):
        self.discard_pile.shuffle()
        return self.draw_pile.draw_from_pile(self.discard_pile,self.discard_pile.n_cards())

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
        n_drawn = self.hand.draw_from_pile( self.draw_pile, n_draw )
        # Couldn't draw full hand from discard pile
        if ( n_drawn != n_draw ):
            # Shuffle discard to make new draw pile
            self.discard_shuffle_to_draw()
            n_remain = n_draw - n_drawn
            n_drawn += self.hand.draw_from_pile( self.draw_pile, n_remain )
        return n_drawn

    def start_turn(self):
        self.turn_action = self.get_n_action()
        self.turn_buy    = self.get_n_buy()
        self.turn_coin   = self.get_n_coin()
        self.turn_draw   = self.get_n_draw()
        return self.draw_to_hand( self.turn_draw )

    def play_card(self,card):
        for c, p in zip(
            [card.action,card.buy,card.coin,card.draw],
            [self.turn_action,self.turn_buy,self.turn_coin,self.turn_draw]
        ):
            if ( c is not None ):
                p += c
        # TODO: implement all the abilities

    def do_actions(self):
        new_card = True
        action_card_list = [None]
        while self.turn_actions > 0:

            if ( new_card ):
                action_card_list = [None]
                for card in self.hand:
                    if ( 'action' in card.type ):
                        action_card_list.append( card )
                new_card = False

            # TODO: Implement brain and move...
            selected_card = random.choice( action_card_list )

            if (selected_card is not None):
                new_card = self.play_card( selected_card )

            self.turn_actions -= 1


    def spend_treasure(self):
        coin = 0
        remaining_cards = self.hand.count_cards()
        for treasure in dominion_cards.treasure_reference:
            if ( treasure in remaining_cards ):
                coin += remaining_cards[treasure] * \
                dominion_cards.treasure_reference[treasure].coin
        self.turn_coin += coin
        return coin

    def do_buy(self,input_kingdom):
        for buy_i in range(0,self.turn_buy):
            card_count_list = [(None,10,)]
            for supply in input_kingdom:
                card = input_kingdom[supply].get_card()
                if ( card.cost <= self.turn_coin ):
                    card_count_list.append(
                        ( card, input_kingdom[supply].count(), )
                    )

            # TODO: Make brain classes and move random junk to there
            buy_card, count = random.choice( card_count_list )
            if ( buy_card is not None ):
                self.turn_coin -= buy_card.cost

                self.discard_pile.draw_from_supply( input_kingdom[buy_card.name] )

    def cleanup(self):
        return self.discard_pile.draw_from_pile( self.hand, self.hand.n_cards() )import sys
