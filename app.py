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
    if 'win' not in request.files or 'loss' not in request.files:
        return "Files not uploaded"

    win_file = request.files['win']
    loss_file = request.files['loss']

    # Save the files if they are PGN files
    if win_file and win_file.filename.endswith('.pgn'):
        win_path = os.path.join(UPLOAD_FOLDER, win_file.filename)
        win_file.save(win_path)

    if loss_file and loss_file.filename.endswith('.pgn'):
        loss_path = os.path.join(UPLOAD_FOLDER, loss_file.filename)
        loss_file.save(loss_path)

    return f"Files uploaded successfully: {win_file.filename}, {loss_file.filename}"

if __name__ == "__main__":
    app.run(debug=True)
