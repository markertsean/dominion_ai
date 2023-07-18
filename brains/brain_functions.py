import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

import decks.cards
import decks.dominion_cards as dc

def combine_deck_count( deck_list ):
    output_dict = {}
    for this_deck in deck_list:
        for key, val in this_deck.items():
            if ( key in output_dict ):
                output_dict[key] += val
            else:
                output_dict[key] = val
    return output_dict

# inp contains key as card name, value as card number
def analyze_deck( inp_card_dict, normalize=True ):
    assert isinstance(inp_card_dict,dict)
    for key, val in inp_card_dict.items():
        assert isinstance(key,str)
        assert isinstance(val,int)

    result_dict = {
        'n_cards':0,

        'action':0.,
        'buy':0.,
        'coin':0.,
        'draw':0.,
        'vp':0.,
        'vp_cards':0,
    }

    # Track these fields both at the straight +1 level, and when modified by ability
    modified_fields = ['action','buy','coin','draw']
    for item in modified_fields:
        result_dict[item+"_mod"] = 0.

    # Add all the flags for cards
    for item in decks.cards.dominion_card_flag_groupings:
        if (item not in result_dict):
            result_dict[item] = 0.

    for card_name in inp_card_dict:
        assert card_name in dc.all_valid_cards, "{} is not a valid dominion card!".format(card_name)

        this_card = dc.all_valid_cards[card_name]

        n = inp_card_dict[card_name]
        result_dict['n_cards' ] += n
        result_dict['action'  ] += n * this_card.action if this_card.action is not None else 0
        result_dict['buy'     ] += n * this_card.buy    if this_card.buy    is not None else 0
        result_dict['coin'    ] += n * this_card.coin   if this_card.coin   is not None else 0
        result_dict['draw'    ] += n * this_card.draw   if this_card.draw   is not None else 0
        result_dict['vp'      ] += n * this_card.vp     if this_card.vp     is not None else 0
        result_dict['vp_cards'] += n                    if this_card.vp     is not None else 0

        for flag in this_card.bool_flag_dict:
            if ( this_card.bool_flag_dict[flag] and (flag in decks.cards.reverse_dominion_card_flag_groupings) ):
                # Track separate modified fields for some attributes, IE attack_curse attack_trash are both attacks
                flag_attr_list = decks.cards.reverse_dominion_card_flag_groupings[flag]
                for attr in flag_attr_list:
                    mod = ''
                    if ( decks.cards.reverse_dominion_card_flag_groupings[flag] in modified_fields ):
                        mod = "_mod"
                    result_dict[attr+mod] += n

    for item in modified_fields:
        result_dict[item+"_mod"] += result_dict[item]

    if ( normalize ):
        for key in result_dict:
            if ( key != "n_cards" ):
                result_dict[key] = result_dict[key] / result_dict["n_cards"]
    return result_dict


# Returns 0/early, 1/mid, 2/late
def game_phase( turn, kingdom, low_pile_n=4, low_province_n=7 ):
    assert isinstance(kingdom,dict)
    assert isinstance(kingdom[list(kingdom.keys())[0]],decks.cards.CardSupply),"input kingdom must be a dict of card supplies!"
    if ( turn <= 4 ):
        return 0
    else:
        # Late game if low on victory cards, or 3 supplies nearly run out
        if ( kingdom['province'].count() <= low_province_n ):
            return 2
        n_low = 0
        for name,supply in kingdom.items():
            if ( supply.count() <= low_pile_n ):
                n_low += 1
                if ( n_low >= 3 ):
                    return 2
    return 1
