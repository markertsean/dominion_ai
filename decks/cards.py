from random import shuffle

'''
Card class for use as parent for all cards
'''
class GenericCard:
    def __init__(self):
        self.name=None

    def __setitem__(self,name,value):
        assert isinstance(name,str),         'Cannot set key value pair for "'+str(self.name)+'" Key must be a str, recieved '+str(type(name))
        assert (name in self.__dict__),         'Cannot set key "'+name+'" in card '+str(self.name)+', key must be one of '+str(self.__dict__.keys())
        assert self.__dict__[name] is None, 'Value of '+str(name)+' for card '+str(self.name)+' is already set!'
        self.__dict__[name] = value

    def __getitem__(self,name):
        assert isinstance(name,str),         'Cannot get key value pair for "'+str(self.name)+'" Key must be a str, recieved '+str(type(name))
        assert (name in self.__dict__),         'Cannot get key "'+name+'" in card '+str(self.name)+', key must be one of '+str(self.__dict__.keys())
        return self.__dict__[name]

    def additional_print():
        return ''

    def __str__(self,tab_level=0):
        out_str = "{}Card '{}'".format('\t'*tab_level,self.name)
        tab_level_1 = tab_level+1
        for key in sorted(self.__dict__.keys()):
            if key != 'name':
                out_str+='\n{}{:20s}\t{:20s}'.format('\t'*tab_level_1,str(key),str(self.__dict__[key]))
        return out_str


class DominionCard(GenericCard):
    def __init__(
        self
        ,name
        ,cost
        ,card_type
        ,ability=None
        ,action=None
        ,buy=None
        ,draw=None
        ,coin=None
        ,victory_points=None
    ):
        assert isinstance(name,str)
        self.name    = name
        self.ability = ability
        self.action  = action
        self.buy     = buy
        self.draw    = draw
        self.coin    = coin
        self.cost    = cost
        self.type    = card_type
        self.vp      = victory_points


class CardPile:
    def __init__(self,name,stack=None):
        self.name  = name

        self.stack = stack
        assert isinstance(self.stack,list) or (self.stack is None)
        if (self.stack is None):
            self.stack = []
        self.valid_stack_check()

    # Verifies only cards are in the deck
    def verify_cards(self,card,allow_list=True):
        if isinstance(card,list) and allow_list:
            for c in card:
                if ( not self.verify_cards(c,False) ):
                    return False
            return True
        else:
            return issubclass(type(card),GenericCard)

    def valid_stack_check(self):
        assert self.verify_cards( self.stack, True ), 'Non-card added to stack '+str(self.stack)

    def n_cards(self):
        return len(self.stack)

    def count_cards(self):
        count_dict = {}
        for card in self.stack:
            if card['name'] not in count_dict:
                count_dict[card['name']] = 1
            else:
                count_dict[card['name']] += 1
        return count_dict

    # End of stack is top of deck
    def draw(self,n=1):
        n_draw = min(n,self.n_cards())
        card_num = self.n_cards() - n_draw
        ret_stack = self.stack[card_num:][::-1]
        del self.stack[card_num:]
        return ret_stack

    # Place cards on top of the deck, end of list
    def topdeck(self,cards):
        self.verify_cards(cards)
        if not isinstance(cards,list):
            cards = [cards]
        self.stack = self.stack + cards

    # Place cards on the bottom of the deck, beggining of list
    def bottomdeck(self,cards):
        self.verify_cards(cards)
        if not isinstance(cards,list):
            cards = [cards]
        self.stack = cards + self.stack

    def shuffle(self):
        shuffle(self.stack)


class CardSupply:
    def __init__(self,card,n):
        assert isinstance(card,DominionCard)
        assert isinstance(n,int) and n>0
        self.card = card
        self.n = n

    def gain(self):
        assert self.n>0
        self.n -= 1
        return self.card

    def return_supply(self,card):
        assert card == self.card
        del card
        self.n += 1

    def count(self):
        return self.n
