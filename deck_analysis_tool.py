import sys
import os
import copy
import math

import PySimpleGUI as sg

project_path = os.getcwd()+'/'
sys.path.append(project_path)

from decks import cards,dominion_cards
from brains import brain_functions as bf
from analysis import deck_analysis_gui as dag



def main():

    kingdom_builder = dag.KingdomSelectorWindow()

    while True:

        event, values = kingdom_builder.window.read()
        if ( event == sg.WIN_CLOSED ):
            break

        elif ( event == "Kingdom=Reset" ):
            kingdom_builder.reset_window()
            continue

        elif ( event == "Kingdom=Accept" ):
            cards_to_use = {}
            for kind in kingdom_builder.all_cards_kind_dict:
                cards_to_use[kind] = []
                for card in kingdom_builder.all_cards_kind_dict[kind]:
                    if ( kingdom_builder.kingdom_card_activation_dict[card] ):
                        cards_to_use[kind].append(card)

            game_window = dag.GameWindow( cards_to_use, mod_stats=kingdom_builder.mod_stats )
            game_window.run()

            continue

        elif ( event == "Kingdom=ModStats" ):

            kingdom_builder.flip_mod_stats_button()

            continue

        # Update cards that are selected from a game
        for card_name in kingdom_builder.kingdom_card_activation_dict.keys():
            if ( event in ("supply={}".format(card_name),"kingdom={}".format(card_name)) ):

                kingdom_builder.kingdom_card_activation_dict[card_name] = \
                    not kingdom_builder.kingdom_card_activation_dict[card_name]

                card_on = kingdom_builder.kingdom_card_activation_dict[card_name]
                color   = kingdom_builder.get_button_color( card_on )

                kingdom_builder.window["supply={}".format(card_name)].update(
                    button_color = color
                )

                kingdom_builder.window["kingdom={}".format(card_name)].update(
                    button_color = color,
                    visible = card_on
                )

                break

    kingdom_builder.window.close()


if ( __name__=='__main__' ):
    main()
