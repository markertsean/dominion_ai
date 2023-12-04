import sys
import os
import copy
import math

import PySimpleGUI as sg

project_path = os.getcwd()+'/'
sys.path.append(project_path)

from decks import cards,dominion_cards
from brains import brain_functions as bf



game_ref = dominion_cards.game_expansion_reference
default_game_name = 'base'
default_game = game_ref[default_game_name]
default_treasure_card_list = list(default_game['treasure'].keys())
default_victory_card_list  = list(default_game['victory' ].keys())
default_kingdom_card_list  = list(default_game['kingdom' ].keys())

kingdom_select_pad_hspace = 400
kingdom_select_pad_vspace = 20

default_kingdom_selector_layout_start = [
    [sg.Text("Select your kingdom cards!",justification='top')],
    [sg.HSeparator(pad=(kingdom_select_pad_hspace,kingdom_select_pad_vspace))],
]

default_kingdom_selector_layout_end = [
    [sg.HSeparator(pad=(kingdom_select_pad_hspace,kingdom_select_pad_vspace))],
    [sg.Button("Accept",key='Kingdom_Accept'),sg.Button("Reset",key='Kingdom_Reset')]
]

default_window_title = "Dominion Hand Analyzer"
default_window_margins = (200,200)


def get_button_color( status ):
    if (status):
        return 'green'
    return 'red'


def gen_selectable_card_buttons_from_kingdom( inp_game_card_list, kingdom_card_status_dict ):
    out_button_list = []
    for card in inp_game_card_list:
        out_button_list.append(
            sg.Button(
                card,
                button_color=get_button_color( kingdom_card_status_dict[card] ),
                key="supply_"+card,
            )
        )
    return out_button_list


def gen_formatted_button_list( button_list, width=5 ):
    formatted_list = [[]]
    i = width
    for button in button_list:
        if ( i % width == 0 ):
            formatted_list.append([])
        formatted_list[-1].append(button)
        i+=1
    return formatted_list


def gen_kingdom_display_layout( inp_game_card_list, kingdom_card_status_dict, all_card_kind_dict ):
    game_buttons = gen_selectable_card_buttons_from_kingdom(
        inp_game_card_list,
        kingdom_card_status_dict
    )

    # Format the column as scrolling is not an option
    game_button_list_formatted = gen_formatted_button_list( game_buttons )

    game_column_selectable_kingdom_cards = sg.Column(
        [[sg.Text("Possible Cards:")]] +
        game_button_list_formatted
    )

    kingdom_kind_dict = {}
    kingdom_kind_formatted_dict = {}
    for kind in all_card_kind_dict:
        kingdom_kind_dict[kind] = []
        for card_name in all_card_kind_dict[kind]:
            button = sg.Button(
                card_name,
                button_color=get_button_color( kingdom_card_status_dict[card_name] ),
                visible=kingdom_card_status_dict[card_name],
                key="kingdom_"+card_name,
            )
            kingdom_kind_dict[kind].append( button )
        kingdom_kind_formatted_dict[kind] = gen_formatted_button_list( kingdom_kind_dict[kind] )

    game_column_selected_kingdom_cards = sg.Column(
        [[sg.Text("Victory Cards:")]] +
        kingdom_kind_formatted_dict['victory'] +
        [[sg.Text("Treasure Cards:")]] +
        kingdom_kind_formatted_dict['treasure'] +
        [[sg.Text("Kingdom Cards:")]] +
        kingdom_kind_formatted_dict['kingdom']
    )

    return default_kingdom_selector_layout_start +         [
            [
                game_column_selectable_kingdom_cards,
                sg.VSeparator(),
                game_column_selected_kingdom_cards,
            ]
        ] + \
        default_kingdom_selector_layout_end


def gen_default_card_dicts():
    # Create bool list of cards by game name
    kingdom_card_activation_dict = {} # Key is card name, val is whether toggled
    game_card_dict = {} # Key is game/expansion name, value is list of all cards originating from it
    all_cards_by_kind = {} # For the layout on the right side of the kindom building panel

    for game_name in game_ref.keys():
        game_card_dict[game_name] = []
        for kind in ['victory','treasure','kingdom']:
            if ( kind in game_ref[game_name] ):
                if ( kind not in all_cards_by_kind ):
                    all_cards_by_kind[kind] = []
                for card in game_ref[game_name][kind]:
                    all_cards_by_kind[kind].append(card)
                    if (
                        (card in default_treasure_card_list) or
                        (card in default_victory_card_list)
                    ):
                        kingdom_card_activation_dict[card] = True
                    else:
                        kingdom_card_activation_dict[card] = False

                    game_card_dict[game_name].append( card )
    return kingdom_card_activation_dict, game_card_dict, all_cards_by_kind


def gen_kingdom_window( title, margins, game_card_list, kingdom_card_activation_dict, all_card_kind_dict ):
    gen_layout = gen_kingdom_display_layout(
        game_card_list,
        kingdom_card_activation_dict,
        all_card_kind_dict,
    )
    gen_layout_copy = copy.deepcopy( gen_layout )
    return sg.Window(
        title=title,
        layout=gen_layout_copy,
        margins=margins,
        element_justification='c'
    )


def gen_game_move_buttons(
    name,
    name_color_label_tuple_list,
    kingdom_cards,
    cards_to_count=None,
    count=True,
    add_all=False,
    add_buttons=True,
):
    assert (name_color_label_tuple_list is None) or (len(name_color_label_tuple_list) == 3)
    assert ( count != (cards_to_count is None) ), "If counting must provide list of card piles to count"
    card_count = {}
    full_deck = {}
    if ( cards_to_count is not None ):
        pile_count_list = [ pile.count_cards() for pile in cards_to_count ]
        full_deck = bf.combine_deck_count( pile_count_list )

    all_button = []
    if add_all:
        all_button = ['all']

    card_name_len = 10
    card_len_str_f = "{:"+str(card_name_len)+"s}"
    font = ('Ubuntu Mono',14)

    out_layout = []
    for card in all_button+kingdom_cards:
        button_list = []
        visible_row = (
            ( card == 'all' ) or
            (cards_to_count is None ) or
            ( True if card in full_deck else False )
        )
        if ( add_buttons ):
            for name_t, color_t, label_t in name_color_label_tuple_list:
                button_list.append(
                    sg.Button(
                        label_t,
                        button_color=color_t,
                        key="move_{}_{}_{}".format(name,name_t,card),
                        visible=visible_row,
                    )
                )
        out_layout.append([
            sg.Text(
                card_len_str_f.format(card),
                key="{}_{}_name".format(name,card),
                font=font,
                visible=visible_row,
            )
        ])
        if count:
            end_text = None
            if ( card =='all' ):
                end_text = ""
            else:
                end_text = "{:2d}".format(
                    0 if card not in full_deck else int(full_deck[card])
                )
            out_layout[-1] += sg.Text(
                "{:2s}".format(str(end_text)),
                key="{}_{}_count".format(name,card),
                font=font,
                visible=visible_row,
            ),
        out_layout[-1] += button_list
    return out_layout


def gen_game_move_buttons_col(
    name,
    name_color_label_tuple_list,
    kingdom_cards,
    cards_to_count=None,
    count=True,
    add_all=False,
    add_buttons=True,
):
    out_layout = gen_game_move_buttons(
        name,
        name_color_label_tuple_list,
        kingdom_cards,
        cards_to_count,
        count,
        add_all,
        add_buttons,
    )
    rotated_out_layout = [[x[i] for x in out_layout] for i in range(len(out_layout[0]))]
    new_out = [ sg.Column([ [col] for col in row ]) for row in rotated_out_layout ]
    return sg.Column( [new_out] )


def gen_deck_stats( pile_list ):
    pile_count_list = [ pile.count_cards() for pile in pile_list ]
    full_deck = bf.combine_deck_count( pile_count_list )
    analysis_deck = bf.analyze_deck( full_deck )
    return analysis_deck


def gen_stat_string_dict( stat_dict ):

    max_char_len = max( [len(key) for key in stat_dict.keys()] )
    name_format_str = "{:"+str(max_char_len)+"s}: "

    out_dict = {}

    for key, val in stat_dict.items():
        out_dict[key] = (name_format_str+"{:0.3f}").format(key,val) if isinstance(val,float) \
            else (name_format_str+"{:5d}").format(key,val)

    return out_dict


def gen_formatted_stat_list( name, stat_dict, font = ('Ubuntu Mono',10), color = 'white', width = 3 ):

    stat_strings = gen_stat_string_dict( stat_dict )

    length = math.ceil( len(stat_dict) / 2. )
    if ( (len(stat_dict) // 2) != length ):
        length += 1

    formatted_list = []
    i = 1
    this_list = []
    for key, val in stat_strings.items():
        if ( i % length == 0 ):
            formatted_list.append(sg.Column(this_list))
            this_list=[]
        this_list.append([
            sg.Text(
                val,
                text_color=color,
                font=font,
                key="status_{}_{}".format(name,key)
            )
        ])
        i+=1
    formatted_list.append(sg.Column(this_list))
    return sg.Column([formatted_list])


def gen_deck_stats_layout( name, pile_list ):
    analysis_deck = gen_deck_stats( pile_list )
    stat_layout_deck = gen_formatted_stat_list( name, analysis_deck )
    return stat_layout_deck


def gen_deck_stats_formatted( name, pile_list ):
    return [[gen_deck_stats_layout(name,pile_list)]]


def update_deck_stats( name, pile_list, kingdom_cards, window ):
    analysis_deck = gen_deck_stats( pile_list )
    stat_strings = gen_stat_string_dict( analysis_deck )

    pile_count_list = [ pile.count_cards() for pile in pile_list ]
    full_deck = bf.combine_deck_count( pile_count_list )

    for key, val in stat_strings.items():
        window["status_{}_{}".format(name,key)].update( val )

    for card in kingdom_cards:
        window["{}_{}_count".format(name,card)].update(
            "{:2d}".format(
                0 if card not in full_deck else int(full_deck[card])
            )
        )

        visible_row = False if (card not in full_deck) or (full_deck[card]<1) else True

        window["{}_{}_name".format(name,card)].update(
            visible = visible_row
        )
        window["{}_{}_count".format(name,card)].update(
            visible = visible_row
        )

        if ( name != 'deck' ):
            for other_name in ['kingdom','draw','hand','discard']:
                if ( name != other_name ):
                    window["move_{}_{}_{}".format(name,other_name,card)].update(
                        visible = visible_row
                    )
    '''
    if ( name != 'deck' ):
        #for card, count in full_deck.items():
        for card in kingdom_cards:
            window["{}_{}_count".format(name,card)].update(
                "{:2d}".format(
                    0 if card not in full_deck else int(full_deck[card])
                )
            )

            visible_row = False if (card not in full_deck) or (full_deck[card]<1) else True

            window["{}_{}_name".format(name,card)].update(
                visible = visible_row
            )
            window["{}_{}_count".format(name,card)].update(
                visible = visible_row
            )

            for other_name in ['kingdom','draw','hand','discard']:
                if ( name != other_name ):
                    window["move_{}_{}_{}".format(name,other_name,card)].update(
                        visible = visible_row
                    )
    '''



def run_game_analysis_window( kind_card_list_dict ):
    dc_all_cards = dominion_cards.all_valid_cards
    kingdom_dict = {}
    for kind, card_list in kind_card_list_dict.items():
        for card in card_list:
            kingdom_dict[card] = cards.CardSupply( dc_all_cards[card], 1000 )
    kingdom_cards = list(kingdom_dict.keys())

    hand = cards.CardPile('Hand')
    draw = cards.CardPile('Draw')
    discard = cards.CardPile('Discard')

    if ( 'copper' in kingdom_cards ):
        draw.topdeck( 7*[ dc_all_cards['copper'] ] )
    if ( 'estate' in kingdom_cards ):
        draw.topdeck( 3*[ dc_all_cards['estate'] ] )

    k_color = "black"
    d_color = "blue"
    h_color = "red"
    x_color = "dark green"
    e_color = "white"
    section_title_font = ('Axial',20)

    layout_K  = [[sg.Text("Kingdom",text_color=k_color,font=section_title_font)],[sg.HSeparator()]]
    buttons_K = gen_game_move_buttons_col(
        "kingdom",
        [
            ( "draw"   , d_color, "D", ),
            ( "hand"   , h_color, "H", ),
            ( "discard", x_color, "X", ),
        ],
        kingdom_cards,
        None,
        False,
        False,
        True,
    )
    layout_K = sg.Column( layout_K + [ [ buttons_K ] ] )

    layout_D = [[sg.Text("Draw",text_color=d_color,font=section_title_font)],[sg.HSeparator()]]
    cards_D = gen_game_move_buttons(
        "draw",
        [
            ( "kingdom", k_color, "K", ),
            ( "hand"   , h_color, "H", ),
            ( "discard", x_color, "X", ),
        ],
        kingdom_cards,
        [draw],
        True,
        True,
        True,
    )
    cards_D = sg.Column(cards_D)
    stat_layout_D = gen_deck_stats_layout( "draw", [draw] )
    layout_D = sg.Column( layout_D + [ [ cards_D, stat_layout_D ] ] )

    layout_H = [[sg.Text("Hand",text_color=h_color,font=section_title_font)],[sg.HSeparator()]]
    cards_H = gen_game_move_buttons(
        "hand",
        [
            ( "kingdom", k_color, "K", ),
            ( "draw"   , d_color, "D", ),
            ( "discard", x_color, "X", ),
        ],
        kingdom_cards,
        [hand],
        True,
        True,
        True,
    )
    cards_H = sg.Column(cards_H)
    stat_layout_H = gen_deck_stats_layout( "hand", [hand] )
    layout_H = sg.Column( layout_H + [ [ cards_H, stat_layout_H ] ] )

    layout_X = [[sg.Text("Discard",text_color=x_color,font=section_title_font)],[sg.HSeparator()]]
    cards_X = gen_game_move_buttons(
        "discard",
        [
            ( "kingdom", k_color, "K", ),
            ( "draw"   , d_color, "D", ),
            ( "hand"   , h_color, "H", ),
        ],
        kingdom_cards,
        [discard],
        True,
        True,
        True,
    )
    cards_X = sg.Column(cards_X)
    stat_layout_X = gen_deck_stats_layout( "discard", [discard] )
    layout_X = sg.Column( layout_X + [ [ cards_X, stat_layout_X ] ] )

    layout_Deck = [[sg.Text("Deck",text_color=e_color,font=section_title_font)],[sg.HSeparator()]]
    cards_Deck = gen_game_move_buttons(
        "deck",
        None,
        kingdom_cards,
        [draw,hand,discard],
        True,
        False,
        False,
    )
    cards_Deck = sg.Column(cards_Deck)
    stat_layout_Deck = gen_deck_stats_layout(
        "deck",
        [hand,draw,discard]
    )
    layout_Deck = sg.Column( layout_Deck + [ [ cards_Deck, stat_layout_Deck ] ] )

    '''
    tool_layout = [
        [layout_K,sg.VSeparator(),layout_Deck],
        [sg.HSeparator()],
        [layout_D,sg.VSeparator(),layout_H,sg.VSeparator(),layout_X]
    ]
    left_col = [
        [layout_K],
        [sg.HSeparator()],
        [layout_Deck],
    ]
    right_col = [
        [layout_D],
        [sg.HSeparator()],
        [layout_H],
        [sg.HSeparator()],
        [layout_X],
    ]
    tool_layout = [
        [
            sg.Column(left_col),
            sg.VSeparator(),
            sg.Column(right_col)
        ]
    ]
    '''
    left_col = [
        [layout_K],
    ]
    mid_col = [
        [layout_Deck],
        [sg.HSeparator()],
        [layout_D],
    ]
    right_col = [
        [layout_H],
        [sg.HSeparator()],
        [layout_X],
    ]
    tool_layout = [
        [
            sg.Column(left_col),
            sg.VSeparator(),
            sg.Column(mid_col),
            sg.VSeparator(),
            sg.Column(right_col)
        ]
    ]

    window = sg.Window(
        title="Analysis",
        layout=tool_layout,
    )

    pile_name_list = ["kingdom","draw","hand","discard"]

    pile_dict = {
        'kingdom': kingdom_dict,
        'draw': draw,
        'hand': hand,
        'discard': discard,
    }

    update_dict = {
        'kingdom': ('deck',[draw,hand,discard]),
        'draw': ('draw',[draw]),
        'hand': ('hand',[hand]),
        'discard': ('discard',[discard]),
    }

    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if (event == sg.WIN_CLOSED):
            break

        elif (event.startswith("move")):
            e_parsed = event.split("_")
            origin_pile = e_parsed[1]
            destination_pile = e_parsed[2]
            card_name = e_parsed[3]

            origin = pile_dict[ origin_pile ]
            destination = pile_dict[ destination_pile ]

            n_cards = 0
            if (
                isinstance(origin,dict) and
                (card_name in origin) and
                isinstance(origin[card_name],cards.CardSupply)
            ):
                n_cards = origin[card_name].count()
            elif ( isinstance(origin,cards.CardPile) ):
                count_dict = origin.count_cards()
                if ( card_name in count_dict ):
                    n_cards = count_dict[card_name]
                elif ( card_name == 'all' ):
                    for key, val in count_dict.items():
                        n_cards += val

            if ( n_cards > 0 ):
                # Move card around
                if ( isinstance(destination,cards.CardPile) ):
                    if ( card_name == 'all' ):
                        destination.stack += origin.stack
                    else:
                        destination.topdeck( dc_all_cards[card_name] )

                if ( isinstance(origin,cards.CardPile) ):
                    if ( card_name == 'all' ):
                        origin.stack = []
                    else:
                        origin.stack.remove( dc_all_cards[card_name] )

                # Update stats
                for update_name in [origin_pile,destination_pile]:
                    pile_to_update, piles = update_dict[update_name]
                    update_deck_stats( pile_to_update, piles, kingdom_cards, window )

    window.close()


def main( inp_path = None ):

    kingdom_card_activation_dict, game_card_dict, all_cards_by_kind = gen_default_card_dicts()

    this_game_name = default_game_name

    window = gen_kingdom_window(
        default_window_title,
        default_window_margins,
        game_card_dict[this_game_name],
        kingdom_card_activation_dict,
        all_cards_by_kind
    )

    while True:

        event, values = window.read()
        if ( event == sg.WIN_CLOSED ):
            break

        elif ( event == "Kingdom_Reset" ):
            kingdom_card_activation_dict, game_card_dict, all_cards_by_kind = gen_default_card_dicts()
            window.close()
            window = gen_kingdom_window(
                default_window_title,
                default_window_margins,
                game_card_dict[this_game_name],
                kingdom_card_activation_dict,
                all_cards_by_kind
            )
            continue

        elif ( event == "Kingdom_Accept" ):
            cards_to_use = {}
            for kind in all_cards_by_kind:
                cards_to_use[kind] = []
                for card in all_cards_by_kind[kind]:
                    if ( kingdom_card_activation_dict[card] ):
                        cards_to_use[kind].append(card)
            stored_window = window
            window.close()
            run_game_analysis_window( cards_to_use )
            window=stored_window
            continue

        # Update cards that are selected from a game
        for card_name in game_card_dict[this_game_name]:
            if ( event in ("supply_"+card_name,"kingdom_"+card_name) ):
                kingdom_card_activation_dict[card_name] = not kingdom_card_activation_dict[card_name]
                window["supply_"+card_name].update(
                    button_color = get_button_color( kingdom_card_activation_dict[card_name] )
                )
                window["kingdom_"+card_name].update(
                    button_color = get_button_color( kingdom_card_activation_dict[card_name] ),
                    visible = kingdom_card_activation_dict[card_name]
                )

                break

    window.close()


if ( __name__=='__main__' ):
    main(project_path)
