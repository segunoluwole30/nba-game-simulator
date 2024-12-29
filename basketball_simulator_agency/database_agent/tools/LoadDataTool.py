from agency_swarm.tools import BaseTool
from pydantic import Field
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
from ..tools.BaseDatabaseTool import BaseDatabaseTool

load_dotenv()

class LoadDataTool(BaseDatabaseTool):
    """
    A tool for loading data from CSV files into the PostgreSQL database.
    Handles both team and player data with proper relationships.
    """
    teams_file: str = Field(
        default="nba_active_players.csv",
        description="Path to the CSV file containing team data"
    )
    players_file: str = Field(
        default="nba_active_players.csv",
        description="Path to the CSV file containing player data"
    )
    stats_file: str = Field(
        default="nba_player_stats.csv",
        description="Path to the CSV file containing player statistics"
    )

    def run(self):
        """Load data from CSV files into the database."""
        try:
            print("Starting data load process...")
            print("Connecting to database...")
            conn = self.get_db_connection()
            print("Database connection successful")
            
            # Load teams data
            print("Loading teams data...")
            teams_data = pd.read_csv('nba_active_players.csv')
            teams = teams_data['current_team'].unique()
            teams = [team for team in teams if isinstance(team, str)]  # Filter out NaN values
            
            # Insert teams
            cursor = conn.cursor()
            for team in teams:
                cursor.execute(
                    "INSERT INTO teams (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                    (team,)
                )
            conn.commit()
            print(f"Loaded {len(teams)} teams")
            
            # Load players data
            print("Loading players data...")
            players_data = pd.read_csv('nba_active_players.csv')
            for _, player in players_data.iterrows():
                cursor.execute(
                    """
                    INSERT INTO players (name, current_team, position, age, height, weight, colleges)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        current_team = EXCLUDED.current_team,
                        position = EXCLUDED.position,
                        age = EXCLUDED.age,
                        height = EXCLUDED.height,
                        weight = EXCLUDED.weight,
                        colleges = EXCLUDED.colleges
                    """,
                    (
                        player['name'],
                        player['current_team'] if pd.notna(player['current_team']) else None,
                        player['position'] if pd.notna(player['position']) else None,
                        player['age'] if pd.notna(player['age']) else None,
                        player['height'] if pd.notna(player['height']) else None,
                        player['weight'] if pd.notna(player['weight']) else None,
                        player['colleges'] if pd.notna(player['colleges']) else None
                    )
                )
            conn.commit()
            print(f"Loaded {len(players_data)} players")
            
            # Load player statistics
            print("Loading player statistics...")
            try:
                stats_file = 'nba_player_stats.csv'
                if not os.path.exists(stats_file):
                    print(f"WARNING: Stats file not found: {stats_file}")
                    print(f"Current directory: {os.getcwd()}")
                    print(f"Directory contents: {os.listdir()}")
                    return
                    
                stats_data = pd.read_csv(stats_file)
                print(f"Found stats file: {stats_file}")
                print(f"Found {len(stats_data)} player statistics records")
                print(f"Stats file columns: {list(stats_data.columns)}")
                
                updated_count = 0
                for _, stats in stats_data.iterrows():
                    cursor.execute(
                        """
                        UPDATE players SET
                            games_played = %s,
                            minutes_per_game = %s,
                            points_per_game = %s,
                            rebounds_per_game = %s,
                            assists_per_game = %s,
                            steals_per_game = %s,
                            blocks_per_game = %s,
                            field_goal_percentage = %s,
                            three_point_percentage = %s,
                            free_throw_percentage = %s,
                            turnovers_per_game = %s
                        WHERE name = %s
                        """,
                        (
                            float(stats['games_played']),
                            float(stats['minutes_per_game']),
                            float(stats['points_per_game']),
                            float(stats['rebounds_per_game']),
                            float(stats['assists_per_game']),
                            float(stats['steals_per_game']),
                            float(stats['blocks_per_game']),
                            float(stats['field_goal_percentage']),
                            float(stats['three_point_percentage']),
                            float(stats['free_throw_percentage']),
                            float(stats['turnovers_per_game']),
                            stats['name']
                        )
                    )
                    updated_count += 1
                
                conn.commit()
                print(f"Successfully updated statistics for {updated_count} players")
                
                # Verify the updates
                print("Verifying player statistics...")
                cursor.execute("""
                    SELECT COUNT(*) FROM players 
                    WHERE points_per_game > 0 
                    OR rebounds_per_game > 0 
                    OR assists_per_game > 0
                """)
                non_zero_stats = cursor.fetchone()[0]
                print(f"Players with non-zero stats: {non_zero_stats}")
                
            except Exception as e:
                print(f"Error loading player statistics: {str(e)}")
                raise
            
            cursor.close()
            conn.close()
            return "Data loaded successfully"
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise

if __name__ == "__main__":
    tool = LoadDataTool()
    print(tool.run()) 