import os
from flask import Flask, render_template, jsonify, request
from basketball_simulator_agency.game_simulation_agent.game_simulation_agent import GameSimulationAgent
from basketball_simulator_agency.database_agent.database_agent import DatabaseAgent
from basketball_simulator_agency.database_agent.tools.CreateSchemasTool import CreateSchemasTool
from basketball_simulator_agency.web_scraper_agent.tools.ScrapePlayersTool import ScrapePlayersTool
from basketball_simulator_agency.database_agent.tools.LoadDataTool import LoadDataTool
from basketball_simulator_agency.web_scraper_agent.tools.ScrapePlayerStatsTool import ScrapePlayerStatsTool

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Print environment variables for debugging
print("=== Environment Variables ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"RENDER: {os.getenv('RENDER')}")
print("=== End Environment Variables ===")

@app.route('/init_schema', methods=['POST'])
def init_schema():
    """Initialize the database schema."""
    try:
        create_schemas = CreateSchemasTool()
        create_schemas.run()
        return jsonify({
            'status': 'success',
            'message': 'Database schema created successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error creating schema: {str(e)}'
        }), 500

@app.route('/scrape_team/<team_name>', methods=['POST'])
def scrape_team(team_name):
    """Scrape a single team's roster."""
    try:
        players_tool = ScrapePlayersTool()
        players_tool.scrape_team(team_name)
        return jsonify({
            'status': 'success',
            'message': f'Successfully scraped {team_name} roster'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error scraping {team_name}: {str(e)}'
        }), 500

@app.route('/get_teams', methods=['GET'])
def get_teams():
    """Get list of NBA teams to scrape."""
    try:
        players_tool = ScrapePlayersTool()
        teams = players_tool.get_teams()
        return jsonify({
            'status': 'success',
            'teams': teams
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting teams: {str(e)}'
        }), 500

@app.route('/load_data', methods=['POST'])
def load_data():
    """Load scraped data into database."""
    try:
        load_tool = LoadDataTool()
        load_tool.run()
        return jsonify({
            'status': 'success',
            'message': 'Data loaded successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error loading data: {str(e)}'
        }), 500

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

@app.route('/scrape_stats', methods=['POST'])
def scrape_stats():
    """Scrape player statistics."""
    try:
        stats_tool = ScrapePlayerStatsTool()
        stats_tool.run()
        return jsonify({
            'status': 'success',
            'message': 'Player statistics scraped successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error scraping stats: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 