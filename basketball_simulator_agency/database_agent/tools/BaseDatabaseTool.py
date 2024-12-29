import psycopg2
import os
from agency_swarm.tools import BaseTool

class BaseDatabaseTool(BaseTool):
    """Base class for database tools."""
    
    def get_db_connection(self):
        """Get a database connection using environment variables."""
        try:
            # Print environment variables for debugging
            print("\nDatabase connection details:")
            print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
            
            # Use DATABASE_URL if available (Render deployment)
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                return psycopg2.connect(database_url)
            
            # Fallback to individual credentials for local development
            return psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST', 'localhost')
            )
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            raise 