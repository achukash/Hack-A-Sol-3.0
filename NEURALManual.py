import chess.pgn
import torch
import torch.nn as nn
import numpy as np

# Define the neural network architecture
class ChessOutcomePredictor(nn.Module):
    def __init__(self):
        super(ChessOutcomePredictor, self).__init__()
        self.fc1 = nn.Linear(34, 128)  # Input layer with 68 features (34 for win and 34 for loss)
        self.fc2 = nn.Linear(128, 64)  # Hidden layer with 64 neurons
        self.fc3 = nn.Linear(64, 32)   # Hidden layer with 32 neurons
        self.fc4 = nn.Linear(32, 1)    # Output layer with 1 neuron for binary classification
        self.dropout = nn.Dropout(0.5) # Dropout layer for regularization
        self.relu = nn.ReLU()          # Activation function
        self.sigmoid = nn.Sigmoid()    # Sigmoid activation for the output layer

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.sigmoid(self.fc4(x))  # Sigmoid activation for binary output
        return x

# Load the trained neural network model
model = ChessOutcomePredictor()
model_path = r'NEURAL.pth'
model.load_state_dict(torch.load(model_path))
model.eval()  # Set the model to evaluation mode

# Function to convert color from string to chess.Color
def color_from_string(color_str):
    return chess.WHITE if color_str == 'white' else chess.BLACK

# Function to extract player info from PGN
def extract_player_info(pgn_file, outcome):
    with open(pgn_file) as pgn:
        game = chess.pgn.read_game(pgn)
        white_player = game.headers["White"]
        black_player = game.headers["Black"]
        white_elo = game.headers.get("WhiteElo", "Unknown")
        black_elo = game.headers.get("BlackElo", "Unknown")
        
        if outcome == 'win':
            if game.headers["Result"] == "1-0":
                return white_player, 'white', white_elo
            else:
                return black_player, 'black', black_elo
        elif outcome == 'loss':
            if game.headers["Result"] == "0-1":
                return white_player, 'white', white_elo
            else:
                return black_player, 'black', black_elo

# Feature extraction functions
def evaluate_phases(board):
    total_moves = len(board.move_stack)
    opening_moves = min(total_moves, 10)
    midgame_moves = max(0, total_moves - opening_moves - (total_moves - 40 if total_moves > 40 else 0))
    endgame_moves = max(0, total_moves - 40)
    return opening_moves, midgame_moves, endgame_moves

    opening_moves = min(total_moves, 10)
    endgame_moves = max(0, total_moves - 40)
    midgame_moves = total_moves - opening_moves - endgame_moves
    return opening_moves, midgame_moves, endgame_moves

def evaluate_tactics(board, color):
    tactics = 0
    for move in board.legal_moves:
        if board.piece_at(move.from_square) and board.piece_at(move.from_square).color == color:
            tactics += len(board.attackers(not color, move.to_square))
    return tactics

def evaluate_checkmate_threats(board, color):
    checkmate_threats = 0
    if board.is_checkmate():
        checkmate_threats += 1
    return checkmate_threats

def evaluate_piece_coordination(board, color):
    coordination = 0
    for square, piece in board.piece_map().items():
        if piece.color == color:
            coordination += len(list(board.attackers(piece.color, square))) > 0
    return coordination

def evaluate_weak_squares(board, color):
    weak_squares = 0
    for square in chess.SQUARES:
        attackers = len(list(board.attackers(not color, square)))
        defenders = len(list(board.attackers(color, square)))
        if attackers > defenders:
            weak_squares += 1
    return weak_squares

def evaluate_captures(board, color):
    captures = 0
    for move in board.move_stack:
        if board.piece_at(move.to_square) and board.piece_at(move.to_square).color != color:
            captures += 1
    return captures

def evaluate_checks(board, color):
    checks = 0
    for move in board.move_stack:
        if board.is_check():
            checks += 1
    return checks

def evaluate_castles(board, color):
    castles = 0
    for move in board.move_stack:
        piece = board.piece_at(move.from_square)
        if piece and piece.piece_type == chess.KING and abs(chess.square_file(move.from_square) - chess.square_file(move.to_square)) > 1:
            castles += 1
    return castles

def evaluate_material_balance(board, color):
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
    material_balance = sum([piece_values.get(piece.piece_type, 0) for piece in board.piece_map().values() if piece.color == color]) - \
                       sum([piece_values.get(piece.piece_type, 0) for piece in board.piece_map().values() if piece.color != color])
    return material_balance

def evaluate_king_safety(board, color):
    king_safety = 0
    king_square = board.king(color)
    if board.is_check():
        king_safety -= 1
    return king_safety

def evaluate_development(board, color):
    development = sum(1 for square, piece in board.piece_map().items() if piece.color == color and piece.piece_type in [chess.KNIGHT, chess.BISHOP])
    return development

def evaluate_space_control(board, color):
    space_control = 0
    for square in chess.SQUARES:
        if board.is_attacked_by(color, square):
            space_control += 1
    return space_control

def evaluate_pawn_weaknesses(board, color):
    weaknesses = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color and piece.piece_type == chess.PAWN:
            # Example: Check if pawn is isolated or doubled
            if is_isolated_pawn(board, square, color):
                weaknesses += 1
    return weaknesses

def is_isolated_pawn(board, square, color):
    file = chess.square_file(square)
    for adjacent_file in [file - 1, file + 1]:
        if 0 <= adjacent_file < 8:
            if board.piece_at(chess.square(adjacent_file, chess.square_rank(square))) and board.piece_at(chess.square(adjacent_file, chess.square_rank(square))).color == color:
                return False
    return True

def is_passed_pawn(board, square, color):
    file = chess.square_file(square)
    for rank in range(chess.square_rank(square) + 1, 8):
        occupied_square = chess.square_rank(chess.square(file, rank))
        if board.piece_at(occupied_square) and board.piece_at(occupied_square).color != color:
            return False
    return True

def evaluate_passed_pawns(board, color):
    passed_pawns = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color and piece.piece_type == chess.PAWN:
            if is_passed_pawn(board, square, color):
                passed_pawns += 1
    return passed_pawns
# Function to extract all features for a player
def extract_features_for_player(board, color):
    total_moves = len(board.move_stack)
    opening_moves, midgame_moves, endgame_moves = evaluate_phases(board)
    features = {
        "total_moves": total_moves,
        "opening_moves": opening_moves,
        "midgame_moves": midgame_moves,
        "endgame_moves": endgame_moves,
        "tactical_opportunities": evaluate_tactics(board, color),
        "checkmate_threats": evaluate_checkmate_threats(board, color),
        "piece_coordination": evaluate_piece_coordination(board, color),
        "weak_squares": evaluate_weak_squares(board, color),
        "passed_pawns": evaluate_passed_pawns(board, color),
        "king_safety": evaluate_king_safety(board, color),
        "material_balance": evaluate_material_balance(board, color),
        "development": evaluate_development(board, color),
        "space_control": evaluate_space_control(board, color),
        "pawn_weaknesses": evaluate_pawn_weaknesses(board, color),
        "captures": evaluate_captures(board, color),
        "checks": evaluate_checks(board, color),
        "castles": evaluate_castles(board, color)
    }
    return features

# Function to combine features for win and loss games
def extract_features_for_game(win_game, loss_game, win_color, loss_color):
    win_board = win_game.board()
    loss_board = loss_game.board()

    win_features = extract_features_for_player(win_board, color_from_string(win_color))
    loss_features = extract_features_for_player(loss_board, color_from_string(loss_color))

    win_features_array = np.array([list(win_features.values())])
    loss_features_array = np.array([list(loss_features.values())])

    # Combine features into a single feature vector
    combined_features = np.hstack([win_features_array, loss_features_array])
    return combined_features

# Function to predict the game outcome using the neural network model
def predict_game_outcome(win_pgn_path, loss_pgn_path):
    # Load games from PGN files
    with open(win_pgn_path) as win_pgn, open(loss_pgn_path) as loss_pgn:
        win_game = chess.pgn.read_game(win_pgn)
        loss_game = chess.pgn.read_game(loss_pgn)

    # Extract player names and colors from the PGN files
    white_player, white_color, _ = extract_player_info(win_pgn_path, 'win')
    black_player, black_color, _ = extract_player_info(loss_pgn_path, 'loss')

    # Extract features
    combined_features = extract_features_for_game(win_game, loss_game, white_color, black_color)

    # Convert the features to a PyTorch tensor
    features_tensor = torch.tensor(combined_features, dtype=torch.float32)

    # Pass the features through the neural network to get the predicted probability
    with torch.no_grad():
                probability = model(features_tensor).item() * 100  # Output probability in percentage

    # Formatting the output
    print(f'Predicted probability of winning the next game as {white_color}: {probability:.2f}%')
    print(f'Predicted probability of winning the next game as {black_color}: {100 - probability:.2f}%')

    return (f'{probability:.2f}%', f'{100 - probability:.2f}%')

# # Example PGN file paths
# win_pgn_path = r"D:\Hackathons\Hack-a-sol-24\split\1012win.pgn"
# loss_pgn_path = r"D:\Hackathons\Hack-a-sol-24\split\1012loss.pgn"

# # Call the function and predict the outcome
# predict_game_outcome(win_pgn_path, loss_pgn_path)
