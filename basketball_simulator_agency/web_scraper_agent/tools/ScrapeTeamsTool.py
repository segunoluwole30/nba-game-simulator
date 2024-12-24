from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class ScrapeTeamsTool(BaseTool):
    """
    A tool for scraping active NBA franchises from basketball-reference.com.
    The tool scrapes team information and saves it to a CSV file.
    """
    output_path: str = Field(
        default="data/nba_franchises.csv",
        description="Path where the CSV file will be saved"
    )

    def run(self):
        """
        Scrapes active NBA franchises and saves them to a CSV file.
        Returns a message indicating success or failure.
        """
        try:
            url = "https://www.basketball-reference.com/teams/"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the active franchises table
            teams_table = soup.find('table', {'id': 'teams_active'})
            
            franchises = []
            for row in teams_table.find_all('tr')[1:]:  # Skip header row
                cols = row.find_all(['td', 'th'])
                if cols:
                    # Get team name from the link in the first column
                    team_link = cols[0].find('a')
                    if team_link:
                        franchise = {
                            'team': team_link.text.strip(),
                            'league': cols[1].text.strip(),
                            'from': cols[2].text.strip(),
                            'to': cols[3].text.strip(),
                            'years': cols[4].text.strip(),
                            'games': cols[5].text.strip(),
                            'wins': cols[6].text.strip(),
                            'losses': cols[7].text.strip(),
                            'win_pct': cols[8].text.strip(),
                            'playoffs': cols[9].text.strip(),
                            'division': cols[10].text.strip(),
                            'conference': cols[11].text.strip(),
                            'championships': cols[12].text.strip()
                        }
                        franchises.append(franchise)
            
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            # Save to CSV
            df = pd.DataFrame(franchises)
            df.to_csv(self.output_path, index=False)
            return f"Successfully scraped {len(franchises)} teams and saved to {self.output_path}"
            
        except Exception as e:
            return f"Error scraping teams: {str(e)}"

if __name__ == "__main__":
    tool = ScrapeTeamsTool()
    print(tool.run()) 