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

    def __str__(self,tab_level=0,keys=None):
        out_str = "{}Card '{}'".format('\t'*tab_level,self.name)
        tab_level_1 = tab_level+1
        if (keys is None):
            keys = self.__dict__.keys()
        for key in sorted(keys):
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
        ,text=None

        # Attributes primarily used for ML training below
        ,**kwargs
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
        self.text    = text

        if ( isinstance(self.type,str) ):
            self.type = [self.type]

        self.card_attributes = [
            'name','ability','action',
            'buy','draw','coin','cost',
            'type','vp','text'
        ]

        # Add any new flags to grouping
        self.bool_flag_dict={
            "cantrip"          : None # +1 card +1 action
            ,"laboratory"      : None # +2 card +1 action
            ,"villiage"        : None # +1 card +2 action

            ,"attack_curse"    : False # Give opponent curse
            ,"attack_discard"  : False # Force opponent discard
            ,"attack_topdeck"  : False # Force something to top of deck
            ,"attack_trash"    : False # Force someone to trash

            ,"cycle_deck"      : False # Go through deck in order to find somthing
            #,"cycle_discard"   : False
            #,"cycle_trash"     : False
            #,"cycle_treasure"  : False

            ,"defensive"       : False

            ,"discard"         : False
            ,"discard_draw"    : False # Combined discard and draw mechanic

            ,"draw_ability"    : False # Draw until certain number," or draw discard combos
            ,"draw_treasure"   : False # Draw treasure

            ,"gainer_general"  : False # Allows gain any card
            ,"gainer_treasure" : False
            #,"gainer_supply"   : False
            #,"gainer_victory"  : False

            ,"junk"            : False # Muck up deck," IE copper," curse," estate," ruins
            ,"junk_synergy"    : False # Benefits from a full deck/slog game

            ,"opponent_draws"  : False

            ,"reaction"        : False

            ,"repeat"          : False # Card ability causes repetition in another card

            #,"search_deck"     : False # Search deck to find somthing
            #,"search_discard"  : False
            #,"search_trash"    : False

            ,"shuffle"         : False # Reshuffle discard and draw new deck

            ,"terminal"        : False # Action card that grants no additional action
            ,"terminal_coin"   : False # Terminal," but grants treasure value
            ,"terminal_draw"   : False # Terminal," but grants draw

            #,"pseudo_trash"    : False # Allows set aside in pile
            ,"trasher"         : False # Trashes general cards
            ,"trash_coin"      : False # Trashed a coin
            ,"trash_gain"      : False # Trashes to gain
            ,"trash_self"      : False # Trashes this card

            ,"upgrades"        : False # Upgrades an existing card

            ,"discard_n"       : False
            ,"draw_n"          : False
            ,"trash_n"         : False
        }

        self.bool_flag_dict["cantrip"   ] = (self.action==1) and (self.draw==1)
        self.bool_flag_dict["laboratory"] = (self.action==1) and (self.draw==2)
        self.bool_flag_dict["villiage"  ] = (self.action==2) and (self.draw==1)

        for arg in kwargs.keys():
            assert arg in self.bool_flag_dict.keys(),\
                "{} is not a valid Dominion Card Flag! Must be one of: [{}]".format(arg,
                    ' '.join([key for key in self.bool_flag_dict.keys()])
                )
            self.bool_flag_dict[arg] = kwargs[arg]

        self.flag_dict = self.__gen_numeric_flag_dict__()


    def __repr__(self,printall=False,tab_level=0):
        out_str = "{}Card '{}'".format('\t'*tab_level,self.name)
        tab_level_1 = tab_level+1

        keys = self.card_attributes
        if (printall):
            keys = self.__dict__.keys()

        for key in sorted(keys):
            if (key != 'name') and (key!='flag_dict') and (key!='bool_flag_dict'):
                out_str+='\n{}{:20s}\t{:20s}'.format('\t'*tab_level_1,str(key),str(self.__dict__[key]))
        return out_str

    def __gen_numeric_flag_dict__(self):
        numeric_flag_dict = {}
        for key in self.bool_flag_dict.keys():
            if ( self.bool_flag_dict[key] is None ):
                numeric_flag_dict[key] = 0
            elif ( isinstance(self.bool_flag_dict[key],bool) ):
                numeric_flag_dict[key] = int(self.bool_flag_dict[key])
            elif ( isinstance(self.bool_flag_dict[key],int) ):
                numeric_flag_dict[key] = self.bool_flag_dict[key]

        return numeric_flag_dict

dominion_card_flag_groupings = {
    "action": [
        "reaction",
        "repeat",
    ],
    "attack": [
        "attack_curse",
        "attack_discard",
        "attack_topdeck",
        "attack_trash",
    ],
    "defensive": [
        "defensive",
    ],
    "discard": [
        "discard",
        "discard_draw",
    ],
    "draw": [
        "cycle_deck",
        "discard_draw",
        "draw_ability",
        "draw_treasure",
        "terminal_draw",
    ],
    "coin": [
        "terminal_coin",
    ],
    "gain": [
        "gainer_general",
        "gainer_treasure",
    ],
    "opponent_benefit": [
        "opponent_draws",
    ],
    "junk": [
        "junk",
    ],
    "junk_synergy": [
        "junk_synergy",
    ],
    "shuffle": [
        "shuffle",
    ],
    "trash": [
        "trasher",
        "trash_coin",
        "trash_gain",
        "trash_self",
    ],
    "upgrade": [
        "upgrades",
    ],
}

reverse_dominion_card_flag_groupings = {}
for attribute, val_list in dominion_card_flag_groupings.items():
    for val in val_list:
        if (val in reverse_dominion_card_flag_groupings):
            reverse_dominion_card_flag_groupings[val].append(attribute)
        else:
            reverse_dominion_card_flag_groupings[val] = [attribute]

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

    def draw_from_supply(self,supply,n=1,bottom=False):
        assert isinstance(supply,CardSupply)
        n_draw = min(n,supply.count())
        supply.remove( n_draw )

        cards = []
        for i in range(0,n_draw):
            cards.append(supply.get_card())

        if ( bottom ):
            self.bottomdeck(cards)
        else:
            self.topdeck(cards)
        return n_draw

    def draw_from_pile(self,pile,n=1,bottom=False):
        assert isinstance(pile,CardPile)
        n_draw = min(n,pile.n_cards())

        cards = pile.draw(n_draw)

        if ( bottom ):
            self.bottomdeck(cards)
        else:
            self.topdeck(cards)
        return n_draw

    def wipe_stack(self):
        self.stack = []

class CardSupply:
    def __init__(self,card,n):
        assert isinstance(card,DominionCard)
        assert isinstance(n,int) and n>0
        self.card = card
        self.n = n
        self.orig_n = n

    def __str__(self):
        out_str = "Supply for card '{}', {} cards\n".format(self.card.name,self.n)
        return out_str+'\n'

    def get_card(self):
        return self.card

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

    def remove(self,n=1):
        assert n>=0
        n_remove = min(self.n,n)
        self.n -= n_remove

    def copy(self):
        return CardSupply( self.card, self.orig_n )
