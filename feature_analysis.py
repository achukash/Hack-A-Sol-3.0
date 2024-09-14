import chess.pgn
import chess.engine
import chess


engine = chess.engine.SimpleEngine.popen_uci(r'D:\ARVIND\Chess\stockfish\stockfish-windows-x86-64-avx2.exe')

print("Chess engine initialized!")

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
    total_moves = sum(1 for _ in game.mainline_moves())
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
        occupied_square = chess.square_rank(chess.square(file, rank))
        if board.piece_at(occupied_square) and board.piece_at(occupied_square).color != color:
            return False
    return True

def evaluate_king_safety(board, color):
    """Evaluate the safety of the king for the specified player color."""
    king_square = board.king(color)
    if not king_square:
        return 0
    return len(board.attackers(not color, king_square))

def evaluate_material_balance(board, color):
    """Evaluate material balance for the specified player color."""
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
    material_balance = sum([piece_values.get(piece.piece_type, 0) for piece in board.piece_map().values() if piece.color == color])
    material_balance -= sum([piece_values.get(piece.piece_type, 0) for piece in board.piece_map().values() if piece.color != color])
    return material_balance

def evaluate_development(board, color):
    """Evaluate development for the specified player color."""
    development_score = 0
    # Example: Count developed pieces (pieces that are not in their starting positions)
    starting_positions = {chess.WHITE: [chess.A1, chess.B1, chess.C1, chess.D1, chess.E1, chess.F1, chess.G1, chess.H1],
                          chess.BLACK: [chess.A8, chess.B8, chess.C8, chess.D8, chess.E8, chess.F8, chess.G8, chess.H8]}
    for square in board.piece_map():
        piece = board.piece_at(square)
        if piece.color == color and square not in starting_positions[color]:
            development_score += 1
    return development_score

def evaluate_space_control(board, color):
    """Evaluate space control for the specified player color."""
    controlled_squares = set()
    for square in board.piece_map():
        piece = board.piece_at(square)
        if piece and piece.color == color:
            controlled_squares.update(board.attacks(square))
    return len(controlled_squares)


def evaluate_pawn_weaknesses(board, color):
    """Evaluate pawn weaknesses for the specified player color."""
    weaknesses = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color and piece.piece_type == chess.PAWN:
            # Example: Check if pawn is isolated or doubled
            if is_isolated_pawn(board, square, color):
                weaknesses += 1
    return weaknesses

def is_isolated_pawn(board, square, color):
    """Check if a pawn is isolated (has no pawns on adjacent files)."""
    file = chess.square_file(square)
    for adjacent_file in [file - 1, file + 1]:
        if 0 <= adjacent_file < 8:
            if board.piece_at(chess.square(adjacent_file, chess.square_rank(square))) and board.piece_at(chess.square(adjacent_file, chess.square_rank(square))).color == color:
                return False
    return True

def evaluate_checks(board, color):
    """Evaluate number of checks delivered by the specified player color."""
    checks = 0
    for move in board.legal_moves:
        if board.is_checkmate():
            checks += 1
    return checks

def evaluate_castles(board, color):
    """Evaluate castling opportunities for the specified player color."""
    if color == chess.WHITE:
        return 1 if board.has_castling_rights(chess.WHITE) else 0
    else:
        return 1 if board.has_castling_rights(chess.BLACK) else 0

def extract_features_for_player(game, color):
    """Extract features for the specified player color, considering all moves in the game."""
    color = chess.WHITE if color == 'white' else chess.BLACK  # Ensure color is correct constant
    board = game.board()
    total_moves = 0
    for move in game.mainline_moves():
        board.push(move)
        total_moves += 1
    
    # Phase evaluation
    opening_moves, midgame_moves, endgame_moves = evaluate_phases(game)
    
    return {
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

def print_player_analysis(win_pgn_path, loss_pgn_path) :
    # Block 4: Perform Analysis for Each Player

# Define file paths
    

    # Extract features for the winning player in the win game
    winner_name, winner_color, winner_elo = extract_player_info(win_pgn_path, 'win')
    print(f"Winning Player: {winner_name}, Color: {winner_color}, ELO: {winner_elo}")

    with open(win_pgn_path) as win_pgn:
        win_game = chess.pgn.read_game(win_pgn)
        features_win = extract_features_for_player(win_game, winner_color)
        print("Features for the Win Game:", features_win)

    # Extract features for the losing player in the loss game
    loser_name, loser_color, loser_elo = extract_player_info(loss_pgn_path, 'loss')
    print(f"Losing Player: {loser_name}, Color: {loser_color}, ELO: {loser_elo}")

    with open(loss_pgn_path) as loss_pgn:
        loss_game = chess.pgn.read_game(loss_pgn)
        features_loss = extract_features_for_player(loss_game, loser_color)
        print("Features for the Loss Game:", features_loss)
    engine.close()
