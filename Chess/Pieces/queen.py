from Chess.Pieces.piece import Piece


class Queen(Piece):
    def __init__(self, color, position):
        super().__init__("Q", color, position)

    def get_legal_moves(self, board, move_history=None, pieces=None):
        # Generate a list of legal moves for the queen based on its movement patterns and the current board state
        legal_moves = []

        # Check the squares that the queen can move to in each direction
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                if row_offset == 0 and col_offset == 0:
                    continue
                new_row = self._position[0] + row_offset
                new_col = self._position[1] + col_offset
                while 0 <= new_row < 8 and 0 <= new_col < 8:
                    # Check if the square is occupied by a friendly piece
                    if board[new_row][new_col] is None or board[new_row][new_col].color != self.color:
                        legal_moves.append((new_row, new_col))
                    # Stop iterating if the square is occupied by an enemy piece
                    if board[new_row][new_col] is not None:
                        break
                    new_row += row_offset
                    new_col += col_offset

        return legal_moves
        pass

    def get_value(self):
        # TODO: Implement a better evaluation function
        # Evaluate the value of the queen based on its position and other factors
        return 9  # Hard coded value for now
