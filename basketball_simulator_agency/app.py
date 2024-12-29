import os
from flask import Flask, render_template, jsonify
from game_simulation_agent.game_simulation_agent import GameSimulationAgent
from database_agent.database_agent import DatabaseAgent

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Print environment variables for debugging
print("=== Environment Variables ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"RENDER: {os.getenv('RENDER')}")
print("=== End Environment Variables ===")

@app.route('/simulate_game/<home_team>/<away_team>')
def simulate_game(home_team, away_team):
    try:
        game_agent = GameSimulationAgent()
        result = game_agent.handle_request(f"Simulate a game between {home_team} and {away_team}")
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/simulate_daily')
def simulate_daily():
    try:
        game_agent = GameSimulationAgent()
        result = game_agent.handle_request("Simulate all NBA games today")
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 