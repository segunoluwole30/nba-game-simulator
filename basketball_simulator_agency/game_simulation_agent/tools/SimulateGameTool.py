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
        is_overtime = False
        overtime_periods = 0
        
        def adjust_minutes(players, is_ot=False):
            """Adjust player minutes to sum to 240 (or more if overtime)"""
            nonlocal overtime_periods
            if is_ot:
                overtime_periods = random.randint(1, 4)  # 1-4 OT periods
            target_minutes = 240 if not is_ot else 240 + (5 * overtime_periods)
            
            # First pass: simulate minutes based on averages
            box_score = []
            total_minutes = 0
            for player in players:
                # Base minutes on player's average with some randomness
                minutes = min(48, max(0, random.gauss(player[2], 2)))
                total_minutes += minutes
                box_score.append({
                    'name': player[0],
                    'position': player[1],
                    'minutes': minutes,
                    'original_mpg': player[2]  # Store original MPG for ratio calculations
                })
            
            # Adjust minutes to hit target
            scale_factor = target_minutes / total_minutes if total_minutes > 0 else 0
            for player in box_score:
                player['minutes'] = round(player['minutes'] * scale_factor)
            
            # Simulate other stats based on adjusted minutes
            for player in box_score:
                minutes = player['minutes']
                mpg_ratio = minutes / player['original_mpg'] if player['original_mpg'] > 0 else 0
                
                # Calculate stats based on minutes played ratio
                points = max(0, random.gauss(players[box_score.index(player)][3] * mpg_ratio, 3))
                rebounds = max(0, random.gauss(players[box_score.index(player)][4] * mpg_ratio, 2))
                assists = max(0, random.gauss(players[box_score.index(player)][5] * mpg_ratio, 2))
                steals = max(0, random.gauss(players[box_score.index(player)][6] * mpg_ratio, 1))
                blocks = max(0, random.gauss(players[box_score.index(player)][7] * mpg_ratio, 1))
                turnovers = max(0, random.gauss(players[box_score.index(player)][11] * mpg_ratio, 1))
                
                # Update player stats
                player.update({
                    'points': int(points),
                    'rebounds': int(rebounds),
                    'assists': int(assists),
                    'steals': int(steals),
                    'blocks': int(blocks),
                    'turnovers': int(turnovers)
                })
                
            return box_score, sum(p['points'] for p in box_score)
        
        # Simulate initial 48 minutes
        home_box_score, home_score = adjust_minutes(home_players)
        away_box_score, away_score = adjust_minutes(away_players)
        
        # If scores are tied, simulate overtime
        if home_score == away_score:
            is_overtime = True
            home_box_score, home_score = adjust_minutes(home_players, is_ot=True)
            away_box_score, away_score = adjust_minutes(away_players, is_ot=True)
        
        return home_score, away_score, home_box_score, away_box_score, is_overtime, overtime_periods

    def format_box_score(self, team_name, box_score):
        """Format box score for display."""
        result = f"\n{team_name} Box Score:\n"
        result += "-" * 80 + "\n"
        result += f"{'Name':<25} {'POS':<5} {'MIN':<5} {'PTS':<4} {'REB':<4} {'AST':<4} {'STL':<4} {'BLK':<4} {'TO':<4}\n"
        result += "-" * 80 + "\n"
        
        # Sort by points scored
        box_score.sort(key=lambda x: x['points'], reverse=True)
        
        for player in box_score:
            result += f"{player['name']:<25} {player['position']:<5} {player['minutes']:<5d} {player['points']:<4d} "
            result += f"{player['rebounds']:<4d} {player['assists']:<4d} {player['steals']:<4d} "
            result += f"{player['blocks']:<4d} {player['turnovers']:<4d}\n"
        
        return result

    def run(self) -> str:
        """Run the game simulation."""
        try:
            # Connect to the database using constructor parameters
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host
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
            home_score, away_score, home_box_score, away_box_score, is_overtime, ot_periods = self.simulate_game(home_players, away_players)
            
            # Format the results
            result = f"\nFinal Score: {self.home_team} {home_score} - {away_score} {self.away_team}"
            if is_overtime:
                result += f" ({ot_periods}OT)" if ot_periods == 1 else f" ({ot_periods}OTs)"
            result += "\n"
            result += self.format_box_score(self.home_team, home_box_score)
            result += "\n"
            result += self.format_box_score(self.away_team, away_box_score)
            
            cur.close()
            conn.close()
            
            return result

        except Exception as e:
            return f"Error simulating game: {str(e)}"

if __name__ == "__main__":
    tool = SimulateGameTool(home_team="Boston Celtics", away_team="Los Angeles Lakers", db_name="basketball_db", db_user="basketball_user", db_password="basketball_password", db_host="localhost")
    print(tool.run()) 