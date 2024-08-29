import tensorflow as tf
from tensorflow.keras import layers, Model
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import custom_object_scope
import re
from scipy.special import softmax




# --- Data Loading and Preprocessing ---
def load_and_preprocess_data():
    df = pd.read_json('/home/im07813/Desktop/checkit/training_dataset.json')
    df = pd.json_normalize(df['games'])

    # Tokenizers
    board_tokenizer = Tokenizer(char_level=True)
    turn_tokenizer = Tokenizer(char_level=True)

    # Tokenize 'board' and 'turn' features 
    board_tokenizer.fit_on_texts(df['board'])
    turn_tokenizer.fit_on_texts(df['turn'])

    board_tokens = board_tokenizer.texts_to_sequences(df['board'])
    turn_tokens = turn_tokenizer.texts_to_sequences(df['turn'])

    board_tokens = tf.keras.preprocessing.sequence.pad_sequences(board_tokens, maxlen=512)
    turn_tokens = tf.keras.preprocessing.sequence.pad_sequences(turn_tokens, maxlen=512)

    features = np.concatenate([board_tokens, turn_tokens], axis=1)

    # Encode labels
    le = LabelEncoder()
    labels = le.fit_transform(df['result'])

    return features, labels, board_tokenizer, turn_tokenizer, le 

# Positional Encoding
class PositionalEncoding(layers.Layer):
    def __init__(self, position, d_model):
        super(PositionalEncoding, self).__init__()
        self.pos_encoding = self.positional_encoding(position, d_model)

    def get_angles(self, position, i, d_model):
        angles = 1 / tf.pow(10000, (2 * (i // 2)) / tf.cast(d_model, tf.float32))
        return position * angles

    def positional_encoding(self, position, d_model):
        angle_rads = self.get_angles(
            position=tf.range(position, dtype=tf.float32)[:, tf.newaxis],
            i=tf.range(d_model, dtype=tf.float32)[tf.newaxis, :],
            d_model=d_model)
        # apply sin to even indices in the array; 2i
        sines = tf.math.sin(angle_rads[:, 0::2])
        # apply cos to odd indices in the array; 2i+1
        cosines = tf.math.cos(angle_rads[:, 1::2])

        pos_encoding = tf.concat([sines, cosines], axis=-1)
        pos_encoding = pos_encoding[tf.newaxis, ...]
        return tf.cast(pos_encoding, tf.float32)

    def call(self, inputs):
        return inputs + self.pos_encoding[:, :tf.shape(inputs)[1], :]

# Transformer Encoder Layer
class TransformerBlock(tf.keras.layers.Layer):
    def __init__(self, embed_dim=64, num_heads=8, ff_dim=256, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = tf.keras.layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential(
            [tf.keras.layers.Dense(ff_dim, activation="relu"), tf.keras.layers.Dense(embed_dim),]
        )
        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


class ChessTransformer:
    def __init__(self, board_tokenizer, turn_tokenizer, le):
        self.model = None 
        self.board_tokenizer = board_tokenizer
        self.turn_tokenizer = turn_tokenizer
        self.le = le

    def create_model(self, input_dim=100, embed_dim=64, num_heads=8, ff_dim=256):
        inputs = layers.Input(shape=(1024,)) 
       
        x = layers.Embedding(input_dim=input_dim, output_dim=embed_dim)(inputs)
        x = PositionalEncoding(1024, embed_dim)(x) 
        x = TransformerBlock(embed_dim, num_heads, ff_dim)(x, training=True)
        x = layers.GlobalAveragePooling1D()(x)
        outputs = layers.Dense(3, activation='softmax')(x)
        return Model(inputs=inputs, outputs=outputs)

    def load(self, path):
        with custom_object_scope({'PositionalEncoding': PositionalEncoding, 'TransformerBlock': TransformerBlock}):
            self.model = tf.keras.models.load_model(path)

    def train(self, features, labels, epochs=1):
        if self.model is None:
            self.model = self.create_model()

        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        self.model.fit(features, labels, epochs=epochs) 
        self.model.save("/home/im07813/Desktop/checkit/transformer.h5")

    def predict(self, fen):
        # Split the FEN string into board and turn components
        match = re.match(r"^(.*?)\s([wb])\s", fen)
        if match is None:
            raise ValueError("Invalid FEN string")
        board, turn = match.groups()

        # Transform the board and turn components
        board_tokens = self.board_tokenizer.texts_to_matrix([board])
        turn_tokens = self.turn_tokenizer.texts_to_matrix([turn])

        # Pad the sequences
        board_tokens = tf.keras.preprocessing.sequence.pad_sequences(board_tokens, maxlen=512)
        turn_tokens = tf.keras.preprocessing.sequence.pad_sequences(turn_tokens, maxlen=512)

        # Concatenate the tokens and make a prediction
        features = np.concatenate([board_tokens, turn_tokens], axis=1)
        prediction = self.model.predict(features)
        
        # Convert the raw prediction to probabilities using the softmax function
        probabilities = softmax(prediction[0])

        # Return the probabilities
        return probabilities

        # Return the prediction
        #return self.le.inverse_transform([np.argmax(prediction)])

# --- Main Program ---
if __name__ == "__main__":
    # Load and preprocess data
    features, labels, board_tokenizer, turn_tokenizer, le = load_and_preprocess_data()

    # Create model instance
    model = ChessTransformer(board_tokenizer = board_tokenizer, turn_tokenizer= turn_tokenizer, le = le) 
    


    # Train (uncomment if needed)
    #model.train(features, labels)

    # Save (uncomment if needed)
    #model.save("/home/im07813/Desktop/chess/AI/transformer/transformer.h5")  

    # Load 
    model.load("/home/im07813/Desktop/chessgpt/AI/transformer/transformer.h5")  

    # Example prediction
    #fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    #prediction = model.predict(fen)
    #print(f"Predicted Result: {prediction}")




