import sys
import os
import copy
import math

import PySimpleGUI as sg

project_path = '/'.join( __file__.split('/')[:-2] )+'/'
sys.path.append(project_path)

from decks import cards,dominion_cards
from brains import brain_functions as bf
from brains import action_brains as ab

class KingdomSelectorWindow():
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

        self.mod_stats = False

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

    def flip_mod_stats_button( self ):
        self.mod_stats = not self.mod_stats
        self.window['Kingdom=ModStats'].update(
            "Mod Stats: {}".format(
                "On" if self.mod_stats else "Off"
            )
        )

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
            [
                sg.Button("Accept",key='Kingdom=Accept'),
                sg.Button("Reset",key='Kingdom=Reset'),
                sg.Button("Mod Stats: Off",key='Kingdom=ModStats'),
            ]
        ]
        self.mod_stats = False

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


class GameWindow():
    def __init__( self, game_cards, mod_stats=False ):

        self.dc_all_cards = dominion_cards.all_valid_cards

        self.mod_stats = mod_stats

        kingdom_dict = {}
        for kind, card_list in game_cards.items():
            for card in card_list:
                kingdom_dict[card] = cards.CardSupply( self.dc_all_cards[card], 1000 )
        self.kingdom_cards = list(kingdom_dict.keys())

        self.hand    = cards.CardPile('Hand')
        self.draw    = cards.CardPile('Draw')
        self.discard = cards.CardPile('Discard')
        self.play    = cards.CardPile('Play')

        # Base game - 7 copper, 3 estate
        self.set_default_draw()

        self.pile_dict = {
            'kingdom': kingdom_dict,
            'draw'   : self.draw,
            'hand'   : self.hand,
            'discard': self.discard,
            'play'   : self.play,
        }
        self.update_dict = {
            'kingdom': ( 'deck'   , [self.draw,self.hand,self.discard] ),
            'draw'   : ( 'draw'   , [self.draw] ),
            'hand'   : ( 'hand'   , [self.hand] ),
            'discard': ( 'discard', [self.discard] ),
            'play'   : ( 'play'   , [self.play] ),
        }

        self.layout_K = self.layout_D    = self.layout_H = None
        self.layout_X = self.layout_Deck = self.layout_P = None

        self.layout_action = None
        self.action_str = "Recommended Play: {}"
        self.action_brain = ab.action_brain_dict['q_brain']("Dummy Brain")

        self.turn_action = 1
        self.turn_buy    = 0
        self.turn_coin   = 0
        self.turn_draw   = 0

        self.layout_abcd = None
        self.abcd_dict = {
            'A':'turn_action',
            'B':'turn_buy',
            'C':'turn_coin',
            'D':'turn_draw',
        }

        self.gen_layouts()

        self.window = None
        self.gen_window()


    # Should be the case in most kingdoms
    def set_default_draw( self ):
        if ( 'copper' in self.kingdom_cards ):
            self.draw.topdeck( 7*[ self.dc_all_cards['copper'] ] )
        if ( 'estate' in self.kingdom_cards ):
            self.draw.topdeck( 3*[ self.dc_all_cards['estate'] ] )


    # Give stats from list like [hand,draw]
    def gen_deck_stats( self, pile_list ):
        pile_count_list = [ pile.count_cards() for pile in pile_list ]
        full_deck = bf.combine_deck_count( pile_count_list )
        analysis_deck = bf.analyze_deck( full_deck, normalize='readable' )
        return analysis_deck

    # If mod button on, accept "_mod" parameters over not "_mod"
    def mod_accepted( self, key, key_list ):
        if ( not self.mod_stats ):
            if ( key.endswith('_mod') ):
                return False
            return True

        else:
            if (
                ( not key.endswith('_mod') ) and
                ( key+"_mod" in key_list )
            ):
                return False
            return True


    # Determines widest variable, float and int formats, saves as string
    def gen_stat_string_dict( self, stat_dict ):
        key_overwrites = {
            'opponent_benefit': 'opp_ben',
            'junk_synergy': 'junk_syn',
        }

        all_keys = stat_dict.keys()
        key_list = []
        for key, val in stat_dict.items():
            if ( self.mod_accepted(key,all_keys) ):
                new_key = key if (key not in key_overwrites) else key_overwrites[key]
                key_list.append(new_key)

        max_char_len = max( [len(key) for key in key_list] )
        name_format_str = "{:"+str(max_char_len)+"s}: "

        out_dict = {}

        for key, val in stat_dict.items():
            if ( self.mod_accepted(key,all_keys) ):
                new_key = key if (key not in key_overwrites) else key_overwrites[key]
                out_dict[new_key] = (name_format_str+"{:0.2f}").format(new_key,val) if isinstance(val,float) \
                    else (name_format_str+"{:4d}").format(new_key,val)

        return out_dict


    # Split stats into a number of columns, returns as column
    def gen_formatted_stat_list(
        self,
        name,
        stat_dict,
        font = ('Ubuntu Mono',10),
        color = 'white',
        cols = 2
    ):
        stat_strings = self.gen_stat_string_dict( stat_dict )

        length = math.ceil( len(stat_strings) / float(cols) )
        if ( (len(stat_strings) // cols) != length ):
            length += 1

        formatted_list = []
        i = 1
        this_list = []
        for key, val in stat_strings.items():
            if ( i % length == 0 ):
                formatted_list.append(sg.Column(this_list))
                this_list=[]
            this_list.append([
                sg.Text(
                    val,
                    text_color=color,
                    font=font,
                    key="status={}={}".format(name,key)
                )
            ])
            i+=1
        formatted_list.append(sg.Column(this_list))
        return sg.Column([formatted_list])


    # Wrapper for formatatted_stat_list, from input of format [draw,hand]
    def gen_deck_stats_layout( self, name, pile_list ):
        analysis_deck = self.gen_deck_stats( pile_list )
        stat_layout_deck = self.gen_formatted_stat_list( name, analysis_deck )
        return stat_layout_deck

    def generate_turn_state(self):
        out_dict = {}
        out_dict['action'] = self.turn_action
        out_dict['buy'   ] = self.turn_buy
        out_dict['coin'  ] = self.turn_coin
        out_dict['draw'  ] = self.turn_draw

        out_dict['hand_pile'   ] = self.hand
        out_dict['draw_pile'   ] = self.draw
        out_dict['discard_pile'] = self.discard

        return out_dict

    def update_action_button( self, c, value=0 ):
        v = self.abcd_dict[c]
        self.__dict__[v] = max(0,self.__dict__[v]+value)
        self.window["{}=text".format(c)].update(self.get_letter_button(c))

    def update_all_action_buttons( self ):
        for c in ['A','B','C','D']:
            self.update_action_button( c )

    def reset_play_area( self ):
        print("RESET PLAY")
        self.turn_action = 1
        self.turn_buy    = 0
        self.turn_coin   = 0
        self.turn_draw   = 0
        self.window["-action-"].update(self.action_str.format("None"))
        self.update_all_action_buttons()

    def update_abcd( self, card_list, reverse=False ):
        if ( isinstance( card_list, type(cards.DominionCard) ) ):
            card_list = [card_list]

        assert isinstance( card_list, list )

        mod = 1
        if reverse:
            mod = -1

        for card in card_list:
            print("\tPLAYED {}".format(card.name))
            self.turn_action += mod * ( card.get_val('action') - 1 )
            self.turn_buy    += mod * ( card.get_val('buy'   )     )
            self.turn_coin   += mod * ( card.get_val('coin'  )     )
            self.turn_draw   += mod * ( card.get_val('draw'  )     )
            self.update_all_action_buttons()

    '''
    When move all cards out of play area, reset all actions
    Whem move any cards into play area, update
    '''
    # Recommend card to play based on cards in hand
    def update_recommendation( self ):
        #REMOVE
        for pile_name, pile in self.pile_dict.items():
            if (pile_name!='kingdom'):
                print("\t",pile_name)
                print("\t",pile.count_cards())

        action = self.action_brain.choose_action(
            self.generate_turn_state()
        )

        if ( action is None ):
            self.window["-action-"].update(self.action_str.format("None"))
            print("\tRECOMMEND {}".format("None"))
        else:
            self.window["-action-"].update(self.action_str.format(action.name))
            print("\tRECOMMEND {}".format(action.name))

    # Perform update for pile_list = [hand,draw...]
    def update_deck_stats( self, name, pile_list ):
        pile_count_list = [ pile.count_cards() for pile in pile_list ]
        full_deck = bf.combine_deck_count( pile_count_list )

        analysis_deck = self.gen_deck_stats( pile_list )
        stat_strings = self.gen_stat_string_dict( analysis_deck )


        for key, val in stat_strings.items():
            self.window["status={}={}".format(name,key)].update( val )

        for card in self.kingdom_cards:
            self.window["{}={}=count".format(name,card)].update(
                "{:2d}".format(
                    0 if card not in full_deck else int(full_deck[card])
                )
            )

            visible_row = False if (card not in full_deck) or (full_deck[card]<1) else True

            self.window["{}={}=name".format(name,card)].update(
                visible = visible_row
            )
            self.window["{}={}=count".format(name,card)].update(
                visible = visible_row
            )

            if ( name != 'deck' ):
                for other_name in ['kingdom','draw','hand','discard','play']:
                    if ( name != other_name ):
                        self.window["move={}={}={}".format(name,other_name,card)].update(
                            visible = visible_row
                        )

    def gen_game_move_buttons(
            self,
            name, # hand, etc
            name_color_label_tuple_list,
            cards_to_count=None,
            count=True,
            add_all=False,
            add_buttons=True,
    ):
        assert (name_color_label_tuple_list is None) or (len(name_color_label_tuple_list) == 4)
        assert ( count != (cards_to_count is None) ), "If counting must provide list of card piles to count"

        card_count = {}
        full_deck = {}
        if ( cards_to_count is not None ):
            pile_count_list = [ pile.count_cards() for pile in cards_to_count ]
            full_deck = bf.combine_deck_count( pile_count_list )

        all_button = []
        if add_all:
            all_button = ['all']

        card_name_len = 10
        card_len_str_f = "{:"+str(card_name_len)+"s}"
        font = ('Ubuntu Mono',14)

        out_layout = []
        for card in all_button+self.kingdom_cards:
            button_list = []
            visible_row = (
                ( card == 'all' ) or
                (cards_to_count is None ) or
                ( True if card in full_deck else False )
            )
            if ( add_buttons ):
                for name_t, color_t, label_t in name_color_label_tuple_list:
                    button_list.append(
                        sg.Button(
                            label_t,
                            button_color=color_t,
                            key="move={}={}={}".format(name,name_t,card),
                            visible=visible_row,
                        )
                    )
            out_layout.append([
                sg.Text(
                    card_len_str_f.format(card),
                    key="{}={}=name".format(name,card),
                    font=font,
                    visible=visible_row,
                )
            ])
            if count:
                end_text = None
                if ( card =='all' ):
                    end_text = ""
                else:
                    end_text = "{:2d}".format(
                        0 if card not in full_deck else int(full_deck[card])
                    )
                out_layout[-1].append(sg.Text(
                    "{:2s}".format(str(end_text)),
                    key="{}={}=count".format(name,card),
                    font=font,
                    visible=visible_row,
                ))
            out_layout[-1] += button_list
        return out_layout

    def gen_game_move_buttons_col(
        self,
        name,
        name_color_label_tuple_list,
        cards_to_count=None,
        count=True,
        add_all=False,
        add_buttons=True,
    ):
        out_layout = self.gen_game_move_buttons(
            name,
            name_color_label_tuple_list,
            cards_to_count,
            count,
            add_all,
            add_buttons,
        )
        rotated_out_layout = [[x[i] for x in out_layout] for i in range(len(out_layout[0]))]
        new_out = [ sg.Column([ [col] for col in row ]) for row in rotated_out_layout ]
        return sg.Column( [new_out] )

    def get_letter_button( self, c ):
        assert c in ['A','B','C','D']
        return '{:1s}: {:02d}'.format(c,self.__dict__[self.abcd_dict[c]])

    def gen_layouts( self ):

        k_color = "black"
        d_color = "blue"
        h_color = "red"
        x_color = "dark green"
        p_color = "purple"
        e_color = "white"
        section_title_font = ('Axial',20)

        layout_K  = [[sg.Text("Kingdom",text_color=k_color,font=section_title_font)],[sg.HSeparator()]]
        buttons_K = self.gen_game_move_buttons_col(
            "kingdom",
            [
                ( "draw"   , d_color, "D", ),
                ( "hand"   , h_color, "H", ),
                ( "discard", x_color, "X", ),
                ( "play"   , p_color, "P", ),
            ],
            None,
            False,
            False,
            True,
        )
        self.layout_K = sg.Column( layout_K + [ [ buttons_K ] ] )

        layout_D = [[sg.Text("Draw",text_color=d_color,font=section_title_font)],[sg.HSeparator()]]
        cards_D = self.gen_game_move_buttons(
            "draw",
            [
                ( "kingdom", k_color, "K", ),
                ( "hand"   , h_color, "H", ),
                ( "discard", x_color, "X", ),
                ( "play"   , p_color, "P", ),
            ],
            [self.draw],
            True,
            True,
            True,
        )
        cards_D = sg.Column(cards_D)
        stat_layout_D = self.gen_deck_stats_layout( "draw", [self.draw] )
        self.layout_D = sg.Column( layout_D + [ [ cards_D, stat_layout_D ] ] )

        layout_H = [[sg.Text("Hand",text_color=h_color,font=section_title_font)],[sg.HSeparator()]]
        cards_H = self.gen_game_move_buttons(
            "hand",
            [
                ( "kingdom", k_color, "K", ),
                ( "draw"   , d_color, "D", ),
                ( "discard", x_color, "X", ),
                ( "play"   , p_color, "P", ),
            ],
            [self.hand],
            True,
            True,
            True,
        )
        cards_H = sg.Column(cards_H)
        stat_layout_H = self.gen_deck_stats_layout( "hand", [self.hand] )
        self.layout_H = sg.Column( layout_H + [ [ cards_H, stat_layout_H ] ] )

        layout_X = [[sg.Text("Discard",text_color=x_color,font=section_title_font)],[sg.HSeparator()]]
        cards_X = self.gen_game_move_buttons(
            "discard",
            [
                ( "kingdom", k_color, "K", ),
                ( "draw"   , d_color, "D", ),
                ( "hand"   , h_color, "H", ),
                ( "play"   , p_color, "P", ),
            ],
            [self.discard],
            True,
            True,
            True,
        )
        cards_X = sg.Column(cards_X)
        stat_layout_X = self.gen_deck_stats_layout( "discard", [self.discard] )
        self.layout_X = sg.Column( layout_X + [ [ cards_X, stat_layout_X ] ] )

        layout_Deck = [[sg.Text("Deck",text_color=e_color,font=section_title_font)],[sg.HSeparator()]]
        cards_Deck = self.gen_game_move_buttons(
            "deck",
            None,
            [self.draw,self.hand,self.discard],
            True,
            False,
            False,
        )
        cards_Deck = sg.Column(cards_Deck)
        stat_layout_Deck = self.gen_deck_stats_layout(
            "deck",
            [self.hand,self.draw,self.discard]
        )
        self.layout_Deck = sg.Column( layout_Deck + [ [ cards_Deck, stat_layout_Deck ] ] )

        layout_P = [[sg.Text("Play",text_color=p_color,font=section_title_font)],[sg.HSeparator()]]
        cards_P = self.gen_game_move_buttons(
            "play",
            [
                ( "kingdom", k_color, "K", ),
                ( "draw"   , d_color, "D", ),
                ( "hand"   , h_color, "H", ),
                ( "discard", x_color, "X", ),
            ],
            [self.play],
            True,
            True,
            True,
        )
        cards_P = sg.Column(cards_P)
        stat_layout_P = self.gen_deck_stats_layout( "play", [self.play] )
        self.layout_P = sg.Column( layout_P + [ [ cards_P, stat_layout_P ] ] )

        # Display which action card best to play based on Q brain
        self.layout_action = sg.Text(
            self.action_str.format("None"),
            font = ('Ubuntu Mono',16),
            text_color = 'white',
            key = "-action-",
        )


        tc = 'white'
        f  = ('Ubuntu Mono',16)
        self.layout_abcd = []
        for c in ['A','B','C','D']:
            self.layout_abcd.append(sg.Column([
                [
                    sg.Text(
                        self.get_letter_button(c),
                        key = "{}=text".format(c),
                        font = f,
                        text_color = tc,
                    ),
                ],
                [
                    sg.Button( "+", font=f, key="{}=inc".format(c) ),
                    sg.Button( "-", font=f, key="{}=dec".format(c) ),
                ]
            ]))

    def gen_window( self ):
        reset_button = sg.Button( "Reset", key="-reset-" )
        close_button = sg.Button( "Close", key="-close-" )

        left_col = [
            [
                sg.Column([
                    [reset_button,sg.VSeparator(),close_button],
                    [self.layout_K],
                    [self.layout_Deck],
                    [self.layout_action],
                    self.layout_abcd,
                ])
            ]
        ]
        mid_col = [
            [self.layout_P],
            [sg.HSeparator()],
            [self.layout_H],
        ]
        right_col = [
            [self.layout_D],
            [sg.HSeparator()],
            [self.layout_X],
        ]
        tool_layout = [
            [
                sg.Column(left_col),
                sg.VSeparator(),
                sg.Column(mid_col),
                sg.VSeparator(),
                sg.Column(right_col)
            ]
        ]

        self.window = sg.Window(
            title="Analysis",
            layout=tool_layout,
        )


    def run( self ):
        while True:
            event, values = self.window.read()
            print(event)
            # End program if user closes window or
            # presses the OK button
            if (event == sg.WIN_CLOSED):
                break

            elif (event=="-reset-"):
                self.draw.stack = []
                self.hand.stack = []
                self.discard.stack = []
                self.play.stack = []
                self.set_default_draw()

                for name, pile_t in self.update_dict.items():
                    pile_to_update, piles = pile_t
                    self.update_deck_stats( pile_to_update, piles )

            elif ((event=="-close-") or (event==sg.WIN_CLOSED)):
                break

            # Increment / decrement a variable
            elif ( event.endswith("=inc") or event.endswith("=dec") ):
                inc_dec = 1 if event.endswith("=inc") else -1
                self.update_action_button( event[0], inc_dec )

            elif (event.startswith("move")):
                e_parsed = event.split("=")
                origin_pile = e_parsed[1]
                destination_pile = e_parsed[2]
                card_name = e_parsed[3]

                origin = self.pile_dict[ origin_pile ]
                destination = self.pile_dict[ destination_pile ]

                n_cards = 0
                if (
                    isinstance(origin,dict) and
                    (card_name in origin) and
                    isinstance(origin[card_name],cards.CardSupply)
                ):
                    n_cards = origin[card_name].count()
                elif ( isinstance(origin,cards.CardPile) ):
                    count_dict = origin.count_cards()
                    if ( card_name in count_dict ):
                        n_cards = count_dict[card_name]
                    elif ( card_name == 'all' ):
                        for key, val in count_dict.items():
                            n_cards += val

                if ( n_cards > 0 ):
                    print("ORIGIN {}".format(origin_pile))
                    print("DESTIN {}".format(destination_pile))
                    # Move card around
                    if ( isinstance(destination,cards.CardPile) ):
                        new_cards = []
                        if ( card_name == 'all' ):
                            destination.stack += origin.stack
                            new_cards = origin.stack
                        else:
                            destination.topdeck( self.dc_all_cards[card_name] )
                            new_cards = [ self.dc_all_cards[card_name] ]

                        # Put cards in play area, update stats
                        if ( destination_pile=='play' ):
                            self.update_abcd( new_cards )

                        elif ( (origin_pile=='play') and (destination_pile=='hand') ):
                            self.update_abcd( new_cards, reverse = True )

                        elif ( (origin_pile=='draw') and (destination_pile=='hand') ):
                            self.update_action_button( 'D', -len(new_cards) )

                    if ( isinstance(origin,cards.CardPile) ):
                        if ( card_name == 'all' ):
                            origin.stack = []
                        else:
                            origin.stack.remove( self.dc_all_cards[card_name] )

                    # Update stats
                    for update_name in [origin_pile,destination_pile]:
                        pile_to_update, piles = self.update_dict[update_name]
                        self.update_deck_stats( pile_to_update, piles )

                    # Emptied play area, reset action buy coin draw reccommendation
                    if (
                        #TODO: consider allowing pile to hand not resetting play area
                        #(destination_pile!='hand') and
                        (origin_pile=='play') and
                        (self.play.n_cards()==0)
                    ):
                        self.reset_play_area()

                    self.update_recommendation()

        self.window.close()
        return
