import sys
import os
import copy

import PySimpleGUI as sg

project_path = '/'.join(__file__.split('/')[:-1])+'/'
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
    [sg.Button("Accept",key='Kingdom_Accept')]
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

def gen_kingdom_display_layout( inp_game_card_list, kingdom_card_status_dict ):
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
    
    victory_button_list = []
    treasure_button_list = []
    kingdom_button_list = []
    for card_name in kingdom_card_status_dict:
        if ( kingdom_card_status_dict[card_name] ):
            card_type = dominion_cards.all_valid_cards[card_name].type
            button = sg.Button(
                card_name,
                button_color=get_button_color( kingdom_card_status_dict[card_name] ),
                key="kingdom_"+card_name,
            )
            
            if (
                ( isinstance(card_type,str ) and ('treasure' == card_type) ) or
                ( isinstance(card_type,list) and ('treasure' in card_type) )
            ):
                treasure_button_list.append( button )
            elif (
                ( isinstance(card_type,str ) and ( ('victory' == card_type) or ('curse' == card_type) ) ) or
                ( isinstance(card_type,list) and ( ('victory' in card_type) or ('curse' in card_type) ) )
            ):
                victory_button_list.append( button )
            else:
                kingdom_button_list.append( button )

    victory_button_list_formatted  = gen_formatted_button_list(  victory_button_list )
    treasure_button_list_formatted = gen_formatted_button_list( treasure_button_list )
    kingdom_button_list_formatted  = gen_formatted_button_list(  kingdom_button_list )

    game_column_selected_kingdom_cards = sg.Column(
        [[sg.Text("Victory Cards:")]] +
        victory_button_list_formatted +
        [[sg.Text("Treasure Cards:")]] +
        treasure_button_list_formatted +
        [[sg.Text("Kingdom Cards:")]] +
        kingdom_button_list_formatted
    )

    return default_kingdom_selector_layout_start +         [
            [
                game_column_selectable_kingdom_cards,
                sg.VSeparator(),
                game_column_selected_kingdom_cards,
                #sg.Column(default_selected_kingdom_card_layout),
            ]
        ] + \
        default_kingdom_selector_layout_end


def gen_window( title, margins, game_card_list, kingdom_card_activation_dict ):
    gen_layout = gen_kingdom_display_layout(
        game_card_list,
        kingdom_card_activation_dict
    )
    gen_layout_copy = copy.deepcopy( gen_layout )
    return sg.Window(
        title=title,
        layout=gen_layout_copy,
        margins=margins,
        element_justification='c'
    )
    #return window


def main( inp_path = None ):
        
    treasure_card_list = default_treasure_card_list
    victory_card_list = default_victory_card_list

    # Create bool list of cards by game name
    kingdom_card_activation_dict = {} # Key is card name, val is whether toggled
    game_card_dict = {} # Key is game/expansion name, value is list of all cards originating from it
    for game_name in game_ref.keys():
        game_card_dict[game_name] = []
        for kind in ['victory','treasure','kingdom']:
            if ( kind in game_ref[game_name] ):
                for card in game_ref[game_name][kind]:
                    if (
                        (card in treasure_card_list) or
                        (card in victory_card_list)
                    ):
                        kingdom_card_activation_dict[card] = True
                    else:
                        kingdom_card_activation_dict[card] = False
                        
                    game_card_dict[game_name].append( card )
    
    
    reset = False
    
    this_game_name = default_game_name
    
    window = gen_window(
        default_window_title,
        default_window_margins,
        game_card_dict[this_game_name],
        kingdom_card_activation_dict
    )
    
    while True:
        
        event, values = window.read()
        print(event,values)
        if ( event == sg.WIN_CLOSED ):
            break

        # Update cards that are selected from a game
        for card_name in game_card_dict[this_game_name]:
            if event == "supply_"+card_name:
                kingdom_card_activation_dict[card_name] = not kingdom_card_activation_dict[card_name]
                window["supply_"+card_name].update(
                    button_color = get_button_color( kingdom_card_activation_dict[card_name] )
                )

                new_window = gen_window(
                    default_window_title,
                    default_window_margins,
                    game_card_dict[this_game_name],
                    kingdom_card_activation_dict
                )
                window.close()
                window=new_window
                
                break
            elif event == "kingdom_"+card_name:
                kingdom_card_activation_dict[card_name] = not kingdom_card_activation_dict[card_name]
                window["supply_"+card_name].update(
                    button_color = get_button_color( kingdom_card_activation_dict[card_name] )
                )

                new_window = gen_window(
                    default_window_title,
                    default_window_margins,
                    game_card_dict[this_game_name],
                    kingdom_card_activation_dict
                )
                window.close()
                window=new_window

                break
            
        if ( reset ):
            treasure_card_list = default_treasure_card_list
            victory_card_list = default_victory_card_list
            reset = False
                    
    window.close()

if ( __name__=='__main__' ):
    main(project_path)