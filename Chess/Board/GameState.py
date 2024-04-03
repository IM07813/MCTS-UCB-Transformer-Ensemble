import pickle
from random import choice

from Chess.Repository.ChessRepository import ChessRepository
from Chess.Exceptions.Checkmate import Checkmate
from Chess.Exceptions.IllegalMoveException import IllegalMove
from Chess.Exceptions.WrongColor import WrongColor
from Chess.Pieces.king import King
from Chess.Pieces.knight import Knight
from Chess.Pieces.pawn import Pawn
from Chess.Pieces.piece import Piece
from Chess.Pieces.queen import Queen
from Chess.Pieces.rook import Rook
from Chess.utils.move_handlers import process_algebraic_notation, process_location, convert_to_algebraic_notation, \
    print_board


class GameState:
    def __init__(self, chess_repository: ChessRepository):
        self.board: ChessRepository = chess_repository

    def make_move(self, move: str):
        """ Make a move on the board

        :param move: The move to make
        :return: None
        """
        # Update the half-move counter
        self.board.half_moves += 1

        # Make a copy of the board and the pieces

        initial_board = pickle.loads(pickle.dumps(self.board.board, -1))
        initial_pieces = pickle.loads(pickle.dumps(self.board.pieces, -1))

        # Calculate the start and end squares
        end, start = process_algebraic_notation(move)

        # Get the piece at the start square
        piece: Piece | King = self.board.board[start[0]][start[1]]
        # Check if the piece is the correct color
        if piece is None:
            raise IllegalMove(convert_to_algebraic_notation(start) + " is empty")
        if piece.color != self.board.turn:
            raise WrongColor("That's not your piece!")
        # Check if the move is legal
        if end not in piece.get_legal_moves(self.board.board, self.board.history, self.board.pieces):
            raise IllegalMove("That move is illegal!")

        # Check if king is in check
        king = None
        for row in self.board.board:
            for square in row:
                if square is not None and square.color == self.board.turn and isinstance(square, King):
                    king = square
                    break

        # Check if the move is a capture
        if self.board.board[end[0]][end[1]] is not None:
            # If the piece is a friendly piece, the move is illegal
            if self.board.board[end[0]][end[1]].color == self.board.turn:
                raise IllegalMove("You can't capture your own piece!")
            # If the piece is an enemy piece, remove it from the list of pieces
            captured_piece = self.board.board[end[0]][end[1]]
            for pieces in self.board.pieces:
                if pieces.position == captured_piece.position and pieces.type == captured_piece.type:
                    self.board.remove_piece(captured_piece)
                    break

            # Update the list of pieces
            self.board.pieces = [piece for row in self.board.board for piece in row if piece is not None]
            self.board.half_moves = 0

        if king.is_in_check(self.board.board, self.board.pieces, self.board.history):
            # Simulate the move to see if the king is still in check
            if self.board.board[end[0]][end[1]] is not None and self.board.board[end[0]][
                end[1]].color != self.board.turn:
                captured_piece = self.board.board[end[0]][end[1]]
                for pieces in self.board.pieces:
                    if pieces.position == captured_piece.position and pieces.type == captured_piece.type:
                        self.board.remove_piece(captured_piece)
            self.board.board[end[0]][end[1]] = piece
            self.board.board[start[0]][start[1]] = None
            piece.position = end
            if king.is_in_check(self.board.board, self.board.pieces, self.board.history):
                self.rollback(initial_board, initial_pieces)
                raise IllegalMove("You must get out of check!")
            self.rollback(pickle.loads(pickle.dumps(initial_board, -1)), pickle.loads(pickle.dumps(initial_pieces, -1)))

        # Castling rights
        if isinstance(piece, Rook):
            # Remove the castling rights if the rook moves
            if start == (0, 0) or start == (7, 0):
                king.castling_rights[0] = False
            if start == (0, 7) or start == (7, 7):
                king.castling_rights[1] = False

        if (king.castling_rights[0] or king.castling_rights) and isinstance(piece, King):
            # Check if the move is a castling move
            if isinstance(piece, King) and abs(end[1] - start[1]) == 2 and (
                    king.castling_rights[0] or king.castling_rights[1]):
                # Check if there are pieces between the king and the rook
                if end[1] > 4 and self.board.board[end[0]][end[1] - 1] is not None and self.board.board[end[0]][
                    end[1] - 2] \
                        is not None:
                    raise IllegalMove("You can't castle through pieces!")
                if end[1] < 4 and self.board.board[end[0]][end[1] + 1] is not None and self.board.board[end[0]][
                    end[1] + 2] \
                        is not None:
                    raise IllegalMove("You can't castle through pieces!")
                # If there are no pieces between the king and the rook, check the castling rights
                elif end not in king.get_legal_moves(self.board.board, self.board.history, self.board.pieces):
                    raise IllegalMove(f'You don\'t have the right to castle '
                                      f'{"king" if king.castling_rights[0] else "queen"} side!')

                # If the king is not in check and there are no pieces between the king and the rook, castle
                else:
                    # Move the rook
                    if end[1] == 6:
                        if self.board.board[end[0]][7] is None:
                            raise IllegalMove("Something went wrong")
                        self.board.board[end[0]][7].position = (end[0], 5)
                        self.board.board[end[0]][5] = self.board.board[end[0]][7]
                        self.board.board[end[0]][7] = None
                    else:
                        if self.board.board[end[0]][0] is None:
                            raise IllegalMove("Something went wrong")
                        self.board.board[end[0]][0].position = (end[0], 3)
                        self.board.board[end[0]][3] = self.board.board[end[0]][0]
                        self.board.board[end[0]][0] = None

            # Remove the castling rights
            king.castling_rights[0] = False
            king.castling_rights[1] = False

        # Check if the move is an en passant capture
        if isinstance(piece, Pawn) and self.board.board[end[0]][end[1]] is None and end[1] != start[1]\
                and isinstance(self.board.board[start[0]][end[1]], Pawn) and self.board.board[start[0]][end[1]].color != \
                self.board.turn:
            # If the pawn moves diagonally and there is no piece at the end square, it is an en passant capture
            self.board.board[start[0]][end[1]] = None

        # Move the piece
        self.board.board[start[0]][start[1]] = None
        self.board.board[end[0]][end[1]] = piece
        piece.position = end
        if isinstance(piece, Pawn):
            self.board.half_moves = 0

        # Check if the king is in check after the move
        if king.is_in_check(self.board.board, self.board.pieces, self.board.history):
            self.rollback(initial_board, initial_pieces)
            raise IllegalMove("You can't move a pinned piece")

        # Check if the move is a pawn promotion
        if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
            # Check if the piece is a pawn and if it is on the last rank
            # If it is, promote it
            self.board.board[start[0]][start[1]] = None
            self.board.board[end[0]][end[1]] = Queen(piece.color, end)

        # Update the board.history
        self.board.history = move

        # Update the turn
        self.board.turn = "b" if self.board.turn == "w" else "w"

        # Update the list of pieces
        self.board.pieces = [piece for row in self.board.board for piece in row if piece is not None]
        self.board.number_of_moves += 1

        # Find the enemy king
        for i in self.board.pieces:
            if isinstance(i, King) and i.color == self.board.turn:
                king = i
                break

        initial_board = pickle.loads(pickle.dumps(self.board.board, -1))
        initial_pieces = pickle.loads(pickle.dumps(self.board.pieces, -1))
        # Check if the king is in checkmate
        if king.is_in_check(self.board.board, self.board.pieces, self.board.history):
            if not king.get_legal_moves(self.board.board, self.board.history, self.board.pieces):
                # If the king has no legal moves, check if the checking piece can be captured or blocked
                move_found = False
                for i in self.board.pieces:
                    if i.color == self.board.turn:
                        if isinstance(i, King):
                            continue
                        legal_moves = i.get_legal_moves(self.board.board, self.board.history, self.board.pieces)
                        initial_position = pickle.loads(pickle.dumps(i.position, -1))
                        for move in legal_moves:
                            move_found = False
                            self.board.board[i.position[0]][i.position[1]] = None
                            self.board.board[move[0]][move[1]] = i
                            i.position = move
                            self.board.pieces = [piece for row in self.board.board for piece in row if
                                                 piece is not None]
                            if not king.is_in_check(self.board.board, self.board.pieces, self.board.history):
                                move_found = True
                                break
                            self.rollback(pickle.loads(pickle.dumps(initial_board, -1)),
                                          pickle.loads(pickle.dumps(initial_pieces, -1)))
                            i.position = initial_position
                if not move_found:
                    self.board.game_over = True
                    self.rollback(initial_board, initial_pieces)
                    self.board.result = 1 if self.board.turn == "w" else 0
                    raise Checkmate(f'Game over: {"1-0" if self.board.turn == "b" else "0-1"}!')

                self.rollback(pickle.loads(pickle.dumps(initial_board, -1)),
                              pickle.loads(pickle.dumps(initial_pieces, -1)))

        # Check if the king is in stalemate
        else:
            if not king.get_legal_moves(self.board.board, self.board.history, self.board.pieces):
                # If the king has no legal moves but is not in check, check if the player has any legal moves
                move_found = False
                for i in self.board.pieces:
                    move_found = False
                    if i.color == self.board.turn:
                        self.rollback(pickle.loads(pickle.dumps(initial_board, -1)),
                                      pickle.loads(pickle.dumps(initial_pieces, -1)))
                        if isinstance(i, King):
                            continue
                        legal_moves = i.get_legal_moves(self.board.board, self.board.history, self.board.pieces)
                        if legal_moves:
                            move_found = True
                            break
                if not move_found:
                    self.board.game_over = True
                    self.rollback(initial_board, initial_pieces)
                    self.board.result = 0.5
                    raise Checkmate(f'Game over: 1/2-1/2!')

                self.rollback(pickle.loads(pickle.dumps(initial_board, -1)),
                              pickle.loads(pickle.dumps(initial_pieces, -1)))

        # Check if the game is over due to insufficient material
        if self.is_insufficient_material():
            self.board.game_over = True
            self.board.result = 0.5
            raise Checkmate(f'Game over: 1/2-1/2!')

        # Check if the game is over due to the 50-move rule
        if self.board.half_moves == 100:
            self.board.game_over = True
            self.board.result = 0.5
            raise Checkmate(f'Game over: 1/2-1/2!')

        # TODO: Check if the game is over due to threefold repetition

    def rollback(self, board, pieces):
        """ Function to roll back the board and pieces to a previous state

         :param board: The board to roll back to
         :param pieces: The pieces to roll back to

         :return: None"""
        self.board.board = board
        self.board.pieces = pieces

    def get_board(self):
        """ Returns the board

         :return: The board"""
        return self.board

    def get_legal_moves(self, start):
        """ Returns the legal moves for the piece at the start square

         :param start: The start square
         :return: The list of legal moves"""
        start = process_location(start)
        piece: Piece | King = self.board.board[start[0]][start[1]]
        if piece is None:
            raise IllegalMove("There is no piece at the start location!")
        return piece.get_legal_moves(self.board.board, self.board.history, self.board.pieces)

    def possible_moves(self):
        """ Return all possible moves for the current player

         :return: A list of all possible moves for the current player"""
        # TODO: Remove the moves that put the king in check
        moves = []
        for i in self.board.pieces:
            if i.color == self.board.turn:
                for move in self.get_legal_moves(convert_to_algebraic_notation(i.position)):
                    moves += [convert_to_algebraic_notation(i.position) + convert_to_algebraic_notation(move)]
        return moves

    def play_random_move(self, moves=None):
        """ Play a random legal move

         :param moves: A list of moves to choose from"""
        if moves is None:
            moves = self.possible_moves()
        if moves:
            move = choice(moves)
            try:
                self.make_move(move)
            except IllegalMove:
                moves.remove(move)
                self.play_random_move(moves)

    def get_value(self) -> float:
        """ Return the value of the board. Positive if white is winning, negative if black is winning

         :return: The value of the board"""
        value = 0
        for piece in self.board.pieces:
            if piece.color == "w":
                if isinstance(piece, Pawn) or isinstance(piece, Knight):
                    value += piece.get_value(self.board.board, self.board.history)
                else:
                    value += piece.get_value()
            else:
                if isinstance(piece, Pawn) or isinstance(piece, Knight):
                    value -= piece.get_value(self.board.board, self.board.history)
                else:
                    value -= piece.get_value()
        return value

    def get_result(self):
        """ Returns the result of the game

         :return: The result of the game"""
        return self.board.result

    def is_insufficient_material(self):
        """ Checks if there is enough material on the board to checkmate

         :return: True if there is not enough material to checkmate, False otherwise"""
        # Check if there is a rook, queen or pawn
        for piece in self.board.pieces:
            if isinstance(piece, Rook) or isinstance(piece, Queen) or isinstance(piece, Pawn):
                return False

        # We will split the pieces into two lists, one for each color
        white_pieces = [piece for piece in self.board.pieces if piece.color == "w"]
        black_pieces = [piece for piece in self.board.pieces if piece.color == "b"]
        # If there are only two pieces left (the two kings), the game is over
        if len(white_pieces) + len(black_pieces) == 2:
            return True

        # King and a minor piece against a king is a draw
        elif len(white_pieces) + len(black_pieces) == 3:
            return True

        # King and bishop or knight against a king and bishop or knight is a draw
        if len(white_pieces) == 2 and len(black_pieces) == 2:
            return True

        # King against a king and two knights is a draw
        if len(white_pieces) == 1 and len(black_pieces) == 3:
            for piece in black_pieces:
                if not isinstance(piece, Knight) or not isinstance(piece, King):
                    return True

        if len(white_pieces) == 3 and len(black_pieces) == 1:
            for piece in white_pieces:
                if not isinstance(piece, Knight) or not isinstance(piece, King):
                    return True

        # If there's enough material, the game is not over
        return False

    def fen(self):
        """ Returns the FEN representation of the board
         :return: The FEN representation of the board"""
        return self.board.fen()

    def game_over(self):
        return self.board.game_over

    def get_turn(self):
        return self.board.turn
    # Potentially useless
    # def validate_move(self, move):
    #     initial_board = pickle.loads(pickle.dumps(self.board.board, -1))
    #     initial_pieces = pickle.loads(pickle.dumps(self.board.pieces, -1))
    #     try:
    #         self.make_move(move)
    #         self.rollback(initial_board, initial_pieces)
    #         return True
    #     except IllegalMove:
    #         self.rollback(initial_board, initial_pieces)
    #         return False


if __name__ == "__main__":

    chess_repository = ChessRepository()
    chess_repository.initialize_board()
    game = GameState(chess_repository)
    game.make_move("d2d4")
    print(game.get_board())
    # for move in ['f2f4', 'e7e5', 'a2a3', 'd8h4']: #['f2f3', 'e7e5', 'a2a3', 'd7d5', 'd2d4', 'g7g5', 'b1d2', 'd8e7', 'd2b1', 'e7e6', 'e2e3', 'b8d7', 'e1d2', 'f7f5', 'h2h4', 'f8c5', 'c2c3', 'c5b4', 'd1e1', 'e8f8', 'e1g3', 'b4d6', 'c3c4', 'd6a3', 'g3e5', 'e6e8', 'a1a2', 'g8e7', 'e5h2', 'f8g8', 'd2d3', 'd7c5', 'd3c3', 'c8e6', 'h2e5', 'a8b8', 'b1d2', 'a3b2', 'c3b2', 'c5a6', 'f1e2', 'e7g6', 'e3e4', 'a6b4', 'b2a3', 'b8a8', 'e5d5', 'f5e4', 'g1h3', 'e8a4', 'a3b2', 'b4d5', 'd2e4', 'a7a6', 'h1h2', 'a4a3', 'a2a3', 'a8e8', 'h3g1', 'd5c3', 'a3a4', 'a6a5', 'h2h1', 'e8d8', 'c4c5', 'c3b1', 'f3f4', 'e6f7', 'h1h3', 'd8a8', 'e2d3', 'g8g7', 'h3h2', 'f7e6', 'g1e2', 'b1d2', 'c1d2', 'g7h6', 'a4a3', 'e6g4', 'a3a5', 'g5h4', 'e4c3', 'a8a7', 'a5a2', 'g6e7', 'f4f5', 'h6h5', 'a2a5', 'h8c8', 'e2g3']:
    #    game.make_move(move)
    #    print_board(game.board)
    # print(game.fen())
    while True:
        try:
            game.make_move(input("The move:"))
            print_board(game.board)
        except IllegalMove as e:
            print(e)
        except WrongColor as e:
            print(e)
        except Checkmate as e:
            print(e)
            break
