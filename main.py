from transformer.transformer import PositionalEncoding
from transformer.transformer import TransformerBlock
from transformer.transformer import ChessTransformer
from MCTS.monte_carlo_tree_search import MCTS
from Chess.Board.GameState import GameState
from Chess.Repository.ChessRepository import ChessRepository
from Chess.UI.console import UI
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder
from transformer.transformer import load_and_preprocess_data


if __name__ == "__main__":
    
    chess_repository = ChessRepository()
    chess_repository.initialize_board()
    game_state = GameState(chess_repository)


    features, labels, board_tokenizer, turn_tokenizer, le = load_and_preprocess_data()
    model = ChessTransformer(board_tokenizer, turn_tokenizer, le) 

    
    model.load("transformer/TrainedModels/transformer.h5")
    
    ui = UI(game_state, model)
    ui.start()
    
    
