from abc import abstractmethod

class QLearner():
    def __init__( self, gamma=1.0 ):
        self.gamma = gamma
    
    @abstractmethod
    def policy(self):
        pass
    
    @abstractmethod
    def reward(self):
        pass
    
    @abstractmethod
    def state_value(self):
        pass
    
    @abstractmethod
    def value_function(self):
        pass
