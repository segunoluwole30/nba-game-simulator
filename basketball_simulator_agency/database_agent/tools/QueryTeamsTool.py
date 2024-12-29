from .BaseDatabaseTool import BaseDatabaseTool

class QueryTeamsTool(BaseDatabaseTool):
    """Tool for querying teams from the database."""
    
    def run(self):
        """Query all teams from the database."""
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            
            # Query teams
            cur.execute("SELECT name FROM teams ORDER BY name")
            teams = [row[0] for row in cur.fetchall()]
            
            cur.close()
            conn.close()
            
            return teams
        except Exception as e:
            error_msg = f"Error querying teams: {str(e)}"
            print(error_msg)  # Print the error
            raise Exception(error_msg) 