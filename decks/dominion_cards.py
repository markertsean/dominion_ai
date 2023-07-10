import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

from decks.cards import DominionCard, CardSupply
import decks.dominion_card_abilities as dca

# Treasure

copper = DominionCard(
    name='copper',
    cost=0,
    card_type='treasure',
    coin=1,

    junk=True,
)

silver = DominionCard(
    name='silver',
    cost=3,
    card_type='treasure',
    coin=2,
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
    victory_points=-1,

    junk=True,
)

estate = DominionCard(
    name='estate',
    cost=2,
    card_type='victory',
    victory_points=1,

    junk=True,
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
base_action_cards = {
    'adventurer': DominionCard(
        name='adventurer',
        cost=6,
        card_type='action',
        text=\
        '''
        Reveal cards from your deck until you reveal 2 treasure cards.
        Put those treasure cards into your hand, and discard the other revealed cards.
        ''',

        ability=dca.adventurer,

        cycle_deck=True,
        draw_n=2,
        draw_treasure=True,
        terminal=True,
        terminal_coin=True,
    ),

    'bureaucrat': DominionCard(
        name='bureaucrat',
        cost=4,
        card_type=['action','attack'],
        text=\
        '''
        Gail a silver card, put it on top of your deck.
        Each other player reveals a Victory card from his hand,
        and puts it on his deck (or reveals a hand with no victory cards)
        ''',

        ability=dca.bureaucrat,

        attack_topdeck=True,
        gainer_treasure=True,
        terminal=True,
    ),

    'cellar': DominionCard(
        name='cellar',
        cost=2,
        card_type='action',
        text=\
        '''
        Discard any number of cards. +1 card per card discarded.
        ''',

        ability=dca.cellar,
        action=1,

        draw_n=10, # Arbitrary high
        discard_draw=True,
        discard_n=10, # Arbitrary high
    ),

    'chancellor': DominionCard(
        name='chancellor',
        cost=3,
        card_type='action',
        text=\
        '''
        You may immediately put your deck into your discard pile
        ''',

        ability=dca.chancellor,
        buy=2,

        shuffle=True,
        terminal=True,
    ),

    'chapel': DominionCard(
        name='chapel',
        cost=2,
        card_type='action',
        text=\
        '''
        Trash up to 4 cards from your hand
        ''',

        ability=dca.chapel,

        terminal=True,
        trasher=True,
        trash_n=4
    ),

    'council_room': DominionCard(
        name='council room',
        cost=5,
        card_type='action',
        text=\
        '''
        Each other player draws a card
        ''',

        ability=dca.council_room,
        buy=1,
        draw=4,

        opponent_draws=True,
        terminal_draw=True,
    ),

    'feast': DominionCard(
        name='feast',
        cost=4,
        card_type='action',
        text=\
        '''
        Trash this card, gain a card costing up to 5
        ''',

        ability=dca.feast,

        terminal=True,
        trash_self=True,
        gainer_general=True,
    ),

    'festival': DominionCard(
        name='festival',
        cost=5,
        card_type='action',

        action=2,
        buy=1,
        coin=2,
    ),

    'gardens': DominionCard(
        name='gardens',
        cost=4,
        card_type='victory',
        text=\
        '''
        Worth 1 vp for every 10 cards in your deck (rounded down)
        ''',

        ability=dca.gardens,

        junk_synergy=True,
    ),

    'laboratory': DominionCard(
        name='laboratory',
        cost=5,
        card_type='action',

        action=1,
        draw=2,
    ),

    'library': DominionCard(
        name='library',
        cost=5,
        card_type='action',
        text=\
        '''
        Draw until you have 7 cards in hand.
        You may set aside any action cards drawn this way, as you draw them.
        Discard the set aside cards after you finish drawing.
        ''',

        ability=dca.library,

        cycle_deck=True,
        draw_ability=True,
        draw_n=7,
        terminal_draw=True,
    ),

    'market': DominionCard(
        name='market',
        cost=5,
        card_type='action',

        action=1,
        buy=1,
        coin=1,
        draw=1,
    ),

    'militia': DominionCard(
        name='militia',
        cost=4,
        card_type=['action','attack'],
        text=\
        '''
        Each other player discards down to 3 cards in his hand
        ''',

        ability=dca.militia,
        coin=2,

        attack_discard=True,
        terminal_coin=True,
    ),

    'mine': DominionCard(
        name='mine',
        cost=5,
        card_type='action',
        text=\
        '''
        Trash a treasure card from your hand.
        Gain a treasure card costing up to 3 more, put it in your hand.
        ''',

        ability=dca.mine,

        gainer_treasure=True,
        terminal=True,
        trash_coin=True,
        trash_gain=True,
        trash_n=1,
        upgrades=True,
    ),

    'moat': DominionCard(
        name='moat',
        cost=2,
        card_type=['action','reaction'],
        text=\
        '''
        When another player plays an attack card, you may reveal this from your hand.
        If you do, you are unaffected by the attack.
        ''',

        ability=dca.moat,
        draw=2,

        defensive=True,
        reaction=True,
        terminal_draw=True,
    ),

    'moneylender': DominionCard(
        name='moneylender',
        cost=4,
        card_type='action',
        text=\
        '''
        Trash a copper from your hand. If you do, +3 coin
        ''',

        ability=dca.moneylender,

        trash_coin=True,
        trash_n=1,
        terminal_coin=True,
    ),

    'remodel': DominionCard(
        name='remodel',
        cost=4,
        card_type='action',
        text=\
        '''
        Trash a card from your hand.
        Gain a card costing up to 2 coin more than the trashed car.
        ''',

        ability=dca.remodel,

        gainer_general=True,
        terminal=True,
        trasher=True,
        trash_n=1,
        upgrades=True,
    ),

    'smithy': DominionCard(
        name='smithy',
        cost=4,
        card_type='action',

        draw=3,

        terminal_draw=True,
    ),

    'spy': DominionCard(
        name='spy',
        cost=4,
        card_type=['action','attack'],
        text=\
        '''
        Each player including you reveals the top card of his deck
        and either discards it or puts it back, your choice
        ''',

        ability=dca.spy,
        action=1,
        draw=1,

        attack_topdeck=True,
        discard=True,
        discard_n=1,
    ),

    'thief': DominionCard(
        name='thief',
        cost=4,
        card_type=['action','attack'],
        text=\
        '''
        Each other player reveals the top 2 cards of his deck.
        If they revealed any treasure cards, they trash one of
        them that you choose. You may gain any or all of these
        trashed cards. They discard the other revealed cards.
        ''',

        ability=dca.thief,

        attack_discard=True,
        attack_trash=True,
        gainer_treasure=True,
        terminal=True,
    ),

    'throne_room': DominionCard(
        name='throne room',
        cost=4,
        card_type='action',
        text=\
        '''
        Choose an action card in your hand. Play it twice.
        ''',

        ability=dca.throne_room,

        repeat=True,
    ),

    'village': DominionCard(
        name='village',
        cost=3,
        card_type='action',

        action=2,
        draw=1,
    ),

    'witch': DominionCard(
        name='witch',
        cost=5,
        card_type=['action','attack'],
        text=\
        '''
        Each other player gains a curse card
        ''',

        ability=dca.witch,
        draw=2,

        attack_curse=True,
        terminal_draw=True,
    ),

    'woodcutter': DominionCard(
        name='woodcutter',
        cost=3,
        card_type='action',

        buy=1,
        coin=2,

        terminal_coin=True,
    ),

    'workshop': DominionCard(
        name='workshop',
        cost=3,
        card_type='action',
        text=\
        '''
        Gain a card costing up to 4
        ''',

        ability=dca.workshop,

        gainer_general=True,
        terminal=True,
    ),
}


# Treasure supplies
copper_supply = CardSupply(copper,60)
silver_supply = CardSupply(silver,40)
gold_supply   = CardSupply(gold  ,30)

treasure_reference = {
    'copper': copper,
    'silver': silver,
    'gold'  : gold,
}

# VP supplies
curse_supply_2p = CardSupply(curse   ,10)
curse_supply_3p = CardSupply(curse   ,20)
curse_supply_4p = CardSupply(curse   ,30)
estate_supply   = CardSupply(estate  ,24)
duchy_supply    = CardSupply(duchy   ,12)
province_supply = CardSupply(province,12)

victory_card_reference = {
    'curse':curse,
    'estate':estate,
    'duchy':duchy,
    'province':province,
}

premade_kingdom_dict = {
    # Base game
    'first_game': [
        'cellar','market','militia','mine',
        'moat','remodel','smithy','village',
        'woodcutter','workshop'
    ],
    'big_money': [
        'adventurer','bureaucrat','chancellor',
        'chapel','feast','laboratory','market',
        'mine','moneylender','throne_room'
    ],
    'interaction': [
        'bureaucrat','chancellor','council_room',
        'festival','library','militia','moat',
        'spy','thief','village'
    ],
    'size_distortion': [
        'cellar','chapel','feast','gardens',
        'laboratory','thief','village','witch',
        'woodcutter','workshop'
    ],
    'village_square': [
        'bureaucrat','cellar','festival','library',
        'market','remodel','smithy','throne_room',
        'village','woodcutter'
    ],
}


all_valid_cards = {}
for card_set in [
    treasure_reference,
    victory_card_reference,
    base_action_cards,

]:
    for card_name, card in card_set.items():
        all_valid_cards[card_name] = card
