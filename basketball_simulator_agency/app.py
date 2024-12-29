from flask import Flask, render_template, request, jsonify
from basketball_simulator_agency.game_simulation_agent.tools.SimulateGameTool import SimulateGameTool
from basketball_simulator_agency.game_simulation_agent.tools.SimulateDailyGamesTool import SimulateDailyGamesTool
from basketball_simulator_agency.database_agent.tools.QueryTeamsTool import QueryTeamsTool
from basketball_simulator_agency.database_agent.tools.CreateSchemasTool import CreateSchemasTool
from basketball_simulator_agency.web_scraper_agent.tools.ScrapeTeamsTool import ScrapeTeamsTool
from basketball_simulator_agency.web_scraper_agent.tools.ScrapePlayersTool import ScrapePlayersTool
from basketball_simulator_agency.database_agent.tools.LoadDataTool import LoadDataTool
import os

app = Flask(__name__)

# Configure for production
if os.environ.get('RENDER'):
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )

@app.route('/')
def index():
    # Get list of teams for dropdowns
    teams_tool = QueryTeamsTool()
    teams = teams_tool.run()
    return render_template('index.html', teams=teams)

@app.route('/init_db', methods=['POST'])
def init_db():
    """Initialize the database with teams and players."""
    try:
        # Create database schemas
        create_schemas = CreateSchemasTool()
        create_schemas.run()
        
        # Scrape teams and players
        teams_tool = ScrapeTeamsTool()
        players_tool = ScrapePlayersTool()
        teams_tool.run()
        players_tool.run()
        
        # Load data into database
        load_tool = LoadDataTool()
        load_tool.run()
        
        return jsonify({
            'status': 'success',
            'message': 'Database initialized successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error initializing database: {str(e)}'
        }), 500

@app.route('/simulate', methods=['POST'])
def simulate_game():
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    
    if not home_team or not away_team:
        return jsonify({'error': 'Please select both teams'})
    
    simulator = SimulateGameTool(home_team=home_team, away_team=away_team)
    result = simulator.run()
    return jsonify({'result': result})

@app.route('/simulate_daily', methods=['POST'])
def simulate_daily():
    try:
        simulator = SimulateDailyGamesTool()
        result = simulator.run()
        
        # If no games are scheduled
        if "No games scheduled for today" in result:
            return jsonify({'result': result})
            
        # Return the full simulation results including box scores
        return jsonify({'result': result})
        
    except Exception as e:
        return jsonify({'error': f'Error simulating daily games: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Render."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 