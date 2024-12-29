import os
import csv
import requests
from bs4 import BeautifulSoup
from typing import ClassVar, Dict
from agency_swarm.tools import BaseTool

class ScrapePlayersTool(BaseTool):
    """Tool for scraping NBA players from ESPN."""
    
    NBA_TEAMS: ClassVar[Dict[str, str]] = {
        'Atlanta Hawks': 'atl/atlanta-hawks',
        'Boston Celtics': 'bos/boston-celtics',
        'Brooklyn Nets': 'bkn/brooklyn-nets',
        'Charlotte Hornets': 'cha/charlotte-hornets',
        'Chicago Bulls': 'chi/chicago-bulls',
        'Cleveland Cavaliers': 'cle/cleveland-cavaliers',
        'Dallas Mavericks': 'dal/dallas-mavericks',
        'Denver Nuggets': 'den/denver-nuggets',
        'Detroit Pistons': 'det/detroit-pistons',
        'Golden State Warriors': 'gs/golden-state-warriors',
        'Houston Rockets': 'hou/houston-rockets',
        'Indiana Pacers': 'ind/indiana-pacers',
        'LA Clippers': 'lac/la-clippers',
        'Los Angeles Lakers': 'lal/los-angeles-lakers',
        'Memphis Grizzlies': 'mem/memphis-grizzlies',
        'Miami Heat': 'mia/miami-heat',
        'Milwaukee Bucks': 'mil/milwaukee-bucks',
        'Minnesota Timberwolves': 'min/minnesota-timberwolves',
        'New Orleans Pelicans': 'no/new-orleans-pelicans',
        'New York Knicks': 'ny/new-york-knicks',
        'Oklahoma City Thunder': 'okc/oklahoma-city-thunder',
        'Orlando Magic': 'orl/orlando-magic',
        'Philadelphia 76ers': 'phi/philadelphia-76ers',
        'Phoenix Suns': 'phx/phoenix-suns',
        'Portland Trail Blazers': 'por/portland-trail-blazers',
        'Sacramento Kings': 'sac/sacramento-kings',
        'San Antonio Spurs': 'sa/san-antonio-spurs',
        'Toronto Raptors': 'tor/toronto-raptors',
        'Utah Jazz': 'utah/utah-jazz',
        'Washington Wizards': 'wsh/washington-wizards'
    }

    def get_teams(self):
        """Get list of NBA teams."""
        return list(self.NBA_TEAMS.keys())

    def scrape_team(self, team_name):
        """Scrape a single team's roster."""
        if team_name not in self.NBA_TEAMS:
            raise ValueError(f"Invalid team name: {team_name}")

        # Initialize or append to CSV file
        file_exists = os.path.isfile('nba_active_players.csv')
        mode = 'a' if file_exists else 'w'
        
        with open('nba_active_players.csv', mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['name', 'current_team', 'position', 'number', 'height', 'weight', 'age', 'college'])

            print(f"Scraping {team_name} roster...")
            team_path = self.NBA_TEAMS[team_name]
            url = f"https://www.espn.com/nba/team/roster/_/name/{team_path}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all player rows
            player_rows = soup.find_all('tr', class_='Table__TR')
            
            for row in player_rows:
                cells = row.find_all('td')
                if len(cells) >= 4:  # Make sure row has enough cells
                    try:
                        # Get the name element and its text
                        name_element = cells[1].find('a')
                        name = name_element.get_text(strip=True) if name_element else cells[1].get_text(strip=True)
                        position = cells[2].get_text(strip=True)
                        
                        # Get player number from first cell
                        number_text = cells[0].get_text(strip=True)
                        # Remove any non-numeric characters except for decimal points
                        number = ''.join(c for c in number_text if c.isdigit())
                        
                        # Write player data
                        writer.writerow([name, team_name, position, number, '', '', '', ''])
                        print(f"Added {name} (#{number if number else 'N/A'}) from {team_name}")
                    except Exception as e:
                        print(f"Error processing player: {str(e)}")
                        continue

    def run(self):
        """Create/update the active players CSV file."""
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Create/overwrite the CSV file
        with open('data/nba_active_players.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'current_team', 'position', 'number', 'height', 'weight', 'age', 'college'])
        
        # Scrape each team's roster
        for team_name in self.NBA_TEAMS:
            try:
                self.scrape_team(team_name)
            except Exception as e:
                print(f"Error scraping {team_name}: {str(e)}")
                continue 