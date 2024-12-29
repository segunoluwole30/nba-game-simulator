from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import pandas as pd
import requests
import time
import csv

class ScrapePlayerStatsTool(BaseTool):
    """
    A tool for scraping NBA player statistics from ESPN's API.
    The tool fetches player stats and saves them to a CSV file.
    """
    output_path: str = Field(
        default="nba_player_stats.csv",
        description="Path where the CSV file will be saved"
    )

    def run(self):
        """Scrape player statistics from ESPN."""
        try:
            # Create output file
            with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'name', 'games_played', 'minutes_per_game', 'points_per_game',
                    'rebounds_per_game', 'assists_per_game', 'steals_per_game',
                    'blocks_per_game', 'field_goal_percentage', 'three_point_percentage',
                    'free_throw_percentage', 'turnovers_per_game'
                ])
            
            # ESPN's internal API endpoint for player stats
            url = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/statistics/byathlete?region=us&lang=en&contentorigin=espn&isqualified=true&page=1&limit=50&category=offensive&sort=offensive.avgPoints%3Adesc"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            all_players = []
            page = 1
            
            while True:
                print(f"\nFetching page {page}...")
                current_url = url.replace("page=1", f"page={page}")
                
                response = requests.get(current_url, headers=headers)
                if response.status_code != 200:
                    print(f"Error fetching page {page}: {response.status_code}")
                    break
                    
                data = response.json()
                
                # Check if we have athlete data
                if 'athletes' not in data or not data['athletes']:
                    print("No more players found")
                    break
                
                # Process each player
                for athlete in data['athletes']:
                    try:
                        # Get basic info
                        player_info = athlete['athlete']
                        name = player_info['displayName']
                        team = player_info.get('teamShortName', '')
                        
                        # Initialize stats dictionary
                        stats = {}
                        
                        # Extract stats from each category
                        for category in athlete['categories']:
                            if category['name'] == 'general':
                                # Games played is the first value in general category
                                stats['GP'] = float(category['values'][0])
                                # Minutes per game is the second value
                                stats['MIN'] = float(category['values'][1])
                                # Rebounds per game is the twelfth value
                                stats['REB'] = float(category['values'][11])
                            elif category['name'] == 'offensive':
                                # Points per game is the first value in offensive category
                                stats['PTS'] = float(category['values'][0])
                                # Field goal percentage is the fourth value
                                stats['FG%'] = float(category['values'][3])
                                # Three point percentage is the seventh value
                                stats['3P%'] = float(category['values'][6])
                                # Free throw percentage is the tenth value
                                stats['FT%'] = float(category['values'][9])
                                # Assists per game is the eleventh value
                                stats['AST'] = float(category['values'][10])
                                # Turnovers per game is the twelfth value
                                stats['TO'] = float(category['values'][11])
                            elif category['name'] == 'defensive':
                                # Steals per game is the first value in defensive category
                                stats['STL'] = float(category['values'][0])
                                # Blocks per game is the second value
                                stats['BLK'] = float(category['values'][1])
                        
                        player_stats = {
                            'name': name,
                            'games_played': stats.get('GP', 0),
                            'minutes_per_game': stats.get('MIN', 0),
                            'points_per_game': stats.get('PTS', 0),
                            'rebounds_per_game': stats.get('REB', 0),
                            'assists_per_game': stats.get('AST', 0),
                            'steals_per_game': stats.get('STL', 0),
                            'blocks_per_game': stats.get('BLK', 0),
                            'field_goal_percentage': stats.get('FG%', 0),
                            'three_point_percentage': stats.get('3P%', 0),
                            'free_throw_percentage': stats.get('FT%', 0),
                            'turnovers_per_game': stats.get('TO', 0)
                        }
                        
                        all_players.append(player_stats)
                        print(f"Processed stats for {name}: {player_stats['points_per_game']} PPG")
                        
                    except Exception as e:
                        print(f"Error processing player: {str(e)}")
                        continue
                
                # Save progress after each page
                df = pd.DataFrame(all_players)
                os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
                df.to_csv(self.output_path, index=False)
                print(f"Saved progress: {len(all_players)} players so far")
                
                # Be nice to the API
                time.sleep(2)
                page += 1
            
            print(f"\nFinished! Scraped stats for {len(all_players)} players")
            return f"Successfully scraped stats for {len(all_players)} players and saved to {self.output_path}"
            
        except Exception as e:
            error_msg = f"Error scraping player stats: {str(e)}"
            print(error_msg)
            return error_msg 