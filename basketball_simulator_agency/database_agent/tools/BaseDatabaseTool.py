import psycopg2
import os
from agency_swarm.tools import BaseTool

class BaseDatabaseTool(BaseTool):
    """Base class for database tools."""
    
    def get_db_connection(self):
        """Get a database connection using environment variables."""
        try:
            # Check for DATABASE_URL (provided by Render)
            database_url = os.getenv('DATABASE_URL')
            
            if database_url:
                print(f"Using DATABASE_URL for connection")
                conn = psycopg2.connect(database_url)
            else:
                # Fallback to local development settings
                print("Using local database settings")
                conn = psycopg2.connect(
                    host='localhost',
                    database='basketball_sim',
                    user='segun',
                    password=''
                )
            
            print("Database connection successful!")
            return conn
        except Exception as e:
            error_msg = f"Failed to connect to database: {str(e)}"
            print(error_msg)  # Print the error
            raise Exception(error_msg) 