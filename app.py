from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

# Game state
active_games = {}

def generate_crash_point():
    # Generate a random crash point with house edge
    # Most crashes occur between 1.00x and 2.00x
    # But occasionally allows for higher multipliers
    r = random.random()
    if r < 0.7:  # 70% chance for lower multipliers
        return round(1.00 + random.random() * 1.00, 2)
    else:  # 30% chance for higher multipliers
        return round(1.00 + random.random() * 10.00, 2)

def game_loop(game_id):
    game = active_games[game_id]
    multiplier = 1.00
    
    while multiplier < game['crash_point'] and not game['stopped']:
        time.sleep(0.1)  # Update every 100ms
        multiplier = round(multiplier + 0.01, 2)
        game['current_multiplier'] = multiplier
        socketio.emit('game_update', {
            'multiplier': multiplier,
            'game_id': game_id
        })
    
    # Game ended (either crashed or stopped)
    game_result = {
        'crashed': not game['stopped'],
        'final_multiplier': multiplier,
        'crash_point': game['crash_point']
    }
    socketio.emit('game_end', game_result)
    del active_games[game_id]

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_game')
def handle_start_game(data):
    game_id = str(time.time())
    crash_point = generate_crash_point()
    
    active_games[game_id] = {
        'crash_point': crash_point,
        'current_multiplier': 1.00,
        'stopped': False,
        'bet_amount': data.get('bet_amount', 0)
    }
    
    # Start game loop in a separate thread
    game_thread = threading.Thread(target=game_loop, args=(game_id,))
    game_thread.start()
    
    return {'game_id': game_id}

@socketio.on('stop_game')
def handle_stop_game(data):
    game_id = data.get('game_id')
    if game_id in active_games:
        game = active_games[game_id]
        game['stopped'] = True
        
        return {
            'success': True,
            'multiplier': game['current_multiplier'],
            'winnings': game['bet_amount'] * game['current_multiplier']
        }
    return {'success': False}

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=5009)
