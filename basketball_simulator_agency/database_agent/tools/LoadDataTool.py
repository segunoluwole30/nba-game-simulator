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
            # Get database connection details from environment variables
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST', 'localhost')
            )
            
            cur = conn.cursor()
            
            # Load teams data - extract unique teams from players file
            players_df = pd.read_csv(self.players_file)
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
            
            # Load players data
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
            
            # Load player statistics
            stats_loaded = 0
            if os.path.exists(self.stats_file):
                print(f"\nFound stats file: {self.stats_file}")
                stats_df = pd.read_csv(self.stats_file)
                print(f"Loaded {len(stats_df)} player statistics records")
                
                for _, stats in stats_df.iterrows():
                    print(f"\nUpdating stats for {stats['name']}:")
                    print(f"Games: {stats['games_played']}")
                    print(f"Points: {stats['points_per_game']}")
                    
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
                        RETURNING id;  -- Add RETURNING to see if any row was updated
                    """, (
                        float(stats['games_played']),  # Changed to float to match the CSV
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
                        print(f"Successfully updated player ID: {result[0]}")
                        # Verify the update
                        cur.execute("""
                            SELECT games_played, points_per_game 
                            FROM players 
                            WHERE name = %s
                        """, (stats['name'],))
                        verify = cur.fetchone()
                        print(f"Verified values in database - Games: {verify[0]}, Points: {verify[1]}")
                    else:
                        print(f"WARNING: No player found with name: {stats['name']}")
                    
                    stats_loaded += 1
                    
                    # Commit after each update
                    conn.commit()
                
                # Final verification with a new connection
                print("\nVerifying all updates with a fresh connection...")
                verify_conn = psycopg2.connect(
                    dbname=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    host=os.getenv('DB_HOST', 'localhost')
                )
                verify_cur = verify_conn.cursor()
                
                verify_cur.execute("""
                    SELECT COUNT(*) 
                    FROM players 
                    WHERE games_played > 0 
                    OR points_per_game > 0
                """)
                verify_count = verify_cur.fetchone()[0]
                print(f"Number of players with non-zero stats: {verify_count}")
                
                # Sample some players to verify
                verify_cur.execute("""
                    SELECT name, games_played, points_per_game 
                    FROM players 
                    WHERE games_played > 0 
                    OR points_per_game > 0 
                    LIMIT 5
                """)
                sample_players = verify_cur.fetchall()
                print("\nSample of players with stats:")
                for player in sample_players:
                    print(f"{player[0]}: Games = {player[1]}, Points = {player[2]}")
                
                verify_cur.close()
                verify_conn.close()
            else:
                print(f"\nStats file not found: {self.stats_file}")
                print(f"Current directory: {os.getcwd()}")
                print(f"Directory contents: {os.listdir('data')}")
            
            cur.close()
            conn.close()
            
            return f"Successfully loaded {teams_loaded} teams, {players_loaded} players, and updated statistics for {stats_loaded} players"
            
        except Exception as e:
            return f"Error loading data: {str(e)}"

if __name__ == "__main__":
    tool = LoadDataTool()
    print(tool.run()) 