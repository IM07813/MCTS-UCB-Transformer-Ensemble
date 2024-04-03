from Chess.Pieces.bishop import Bishop
from Chess.Pieces.king import King
from Chess.Pieces.knight import Knight
from Chess.Pieces.pawn import Pawn
from Chess.Pieces.piece import Piece
from Chess.Pieces.queen import Queen
from Chess.Pieces.rook import Rook


class ChessRepository:
    def __init__(self):
        # The __board is a 2D array of 8x8 squares
        self.__board: list[list[Piece | None]] = [[None for _ in range(8)] for _ in range(8)]
        self.__turn = "w"  # White makes the first move
        self.__history = []  # Here we will store the history of moves
        self.__game_over = False  # Game is still ongoing
        self.__pieces: list[Piece] = []  # List of __pieces
        self.__castling_rights = {"w": {"O-O": True, "O-O-O": True},
                                  "b": {"O-O": True, "O-O-O": True}}  # Castling rights
        self.__result = None  # The result of the game
        self.__number_of_moves = 0  # The number of half-moves made since game start
        self.__half_moves = 0  # The number of half-moves since the last capture or pawn move

    def initialize_board(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        """ Initialize the board with the FEN provided, or the initial chess position if no FEN is provided

         :param fen: The FEN to initialize the board with"""
        pieces = {"r": Rook, "n": Knight, "b": Bishop, "q": Queen, "k": King, "p": Pawn}
        fen = fen.split(" ")
        fen_pieces = fen[0].split("/")
        fen_pieces.reverse()
        pos = (0, 0)
        for row in fen_pieces:
            for char in row:
                if char.isdigit():
                    for _ in range(int(char)):
                        self.__board[pos[0]][pos[1]] = None
                        pos = (pos[0], pos[1] + 1)
                if char.lower() in pieces:
                    if char.islower():
                        piece = pieces[char]("b", pos)
                        self.__pieces.append(piece)
                        self.__board[pos[0]][pos[1]] = piece
                    else:
                        piece = pieces[char.lower()]("w", pos)
                        self.__pieces.append(piece)
                        self.__board[pos[0]][pos[1]] = piece
                    pos = (pos[0], pos[1] + 1)
            pos = (pos[0] + 1, 0)
        # Set the game variables from the FEN string
        self.turn = fen[1]  # Set the turn
        self.__castling_rights = {
            "w": {"O-O": True if "K" in fen[2] else False, "O-O-O": True if "Q" in fen[2] else False},
            "b": {"O-O": True if "k" in fen[2] else False, "O-O-O": True if "q" in fen[2] else False}
        }
        self.__half_moves = int(fen[4])
        self.__number_of_moves = int(fen[5])

    def fen(self):
        """ Returns a FEN representation of the board

         :return: A FEN representation of the board"""
        FEN = ""
        for row in self.board:
            empty_squares = 0
            fen = ""
            for piece in row:
                if piece is None:
                    empty_squares += 1
                    continue
                elif empty_squares != 0:
                    fen += str(empty_squares)
                if piece.color == "w":
                    fen += piece.type
                    empty_squares = 0
                else:
                    fen += piece.type.lower()
                    empty_squares = 0
            if empty_squares != 0:
                fen += str(empty_squares)
            FEN = fen + "/" + FEN
        FEN = FEN[:-1]  # Remove the last slash
        FEN += " " + self.turn  # Add the turn

        # Castling rights
        castling_rights = ""
        if self.castling_rights["w"]["O-O"]:
            castling_rights += "K"
        if self.castling_rights["w"]["O-O-O"]:
            castling_rights += "Q"
        if self.castling_rights["b"]["O-O"]:
            castling_rights += "k"
        if self.castling_rights["b"]["O-O-O"]:
            castling_rights += "q"
        if not castling_rights:
            castling_rights = "-"
        FEN += " " + castling_rights
        # TODO: En passant
        FEN += " -"  # Placeholder, no en passant support

        FEN += " " + str(self.half_moves)  # Number of half moves since the last capture or pawn move
        FEN += " " + str(self.number_of_moves // 2 + 1)  # Number of full moves
        return FEN

    # Getters
    @property
    def board(self):
        return self.__board

    @property
    def history(self):
        return self.__history

    @property
    def game_over(self):
        return self.__game_over

    @property
    def pieces(self):
        return self.__pieces

    @property
    def castling_rights(self):
        return self.__castling_rights

    @property
    def result(self):
        return self.__result

    @property
    def number_of_moves(self):
        return self.__number_of_moves

    @property
    def half_moves(self):
        return self.__half_moves

    @property
    def turn(self):
        return self.__turn

    # Setters
    @board.setter
    def board(self, board):
        self.__board = board

    @pieces.setter
    def pieces(self, pieces):
        self.__pieces = pieces

    @turn.setter
    def turn(self, turn):
        self.__turn = turn

    @castling_rights.setter
    def castling_rights(self, castling_rights):
        self.__castling_rights = castling_rights

    @half_moves.setter
    def half_moves(self, half_moves):
        self.__half_moves = half_moves

    @number_of_moves.setter
    def number_of_moves(self, number_of_moves):
        self.__number_of_moves = number_of_moves

    @game_over.setter
    def game_over(self, game_over):
        self.__game_over = game_over

    @result.setter
    def result(self, result):
        self.__result = result

    @history.setter
    def history(self, history):
        self.__history.append(history)

    def remove_piece(self, piece):
        """ Remove a piece from the board

         :param piece: The piece to remove"""
        self.__board[piece.position[0]][piece.position[1]] = None
        self.__pieces = [p for p in self.__pieces if p != piece and p is not None]
