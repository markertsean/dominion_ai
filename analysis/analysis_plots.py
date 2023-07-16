import random
import os
import sys
import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

import util.input_output as io
import decks.dominion_cards as dc
import decks.cards
import brains.brain_functions as bf

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
    a = player_df['turn'].values
    plt.xticks(np.arange(len(a)+2), np.arange(0, len(a)+2))
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
    a = player_df['turn'].values
    plt.xticks(np.arange(len(a)+2), np.arange(0, len(a)+2))
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

    points_group_start = points_df_start.groupby(
        ['player','turn'],
        as_index=False
    ).agg({'victory_points':['mean','std','count']})
    points_group_end   = points_df_end.groupby(
        ['player','turn'],
        as_index=False
    ).agg({'victory_points':['mean','std','count']})

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
    a = player_df['turn'].values
    plt.xticks(np.arange(len(a)+2), np.arange(0, len(a)+2))
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
    plt.xticks(x)
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


def gen_analysis_dfs( game_settings, game_data, turn_df, output_image=False ):

    game_nums = sorted( list(game_data.keys()) )
    player_list = sorted( list(game_data[game_nums[0]]['turn_order']) )

    game_num_dict = {}
    n_cards_dict = {}
    victory_points = {}
    deck_analysis = {}

    for player in player_list:
        game_num_dict[player] = []
        n_cards_dict[player] = []
        victory_points[player] = []
        deck_analysis[player] = {}

    # loop over each game, calculating metrics
    for game_num in game_nums:
        this_game = game_data[game_num]
        for player in player_list:
            game_num_dict[player].append( game_num )
            player_cards = this_game['final_cards'][player]
            n_cards_at_end = 0
            for card_name, card_count in player_cards.items():
                n_cards_at_end += card_count

            analysis = bf.analyze_deck( this_game['final_cards'][player] )

            n_cards_dict[player].append( n_cards_at_end )
            victory_points[player].append( this_game['final_vp'][player] )
            for key in analysis:
                if (key in deck_analysis[player]):
                    deck_analysis[player][key].append(analysis[key])
                else:
                    deck_analysis[player][key] = [analysis[key]]

    combined_dict = {
        "game":[],
        "player":[],
        "victory_points":[],
    }
    for player in player_list:
        for g_num,card_num,vp in zip(game_num_dict[player],n_cards_dict[player],victory_points[player]):
            combined_dict["player"].append( player )
            combined_dict["game"].append( g_num )
            combined_dict["victory_points"].append( vp )

        for key in deck_analysis[player]:
            if ( key in combined_dict ):
                combined_dict[key] += deck_analysis[player][key]
            else:
                combined_dict[key] = deck_analysis[player][key]
    game_result_df = pd.DataFrame( combined_dict ).sort_values(['game','player']).reset_index(drop=True)

    win_df = game_result_df[['game','victory_points','n_cards']].sort_values(
        ['victory_points','n_cards'],ascending=[False,True]
    ).drop_duplicates(['game']).reset_index(drop=True)
    win_df['win'] = 1

    game_result_df = game_result_df.merge(
        right=win_df,
        on=['game','victory_points','n_cards'],
        how='outer'
    ).fillna(0)

    all_turn_df = turn_df.copy()
    all_turn_df['deck_analysis'] = None
    for index, row in all_turn_df.iterrows():
        all_turn_df.at[index,'deck_analysis'] = bf.analyze_deck(
            bf.combine_deck_count(
                [ row['hand_start'], row['discard_start'], row['draw_start'] ]
            )
        )

    for key in all_turn_df.loc[0,'deck_analysis'].keys():
        all_turn_df[key] = 0.

    for index, row in all_turn_df.iterrows():
        deck_analysis = row['deck_analysis']
        for key,val in deck_analysis.items():
            all_turn_df.at[index,key] = val

    all_turn_df = all_turn_df[['game','turn','player','colors']+list(all_turn_df.loc[0,'deck_analysis'].keys())]

    return game_result_df, all_turn_df

def gen_turn_analysis_plots(
    game_settings,
    game_data,
    turn_df,
    turn_analysis_df,
    output_image=False,
    min_count=3,
    non_plot_cols=['game','turn','player','colors']
):
    anal_cols = []
    for col in turn_analysis_df.columns:
        if col not in non_plot_cols:
            anal_cols.append(col)

    color_dict = player_color( turn_df )
    label_dict = player_verbose_label( game_settings, turn_df )

    for col in anal_cols:
        # Groupby player, average points per turn over each game
        agg_df = turn_analysis_df[
            ['turn','player','colors',col]
        ].copy()
        agg_group = agg_df.groupby(['player','turn'],as_index=False).agg({col:['mean','std','count']})
        agg_group = agg_group.loc[agg_group[(col,'count')]>min_count]
        agg_group['colors'] = player_color_series(agg_group)

        plt.clf()
        for player in sorted(agg_group.player.unique()):
            player_df = agg_group.loc[agg_group['player']==player]
            plt.fill_between(
                player_df['turn'],
                player_df[(col,'mean')] - player_df[(col,'std')],
                player_df[(col,'mean')] + player_df[(col,'std')],
                color=color_dict[player],
                alpha=0.2,
            )
            plt.plot(
                player_df['turn'],
                player_df[(col,'mean')],
                label=label_dict[player],
                color=color_dict[player],
            )
        a = player_df['turn'].values
        plt.xticks(np.arange(len(a)+2), np.arange(0, len(a)+2))
        plt.xlim(left=1)
        plt.ylim(bottom=0)
        plt.legend(loc=2,fontsize=8)
        plt.xlabel("Turn")
        plt.ylabel("{} (Average)".format(col))
        plt.title("Average {} over hand in {} games:".format(col,game_settings['n_games']))
        if ( not output_image ):
            plt.show()
        else:
            out_path = get_output_image_path()
            full_fn_path = out_path + "turn_average_{}.png".format(col)
            plt.savefig(full_fn_path)
            print("Wrote "+full_fn_path)

def gen_game_analysis_plots(
    game_settings,
    game_data,
    turn_df,
    game_analysis_df,
    output_image=False,
    min_count=3,
    non_plot_cols=['game','turn','player','colors','win']
):
    anal_cols = []
    for col in game_analysis_df.columns:
        if col not in non_plot_cols:
            anal_cols.append(col)

    color_dict = player_color( turn_df )
    label_dict = player_verbose_label( game_settings, turn_df )
    '''
    ['game', 'player', 'victory_points', 'n_cards', 'action', 'buy', 'coin',
       'draw', 'vp', 'vp_cards', 'action_mod', 'buy_mod', 'coin_mod',
       'draw_mod', 'attack', 'defensive', 'discard', 'gain',
       'opponent_benefit', 'junk', 'junk_synergy', 'shuffle', 'trash',
       'upgrade', 'win'],
    '''

    # Bar plot of variable comparing wins
    this_df = game_analysis_df[['win']+sorted(anal_cols)].copy()
    plt.clf()
    corr = this_df.corr()
    ax = sns.heatmap(
        corr,
        vmin=-1, vmax=1, center=0,
        cmap=sns.color_palette("coolwarm", as_cmap=True),#sns.diverging_palette(220, 20,200),
        square=True,
        annot=True,
        annot_kws={"fontsize":6}
    )
    ax.set_xticklabels(
        ax.get_xticklabels(),
        rotation=45,
        horizontalalignment='right'
    )
    if ( not output_image ):
        plt.show()
    else:
        out_path = get_output_image_path()
        full_fn_path = out_path + "corr_plot.png"
        plt.savefig(full_fn_path)
        print("Wrote "+full_fn_path)

    this_df = this_df.melt( id_vars='win' )
    plt.clf()
    sns.barplot(x='variable',y='value',hue='win',data=this_df,palette='colorblind',errcolor='r')
    plt.yscale('log')
    plt.xticks(rotation = 65)
    plt.xlim(left=1)
    plt.xlabel("Feature")
    plt.ylabel("Average value over games".format(col))
    plt.title("Average values between wins/losses across {} games".format(game_settings['n_games']))
    if ( not output_image ):
        plt.show()
    else:
        out_path = get_output_image_path()
        full_fn_path = out_path + "bar_plot_wins.png"
        plt.savefig(full_fn_path)
        print("Wrote "+full_fn_path)

    for col in anal_cols:
        this_df = game_analysis_df[
            ['victory_points',col]
        ].copy()

        plt.clf()
        plt.scatter(
            this_df[col],
            this_df['victory_points'],
            color='r',
            alpha=0.3,
        )
        plt.xlabel(col)
        plt.ylabel("victory_points")
        if ( not output_image ):
            plt.show()
        else:
            out_path = get_output_image_path()
            full_fn_path = out_path + "victory_points_per_{}.png".format(col)
            plt.savefig(full_fn_path)
            print("Wrote "+full_fn_path)
