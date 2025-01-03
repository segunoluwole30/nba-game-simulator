import os
from flask import Flask, render_template, jsonify, request
from basketball_simulator_agency.database_agent.tools.CreateSchemasTool import CreateSchemasTool
from basketball_simulator_agency.web_scraper_agent.tools.ScrapePlayersTool import ScrapePlayersTool
from basketball_simulator_agency.database_agent.tools.LoadDataTool import LoadDataTool
from basketball_simulator_agency.web_scraper_agent.tools.ScrapePlayerStatsTool import ScrapePlayerStatsTool
import psycopg2
from urllib.parse import urlparse
from agency_swarm import Agency
from basketball_simulator_agency.game_simulation_agent.tools.SimulateGameTool import SimulateGameTool
from basketball_simulator_agency.game_simulation_agent.tools.SimulateDailyGamesTool import SimulateDailyGamesTool

app = Flask(__name__)

# Initialize database and load data on startup
try:
    # Verify OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("WARNING: OPENAI_API_KEY not set. Game simulations will not work!")
    else:
        print("OpenAI API key verified")
    
    print("Initializing database schema...")
    create_schemas = CreateSchemasTool()
    create_schemas.run()
    
    print("Scraping player data...")
    players_tool = ScrapePlayersTool()
    players_tool.run()
    
    print("Scraping player statistics...")
    stats_tool = ScrapePlayerStatsTool()
    stats_tool.run()
    
    print("Loading player data...")
    load_tool = LoadDataTool()
    load_tool.run()
    
    print("Database initialization complete!")
except Exception as e:
    print(f"Error during initialization: {str(e)}")
    print("Continuing with partial initialization...")

@app.route('/')
def index():
    """Render the main page with team options."""
    try:
        # Get list of teams from ScrapePlayersTool
        scraper = ScrapePlayersTool()
        teams = scraper.get_teams()
        return render_template('index.html', teams=teams)
    except Exception as e:
        print(f"Error getting teams: {str(e)}")
        return render_template('index.html', teams=[])

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

def verify_db_connection():
    """Verify database connection is working."""
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise Exception("DATABASE_URL environment variable not set")
            
        print(f"Verifying database connection...")
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        
        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname
        )
        conn.close()
        print("Database connection verified successfully")
        return True
    except Exception as e:
        print(f"Database connection verification failed: {str(e)}")
        return False

@app.route('/simulate_game/<home_team>/<away_team>')
def simulate_game(home_team, away_team):
    try:
        print(f"\nAttempting to simulate game: {home_team} vs {away_team}")
        
        # Get database connection details
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise Exception("DATABASE_URL environment variable not set")
            
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        
        if not verify_db_connection():
            raise Exception("Could not connect to database")
            
        # Create SimulateGameTool with team names and database details
        game_tool = SimulateGameTool(
            home_team=home_team, 
            away_team=away_team,
            db_name=database,
            db_user=username,
            db_password=password,
            db_host=hostname
        )
        result = game_tool.run()
        print("Game simulation completed successfully")
        
        return jsonify({"result": result})
    except Exception as e:
        print(f"Error in simulate_game: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return jsonify({"error": f"Error simulating game: {str(e)}"}), 500

@app.route('/simulate_daily')
def simulate_daily():
    try:
        print("\nAttempting to simulate daily games")
        
        # Get database connection details
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise Exception("DATABASE_URL environment variable not set")
            
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        
        if not verify_db_connection():
            raise Exception("Could not connect to database")
            
        # Use SimulateDailyGamesTool with database parameters
        daily_tool = SimulateDailyGamesTool(
            db_name=database,
            db_user=username,
            db_password=password,
            db_host=hostname
        )
        result = daily_tool.run()
        print("Daily games simulation completed successfully")
        
        return jsonify({"result": result})
    except Exception as e:
        print(f"Error in simulate_daily: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return jsonify({"error": f"Error simulating daily games: {str(e)}"}), 500

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