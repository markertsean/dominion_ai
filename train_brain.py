#!/usr/bin/env python
# coding: utf-8

import random
import sys
import os

project_path = '/'.join(__file__.split('/')[:-1])+'/'
sys.path.append(project_path)

import decks
from player.player import Player
from games import game_engine
from util import settings
from util.logger import GameResultsLogger
from util.logger import game_logger as gamelog
from brains import buy_brains

def init_players( inp_settings ):
    player_names = ['Alice','Bill','Cindy','Dan']
    player_list = []
    for i in range(0,inp_settings['n_players']):

        p_str = "player_{}".format(i+1)

        # Set up buy_brain, default to 0
        buy_brain = buy_brains.buy_brain_dict['random']()
        bb_str = p_str+"_buy_brain"
        if (
            (bb_str in inp_settings.keys()) and
            (inp_settings[bb_str] is not None ) and
            (inp_settings[bb_str] != 'random' )
        ):
            n_lower = 0
            brain = buy_brains.buy_brain_dict[ inp_settings[bb_str] ]
            if ( bb_str+"_n_lower" in inp_settings.keys() ):
                n_lower = inp_settings[bb_str+"_n_lower"]
            buy_brain = brain(n_lower)

        player_list.append( Player(
            player_names[i],
            buy_brain=buy_brain,
            logger=gamelog
        ))

    return player_list


'''
Main method does a few things:
    Read in settings
    Set up logger
    Loop over games
'''
def main( config_fn ):

    inp_settings = settings.read_settings( config_fn, True )

    results_logger = GameResultsLogger()

    # Activate logger if logging, and save settings
    if (
        ( isinstance(inp_settings['log'],bool) and inp_settings['log'] ) or
        ( isinstance(inp_settings['log'],float) )
    ):
        results_logger.start_logger()
        gamelog.start_logger(debug=inp_settings['debug'])
        gamelog.activate()
        if ( inp_settings['print'] ):
            gamelog.activate_print_log()
        else:
            gamelog.deactivate_print_log()
    else:
        for key in inp_settings:
            print(key+"\t"+str(inp_settings[key]))

    for key in inp_settings.keys():
        gamelog.log("SETTING: {}={}".format(key,inp_settings[key]))

    # Set up players
    player_list = init_players( inp_settings )
    for p in player_list:
        print(p.buy_brain)
    old_player_order_list = [player_list[-1]] + player_list[:-1]

    win_list = []

    for game_num in range(0,inp_settings['n_games']):

        # Either log is always on, or probabilistically on to avoid excessive logging of games
        gamelog.deactivate()
        if (
            ( isinstance(inp_settings['log'],bool ) and inp_settings['log'] ) or
            (
                isinstance(inp_settings['log'],float) and
                ( inp_settings['log']>=random.random() )
            )
        ):
            gamelog.activate()

        gamelog.log("TABLE: game {} {}".format(game_num,50*'='))

        # Rotate first player
        player_order_list = old_player_order_list[1:] + [old_player_order_list[0]]
        old_player_order_list = player_order_list

        gamelog.log("TABLE: players {}".format(
            ' '.join(["{}-{}".format(i,player_order_list[i].name) for i in range(0,len(player_order_list))])
        ))

        this_game = game_engine.DominionGame(
            kingdom=inp_settings['kingdom'],
            n_players=len(player_order_list),
            max_turns=inp_settings['max_turns'],
            logger=gamelog,
        )

        player_points, player_cards = this_game.run_game( player_order_list )
        for name in player_points.keys():
            card_count = player_cards[name]
            player_str ="player='{}' victory_points={} cards={{{}}}".format(
                name,
                player_points[name],
                " ".join(["'{}':{},".format(card,card_count[card]) for card in sorted(card_count.keys()) ])
            )
            gamelog.log("TABLE: "+player_str)
            results_logger.log("game='{}' ".format(game_num)+player_str)

            print("game '{}' ".format(game_num)+player_str)

    gamelog.close_log()


if ( __name__=='__main__' ):
    settings_file = 'train.conf'
    if ( len(sys.argv) > 1 ):
        settings_file = sys.argv[1]
    main(project_path+settings_file)
