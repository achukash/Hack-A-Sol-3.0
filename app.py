from flask import Flask, request, render_template, redirect, url_for
import os

app = Flask(__name__)

# Folder to save uploaded files
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route to render index.html (the HTML template you provided)
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'player1' not in request.files or 'player2' not in request.files:
        return "Files not uploaded"

    player1_file = request.files['player1']
    player2_file = request.files['player2']

    # Save the files if they are PGN files
    if player1_file and player1_file.filename.endswith('.pgn'):
        player1_path = os.path.join(UPLOAD_FOLDER, player1_file.filename)
        player1_file.save(player1_path)

    if player2_file and player2_file.filename.endswith('.pgn'):
        player2_path = os.path.join(UPLOAD_FOLDER, player2_file.filename)
        player2_file.save(player2_path)

    return f"Files uploaded successfully: {player1_file.filename}, {player2_file.filename}"

if __name__ == "__main__":
    app.run(debug=True)
