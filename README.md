# NBA Game Simulator

A web application that simulates NBA basketball games using real player statistics. The simulator uses player data from ESPN and provides realistic game simulations with detailed box scores.

Live Demo: [https://nba-game-simulator.onrender.com](https://nba-game-simulator.onrender.com)

## Features

- Web scraping of current NBA rosters and player statistics
- Database storage of player data
- Single game simulation between any two NBA teams
- Daily games simulation (simulates all NBA games scheduled for the current day)
- Realistic box scores with accurate minute distribution
- Support for overtime games (1-4 OT periods)
- Web interface for easy team selection and simulation
- API endpoints for programmatic access
- Hosted on Render with PostgreSQL database

## Prerequisites

For local development:
- Python 3.8+
- PostgreSQL database
- OpenAI API key (for game simulations)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nba-game-simulator.git
cd nba-game-simulator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# For local development
export DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
export OPENAI_API_KEY="your-api-key"
```

### Deployment on Render

The application is deployed on Render with the following configuration:

1. Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn basketball_simulator_agency.app:app`
   - Environment Variables:
     - `DATABASE_URL` (provided by Render PostgreSQL)
     - `OPENAI_API_KEY` (your OpenAI API key)
     - `PYTHON_VERSION`: "3.8.0"

2. PostgreSQL Database:
   - Automatically provisioned by Render
   - Connection details provided via `DATABASE_URL`

## Usage

### Web Interface

#### Production
Visit [https://nba-game-simulator.onrender.com](https://nba-game-simulator.onrender.com) to use the live application.

#### Local Development
1. Start the Flask application:
```bash
python -m basketball_simulator_agency.app
```

2. Open your browser and navigate to `http://localhost:5000`
3. Select teams from the dropdowns and click "Simulate Game"
4. For daily simulations, click "Simulate Today's Games"

### Direct Tool Usage

You can also use the simulation tools directly in Python:

1. Simulate a specific game:
```python
from basketball_simulator_agency.game_simulation_agent.tools.SimulateGameTool import SimulateGameTool

game_tool = SimulateGameTool(
    home_team="Boston Celtics",
    away_team="Los Angeles Lakers",
    db_name="your_db_name",
    db_user="your_db_user",
    db_password="your_db_password",
    db_host="your_db_host"
)
print(game_tool.run())
```

2. Simulate all of today's games:
```python
from basketball_simulator_agency.game_simulation_agent.tools.SimulateDailyGamesTool import SimulateDailyGamesTool

tool = SimulateDailyGamesTool(
    db_name="your_db_name",
    db_user="your_db_user",
    db_password="your_db_password",
    db_host="your_db_host"
)
print(tool.run())
```

## Project Structure

```
basketball_simulator_agency/
├── app.py                 # Flask application
├── templates/            # HTML templates
├── database_agent/      # Database management tools
├── web_scraper_agent/   # Web scraping tools
└── game_simulation_agent/ # Game simulation logic
```

## Sample Output

When you simulate a game, you'll get output similar to this:

```
Final Score: Boston Celtics 115 - Los Angeles Lakers 112 (2OTs)

Boston Celtics Box Score:
--------------------------------------------------------------------------------
Name                      POS   MIN   PTS  REB  AST  STL  BLK  TO  
--------------------------------------------------------------------------------
Jayson Tatum             SF    42    32   9    6    2    1    3   
Jaylen Brown             SG    40    28   6    4    1    0    2   
Kristaps Porzingis       C     38    22   11   2    0    3    1   
[... more players ...]

Los Angeles Lakers Box Score:
[... similar format ...]
```

## Data Sources

This project uses data from ESPN's NBA section. All data is scraped from publicly available pages. The project is for educational purposes only and is not affiliated with or endorsed by ESPN, the NBA, or any NBA teams.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Legal Notice

This project is for educational purposes only. It is not affiliated with, endorsed by, or connected to ESPN, the NBA, or any NBA teams. All team names, player names, and statistics are property of their respective owners. 