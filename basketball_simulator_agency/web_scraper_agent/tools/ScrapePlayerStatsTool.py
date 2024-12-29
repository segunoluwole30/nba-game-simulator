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
            print("Starting player stats scraping...")
            all_players = []
            
            # ESPN's internal API endpoint for player stats
            url = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/statistics/byathlete?region=us&lang=en&contentorigin=espn&isqualified=true&page=1&limit=50&category=offensive&sort=offensive.avgPoints%3Adesc"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Create output file and write header
            with open('nba_player_stats.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'name', 'games_played', 'minutes_per_game', 'points_per_game',
                    'rebounds_per_game', 'assists_per_game', 'steals_per_game',
                    'blocks_per_game', 'field_goal_percentage', 'three_point_percentage',
                    'free_throw_percentage', 'turnovers_per_game'
                ])
            
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
                        
                        # Initialize stats dictionary
                        stats = {}
                        
                        # Extract stats from each category
                        for category in athlete['categories']:
                            if category['name'] == 'general':
                                stats['GP'] = float(category['values'][0])
                                stats['MIN'] = float(category['values'][1])
                                stats['REB'] = float(category['values'][11])
                            elif category['name'] == 'offensive':
                                stats['PTS'] = float(category['values'][0])
                                stats['FG%'] = float(category['values'][3])
                                stats['3P%'] = float(category['values'][6])
                                stats['FT%'] = float(category['values'][9])
                                stats['AST'] = float(category['values'][10])
                                stats['TO'] = float(category['values'][11])
                            elif category['name'] == 'defensive':
                                stats['STL'] = float(category['values'][0])
                                stats['BLK'] = float(category['values'][1])
                        
                        # Create player stats row
                        player_stats = [
                            name,
                            stats.get('GP', 0),
                            stats.get('MIN', 0),
                            stats.get('PTS', 0),
                            stats.get('REB', 0),
                            stats.get('AST', 0),
                            stats.get('STL', 0),
                            stats.get('BLK', 0),
                            stats.get('FG%', 0),
                            stats.get('3P%', 0),
                            stats.get('FT%', 0),
                            stats.get('TO', 0)
                        ]
                        
                        # Append to file immediately
                        with open('nba_player_stats.csv', 'a', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(player_stats)
                        
                        print(f"Processed stats for {name}: {stats.get('PTS', 0)} PPG")
                        
                    except Exception as e:
                        print(f"Error processing player {name if 'name' in locals() else 'unknown'}: {str(e)}")
                        continue
                
                # Be nice to the API
                time.sleep(2)
                page += 1
            
            print(f"\nFinished! Scraped stats for all available players")
            return "Successfully scraped player stats"
            
        except Exception as e:
            error_msg = f"Error scraping player stats: {str(e)}"
            print(error_msg)
            return error_msg 