from agency_swarm.tools import BaseTool
import psycopg2
from dotenv import load_dotenv
import os
from ..tools.BaseDatabaseTool import BaseDatabaseTool

load_dotenv()

class CreateSchemasTool(BaseDatabaseTool):
    """Tool for creating database schemas."""

    def run(self):
        """Create the necessary database tables."""
        try:
            # Get database connection using parent class method
            conn = self.get_db_connection()
            cur = conn.cursor()
            
            # Drop existing tables if they exist
            cur.execute("""
                DROP TABLE IF EXISTS players CASCADE;
                DROP TABLE IF EXISTS teams CASCADE;
            """)
            
            # Create teams table
            cur.execute("""
                CREATE TABLE teams (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL
                );
            """)
            
            # Create players table with nullable fields where appropriate
            cur.execute("""
                CREATE TABLE players (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    current_team VARCHAR(100) REFERENCES teams(name),
                    position VARCHAR(10),
                    height VARCHAR(10),
                    weight INTEGER,  -- Stored without 'lbs' suffix
                    age INTEGER,     -- Stored as integer
                    colleges VARCHAR(100),  -- Renamed from college to colleges to match scraper
                    games_played INTEGER DEFAULT 0,
                    minutes_per_game FLOAT DEFAULT 0,
                    points_per_game FLOAT DEFAULT 0,
                    rebounds_per_game FLOAT DEFAULT 0,
                    assists_per_game FLOAT DEFAULT 0,
                    steals_per_game FLOAT DEFAULT 0,
                    blocks_per_game FLOAT DEFAULT 0,
                    field_goal_percentage FLOAT DEFAULT 0,
                    three_point_percentage FLOAT DEFAULT 0,
                    free_throw_percentage FLOAT DEFAULT 0,
                    turnovers_per_game FLOAT DEFAULT 0
                );
            """)
            
            # Commit the changes
            conn.commit()
            
            # Close cursor and connection
            cur.close()
            conn.close()
            
            return "Successfully created database schemas"
            
        except Exception as e:
            return f"Error creating schemas: {str(e)}"

if __name__ == "__main__":
    tool = CreateSchemasTool()
    print(tool.run()) 