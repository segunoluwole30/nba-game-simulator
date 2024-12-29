from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from .SimulateGameTool import SimulateGameTool

class SimulateDailyGamesTool(BaseTool):
    """Tool for simulating all NBA games scheduled for today."""
    
    output_file: str = Field(
        default="/tmp/daily_simulations.txt",
        description="Path where the simulation results will be saved"
    )
    db_name: str = Field(
        description="Database name"
    )
    db_user: str = Field(
        description="Database user"
    )
    db_password: str = Field(
        description="Database password"
    )
    db_host: str = Field(
        description="Database host",
        default="localhost"
    )

    def get_todays_games(self):
        """Scrape today's NBA games from ESPN."""
        try:
            url = "https://www.espn.com/nba/schedule/_/date/" + datetime.now().strftime("%Y%m%d")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Map of ESPN team names to official names in our database
            TEAM_NAME_MAP = {
                'Atlanta': 'Atlanta Hawks',
                'Boston': 'Boston Celtics',
                'Brooklyn': 'Brooklyn Nets',
                'Charlotte': 'Charlotte Hornets',
                'Chicago': 'Chicago Bulls',
                'Cleveland': 'Cleveland Cavaliers',
                'Dallas': 'Dallas Mavericks',
                'Denver': 'Denver Nuggets',
                'Detroit': 'Detroit Pistons',
                'Golden State': 'Golden State Warriors',
                'Houston': 'Houston Rockets',
                'Indiana': 'Indiana Pacers',
                'LA': 'Los Angeles Clippers',
                'Los Angeles': 'Los Angeles Lakers',
                'Memphis': 'Memphis Grizzlies',
                'Miami': 'Miami Heat',
                'Milwaukee': 'Milwaukee Bucks',
                'Minnesota': 'Minnesota Timberwolves',
                'New Orleans': 'New Orleans Pelicans',
                'New York': 'New York Knicks',
                'Oklahoma City': 'Oklahoma City Thunder',
                'Orlando': 'Orlando Magic',
                'Philadelphia': 'Philadelphia 76ers',
                'Phoenix': 'Phoenix Suns',
                'Portland': 'Portland Trail Blazers',
                'Sacramento': 'Sacramento Kings',
                'San Antonio': 'San Antonio Spurs',
                'Toronto': 'Toronto Raptors',
                'Utah': 'Utah Jazz',
                'Washington': 'Washington Wizards'
            }
            
            print(f"Fetching schedule from: {url}")
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch schedule: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            print("Fetched schedule page. Looking for games...")
            
            games = []
            
            # Find all game containers
            game_containers = soup.find_all('div', class_='matchTeams')
            print(f"Found {len(game_containers)} game containers")
            
            for container in game_containers:
                # Find team links
                team_links = container.find_all('a')
                if len(team_links) >= 2:
                    away_team = team_links[0].text.strip()
                    home_team = team_links[1].text.strip()
                    
                    # Map to official team names
                    if away_team in TEAM_NAME_MAP and home_team in TEAM_NAME_MAP:
                        away_team_full = TEAM_NAME_MAP[away_team]
                        home_team_full = TEAM_NAME_MAP[home_team]
                        print(f"Found game: {away_team_full} @ {home_team_full}")
                        games.append((away_team_full, home_team_full))
                    else:
                        print(f"Warning: Could not map team names: {away_team} @ {home_team}")
            
            if not games:
                print("No games found in today's schedule")
            else:
                print(f"Successfully found {len(games)} games for today")
                
            return games
            
        except Exception as e:
            print(f"Error scraping schedule: {str(e)}")
            return []

    def run(self) -> str:
        """Run daily game simulations."""
        try:
            # Get today's games
            print("\nFetching today's games...")
            games = self.get_todays_games()
            if not games:
                return "No games scheduled for today. (If this seems incorrect, there might be an issue with the schedule scraping)"

            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

            # Prepare the output
            today = datetime.now().strftime("%A, %B %d, %Y")
            result = f"NBA Game Simulations for {today}\n"
            result += "=" * 80 + "\n\n"

            # Simulate each game
            for away_team, home_team in games:
                result += f"Game: {away_team} @ {home_team}\n"
                result += "-" * 80 + "\n"
                
                # Create a new simulator instance for each game with proper parameters
                simulator = SimulateGameTool(
                    home_team=home_team,
                    away_team=away_team,
                    db_name=self.db_name,
                    db_user=self.db_user,
                    db_password=self.db_password,
                    db_host=self.db_host
                )
                game_result = simulator.run()
                
                # Add game results
                result += game_result
                result += "\n" + "=" * 80 + "\n\n"

            # Save to file
            with open(self.output_file, 'w') as f:
                f.write(result)

            # Return the actual results instead of just a success message
            return result

        except Exception as e:
            return f"Error simulating daily games: {str(e)}"

if __name__ == "__main__":
    tool = SimulateDailyGamesTool()
    print(tool.run()) 