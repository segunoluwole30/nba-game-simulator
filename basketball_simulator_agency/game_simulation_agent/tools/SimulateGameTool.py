from agency_swarm.tools import BaseTool
from pydantic import Field
import psycopg2
import random
from dotenv import load_dotenv
import os

class SimulateGameTool(BaseTool):
    """Tool for simulating a basketball game between two teams."""
    
    home_team: str = Field(
        description="Name of the home team"
    )
    away_team: str = Field(
        description="Name of the away team"
    )

    def get_team_players(self, cur, team_name):
        """Get players and their stats for a team."""
        cur.execute("""
            SELECT 
                p.name,
                p.position,
                p.minutes_per_game,
                p.points_per_game,
                p.rebounds_per_game,
                p.assists_per_game,
                p.steals_per_game,
                p.blocks_per_game,
                p.field_goal_percentage,
                p.three_point_percentage,
                p.free_throw_percentage,
                p.turnovers_per_game
            FROM players p
            WHERE p.current_team = %s
            AND p.minutes_per_game > 0
            ORDER BY p.minutes_per_game DESC;
        """, (team_name,))
        
        return cur.fetchall()

    def simulate_game(self, home_players, away_players):
        """Simulate a game between two teams."""
        # Initialize game stats
        home_score = 0
        away_score = 0
        home_box_score = []
        away_box_score = []
        
        # Simulate each player's performance
        for player in home_players:
            # Add some randomness to stats based on averages
            minutes = min(48, max(0, random.gauss(player[2], 3)))
            points = max(0, random.gauss(player[3] * (minutes/player[2]) if player[2] > 0 else 0, 4))
            rebounds = max(0, random.gauss(player[4] * (minutes/player[2]) if player[2] > 0 else 0, 2))
            assists = max(0, random.gauss(player[5] * (minutes/player[2]) if player[2] > 0 else 0, 2))
            steals = max(0, random.gauss(player[6] * (minutes/player[2]) if player[2] > 0 else 0, 1))
            blocks = max(0, random.gauss(player[7] * (minutes/player[2]) if player[2] > 0 else 0, 1))
            turnovers = max(0, random.gauss(player[11] * (minutes/player[2]) if player[2] > 0 else 0, 1))
            
            home_score += int(points)
            home_box_score.append({
                'name': player[0],
                'position': player[1],
                'minutes': round(minutes, 1),  # Keep minutes as decimal
                'points': int(points),
                'rebounds': int(rebounds),
                'assists': int(assists),
                'steals': int(steals),
                'blocks': int(blocks),
                'turnovers': int(turnovers)
            })
        
        for player in away_players:
            # Add some randomness to stats based on averages
            minutes = min(48, max(0, random.gauss(player[2], 3)))
            points = max(0, random.gauss(player[3] * (minutes/player[2]) if player[2] > 0 else 0, 4))
            rebounds = max(0, random.gauss(player[4] * (minutes/player[2]) if player[2] > 0 else 0, 2))
            assists = max(0, random.gauss(player[5] * (minutes/player[2]) if player[2] > 0 else 0, 2))
            steals = max(0, random.gauss(player[6] * (minutes/player[2]) if player[2] > 0 else 0, 1))
            blocks = max(0, random.gauss(player[7] * (minutes/player[2]) if player[2] > 0 else 0, 1))
            turnovers = max(0, random.gauss(player[11] * (minutes/player[2]) if player[2] > 0 else 0, 1))
            
            away_score += int(points)
            away_box_score.append({
                'name': player[0],
                'position': player[1],
                'minutes': round(minutes, 1),  # Keep minutes as decimal
                'points': int(points),
                'rebounds': int(rebounds),
                'assists': int(assists),
                'steals': int(steals),
                'blocks': int(blocks),
                'turnovers': int(turnovers)
            })
        
        return home_score, away_score, home_box_score, away_box_score

    def format_box_score(self, team_name, box_score):
        """Format box score for display."""
        result = f"\n{team_name} Box Score:\n"
        result += "-" * 80 + "\n"
        result += f"{'Name':<25} {'POS':<5} {'MIN':<5} {'PTS':<4} {'REB':<4} {'AST':<4} {'STL':<4} {'BLK':<4} {'TO':<4}\n"
        result += "-" * 80 + "\n"
        
        # Sort by points scored
        box_score.sort(key=lambda x: x['points'], reverse=True)
        
        for player in box_score:
            result += f"{player['name']:<25} {player['position']:<5} {player['minutes']:<5.1f} {player['points']:<4d} "
            result += f"{player['rebounds']:<4d} {player['assists']:<4d} {player['steals']:<4d} "
            result += f"{player['blocks']:<4d} {player['turnovers']:<4d}\n"
        
        return result

    def run(self) -> str:
        """Run the game simulation."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Connect to the database
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST', 'localhost')
            )
            
            cur = conn.cursor()
            
            # Get players for both teams
            home_players = self.get_team_players(cur, self.home_team)
            away_players = self.get_team_players(cur, self.away_team)
            
            if not home_players:
                return f"No players found for home team: {self.home_team}"
            if not away_players:
                return f"No players found for away team: {self.away_team}"
            
            # Simulate the game
            home_score, away_score, home_box_score, away_box_score = self.simulate_game(home_players, away_players)
            
            # Format the results
            result = f"\nFinal Score: {self.home_team} {home_score} - {away_score} {self.away_team}\n"
            result += self.format_box_score(self.home_team, home_box_score)
            result += "\n"
            result += self.format_box_score(self.away_team, away_box_score)
            
            cur.close()
            conn.close()
            
            return result
            
        except Exception as e:
            return f"Error simulating game: {str(e)}"

if __name__ == "__main__":
    tool = SimulateGameTool(home_team="Boston Celtics", away_team="Los Angeles Lakers")
    print(tool.run()) 