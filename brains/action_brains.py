import random
import sys
import numpy as np

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

import decks
from decks import cards, dominion_cards
from brains import q_learning


class ActionBrain:
    def __init__(self,name):
        self.name=name
    def __repr__(self):
        return "ActionBrain obj-{}".format(str(self.__dict__))
    def choose_action(self):
        pass

class ActionRandom(ActionBrain):
    def __init__(self):
        self.name="action_random"
    def choose_action(self,inp_card_list):
        return random.choice( inp_card_list )

# Increase number of actions if possible, else, draws, else, others
# Settings format is "player_1_action_brain=attribute_prioritizer throne_room,action,draw,chancellor,ability False"
class ActionAttributePrioritizer(ActionBrain):
    def __init__(self,order,tiebreak_cost,ability_prioritize=['throne_room']):
        self.name="action_attribute_prioritizer"
        self.card_attributes = ['action','draw','buy','coin','ability']
        self.valid_cards = [card for card in dominion_cards.base_action_cards.keys()]
        self.order = order
        for item in self.order:
            assert item in self.card_attributes+self.valid_cards,\
            str(item)+' must be one of: '+str(self.card_attributes+self.valid_cards)
        self.tiebreak_cost = tiebreak_cost
        self.ability_prioritize_list = ability_prioritize
        for card in self.ability_prioritize_list:
            assert card in self.valid_cards,str(card)+" must be one of: "+str(self.valid_cards)

    # Selects card that maximizes attribute, IE action, draw, etc, with random break for ties
    def select_highest_attribute(self,inp_card_list,attribute,tiebreak_cost=False):
        valid_card_list = [card for card in inp_card_list if card is not None]
        card_list = [card for card in valid_card_list if card.__dict__[attribute] is not None]
        if ( len(card_list) == 1 ):
            return card_list[0]
        if (len(card_list)>0):
            increases = [card.__dict__[attribute] for card in card_list]
            max_val = max(increases)
            play_list = [card for card in card_list if card[attribute] == max_val]
            if ( len(play_list)==1 ):
                return play_list[0]
            if (tiebreak_cost):
                return self.select_highest_attribute(play_list,'cost')
            return random.choice(play_list)
        return None

    # Abilities less straightforward, allow priority cards but otherwise random
    def select_ability(self,inp_card_list,tiebreak_cost=False):
        valid_card_list = [card for card in inp_card_list if card is not None]
        card_list = [card for card in valid_card_list if card.__dict__['ability'] is not None]
        if ( len(card_list) == 1 ):
            return card_list[0]
        if (len(card_list)>0):
            for ability in self.ability_prioritize_list:
                for card in card_list:
                    if (ability == card.ability):
                        return card
            if (tiebreak_cost):
                return self.select_highest_attribute(card_list,'cost')
            return random.choice(card_list)
        return None

    def choose_action(self,inp_card_list):
        card_list = []
        if ( None in inp_card_list ):
            card_list=[None]
        card_list += [ card for card in inp_card_list if card is not None and 'action' in card.type ]
        card_list = list(set(card_list))
        card_names = {}
        for card in card_list:
            if (card is not None):
                card_names[card.name]=card
        for item in self.order:
            result = None
            if ( item in card_names.keys() ):
                result = card_names[item]
            elif (item == 'ability'):
                result = self.select_ability(
                    card_list,
                    self.tiebreak_cost,
                )
            elif (item in self.card_attributes):
                result = self.select_highest_attribute(
                    card_list,
                    item,
                    self.tiebreak_cost,
                )
            if (result is not None):
                return result
        if (len(card_list)>0):
            return random.choice(card_list)
        return None


class QTree(q_learning.QLearner):
    def __init__( self, gamma=0.5, max_depth=5 ):
        self.name = "q_brain"
        self.gamma = gamma
        self.max_depth = max_depth

        self.card_field_order = ['action','buy','draw','coin','vp']
        self.state_keys = set( self.card_field_order + ['hand_pile','draw_pile','discard_pile'] )
        self.debug=False

    # TODO: remove
    def printd( self, *args ):
        if ( self.debug ):
            print(*args)

    # Allows either passing action as string or DominionCard type, returns latter
    def convert_to_card( self, card_or_name ):
        assert isinstance(card_or_name,(str,cards.DominionCard))
        if (isinstance(card_or_name,cards.DominionCard)):
            return card_or_name
        else:
            assert card_or_name in dominion_cards.all_valid_cards
            return dominion_cards.all_valid_cards[card_or_name]

    # Check if card can be played in action phase
    def usable_card( self, inp_card ):
        inp_card = self.convert_to_card( inp_card )
        for t in inp_card.type:
            if ( t in ('action','attack','reaction',) ):
                return True
        return False

    def usable_card_in_deck( self, inp_deck ):
        assert isinstance(inp_deck,cards.CardPile)
        for card in inp_deck.stack:
            if ( self.usable_card(card) ):
                return True
        return False

    def expected_n_cards_from_count( self, k_pick, n_card, n_other, depth = 0 ):
        if ( ( k_pick <= 0 ) or ( n_card <= 0 ) ):
            return 0.

        # Probability of drawing our card
        pc = n_card / ( 1. * n_card + n_other )
        pn = 1. - pc

        out_c = out_n = 0.

        # Count 1 if card drawn, then propogate the probability with expectation from next draw
        # Otherwise, 0 and expectation for next draw
        if ( n_card > 0 ):
            out_c = pc * ( 1. + self.expected_n_cards_from_count( k_pick-1, n_card-1, n_other   ,depth+1) )
        if ( n_other > 0 ):
            out_n = pn * ( 0. + self.expected_n_cards_from_count( k_pick-1, n_card  , n_other-1 ,depth+1) )

        return out_c+out_n

    def expected_n_cards_from_prob( self, card_name, k_pick, n_in_pile, prob_dict ):
        if (
            ( k_pick <= 0 ) or
            ( n_in_pile <= 0 ) or
            ( card_name not in prob_dict ) or
            ( prob_dict[card_name] == 0 )
        ):
            return 0.

        n_card = prob_dict[card_name] * n_in_pile
        n_other = n_in_pile - n_card

        return self.expected_n_cards_from_count( k_pick, n_card, n_other )

    def reward( self, card ):
        card = self.convert_to_card(card)
        out_list = []
        for attr in self.card_field_order:
            assert attr in card.__dict__
            val = card.__dict__[attr]
            out_list.append( float(val)  if val is not None else 0. )

        # TODO consider making a tensor, other dtype
        return np.array(out_list)

    # 1 / n_playable cards, equal prob play any unique card
    # s = all_decks, a = card name played
    def policy( self, state_dict, action ):
        unique_cards = set( state_dict['hand_pile'].stack )
        additional_card_count = min(
            state_dict['draw'],
            state_dict['draw_pile'].n_cards() + state_dict['discard_pile'].n_cards()
        )
        playable_card_list = []
        for card in unique_cards:
            if (self.usable_card(card)):
                playable_card_list.append(card)
        l = len(playable_card_list)+additional_card_count
        return 1. / l if l > 0 else 0.

    # Q for playing card "action" from hand in "all_deck_dict" (state)
    def value_function( self, state_dict, action ):
        assert set(state_dict.keys()) == self.state_keys

        if ( not self.usable_card( action ) ):
            return np.zeros( len( self.card_field_order ) )

        # Remove card from new hand to create new state
        new_hand = cards.CardPile('hand_pile',state_dict['hand_pile'].stack.copy())
        card = self.convert_to_card(action)
        assert action in new_hand.stack
        new_hand.stack.remove( action )
        new_state_dict = state_dict.copy()
        new_state_dict['hand_pile'] = new_hand

        # Play the card, modifiying relevant fields
        new_state_dict['action'] = new_state_dict['action'] - 1
        for field in self.card_field_order:
            if ( action.__dict__[field] is not None ):
                new_state_dict[field] += action.__dict__[field]

        r_t = self.reward( action )
        v_s_t_1 = self.state_value( new_state_dict )
        return r_t + self.gamma * v_s_t_1

    '''
    V^pi(s) = SUM_a pi(s,a) SUM_s' P^a_ss' R^a_ss' + g SUM_a pi(s,a) SUM_s' P^a_ss' V^pi(s')
    pi(s,a) = 1/n_cards
    R^a_ss' - r_t for card played
    P^a_ss' - where we factor in 1's for definite cards, probabilities for possible draws
    '''
    def state_value( self, state_dict, depth=0 ):

        if (
            (state_dict['action'] == 0) or
            (depth>self.max_depth)
        ):
            # TODO: datatype
            return np.array( [ 0 for i in range( len( self.card_field_order ) ) ] )

        '''
        Handle the fact we need to draw cards
        First draw from the draw deck, then the discard if draw empty
        If draw more than number of cards in a deck, it is definite.
        Directly move cards to hand, subtract from draw count.
        Else, probable. Do not move cards, do not reduce draw count
        '''
        new_draw_count = state_dict['draw']

        new_draw = cards.CardPile('new_draw_pile',state_dict['draw_pile'].stack.copy())
        new_discard = cards.CardPile('new_discard_pile',state_dict['discard_pile'].stack.copy())
        definitely_draw = {}
        definitely_discard = {}
        ######### TODO: Implement probably
        probably_draw = {}
        probably_discard = {}

        n_in_next_draw_pile = 0
        #proba_draw_pile = cards.CardPile('prob',draw.stack.copy())

        #self.debug=True
        self.printd('-'*depth,"hand",state_dict['hand_pile'].count_cards())
        self.printd('-'*depth,"draw",state_dict['draw_pile'].count_cards())
        self.printd('-'*depth,"discard",state_dict['discard_pile'].count_cards())

        for field in self.card_field_order:
            self.printd('-'*depth,field,state_dict[field])

        self.printd('-'*depth,"def draw",definitely_draw)
        self.printd('-'*depth,"def discard",definitely_discard)

        if ( state_dict['draw'] > 0 ):
            draw_proba = False

            # If will draw all of draw pile, will add them to hand
            if ( new_draw_count >= draw.n_cards() ):
                definitely_draw = draw.count_cards()
                new_draw = cards.CardPile('new_draw_pile',[])
                new_draw_count -= sum(definitely_draw.values())

            # If will draw part of draw pile, save probabilities of single draw
            elif ( state_dict['draw_pile'].n_cards() > 0 ):
                draw_proba = True
                probably_draw = state_dict['draw_pile'].count_cards()
                n_in_next_draw_pile = 1. * state_dict['draw_pile'].n_cards()
                for key, val in probably_draw.items():
                    probably_draw[key] = val / n_in_next_draw_pile

            if ( not draw_proba ):
                if ( new_draw_count >= discard.n_cards() ):
                    definitely_discard = discard.count_cards()
                    new_discard = cards.CardPile('new_discard_pile',[])
                    new_draw_count -= sum(definitely_discard.values())

                elif ( state_dict['discard_pile'].n_cards() > 0 ):
                    probably_discard = state_dict['discard_pile'].count_cards()
                    n_in_next_draw_pile = 1. * state_dict['discard_pile'].n_cards()
                    for key, val in probably_discard.items():
                        probably_discard[key] = val / n_in_next_draw_pile

        self.printd('-'*depth,"def draw",definitely_draw)
        self.printd('-'*depth,"def discard",definitely_discard)
        self.printd('-'*depth,"prob draw",probably_draw)
        self.printd('-'*depth,"prob discard",probably_discard)
        # need ro recursively call function, using hand + definitely draw, run probably draw somehow

        new_hand = cards.CardPile('new_hand',state_dict['hand_pile'].stack.copy())
        self.printd('-'*depth,"New Hand pre",new_hand.count_cards())
        # Add cards we will definitely draw to the hand
        for draw_count_dict in [definitely_draw,definitely_discard]:
            for def_card, count in draw_count_dict.items():
                new_hand.topdeck( [dominion_cards.all_valid_cards[def_card]] * count )
        self.printd('-'*depth,"New Hand post",new_hand.count_cards())

        # Need to count treasures in reward, not through action card format
        treasure_reward = np.zeros( len( self.card_field_order ) )
        all_hand_cards = new_hand.stack.copy()
        for card in new_hand.stack:
            if (
                ('treasure' in card.type) and
                ( not self.usable_card( card ) )
            ):
                treasure_reward += self.reward( card )
                all_hand_cards.remove( card )
        self.printd('-'*depth,"new_hand_stack",new_hand.count_cards())
        #self.printd('-'*depth,"all_hand_cards",all_hand_cards)
        new_hand.stack = all_hand_cards
        self.printd('-'*depth,"new_hand_stack",new_hand.count_cards())
        self.printd('-'*depth,"def treasure drawn",treasure_reward)
        self.printd('-'*depth,"New Hand post treasure",new_hand.count_cards())

        prob_comb = probably_draw.copy()
        prob_comb.update( probably_discard )

        new_hand_card_name_set = set( [ card.name for card in new_hand.stack ] )

        possible_card_set = new_hand_card_name_set.union( set( prob_comb.keys() ) )

        #TODO need to update with new state dict?
        new_state_dict = state_dict.copy()
        new_state_dict['hand_pile'] = new_hand
        new_state_dict['draw_pile'] = new_draw
        new_state_dict['discard_pile'] = new_discard
        new_state_dict['draw'] = new_draw_count
        self.printd('-'*depth,"New hand",new_hand.count_cards())
        self.printd('-'*depth,"New draw",new_draw.count_cards())
        self.printd('-'*depth,"New discard",new_discard.count_cards())

        pi_s_a_all = self.policy( new_state_dict, None ) # No need to pass action, 1/n_cards

        r_1_list = []
        r_2_list = []
        t_list = []

        self.printd('-'*depth,'action cards',possible_card_set)

        for card_name in possible_card_set:

            self.printd('-'*depth,'card_name',card_name)

            card = self.convert_to_card( card_name )

            P_a_ss = 1.

            # If probable draw, need 1 - prob not drawing
            if ( card_name not in new_hand_card_name_set ):
                P_a_ss = 1 - np.power( 1 - prob_comb[card_name], new_draw_count )

            self.printd('-'*depth,'P_a_ss',P_a_ss)
            # If a treasure card drawn, won't change state, just save treasure reward
            if ( not self.usable_card( card ) ):
                self.printd('-'*depth,'Base T reward',self.reward( card ))
                self.printd('-'*depth,'P T reward',P_a_ss * self.reward( card ))
                if ( card_name in new_hand_card_name_set ):
                    t_list.append( P_a_ss * self.reward( card ) * new_hand.count_cards()[card_name] )
                else:
                    t_list.append( self.reward( card ) *
                         self.expected_n_cards_from_prob(
                             card_name,
                             new_state_dict['draw'],
                             n_in_next_draw_pile,
                             prob_comb
                         )
                    )
                continue


            self.printd('-'*depth,'playing card')
            r_1_list.append( pi_s_a_all * P_a_ss * self.reward(card_name) )
            # V^pi(s) = SUM_a pi(s,a) SUM_s' P^a_ss' R^a_ss' + g SUM_a pi(s,a) SUM_s' P^a_ss' V^pi(s')

            play_state_dict = new_state_dict.copy()
            play_state_dict['action'] = play_state_dict['action'] - 1
            for field in self.card_field_order:
                play_state_dict[field] = play_state_dict[field] + \
                ( 0 if card.__dict__[field] is None else card.__dict__[field] )

            if ( card_name in new_hand_card_name_set ):
                play_hand = play_state_dict['hand_pile'].stack.copy()
                play_hand.remove( card )
                play_state_dict['hand_pile'].stack = play_hand
            elif ( card_name in probably_draw.keys() ):
                play_draw = play_state_dict['draw_pile'].stack.copy()
                play_draw.remove( card )
                play_state_dict['draw_pile'].stack = play_draw
            else:
                play_disc = play_state_dict['discard_pile'].stack.copy()
                play_disc.remove( card )
                play_state_dict['discard_pile'].stack = play_disc

            self.printd('-'*depth,'state',play_state_dict)
            r_2_list.append( self.gamma * pi_s_a_all * P_a_ss * self.state_value( play_state_dict , depth+1 ) )
            self.printd('-'*depth,r_1_list[-1],r_2_list[-1])

        return sum( r_1_list ) + sum( r_2_list ) + treasure_reward + sum( t_list )

action_brain_dict = {
    'random':ActionRandom,
    'attribute_prioritizer':ActionAttributePrioritizer,
}
