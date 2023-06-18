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
