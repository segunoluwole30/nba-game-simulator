import psycopg2
import os
from agency_swarm.tools import BaseTool

class BaseDatabaseTool(BaseTool):
    """Base class for database tools."""
    
    def get_db_connection(self):
        """Get a database connection using environment variables."""
        try:
            # Use environment variables provided by Render
            db_host = os.getenv('DB_HOST', 'localhost')
            db_name = os.getenv('DB_NAME', 'basketball_sim')
            db_user = os.getenv('DB_USER', 'segun')
            db_password = os.getenv('DB_PASSWORD', '')
            
            # Print connection details (excluding password)
            print(f"Attempting database connection with:")
            print(f"Host: {db_host}")
            print(f"Database: {db_name}")
            print(f"User: {db_user}")
            
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password
            )
            print("Database connection successful!")
            return conn
        except Exception as e:
            error_msg = f"Failed to connect to database: {str(e)}"
            print(error_msg)  # Print the error
            raise Exception(error_msg) 