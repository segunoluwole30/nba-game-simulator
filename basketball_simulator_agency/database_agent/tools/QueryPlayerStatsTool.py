from agency_swarm.tools import BaseTool
from pydantic import Field
import psycopg2
from dotenv import load_dotenv
import os

class QueryPlayerStatsTool(BaseTool):
    """Tool for querying player statistics from the database."""
    
    team_name: str = Field(
        description="Name of the team to query player statistics for (can be partial name like 'Lakers' or 'Mavs')"
    )

    def run(self) -> str:
        """Query player statistics for a specific team."""
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
            
            # First, find the full team name
            cur.execute("""
                SELECT DISTINCT current_team 
                FROM players 
                WHERE current_team ILIKE %s
            """, (f"%{self.team_name}%",))
            
            team_results = cur.fetchall()
            
            if not team_results:
                return f"No team found matching: {self.team_name}"
            elif len(team_results) > 1:
                return f"Multiple teams found matching '{self.team_name}': {', '.join(t[0] for t in team_results)}"
            
            full_team_name = team_results[0][0]
            
            # Query player statistics using the full team name
            cur.execute("""
                SELECT 
                    p.name,
                    p.position,
                    p.games_played,
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
                ORDER BY p.points_per_game DESC;
            """, (full_team_name,))
            
            rows = cur.fetchall()
            
            if not rows:
                return f"No players found for team: {full_team_name}"
            
            # Format the results
            result = f"\nPlayer Statistics for {full_team_name}:\n"
            result += "-" * 80 + "\n"
            result += f"{'Name':<25} {'POS':<5} {'GP':<4} {'MIN':<5} {'PTS':<5} {'REB':<5} {'AST':<5} {'STL':<5} {'BLK':<5} {'FG%':<6} {'3P%':<6} {'FT%':<6} {'TO':<4}\n"
            result += "-" * 80 + "\n"
            
            for row in rows:
                result += f"{row[0]:<25} {row[1]:<5} {row[2]:<4} {row[3]:<5.1f} {row[4]:<5.1f} {row[5]:<5.1f} {row[6]:<5.1f} {row[7]:<5.1f} {row[8]:<5.1f} {row[9]:<6.1f} {row[10]:<6.1f} {row[11]:<6.1f} {row[12]:<4.1f}\n"
            
            cur.close()
            conn.close()
            
            return result
            
        except Exception as e:
            return f"Error querying player stats: {str(e)}"

if __name__ == "__main__":
    tool = QueryPlayerStatsTool(team_name="Celtics")
    print(tool.run()) 