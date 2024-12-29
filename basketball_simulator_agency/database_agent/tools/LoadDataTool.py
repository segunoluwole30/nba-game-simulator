from agency_swarm.tools import BaseTool
from pydantic import Field
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

class LoadDataTool(BaseTool):
    """
    A tool for loading data from CSV files into the PostgreSQL database.
    Handles both team and player data with proper relationships.
    """
    teams_file: str = Field(
        default="data/nba_active_players.csv",
        description="Path to the CSV file containing team data"
    )
    players_file: str = Field(
        default="data/nba_active_players.csv",
        description="Path to the CSV file containing player data"
    )
    stats_file: str = Field(
        default="data/nba_player_stats.csv",
        description="Path to the CSV file containing player statistics"
    )

    def run(self):
        """
        Loads team and player data from CSV files into the database.
        Returns a message indicating success or failure.
        """
        try:
            print("\nStarting data load process...")
            
            # Get database connection details from environment variables
            print("Connecting to database...")
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST', 'localhost')
            )
            print("Database connection successful")
            
            cur = conn.cursor()
            
            # Load teams data - extract unique teams from players file
            print("\nLoading teams data...")
            players_df = pd.read_csv(self.players_file)
            print(f"Found {len(players_df)} players in CSV")
            unique_teams = players_df['current_team'].unique()
            teams_loaded = 0
            
            # Insert each unique team
            for team_name in unique_teams:
                if pd.notna(team_name):  # Skip any NA values
                    cur.execute("""
                        INSERT INTO teams (name)
                        VALUES (%s)
                        ON CONFLICT (name) DO NOTHING
                        RETURNING id;
                    """, (team_name,))
                    teams_loaded += 1
            print(f"Loaded {teams_loaded} teams")
            
            # Load players data
            print("\nLoading players data...")
            players_loaded = 0
            
            for _, player in players_df.iterrows():
                cur.execute("""
                    INSERT INTO players (
                        name, current_team, position, height, weight, 
                        age, colleges
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        current_team = EXCLUDED.current_team,
                        position = EXCLUDED.position,
                        height = EXCLUDED.height,
                        weight = EXCLUDED.weight,
                        age = EXCLUDED.age,
                        colleges = EXCLUDED.colleges
                    RETURNING id;
                """, (
                    player['name'],
                    player['current_team'],
                    player['position'],
                    player['height'],
                    int(player['weight']) if pd.notna(player['weight']) else None,
                    int(player['age']) if pd.notna(player['age']) else None,
                    player['colleges'] if pd.notna(player['colleges']) else None
                ))
                players_loaded += 1
            print(f"Loaded {players_loaded} players")
            
            # Load player statistics
            print("\nLoading player statistics...")
            stats_loaded = 0
            if os.path.exists(self.stats_file):
                print(f"Found stats file: {self.stats_file}")
                stats_df = pd.read_csv(self.stats_file)
                print(f"Found {len(stats_df)} player statistics records")
                
                # Print column names for debugging
                print("\nStats file columns:", stats_df.columns.tolist())
                
                for _, stats in stats_df.iterrows():
                    print(f"\nProcessing stats for {stats['name']}:")
                    
                    # Update the player's stats
                    cur.execute("""
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
                        RETURNING id;
                    """, (
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
                    ))
                    
                    result = cur.fetchone()
                    if result:
                        print(f"Updated player ID: {result[0]}")
                        stats_loaded += 1
                    else:
                        print(f"WARNING: No player found with name: {stats['name']}")
                    
                    # Commit after each update
                    conn.commit()
                
                print(f"\nSuccessfully updated statistics for {stats_loaded} players")
                
                # Verify the updates
                print("\nVerifying player statistics...")
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM players 
                    WHERE games_played > 0 
                    OR points_per_game > 0
                """)
                verify_count = cur.fetchone()[0]
                print(f"Players with non-zero stats: {verify_count}")
                
            else:
                print(f"\nWARNING: Stats file not found: {self.stats_file}")
                print(f"Current directory: {os.getcwd()}")
                print(f"Directory contents: {os.listdir('data')}")
            
            cur.close()
            conn.close()
            
            return f"Successfully loaded {teams_loaded} teams, {players_loaded} players, and updated statistics for {stats_loaded} players"
            
        except Exception as e:
            print(f"\nERROR: {str(e)}")
            return f"Error loading data: {str(e)}"

if __name__ == "__main__":
    tool = LoadDataTool()
    print(tool.run()) 