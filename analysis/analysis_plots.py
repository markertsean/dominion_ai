import random
import os
import sys
import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

import util.input_output as io
import decks.dominion_cards as dc

plt.rcParams['figure.figsize'] = (14,10)
plt.style.use('dark_background')

__province_metric = 3

__date_set = False
__output_date = None

def set_image_output_path( date_str ):
    assert isinstance(date_str,str)
    global __date_set
    global __output_date
    __output_date = date_str
    __date_set = True

def get_output_image_path():
    assert __date_set
    image_path = io.get_data_path() + "analysis/" + __output_date
    if ( image_path[-1] != '/' ):
        image_path += '/'
    os.makedirs(image_path,exist_ok=True)
    return image_path

def get_latest_game_file():
    file_path = io.get_game_turn_path()
    return io.get_latest_dated_file(file_path)

def get_province_metric():
    global __province_metric
    return __province_metric

def get_point_metric():
    return 6 * get_province_metric()

def player_color(inp_df,col='player'):
    player_colors = ['r','g','b','m','c','y']
    player_names = inp_df[col].unique()
    color_dict = {}
    for i in range(0,len(player_names)):
        color_dict[player_names[i]] = player_colors[i]
    return color_dict

def player_color_series( inp_df, col='player' ):
    color_dict = player_color(inp_df,col)
    colors = inp_df[col].replace(color_dict)
    return colors

def player_verbose_label( inp_settings, inp_df, col='player' ):
    player_names = sorted(inp_df[col].unique())
    label_dict = {}
    for i in range(0,len(player_names)):
        label_dict[player_names[i]] = "{}\nBuy: {}\nAct: {}".format(
            player_names[i],
            ' '.join([str(val) for key,val in inp_settings.items() if 'player_{}_buy_brain'.format(i+1) in key ]),
            ' '.join([str(val) for key,val in inp_settings.items() if 'player_{}_action_brain'.format(i+1) in key ])
        )
    return label_dict

def get_all_game_pkls( file_date ):
    max_turns = 0
    game_file_path = io.get_game_turn_path() + file_date + "/"
    assert os.path.exists(game_file_path), game_file_path + " does not exist!"
    game_file_list = os.listdir( game_file_path )
    
    game_dict = {}
    game_turn_list = []
    settings = None
    for game_file_name in sorted(game_file_list):
        # Sloppy check for game_N.pkl
        if (game_file_name.startswith("game_") and game_file_name.endswith(".pkl")):
            file_name = game_file_path + game_file_name
            with open( file_name, 'rb' ) as f:
                input_pkl = pkl.load( f )
                if (settings is None ):
                    settings = input_pkl['input_settings']

                game_num = input_pkl["game_number"]
                game_dict[game_num] = {}
                game_dict[game_num]['kingdom_cards'] = input_pkl['kingdom_cards']
                game_dict[game_num]['turn_order'   ] = input_pkl['turn_order'   ]
                game_dict[game_num]['final_vp'     ] = input_pkl['final_vp'     ]
                game_dict[game_num]['final_cards'  ] = input_pkl['final_cards'  ]
                
                for turn_num, turn in input_pkl["turns"].items():
                    for player, p_turn in turn.items():
                        row = {}
                        row['game'  ] = game_num
                        row['turn'  ] = turn_num
                        row['player'] = player
                        for key,item in p_turn.items():
                            row[key] = item
                        game_turn_list.append(row)
                
    turn_df = pd.DataFrame.from_records( game_turn_list )
    return settings, game_dict, turn_df

def gen_vp_avg_plot( game_settings, game_data, turn_df, output_image=False, min_count=3 ):
    assert isinstance(output_image,bool)

    kingdom_name = game_settings['kingdom']

    color_dict = player_color( turn_df )
    label_dict = player_verbose_label( game_settings, turn_df )

    # Groupby player, average points per turn over each game
    points_df = turn_df[
        ['turn','player','victory_points_end','colors']
    ].copy().rename({'victory_points_end':'victory_points'},axis=1)
    points_group = points_df.groupby(['player','turn'],as_index=False).agg({'victory_points':['mean','std','count']})
    points_group = points_group.loc[points_group[('victory_points','count')]>min_count]
    points_group['colors'] = player_color_series(points_group)
    
    title_str = "Time to {} provinces:".format(get_province_metric())
    plt.clf()
    for player in sorted(points_group.player.unique()):
        player_df = points_group.loc[points_group['player']==player]
        plt.fill_between(
            player_df['turn'],
            player_df[('victory_points','mean')] - player_df[('victory_points','std')],
            player_df[('victory_points','mean')] + player_df[('victory_points','std')],
            color=color_dict[player],
            alpha=0.2,
        )
        plt.plot(
            player_df['turn'],
            player_df[('victory_points','mean')],
            label=label_dict[player],
            color=color_dict[player],
        )
        ind = player_df[('victory_points','mean')] >= get_point_metric()
        title_str += " {} {} turns,".format(player,player_df.loc[ind,'turn'].min())
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.legend(loc=2,fontsize=8)
    plt.title(title_str)
    plt.xlabel("Turn")
    plt.ylabel("Victory Points (Average)")
    if ( not output_image ):
        plt.show()
    else:
        out_path = get_output_image_path()
        full_fn_path = out_path + "vp_average_turn.png"
        plt.savefig(full_fn_path)
        print("Wrote "+full_fn_path)
        
def gen_vp_sum_plot( game_settings, game_data, turn_df, output_image=False, min_count=3 ):
    assert isinstance(output_image,bool)

    kingdom_name = game_settings['kingdom']

    color_dict = player_color( turn_df )
    label_dict = player_verbose_label( game_settings, turn_df )

    # Groupby player, average points per turn over each game
    points_df = turn_df[
        ['turn','player','victory_points_end','colors']
    ].copy().rename({'victory_points_end':'victory_points'},axis=1)
    points_group = points_df.groupby(['player','turn'],as_index=False).agg({'victory_points':['sum','count']})
    points_group['colors'] = player_color_series(points_group)
    
    plt.clf()
    for player in sorted(points_group.player.unique()):
        player_df = points_group.loc[points_group['player']==player].copy()
        x = player_df[('victory_points','sum')].values
        x=x[::-1]
        for i in range(0,x.shape[0]):
            x[i] += x[i:].sum()
        x=x[::-1]
        player_df[('victory_points','sum')] = x*1./game_settings['n_games']
        plt.plot(
            player_df['turn'],
            player_df[('victory_points','sum')],
            label=label_dict[player],
            color=color_dict[player],
        )
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.legend(loc=2,fontsize=8)
    plt.title("Cumulative Victory Points / Number of Games")
    plt.xlabel("Turn")
    plt.ylabel("Victory Points (Cumulative Average)")
    if ( not output_image ):
        plt.show()
    else:
        out_path = get_output_image_path()
        full_fn_path = out_path + "vp_cumulative_turn.png"
        plt.savefig(full_fn_path)
        print("Wrote "+full_fn_path)

def gen_first_last_avg_plot( game_settings, game_data, turn_df, output_image=False, n_games=5, min_count=3 ):
    assert isinstance(output_image,bool)

    kingdom_name = game_settings['kingdom']

    color_dict = player_color( turn_df )
    label_dict = player_verbose_label( game_settings, turn_df )

    # Groupby player, average points per turn over each game
    points_df_start = turn_df.loc[
        turn_df['game']<n_games,
        ['turn','player','victory_points_end','colors']
    ].copy().rename({'victory_points_end':'victory_points'},axis=1)
    points_df_end = turn_df.loc[
        turn_df['game']>turn_df['game'].max()-n_games,
        ['turn','player','victory_points_end','colors']
    ].copy().rename({'victory_points_end':'victory_points'},axis=1)
    
    points_group_start = points_df_start.groupby(['player','turn'],as_index=False).agg({'victory_points':['mean','std','count']})
    points_group_end   = points_df_end  .groupby(['player','turn'],as_index=False).agg({'victory_points':['mean','std','count']})

    points_group_start = points_group_start.loc[points_group_start[('victory_points','count')]>min_count]
    points_group_end   = points_group_end  .loc[points_group_end  [('victory_points','count')]>min_count]

    
    plt.clf()
    for group_df, style in zip([points_group_start,points_group_end],['-','--']):
        for player in sorted(group_df.player.unique()):
            player_df = group_df.loc[group_df['player']==player]
            label = None
            if (style=='-'):
                label=label_dict[player]
            plt.fill_between(
                player_df['turn'],
                player_df[('victory_points','mean')] - player_df[('victory_points','std')],
                player_df[('victory_points','mean')] + player_df[('victory_points','std')],
                color=color_dict[player],
                alpha=0.2,
                linestyle=style,
            )
            plt.plot(
                player_df['turn'],
                player_df[('victory_points','mean')],
                label=label,
                color=color_dict[player],
                linestyle=style,
            )
            ind = player_df[('victory_points','mean')] >= get_point_metric()
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.legend(loc=2,fontsize=8)
    plt.xlabel("Turn")
    plt.ylabel("Victory Points (Average)")
    if ( not output_image ):
        plt.show()
    else:
        out_path = get_output_image_path()
        full_fn_path = out_path + "vp_first_last_turn.png"
        plt.savefig(full_fn_path)
        print("Wrote "+full_fn_path)

def gen_cum_wins( game_settings, game_data, turn_df, output_image=False ):
    assert isinstance(output_image,bool)

    x = []
    y = {}
    for player in game_data[list(game_data.keys())[0]]['final_vp'].keys():
        y[player] = []

    for game_num in sorted(game_data.keys()):
        game_score = game_data[game_num]['final_vp']
        x.append(game_num)
        high_score = 0
        for player in game_score.keys():
            if ( game_score[player] > high_score ):
                high_score = game_score[player]
        for player in game_score.keys():
            if ( game_score[player] == high_score ):
                if ( len(y[player]) == 0 ):
                    y[player].append(1)
                else:
                    y[player].append( y[player][-1] + 1 )
            else:
                if ( len(y[player]) == 0 ):
                    y[player].append(0)
                else:
                    y[player].append( y[player][-1] )

    color_dict = player_color( turn_df )
    label_dict = player_verbose_label( game_settings, turn_df )

    plt.clf()
    for player in sorted(y.keys()):
        plt.plot(
            x,
            np.array(y[player]) / max(x),
            label=label_dict[player],
            color=color_dict[player],
        )
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.legend(loc=2,fontsize=8)
    plt.title("Cumulative wins over {} games".format(max(x)))
    plt.xlabel("Turn")
    plt.ylabel("Cumulative Wins / N Games")
    if ( not output_image ):
        plt.show()
    else:
        out_path = get_output_image_path()
        full_fn_path = out_path + "win_cumulative_turn.png"
        plt.savefig(full_fn_path)
        print("Wrote "+full_fn_path)

