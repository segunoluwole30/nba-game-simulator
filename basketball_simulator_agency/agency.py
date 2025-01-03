import os
from agency_swarm import Agency
from web_scraper_agent.web_scraper_agent import WebScraperAgent
from database_agent.database_agent import DatabaseAgent
from game_simulation_agent.game_simulation_agent import GameSimulationAgent

# Set up settings path
settings_path = os.path.expanduser("~/.basketball_simulator_agency")
os.makedirs(settings_path, exist_ok=True)
os.environ["AGENT_SETTINGS_PATH"] = settings_path

# Initialize agents
web_scraper = WebScraperAgent()
db_agent = DatabaseAgent()
game_sim = GameSimulationAgent()

# Create agency with communication flows
agency = Agency(
    [
        game_sim,  # Make GameSimulationAgent the entry point
        [game_sim, db_agent],  # Game simulation can request data from database
        [db_agent, web_scraper],  # Database can request fresh data from scraper if needed
    ],
    shared_instructions="agency_manifesto.md"
)

if __name__ == "__main__":
    # Run the agency in interactive demo mode
    agency.run_demo() 