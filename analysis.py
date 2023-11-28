import sys
import os
import copy

import PySimpleGUI as sg

project_path = os.getcwd()+'/'
sys.path.append(project_path)

from decks import cards,dominion_cards



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


def gen_window( title, margins, game_card_list, kingdom_card_activation_dict, all_card_kind_dict ):
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


def main( inp_path = None ):

    kingdom_card_activation_dict, game_card_dict, all_cards_by_kind = gen_default_card_dicts()

    this_game_name = default_game_name

    window = gen_window(
        default_window_title,
        default_window_margins,
        game_card_dict[this_game_name],
        kingdom_card_activation_dict,
        all_cards_by_kind
    )

    while True:

        event, values = window.read()
        print(event,values)
        if ( event == sg.WIN_CLOSED ):
            break

        elif ( event == "Kingdom_Reset" ):
            kingdom_card_activation_dict, game_card_dict, all_cards_by_kind = gen_default_card_dicts()
            window.close()
            window = gen_window(
                default_window_title,
                default_window_margins,
                game_card_dict[this_game_name],
                kingdom_card_activation_dict,
                all_cards_by_kind
            )
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
