import random
import sys

sys.path.append('/'.join( __file__.split('/')[:-2] )+'/')

import decks


class BuyBrain:
    def __init__(self,name):
        self.name=name
    def __repr__(self):
        return "BuyBrain obj-{}".format(str(self.__dict__))
    def choose_buy(self):
        pass

class BuyRandom(BuyBrain):
    def __init__(self):
        self.name = 'random'

    def choose_buy(self,buy_inputs):
        kingdom_card_counts = buy_inputs['kingdom_counts']
        buy_card, count = random.choice( kingdom_card_counts )
        return buy_card

'''
Selects random card that is the max we can afford, or within lower_cost lower
IE, if have 6 treasure and lc 1, will buy random 6 or 5 card
'''
class BuyTopRandom(BuyBrain):
    def __init__(self,lower_cost=0):
        self.name = 'top_random'
        assert isinstance(lower_cost,int)
        assert lower_cost>=0
        self.lower_cost = lower_cost

    '''
    Separate from choose_buy for use in child classes
    '''
    def pick_random_top(self,kingdom_card_counts):
        max_cost = max([card.cost if (card is not None) else 0 for card, count in kingdom_card_counts ])
        card_list = []
        for card, count in kingdom_card_counts:
            if (
                (card is None) or
                (max_cost - card.cost) <= self.lower_cost
            ):
                card_list.append(card)
        return random.choice( card_list )

    def choose_buy(self,buy_inputs):
        kingdom_card_counts = buy_inputs['kingdom_counts']
        return self.pick_random_top( kingdom_card_counts )

'''
As RandomTop, but prefers provinces
if can afford them
'''
class BuyProvinceTopRandom(BuyTopRandom):
    def __init__(self,lower_cost=0):
        self.name = 'province_top_random'
        assert isinstance(lower_cost,int)
        assert lower_cost>=0
        self.lower_cost = lower_cost

    def choose_buy(self,buy_inputs):
        kingdom_card_counts = buy_inputs['kingdom_counts']
        cards = [card for card, count in kingdom_card_counts if card is not None]
        for card in cards:
            if ( 'province' == card.name ):
                return card
        return self.pick_random_top( kingdom_card_counts )

buy_brain_dict = {
    'random':BuyRandom,
    'top_random':BuyTopRandom,
    'province_top_random':BuyProvinceTopRandom,
}
