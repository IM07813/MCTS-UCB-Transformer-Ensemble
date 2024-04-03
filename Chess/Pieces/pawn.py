from Chess.Pieces.piece import Piece
from Chess.utils.move_handlers import process_algebraic_notation


class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__("P", color, position)

    def get_legal_moves(self, board, move_history, pieces=None):
        # Generate a list of legal moves for the pawn based on its movement patterns and the current board state

        # Check the direction the pawn is moving in
        direction = 1 if self.color == "w" else -1
        legal_moves = []
        # Check if the square in front of the pawn is empty
        # print(self.position)
        row = self._position[0] + direction
        col = self._position[1]
        if 0 <= row < 8 and 0 <= col < 8:
            if board[row][col] is None:
                legal_moves.append((row, col))
                # If the pawn is at its starting position, it can also move two squares forward
                if (self.color == "w" and self._position[0] == 1) or (self.color == "b" and self._position[0] == 6):
                    row += direction
                    if board[row][col] is None:
                        legal_moves.append((row, col))

            # Check if there are pieces to capture diagonally
            for col_offset in [-1, 1]:
                row = self._position[0] + direction
                col = self._position[1] + col_offset
                if 0 <= row < 8 and 0 <= col < 8:
                    if board[row][col] is not None and board[row][col].color != self.color:
                        legal_moves.append((row, col))

        # Check if there is an en passant capture available
        if len(move_history) > 0:
            last_move = move_history[-1]
            end, start = process_algebraic_notation(last_move)
            last_move = (end, start)
            last_piece = board[end[0]][end[1]]
            if isinstance(last_piece, Pawn) and last_piece.color != self.color:
                # if ((self.color == "b" and last_move[0][0] == 3 and last_move[1][0] == 1) or\
                #    (self.color == "w" and last_move[0][0] == 4 and last_move[1][0] == 6)) and\
                #         self.position[0] == last_move[1][0]:
                if abs(last_move[0][0] - last_move[1][0]) == 2 and self.position[0] == last_move[0][0] and \
                        (self.position[1] + 1 == last_move[0][1] or self.position[1] - 1 == last_move[0][1]):
                    legal_moves.append((last_move[1][0] - direction, last_move[1][1]))
        return legal_moves

    def get_value(self, board, move_history) -> float:
        # Evaluate the value of the pawn based on its position and other factors
        return 1 + self.positional_value(board, move_history)

    def positional_value(self, board, move_history) -> float:
        """ Returns the positional value of the pawn based on its position on the board
            :param board: The current board state
            :param move_history: The history of moves made in the game
            :return: The positional value of the pawn """
        pawn_file = self.position[1]
        pawn_rank = self.position[0]
        pawn_color = self.color
        pawn_structure_value = 0
        pawn_mobility_value = 0
        pawn_protection_value = 0
        pawn_advancement_value = 0
        pawn_center_control_value = 0
        # Pawn structure value
        if pawn_rank in [3, 4]:
            pawn_structure_value += 0.1
        if pawn_color == "w":
            if self.position in [(3, 3), (3, 4)]:
                pawn_center_control_value += 0.1
        else:
            if self.position in [(4, 3), (4, 4)]:
                pawn_center_control_value += 0.1
        # Pawn mobility value
        pawn_mobility_value = len(self.get_legal_moves(board, move_history)) * 0.1
        # Pawn advancement value
        if pawn_color == "w":
            pawn_advancement_value = (8 - pawn_rank) * 0.1
        else:
            pawn_advancement_value = pawn_rank * 0.1
        return pawn_structure_value + pawn_mobility_value + pawn_protection_value + pawn_advancement_value + \
            pawn_center_control_value
