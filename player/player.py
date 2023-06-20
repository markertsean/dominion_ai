import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

from decks import cards

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

    def __repr__(self):
        ret_str  = "Player: "+self.name
        ret_str += "\n\tVP     : {}".format(self.victory_points)
        ret_str += "\n\tDraw   : {}".format(self.draw_pile.count_cards())
        ret_str += "\n\tHand   : {}".format(self.hand.count_cards())
        ret_str += "\n\tDiscard: {}".format(self.discard_pile.count_cards())
        return ret_str+"\n"
