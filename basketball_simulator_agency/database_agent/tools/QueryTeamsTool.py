from agency_swarm.tools import BaseTool
import psycopg2
from dotenv import load_dotenv
import os

class QueryTeamsTool(BaseTool):
    """Tool for querying all NBA teams from the database."""

    def run(self) -> list:
        """Query all team names from the database."""
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
            
            # Query all team names
            cur.execute("SELECT name FROM teams ORDER BY name;")
            teams = [row[0] for row in cur.fetchall()]
            
            cur.close()
            conn.close()
            
            return teams
            
        except Exception as e:
            print(f"Error querying teams: {str(e)}")
            return [] 