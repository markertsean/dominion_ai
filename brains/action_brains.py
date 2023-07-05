import random
import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

import decks
from decks import cards, dominion_cards


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
        print(self.card_attributes)
        print(self.valid_cards)
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

action_brain_dict = {
    'random':ActionRandom,
    'attribute_prioritizer':ActionAttributePrioritizer,
}
