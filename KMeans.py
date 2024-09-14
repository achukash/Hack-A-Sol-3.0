import chess
import chess.pgn
import joblib
import numpy as np

# Load the scaler and model
scaler = joblib.load('scaler.pkl')
kmeans_model = joblib.load('kmeans_model.pkl')

def color_from_string(color_str):
    """Convert a color string ('white' or 'black') to chess.Color constant."""
    return chess.WHITE if color_str == 'white' else chess.BLACK

def extract_player_info(pgn_file, outcome):
    """Extract the winning or losing player's name, color, and ELO from the PGN file."""
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

def evaluate_phases(game):
    """Evaluate the number of moves in different phases: opening, midgame, endgame"""
    total_moves = 50#sum(1 for _ in game.mainline_moves())
    opening_moves = min(total_moves, 10)  # Define first 10 moves as opening
    endgame_moves = max(0, total_moves - 40)  # Last 20% of the game as endgame
    midgame_moves = total_moves - opening_moves - endgame_moves
    return opening_moves, midgame_moves, endgame_moves

def evaluate_tactics(board, color):
    """Evaluate tactical opportunities based on attack patterns"""
    tactics = 0
    for move in board.legal_moves:
        if board.piece_at(move.from_square) and board.piece_at(move.from_square).color == color:
            tactics += len(board.attackers(not color, move.to_square))
    return tactics

def evaluate_checkmate_threats(board, color):
    """Evaluate checkmate threats: Detect if there are threats of checkmate"""
    checkmate_threats = 0
    if board.is_checkmate():
        checkmate_threats += 1
    return checkmate_threats

def evaluate_piece_coordination(board, color):
    """Evaluate piece coordination: Friendly pieces defending each other"""
    coordination = 0
    for square, piece in board.piece_map().items():
        if piece.color == color:
            coordination += len(list(board.attackers(piece.color, square))) > 0
    return coordination

def evaluate_weak_squares(board, color):
    """Evaluate weak squares: Count squares that are weak for the current player."""
    weak_squares = 0
    color = chess.WHITE if color == 'white' else chess.BLACK
    for square in chess.SQUARES:
        attackers = len(list(board.attackers(not color, square)))
        defenders = len(list(board.attackers(color, square)))
        if attackers > defenders:
            weak_squares += 1  # More attackers than defenders
    return weak_squares

def evaluate_captures(board, color):
    """Evaluate captures: Count the number of captures made by the player"""
    captures = 0
    for move in board.move_stack:
        if board.piece_at(move.to_square) and board.piece_at(move.to_square).color != color:
            captures += 1
    return captures

def evaluate_checks(board, color):
    """Evaluate checks: Count the number of checks given by the player"""
    checks = 0
    for move in board.move_stack:
        if board.is_check():
            checks += 1
    return checks

def evaluate_castles(board, color):
    """Evaluate castles: Check if the player castled"""
    castles = 0
    for move in board.move_stack:
        piece = board.piece_at(move.from_square)
        if piece and piece.piece_type == chess.KING and abs(chess.square_file(move.from_square) - chess.square_file(move.to_square)) > 1:
            castles += 1
    return castles

def evaluate_material_balance(board, color):
    """Evaluate material balance: Difference in material value"""
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
    material_balance = sum([piece_values.get(piece.piece_type, 0) for piece in board.piece_map().values() if piece.color == color]) - \
                       sum([piece_values.get(piece.piece_type, 0) for piece in board.piece_map().values() if piece.color != color])
    return material_balance

def evaluate_king_safety(board, color):
    """Evaluate king safety: Assess king safety"""
    king_safety = 0
    king_square = board.king(color)
    if board.is_check():
        king_safety -= 1
    return king_safety

def evaluate_development(board, color):
    """Evaluate development: Number of pieces developed"""
    development = sum(1 for square, piece in board.piece_map().items() if piece.color == color and piece.piece_type in [chess.KNIGHT, chess.BISHOP])
    return development

def evaluate_space_control(board, color):
    """Evaluate space control: Number of squares controlled by the player"""
    space_control = 0
    for square in chess.SQUARES:
        if board.is_attacked_by(color, square):
            space_control += 1
    return space_control

def evaluate_pawn_weaknesses(board, color):
    """Evaluate pawn weaknesses: Count isolated or doubled pawns"""
    pawn_weaknesses = 0
    # Implement logic for detecting isolated or doubled pawns here
    return pawn_weaknesses

def evaluate_passed_pawns(board, color):
    """Evaluate passed pawns for the specified player color."""
    passed_pawns = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color and piece.piece_type == chess.PAWN:
            if is_passed_pawn(board, square, color):
                passed_pawns += 1
    return passed_pawns

def is_passed_pawn(board, square, color):
    """Check if a pawn is a passed pawn."""
    file = chess.square_file(square)
    for rank in range(chess.square_rank(square) + 1, 8):
        occupied_square = chess.square(file, rank)
        if board.piece_at(occupied_square) and board.piece_at(occupied_square).color != color:
            return False
    return True

def extract_features_for_player(board, color):
    """Extract features for the specified player color, considering all moves in the game."""
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

def extract_features_for_game(win_game, loss_game, win_color, loss_color):
    """Extract and combine features for win and loss scenarios."""
    win_board = win_game.board()
    loss_board = loss_game.board()

    win_features = extract_features_for_player(win_board, color_from_string(win_color))
    loss_features = extract_features_for_player(loss_board, color_from_string(loss_color))

    win_features_array = np.array([list(win_features.values())])
    loss_features_array = np.array([list(loss_features.values())])

    # Combine features into a single feature vector
    combined_features = np.hstack([win_features_array, loss_features_array])
    return combined_features

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

    # Scale the features
    scaled_features = scaler.transform(combined_features.reshape(1, -1))

    # Get distances to cluster centroids
    distances = kmeans_model.transform(scaled_features)

    # Calculate pseudo-probabilities based on inverse distances
    probabilities = 1 / (1 + distances)  # Shape (1, n_clusters)

    # Normalize probabilities so they sum to 1
    probabilities_normalized = probabilities / np.sum(probabilities)

    # Formatting the output
    print(f'Predicted probability of winning the next game as {white_color}: {probabilities_normalized[0][0]*100:.2f}%')
    print(f'Predicted probability of winning the next game as {black_color}: {probabilities_normalized[0][1]*100:.2f}%')

    return (f'{probabilities_normalized[0][0]*100:.2f}%', f'{probabilities_normalized[0][1]*100:.2f}%')

