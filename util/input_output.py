import os
import sys
import pickle as pkl

__project_path = '/'.join( __file__.split('/')[:-2] )+'/'

def get_data_path():
    return __project_path+"data/"

def get_game_turn_path():
    return get_data_path() + "games/"

def write_game( game_dict ):
    out_path = get_game_turn_path() + game_dict['program_start_time'] + "/"
    os.makedirs(out_path,exist_ok=True)

    file_name = "game_{}.pkl".format(game_dict["game_number"])
    with open( out_path+file_name, "wb" ) as f:
        pkl.dump(game_dict, f, protocol=pkl.HIGHEST_PROTOCOL)
