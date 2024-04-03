from abc import abstractmethod


class Piece:
    def __init__(self, type, color, position):
        self.type: str = type
        self.color: str = color
        self._position: tuple[int, int] = position

    def get_legal_moves(self, board, move_history, pieces):
        """ Generate a list of legal moves for the piece based on its movement patterns and the current board state

        :param board: The current state of the board
        :param move_history: The history of moves that have been made
        :param pieces: The pieces on the board
        :return: A list of legal moves """
        pass

    @abstractmethod
    def get_value(self, *args):
        """ Evaluate the value of the piece based on its position and other factors """
        pass

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    def __repr__(self):
        return self.color + self.type
