import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

from decks.cards import DominionCard

# Treasure

copper = DominionCard(
    name='copper',
    cost=0,
    card_type='treasure',
)

silver = DominionCard(
    name='silver',
    cost=3,
    card_type='treasure',
)

gold = DominionCard(
    name='gold',
    cost=6,
    card_type='treasure',
    coin=3,
)


# Victory cards

curse = DominionCard(
    name='curse',
    cost=0,
    card_type=['curse'],
    victory_points=-1
)

estate = DominionCard(
    name='estate',
    cost=2,
    card_type='victory',
    victory_points=2,
)

duchy = DominionCard(
    name='duchy',
    cost=5,
    card_type='victory',
    victory_points=3,
)

province = DominionCard(
    name='province',
    cost=8,
    card_type='victory',
    victory_points=6,
)


# Action cards

'''
Reveal cards from your deck until you reveal 2 treasure cards.
Put those treasure cards into your hand, and discard the other revealed cards.
'''
adventurer = DominionCard(
    name='adventurer',
    cost=6,
    card_type='action',
    ability=None,
)

'''
Gail a silver card, put it on top of your deck.
Each other player reveals a Victory card from his hand,
and puts it on his deck (or reveals a hand with no victory cards)
'''
bureaucrat = DominionCard(
    name='bureaucrat',
    cost=4,
    card_type=['action','attack'],
    ability=None,
)

'''
Discard any number of cards. +1 card per card discarded.
'''
cellar = DominionCard(
    name='cellar',
    cost=2,
    card_type='action',
    ability=None,
    action=1,
)

'''
Trash up to 4 cards from your hand
'''
chapel = DominionCard(
    name='chapel',
    cost=2,
    card_type='action',
    ability=None,
)

'''
Each other player draws a card
'''
council_room = DominionCard(
    name='council room',
    cost=5,
    card_type='action',
    ability=None,
    buy=1,
    draw=4,
)

'''
Trash this card, gain a card costing up to 5
'''
feast = DominionCard(
    name='feast',
    cost=4,
    card_type='action',
)

festival = DominionCard(
    name='festival',
    cost=5,
    card_type='action',
    action=2,
    buy=1,
    coin=2,
)

'''
Worth 1 vp for every 10 cards in your deck (rounded down)
'''
gardens = DominionCard(
    name='gardens',
    cost=4,
    card_type='victory',
    ability=None
)

laboratory = DominionCard(
    name='laboratory',
    cost=5,
    card_type='action',
    action=1,
    draw=2,
)

'''
Draw until you have 7 cards in hand.
You may set aside any action cards drawn this way, as you draw them.
Discard the set aside cards after you finish drawing.
'''
library = DominionCard(
    name='library',
    cost=5,
    card_type='action',
    ability=None,
)

market = DominionCard(
    name='market',
    cost=5,
    card_type='action',
    action=1,
    buy=1,
    coin=1,
    draw=1,
)

'''
Each other player discards down to 3 cards in his hand
'''
militia = DominionCard(
    name='militia',
    cost=4,
    card_type=['action','attack'],
    ability=None,
    buy=2,
)

'''
Trash a treasure card from your hand.
Gain a treasure card costing up to 3 more, put it in your hand.
'''
mine = DominionCard(
    name='mine',
    cost=5,
    card_type='action',
    ability=None,
)

'''
When another player plays an attack card, you may reveal this from your hand.
If you do, you are unaffected by the attack.
'''
moat = DominionCard(
    name='moat',
    cost=2,
    card_type=['action','reaction'],
    ability=None,
    draw=2,
)

'''
Trash a copper from your hand. If you do, +3 coin
'''
moneylender = DominionCard(
    name='moneylender',
    cost=4,
    card_type='action',
    ability=None,
)

'''
Trash a card from your hand.
Gain a card costing up to 2 coin more than the trashed car.
'''
remodel = DominionCard(
    name='remodel',
    cost=4,
    card_type='action',
    ability=None,
)

smithy = DominionCard(
    name='smithy',
    cost=4,
    card_type='action',
    draw=3,
)

'''
Each player including you reveals the top card of hist deck
and either discards it or puts it back, your choice
'''
spy = DominionCard(
    name='spy',
    cost=4,
    card_type=['action','attack'],
    ability=None,
    action=1,
    draw=1,
)

'''
Each other player reveals the top 2 cards of his deck.
If they revealed any treasure cards, they trash one of
them that you choose. You may gain any or all of these
trashed cards. They discard the other revealed cards.
'''
thief = DominionCard(
    name='thief',
    cost=4,
    card_type=['action','attack'],
    ability=None,
)

'''
Choose an action card in your hand. Play it twice.
'''
throne_room = DominionCard(
    name='throne room',
    cost=4,
    card_type='action',
    ability=None
)

village = DominionCard(
    name='village',
    cost=3,
    card_type='action',
    action=2,
    draw=1,
)

'''
Each other player gains a curse card
'''
witch = DominionCard(
    name='witch',
    cost=5,
    card_type=['action','attack'],
    ability=None,
    draw=2,
)

woodcutter = DominionCard(
    name='woodcutter',
    cost=3,
    card_type='action',
    buy=1,
    coin=2,
)

'''
Gain a card costing up to 4
'''
workshop = DominionCard(
    name='workshop',
    cost=3,
    card_type='action',
    ability=None,
)
