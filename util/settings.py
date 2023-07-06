import os
import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

from brains.buy_brains import buy_brain_dict
from brains.action_brains import action_brain_dict

def interpret( val ):
    assert isinstance(val,str)
    if ( val.isnumeric() ):
        return int(val)
    elif (
        ( '.' in val ) and
        ( val.replace('.','').isnumeric() )
    ):
        return float(val)
    elif ( val.upper() == 'TRUE' ):
        return True
    elif ( val.upper() == 'FALSE' ):
        return False
    elif ( val.upper() == 'NONE' ):
        return None
    else:
        return val

def validate( inp ):
    assert 'n_players' in inp
    assert isinstance(inp['n_players'],int)
    assert (inp['n_players'] > 1) and (inp['n_players'] < 5)

    assert 'n_games' in inp
    assert isinstance(inp['n_games'],int)
    # 0 useful for debugging
    assert inp['n_games'] >= 0

    assert 'log' in inp
    assert isinstance(inp['log'],bool) or ( isinstance(inp['log'],float) and (inp['log']>0) and (inp['log']<=1.0) )

    assert 'print' in inp
    assert isinstance(inp['print'],bool)

    assert 'debug' in inp
    assert isinstance(inp['debug'],bool)

    assert 'max_turns' in inp
    assert isinstance(inp['max_turns'],int) and (inp['max_turns'] > 0)

    assert 'kingdom' in inp
    assert isinstance(inp['kingdom'],str)

    for i in range(1,5):
        s = str(i)

        #TODO: remove for more specific brains
        key = "player_"+s+"_brain"
        if ( key in inp ):
            assert isinstance(inp[key],str) or (inp[key] is None), key+' must be a string, recieved "'+str(inp[key])+'"'
            # TODO: check for file exist once implement files

        key = "player_"+s+"_buy_brain"
        if ( key in inp ):
            val = inp[key]
            assert isinstance(val,str) or (val is None), key+' must be a string, recieved "'+str(inp[key])+'"'
            if ( val is not None ):
                val_num=None

                if ( val.startswith( 'big_money' ) ):
                    l_items=val.split(' ')
                    val = l_items[0]
                    print(l_items)
                    if ( len(l_items)>1 ):
                        card_list = list(l_items[1].split(','))
                        inp[key+'_big_money_cards'] = card_list
                elif ( (val[-1].isnumeric()) ):
                    val_num = val[-1]
                    val = val[:-1].strip()
                    inp[key+"_n_lower"] = int(val_num)
                assert ( val in buy_brain_dict.keys() ),key+"must be one of: "+str(buy_brain_dict.keys())
                inp[key] = val
                # TODO: check for file exist once implement files

        key = "player_"+s+"_action_brain"
        if ( key in inp ):
            val = inp[key]
            assert isinstance(val,str) or (val is None), key+' must be a string, recieved "'+str(inp[key])+'"'
            if ( val is not None ):
                line = val
                l_items = line.split(' ')
                name = l_items[0]

                if (name=='attribute_prioritizer'):
                    assert (len(l_items)==3),"attribute prioritizer must be of form:'attribute_prioritizer <card name,ability,buy,etc> <True/False>', recieved: {}".format(val)
                    inp[key] = name
                    inp[key+'_'+name+'_order'] = list(l_items[1].split(','))
                    inp[key+'_'+name+'_tiebreak_cost'] = l_items[2]

                assert ( name in action_brain_dict.keys() ),key+"must be one of: "+str(action_brain_dict.keys())+" recieved "+name
                inp[key] = name

        key = key+"_output"
        if ( key in inp ):
            assert isinstance(inp[key],str) or (inp[key] is None), key+' must be a string, recieved "'+str(inp[key])+'"'

        key = "output_player_"+s+"_brain"
        if ( key in inp ):
            assert isinstance(inp[key],bool) or (inp[key] is None), key+' must be a bool, recieved "'+str(inp[key])+'"'

def print_settings( filename, inp_dict ):
    assert isinstance(inp_dict,dict)

    print("Settings for inp file:",filename)
    for key in inp_dict:
        print('\t{:20s}\t{:20s}'.format(key,str(inp_dict[key])))

'''
n_players = number of players, must be between 2-4 inclusive
n_games = number of games to train
log = True/False or decimal<1 - whether to output a log, if a float < 1 will randomly decide to output
player_n_brain = Which brain to use for player. Can be name, or file to select.
output_player_n_brain = True/False, only works for brains with output option
player_n_brain_output = File name, if none provided, will copy input name for file with new date, or name based on class
'''
def read_settings( filename, print_result=False ):
    inp_settings = {}
    assert isinstance(filename,str), 'input file name must be a string!'
    assert os.path.exists(filename), filename+" does not exist!"
    with open(filename) as f:
        for full_line in f:
            line=full_line
            if ( len(line.strip())>0 ):
                assert '=' in line, '"'+line+'" does not contain an "=", settings must be of form "key=val"'
                l = line.replace('\n','').split('=')
                inp_settings[l[0]] = interpret(l[1])

    validate(inp_settings)
    if (print_result):
        print_settings(filename,inp_settings)

    return inp_settings
