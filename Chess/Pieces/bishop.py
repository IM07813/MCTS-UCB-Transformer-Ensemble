from Chess.Pieces.piece import Piece


class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__("B", color, position)

    def get_legal_moves(self, board, move_history=None, pieces=None):
        # Generate a list of legal moves for the bishop based on its movement patterns and the current board state
        legal_moves = []

        # Check the squares that the bishop can move to in each direction
        for row_offset, col_offset in [[1, 1], [1, -1], [-1, 1], [-1, -1]]:
            new_row = self.position[0] + row_offset
            new_col = self.position[1] + col_offset
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

    def get_value(self):
        # TODO: Implement a better evaluation function
        # Evaluate the value of the bishop based on its position and other factors
        return 3 # Hard coded value for now
