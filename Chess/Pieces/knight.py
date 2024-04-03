from Chess.Pieces.piece import Piece


class Knight(Piece):
    def __init__(self, color, position):
        super().__init__("N", color, position)

    def get_legal_moves(self, board, move_history=None, pieces=None):
        # Generate a list of legal moves for the knight based on its movement patterns and the current board state
        legal_moves = []

        # Check the eight squares that the knight can move to
        for row_offset in [-2, -1, 1, 2]:
            for col_offset in [-2, -1, 1, 2]:
                if abs(row_offset) == abs(col_offset):
                    continue
                new_row = self._position[0] + row_offset
                new_col = self._position[1] + col_offset
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    # Check if the square is occupied by a friendly piece
                    if board[new_row][new_col] is None or board[new_row][new_col].color != self.color:
                        legal_moves.append((new_row, new_col))

        return legal_moves
        pass

    def get_value(self, board, move_history=None) -> float:
        # TODO: Implement a better evaluation function
        # Evaluate the value of the knight based on its position and other factors
        return 3 + self.positional_value(board)

    def positional_value(self, board):
        """ Returns the positional value of the knight based on its position on the board"""
        knight_moves = self.get_legal_moves(board)
        knight_mobility_value = 0
        knight_control_value = 0
        knight_outpost_value = 0
        # Knight mobility value
        knight_mobility_value = len(knight_moves) * 0.1
        # Knight control value
        for square in knight_moves:
            if square in ["d4", "d5", "e4", "e5"]:
                knight_control_value += 0.1
        return knight_mobility_value + knight_control_value
