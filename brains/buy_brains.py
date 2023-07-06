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

class BuyBigMoney(BuyBrain):
    def __init__(self,cards=None):
        self.name = 'big_money'
        self.cards = None
        if ( cards is not None ):
            if ( isinstance(cards,str) ):
                cards=[cards]
            assert isinstance(cards,list),\
            "Input cards must be string or list of strings, recieved {}".format(type(cards))
            self.cards = cards
            for card in cards:
                self.name += '-'+card

    def choose_buy(self,buy_inputs):
        kingdom_card_counts = buy_inputs['kingdom_counts']

        cards = [card for card, count in kingdom_card_counts if card is not None]
        card_names = [card.name for card in cards]

        # Default big money
        ind = None
        bm_card = None
        if ( "province" in card_names ):
            ind = card_names.index("province")
            bm_card = cards[ind]
        elif ( "gold" in card_names ):
            ind = card_names.index("gold")
            bm_card = cards[ind]
        elif ( "silver" in card_names ):
            ind = card_names.index("silver")
            bm_card = cards[ind]

        # Big money with cards, see if worth buying
        #TODO: replace the randoms with early/late game checks, indclude duchy
        if ( self.cards is not None ):
            best_card = None
            for card_name in self.cards:
                if ( card_name in card_names ):
                    card = cards[ card_names.index(card_name) ]
                    if (
                        (best_card is None) or
                        (best_card.cost < card.cost ) or
                        ((best_card.cost==card.cost) and (random.random()>0.5))
                    ):
                        best_card = card
            if ( (bm_card is None) and (best_card is not None) ):
                bm_card = best_card
            elif (
                (bm_card is not None) and
                (best_card is not None) and
                (
                    (bm_card.cost < best_card.cost) or
                    ((bm_card.cost == best_card.cost) and (random.random()>0.5))
                )
            ):
                bm_card = best_card
        return bm_card

buy_brain_dict = {
    'random':BuyRandom,
    'top_random':BuyTopRandom,
    'province_top_random':BuyProvinceTopRandom,
    'big_money':BuyBigMoney,
}
