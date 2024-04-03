from Chess.Board.GameState import GameState


class HashTable:
    def __init__(self, size):
        """ Initialize the hash table

        :param size: The size of the hash table (should be a prime number) """
        self.size = size
        self.table = [None] * size

    def hash(self, state: GameState) -> int:
        """ Create a unique hash value for the current state

         :param state: The current state
         :return: The hash value"""
        return hash(str(state)) % self.size

    def lookup(self, state: GameState):
        """ Look up the value and best move for the current state in the hash table

         :param state: The current state
         :return: The value and best move for the current state"""
        h = self.hash(state)
        if self.table[h]:
            return self.table[h]
        return None

    def store(self, state: GameState, value: int | float, move):
        """ Store the value and best move for the current state in the hash table

         :param state: The current state
         :param value: The value of the current state
         :param move: The best move for the current state"""

        h = self.hash(state)
        self.table[h] = (value, move)
