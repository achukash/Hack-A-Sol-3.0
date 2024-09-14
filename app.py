from flask import Flask, request, render_template, redirect, url_for
import os
import feature_analysis  # Assuming feature_analysis has your analysis functions
from user_stats import get_user_stats
import KMeans

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


@app.route('/payment' ,methods=['POST'])
def payment():
    if 'win' not in request.files or 'loss' not in request.files:
        return "Files not uploaded"
    global win_path, loss_path
    win_file = request.files['win']
    loss_file = request.files['loss']
    print(win_file)
    # Save the files if they are PGN files
    if win_file and win_file.filename.endswith('.pgn'):
        win_path = os.path.join(UPLOAD_FOLDER, win_file.filename)
        win_file.save(win_path)

    if loss_file and loss_file.filename.endswith('.pgn'):
        loss_path = os.path.join(UPLOAD_FOLDER, loss_file.filename)
        loss_file.save(loss_path)
    return render_template('payment.html')
# Route to handle file upload
@app.route('/upload')
def upload_files():
    
    
    # Analyze the files and get chess data  
        # Analyze the files and get chess data  
    win_data, loss_data, username, opponent_name = feature_analysis.print_player_analysis(win_path, loss_path)


# Predict the outcome
    prediction = KMeans.predict_game_outcome(win_path, loss_path)
    # Redirect to the analysis page and pass chess_data to it
    return render_template('index.html', win_data = win_data, loss_data = loss_data, player_data=get_user_stats(username), 
                           opponent_data=get_user_stats(opponent_name),username=username, opponent_name=opponent_name, paid = True,
                          prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
