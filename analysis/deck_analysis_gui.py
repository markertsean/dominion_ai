import sys
import os
import copy
import math

import PySimpleGUI as sg

project_path = '/'.join( __file__.split('/')[:-2] )+'/'
sys.path.append(project_path)

from decks import cards,dominion_cards
from brains import brain_functions as bf


class Kingdom_Selector_Window():
    def __init__(self):
        self.game_ref = dominion_cards.game_expansion_reference

        # Base game will be used to build intial window,
        # using victory cards and coins
        self.default_game_name = 'base'
        self.default_game = self.game_ref[self.default_game_name]

        self.default_treasure_card_list = list(self.default_game['treasure'].keys())
        self.default_victory_card_list  = list(self.default_game['victory' ].keys())
        self.default_kingdom_card_list  = list(self.default_game['kingdom' ].keys())

        self.default_window_title = "Dominion Hand Analyzer"
        self.default_window_margins = (200,200)


        self.this_game_name = self.default_game_name

        self.kingdom_card_activation_dict,\
            self.game_card_dict,\
            self.all_cards_kind_dict = self.gen_default_card_dicts()

        self.window = None
        self.reset_window()

    # Red buttons off, green buttons on
    def get_button_color( self, inp ):
        assert isinstance(inp,(bool,str,))
        if isinstance(inp,str):
            status = self.kingdom_card_activation_dict[inp]
        else:
            status=inp
        if (status):
            return 'green'
        return 'red'

    # Create dicts for card on/off, cards in game/expansion, category active cards are in
    def gen_default_card_dicts(self):
        # Create bool list of cards by game name
        kingdom_card_activation_dict = {} # Key is card name, val is whether toggled
        game_card_dict = {}               # Key is expansion name, value is list of all cards originating from it
        all_cards_by_kind = {}            # For the layout on the right side of the kindom building panel

        for game_name in self.game_ref.keys():
            game_card_dict[game_name] = []
            for kind in ['victory','treasure','kingdom']:
                if ( kind in self.game_ref[game_name] ):
                    if ( kind not in all_cards_by_kind ):
                        all_cards_by_kind[kind] = []
                    for card in self.game_ref[game_name][kind]:
                        all_cards_by_kind[kind].append(card)
                        if (
                            (card in self.default_treasure_card_list) or
                            (card in self.default_victory_card_list)
                        ):
                            kingdom_card_activation_dict[card] = True
                        else:
                            kingdom_card_activation_dict[card] = False

                        game_card_dict[game_name].append( card )
        return kingdom_card_activation_dict, game_card_dict, all_cards_by_kind


    def gen_kingdom_window( self, game_name ):
        game_card_list = self.game_card_dict[game_name]

        gen_layout = self.gen_kingdom_display_layout( game_card_list )
        gen_layout_copy = copy.deepcopy( gen_layout )

        return sg.Window(
            title=self.default_window_title,
            layout=gen_layout_copy,
            margins=self.default_window_margins,
            element_justification='c'
        )


    def gen_selectable_card_buttons_from_kingdom( self, inp_game_card_list ):
        out_button_list = []
        for card in inp_game_card_list:
            out_button_list.append(
                sg.Button(
                    card,
                    button_color=self.get_button_color( self.kingdom_card_activation_dict[card] ),
                    key="supply={}".format(card),
                )
            )
        return out_button_list


    def gen_formatted_button_list( self, button_list, width=5 ):
        formatted_list = [[]]
        i = width
        for button in button_list:
            if ( i % width == 0 ):
                formatted_list.append([])
            formatted_list[-1].append(button)
            i+=1
        return formatted_list


    def gen_kingdom_display_layout( self, inp_game_card_list ):
        game_buttons = self.gen_selectable_card_buttons_from_kingdom(
            inp_game_card_list
        )

        # Format the column as scrolling is not an option
        game_button_list_formatted = self.gen_formatted_button_list( game_buttons )

        game_column_selectable_kingdom_cards = sg.Column(
            [[sg.Text("Possible Cards:")]] +
            game_button_list_formatted
        )

        kingdom_kind_dict = {}
        kingdom_kind_formatted_dict = {}
        for kind in self.all_cards_kind_dict:
            kingdom_kind_dict[kind] = []
            for card_name in self.all_cards_kind_dict[kind]:
                button = sg.Button(
                    card_name,
                    button_color=self.get_button_color( self.kingdom_card_activation_dict[card_name] ),
                    visible=self.kingdom_card_activation_dict[card_name],
                    key="kingdom={}".format(card_name),
                )
                kingdom_kind_dict[kind].append( button )
            kingdom_kind_formatted_dict[kind] = self.gen_formatted_button_list( kingdom_kind_dict[kind] )

        game_column_selected_kingdom_cards = sg.Column(
            [[sg.Text("Victory Cards:")]] +
            kingdom_kind_formatted_dict['victory'] +
            [[sg.Text("Treasure Cards:")]] +
            kingdom_kind_formatted_dict['treasure'] +
            [[sg.Text("Kingdom Cards:")]] +
            kingdom_kind_formatted_dict['kingdom']
        )

        kingdom_select_pad_hspace = 400
        kingdom_select_pad_vspace = 20

        default_kingdom_selector_layout_start = [
            [sg.Text("Select your kingdom cards!",justification='top')],
            [sg.HSeparator(pad=(kingdom_select_pad_hspace,kingdom_select_pad_vspace))],
        ]

        default_kingdom_selector_layout_end = [
            [sg.HSeparator(pad=(kingdom_select_pad_hspace,kingdom_select_pad_vspace))],
            [sg.Button("Accept",key='Kingdom=Accept'),sg.Button("Reset",key='Kingdom=Reset')]
        ]

        return default_kingdom_selector_layout_start +         [
                [
                    game_column_selectable_kingdom_cards,
                    sg.VSeparator(),
                    game_column_selected_kingdom_cards,
                ]
            ] + \
            default_kingdom_selector_layout_end


    def gen_window( self, game_name ):
        assert game_name in self.game_ref.keys()
        return self.gen_kingdom_window(
            game_name
        )

    def reset_window( self ):
        if ( self.window is not None ):
            self.window.close()
        self.kingdom_card_activation_dict,\
            self.game_card_dict,\
            self.all_cards_kind_dict = self.gen_default_card_dicts()
        self.window = self.gen_window(
            self.default_game_name
        )
