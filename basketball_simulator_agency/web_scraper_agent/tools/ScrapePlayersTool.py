from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import ClassVar, Dict, List
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

class ScrapePlayersTool(BaseTool):
    """Tool for scraping NBA team rosters and player information."""
    
    NBA_TEAMS: ClassVar[Dict[str, str]] = {
        'Boston Celtics': 'BOS',
        'Brooklyn Nets': 'BKN',
        'New York Knicks': 'NYK',
        'Philadelphia 76ers': 'PHI',
        'Toronto Raptors': 'TOR',
        'Chicago Bulls': 'CHI',
        'Cleveland Cavaliers': 'CLE',
        'Detroit Pistons': 'DET',
        'Indiana Pacers': 'IND',
        'Milwaukee Bucks': 'MIL',
        'Atlanta Hawks': 'ATL',
        'Charlotte Hornets': 'CHA',
        'Miami Heat': 'MIA',
        'Orlando Magic': 'ORL',
        'Washington Wizards': 'WAS',
        'Denver Nuggets': 'DEN',
        'Minnesota Timberwolves': 'MIN',
        'Oklahoma City Thunder': 'OKC',
        'Portland Trail Blazers': 'POR',
        'Utah Jazz': 'UTAH',
        'Golden State Warriors': 'GSW',
        'Los Angeles Clippers': 'LAC',
        'Los Angeles Lakers': 'LAL',
        'Phoenix Suns': 'PHX',
        'Sacramento Kings': 'SAC',
        'Dallas Mavericks': 'DAL',
        'Houston Rockets': 'HOU',
        'Memphis Grizzlies': 'MEM',
        'New Orleans Pelicans': 'NO',
        'San Antonio Spurs': 'SAS'
    }

    output_path: str = Field(
        default="data/nba_active_players.csv",
        description="Path where the CSV file will be saved"
    )

    def run(self) -> str:
        """Run the player scraping tool."""
        try:
            all_players = []
            
            # Scrape each team's roster
            for team_name, team_abbrev in self.NBA_TEAMS.items():
                print(f"\nScraping {team_name} roster...")
                url = f"https://www.espn.com/nba/team/roster/_/name/{team_abbrev.lower()}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"Error fetching {team_name} roster: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                roster_table = soup.find('table', class_='Table')
                
                if not roster_table:
                    print(f"No roster table found for {team_name}")
                    continue
                
                # Find all player rows
                player_rows = roster_table.find_all('tr', class_='Table__TR')
                
                # Find the header row to determine column positions
                header_row = roster_table.find('tr', class_='Table__TR Table__even')
                if header_row:
                    headers = [th.text.strip().lower() for th in header_row.find_all('th')]
                    college_idx = next((i for i, h in enumerate(headers) if 'college' in h), 7)
                else:
                    college_idx = 7
                
                for row in player_rows:
                    try:
                        # Skip header rows
                        if row.find('th'):
                            continue
                            
                        cells = row.find_all('td')
                        if len(cells) < 8:  # Make sure we have enough cells
                            continue
                            
                        # Extract player info
                        name_cell = cells[1].find('a')
                        if not name_cell:
                            continue
                            
                        name = name_cell.text.strip()
                        position = cells[2].text.strip()  # Position is in column 3
                        age = cells[3].text.strip()      # Age is in column 4
                        height = cells[4].text.strip()    # Height is in column 5
                        weight = cells[5].text.strip()    # Weight is in column 6
                        college = cells[6].text.strip() if len(cells) > 6 else None  # College is in column 7
                        
                        # Try to convert age to integer, skip row if age is invalid
                        try:
                            age_value = int(age) if age and age != '--' else None
                        except ValueError:
                            print(f"Skipping {name} - Invalid age value: {age}")
                            continue
                        
                        player_info = {
                            'name': name,
                            'current_team': team_name,
                            'position': position,
                            'height': height,
                            'weight': weight.replace(' lbs', ''),  # Remove 'lbs' suffix
                            'age': age_value,
                            'colleges': college if college and college != '--' else None
                        }
                        
                        all_players.append(player_info)
                        print(f"Added {name} from {team_name}")
                        
                    except Exception as e:
                        print(f"Error processing player row: {str(e)}")
                        continue
                
                # Be nice to ESPN's servers
                time.sleep(2)
            
            # Save all players to CSV
            df = pd.DataFrame(all_players)
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            df.to_csv(self.output_path, index=False)
            
            print(f"\nFinished! Scraped {len(all_players)} players from {len(self.NBA_TEAMS)} teams")
            return f"Successfully scraped {len(all_players)} players and saved to {self.output_path}"
            
        except Exception as e:
            error_msg = f"Error scraping players: {str(e)}"
            print(error_msg)
            return error_msg

if __name__ == "__main__":
    tool = ScrapePlayersTool()
    print(tool.run()) 