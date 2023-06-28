import random
import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')


from decks.cards import DominionCard, CardPile, CardSupply
from decks import dominion_cards
from util.logger import GameLogger

'''
Reveal cards from your deck until you reveal 2 treasure cards.
Put those treasure cards into your hand, and discard the other revealed cards.
'''
def adventurer( inp_params ):

    player       = inp_params['player']
    hand         = inp_params['player'].hand
    draw_pile    = inp_params['player'].draw_pile
    discard_pile = inp_params['player'].discard_pile

    drawn_card_list = []
    treasure_cards = []
    while draw_pile.n_cards() > 0:
        card = draw_pile.draw()[0]
        if ('treasure' in card.type):
            treasure_cards.append(card)
            if ( len(treasure_cards)==2 ):
                break
        else:
            drawn_card_list.append(card)
    # May have to shuffle discard and repeat
    if ( len(treasure_cards)!=2 ):
        discard_pile.shuffle()
        draw_pile.draw_from_pile(discard_pile,n=discard_pile.n_cards())

        while draw_pile.n_cards() > 0:
            card = draw_pile.draw()[0]
            if ('treasure' in card.type):
                treasure_cards.append(card)
                if ( len(treasure_cards)==2 ):
                    break
                else:
                    drawn_card_list.append(card)
    player.log("played adventurer, drew [{}], treasures [{}]".format(
        " ".join(["'{}'".format(card.name) for card in drawn_card_list]),
        " ".join(["'{}'".format(card.name) for card in treasure_cards])
    ))
    discard_pile.topdeck(drawn_card_list)
    hand.topdeck(treasure_cards)

'''
Gain a silver card, put it on top of your deck.
Each other player reveals a Victory card from his hand,
and puts it on his deck (or reveals a hand with no victory cards)
'''
def bureaucrat( inp_params ):

    kingdom = inp_params['kingdom']
    player  = inp_params['player']
    logstr = "played bureaucrat, "
    if ( kingdom['silver'].count() > 0 ):
        logstr += "kingdom contains '{}' silver, player gains a silver".format(
            kingdom['silver'].count()
        )
        player.draw_pile.topdeck( kingdom['silver'].gain() )
    else:
        logstr += "kingdom contains '0' silver, player does not gain a silver"

    for opp in inp_params['opponents']:
        showed_victory = False
        victory_index = 0
        for card in opp.hand.stack:
            if ('victory' in card.type):
                showed_victory=True
                break
            victory_index += 1
        if (showed_victory):
            card = opp.hand.stack.pop(victory_index)
            opp.draw_pile.topdeck(card)
            logstr += ", {} showed victory card and topdecks it".format(opp.name)
        else:
            logstr += ", {} does not show a victory card".format(opp.name)

    player.log(logstr)

'''
Discard any number of cards. +1 card per card discarded.
'''
def cellar( inp_params ):
    player = inp_params['player']
    player.log('played cellar, discarding and drawing - ')
    discards = player.decide_discard( player.hand )
    n_discard = len(discards)
    player.discard_pile.topdeck( discards )
    player.draw_to_hand( n_discard )

'''
You may immediately put your deck into your discard pile
'''
def chancellor( inp_params ):
    player = inp_params['player']
    player.discard_pile.draw_from_pile( player.draw_pile, player.draw_pile.n_cards() )

'''
Trash up to 4 cards from your hand
'''
def chapel( inp_params ):
    player = inp_params['player']
    trash  = inp_params['trash']
    player.log('played chapel')
    trashed = player.decide_trash( player.hand, 4 )
    n_trash = len(trashed)
    trash.topdeck( trashed )

'''
Each other player draws a card
'''
def council_room( inp_params ):
    inp_params['player'].log("plays council room, each other player draws 1")
    for opp in inp_params['opponents']:
        opp.draw_to_hand(1)

'''
Trash this card, gain a card costing up to 5
'''
def feast( inp_params ):
    feast_card = dominion_cards.base_action_cards['feast']
    player  = inp_params['player']
    player.log("plays feast, trashing a feast and gaining card up to 5")
    if feast_card in player.play_pile.stack:
        player.play_pile.stack.remove( feast_card )
    inp_params['trash'].topdeck( feast_card )
    temp_coins = player.turn_coin
    temp_buys  = player.turn_buy
    player.turn_coin = 5
    player.turn_buy  = 1
    player.do_buy( inp_params['kingdom'] )
    player.turn_coin = temp_coins
    player.turn_buy  = temp_buys

'''
Worth 1 vp for every 10 cards in your deck (rounded down)
'''
def gardens( inp_params ):
    card_count = 0
    player=inp_params['player']
    for pile in [player.hand,player.discard_pile,player.draw_pile]:
        card_count += pile.n_cards()
    return card_count//10

'''
Draw until you have 7 cards in hand.
You may set aside any action cards drawn this way, as you draw them.
Discard the set aside cards after you finish drawing.
'''
def library( inp_params ):
    player = inp_params['player']
    discards = []
    player.log("plays library, hand contains '{}' cards of 7".format(player.hand.n_cards()))
    while player.hand.n_cards()<7:
        # End of deck, stop
        if ( player.draw_to_hand(1) == 0 ):
            break
        # TODO: add better logic
        # Ignore action cards if no actions left
        if (
            (player.turn_action == 0) and
            ('action' in player.hand.stack[-1].type)
        ):
            player.log("has no actions, setting aside card '{}'".format(player.hand.stack[-1].name))
            discards.append(player.hand.stack.pop(-1))
    player.discard_pile.topdeck(discards)

'''
Each other player discards down to 3 cards in his hand
'''
def militia( inp_params ):
    inp_params['player'].log('plays militia')
    for opp in inp_params['opponents']:
        if ( not opp.defends() and (opp.hand.n_cards()>3)):
            discard_list = opp.force_discard( opp.hand, opp.hand.n_cards()-3 )

'''
Trash a treasure card from your hand.
Gain a treasure card costing up to 3 more, put it in your hand.
'''
def mine( inp_params ):
    player = inp_params['player']
    copper = None
    silver = None
    i = 0
    log_str = "plays mine"
    for card in player.hand.stack:
        if ( (card.name == 'copper') and (copper is None) ):
            copper = i
        elif ( (card.name == 'silver') and (silver is None) ):
            silver = i
        i += 1
    if ( copper is not None ):
        log_str += ", mining a copper"
        card = player.hand.stack.pop( copper )
        inp_params['trash'].topdeck(card)
        player.hand.topdeck( dominion_cards.silver )
    elif ( silver is not None ):
        log_str += ", mining a silver"
        card = player.hand.stack.pop( silver )
        inp_params['trash'].topdeck(card)
        player.hand.topdeck( dominion_cards.gold )
    player.log(log_str)

'''
When another player plays an attack card, you may reveal this from your hand.
If you do, you are unaffected by the attack.
''',
def moat( inp_params ):
    pass

'''
Trash a copper from your hand. If you do, +3 coin
'''
def moneylender( inp_params ):
    player = inp_params['player']
    i = 0
    ind = None
    log_str = "plays moneylender"
    for card in player.hand.stack:
        if (card.name=='copper'):
            ind = i
            break
        i += 1
    if ( ind is not None ):
        card = player.hand.stack.pop(ind)
        inp_params['trash'].topdeck(card)
        player.turn_coin += 3
        log_str += ", trashed a copper for +3 buy"
    else:
        log_str += ", did not trash a copper"
    player.log(log_str)

'''
Trash a card from your hand.
Gain a card costing up to 2 coin more than the trashed card.
'''
def remodel( inp_params ):
    player  = inp_params['player']
    player.log("plays feast, trashing a feast and gaining card up to 5")
    # TODO: better logic
    card = player.force_trash( player.hand, 1 )[0]
    player.hand.stack.remove( card )
    inp_params['trash'].topdeck( card )
    temp_coins = player.turn_coin
    temp_buys  = player.turn_buy
    player.turn_coin = 2 + card.cost
    player.turn_buy  = 1
    player.do_buy( inp_params['kingdom'] )
    player.turn_coin = temp_coins
    player.turn_buy  = temp_buys

'''
Each player including you reveals the top card of his deck
and either discards it or puts it back, your choice
'''
def spy( inp_params ):
    inp_params['player'].log("plays spy")
    for opp in inp_params['opponents']:
        if (opp.draw_pile.n_cards()==0):
            continue
        card = opp.draw_pile.stack.pop(-1)
        logstr = "shows '{}'".format(card.name)
        # TODO: better logic
        if (
            ('action' in card.type) or
            (
                ('treasure' in card.type) and
                (
                    (isinstance(card.coin,int)) and
                    (card.coin > 1)
                )
            )
        ):
            opp.discard_pile.topdeck(card)
            logstr+=" and discards it"
        else:
            opp.draw_pile.topdeck(card)
            logstr+=" and returns it"
        opp.log(logstr)

'''
Each other player reveals the top 2 cards of his deck.
If they revealed any treasure cards, they trash one of
them that you choose. You may gain any or all of these
trashed cards. They discard the other revealed cards.
'''
def thief( inp_params ):
    player = inp_params['player']
    player.log('plays theif')
    for opp in inp_params['opponents']:
        if (opp.defends()):
            continue
        card_list = []
        logstr = "shows"
        disstr = ""
        for i in range(0,2):
            if (opp.draw_pile.n_cards()==0):
                continue
            card = opp.draw_pile.stack.pop(-1)
            logstr+=" '{}'".format(card.name)

            if (
                ('treasure' in card.type) and
                (card.name!='copper')
            ):
                card_list.append(card)
            else:
                opp.discard_pile.topdeck( card )
                disstr += ", discards '{}'".format(card.name)

        logstr+=disstr+","
        gained_card = False

        for card in card_list:
            if ( gained_card ):
                inp_params['trash'].topdeck(card)
                logstr += ", trashes '{}'".format(card.name)
            elif ( card.name=='gold' ):
                player.discard_pile.topdeck(card)
                gained_card = True
                logstr += ", player takes '{}'".format(card.name)
        for card in card_list:
            if ( gained_card ):
                inp_params['trash'].topdeck(card)
                logstr += ", trashes '{}'".format(card.name)
            elif ( card.name=='silver' ):
                player.discard_pile.topdeck(card)
                gained_card = True
                logstr += ", player takes '{}'".format(card.name)
        opp.log(logstr)

'''
Choose an action card in your hand. Play it twice.
'''
def throne_room( inp_params ):
    player = inp_params['player']

    logstr = "plays throne room"

    action_card_list = []
    for card in player.hand.stack:
        if ( 'action' in card.type ):
            action_card_list.append( card )

    if ( len(action_card_list) < 1 ):
        logstr += " with no cards to play"
        player.log(logstr)
        return

    # TODO: Implement brain and move...
    selected_card = random.choice( action_card_list )
    logstr += ", double plays '{}'".format(selected_card.name)
    player.log(logstr)

    player.hand.stack.remove( selected_card )
    player.play_pile.topdeck( selected_card )
    player.play_card( selected_card, inp_params )
    player.log("played '{}'".format(selected_card.name))
    player.play_card( selected_card, inp_params )
    player.log("played '{}'".format(selected_card.name))

'''
Each other player gains a curse card
'''
def witch( inp_params ):
    inp_params['player'].log("plays witch")
    for opp in inp_params['opponents']:
        if ( opp.defends() ):
            continue
        if ( opp.discard_pile.draw_from_supply( inp_params['kingdom']['curse'], 1 ) > 0 ):
            opp.log('draws a curse')

'''
Gain a card costing up to 4
'''
def workshop( inp_params ):
    player  = inp_params['player']
    player.log("plays workshop, gaining card up to 4")
    temp_coins = player.turn_coin
    temp_buys  = player.turn_buy
    player.turn_coin = 4
    player.turn_buy  = 1
    player.do_buy( inp_params['kingdom'] )
    player.turn_coin = temp_coins
    player.turn_buy  = temp_buys
