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
    assert inp['n_games'] > 0

    assert 'log' in inp
    assert isinstance(inp['log'],bool) or ( isinstance(inp['log'],float) and (inp['log']>0) and (inp['log']<=1.0) )

    assert 'print' in inp
    assert isinstance(inp['print'],bool)

    assert 'max_turns' in inp
    assert isinstance(inp['max_turns'],int) and (inp['max_turns'] > 0)

    assert 'kingdom' in inp
    assert isinstance(inp['kingdom'],str)

    for i in range(1,5):
        s = str(i)

        key = "player_"+s+"_brain"
        if ( key in inp ):
            assert isinstance(inp[key],str) or (inp[key] is None), key+' must be a string, recieved "'+str(inp[key])+'"'
            # TODO: check for file exist once implement files

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
    with open(filename) as f:
        for full_line in f:
            line=full_line.strip()
            if (len(line)>0):
                assert '=' in line, '"'+line+'" does not contain an "=", settings must be of form "key=val"'
                l = line.replace(' ','').split('=')
                inp_settings[l[0]] = interpret(l[1])

    validate(inp_settings)
    if (print_result):
        print_settings(filename,inp_settings)

    return inp_settings
