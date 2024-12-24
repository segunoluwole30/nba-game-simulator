# Basketball Simulator Agency

A Python-based basketball simulation system that uses real NBA data to create realistic game simulations. The system combines web scraping, database management, and statistical simulation to provide accurate and engaging basketball game results.

## Features

- **Web Scraping**: Automatically fetches current NBA data
  - Team rosters and information
  - Player statistics and biographical data
  - Data from basketball-reference.com and ESPN

- **Database Management**: PostgreSQL database for storing and managing data
  - Team and player information
  - Current season statistics
  - Efficient data retrieval for simulations

- **Game Simulation**: Realistic basketball game simulation
  - Player-specific performance based on real statistics
  - Detailed box scores for each game
  - Team-based gameplay dynamics

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Required Python packages (see requirements.txt)
- OpenAI API key (optional - needed only for agency interaction mode)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/segunoluwole30/ai-agents.git
cd ai-agents
```

2. Install required packages:
```bash
pip install -r basketball_simulator_agency/requirements.txt
```

3. Set up environment variables:
```bash
cp basketball_simulator_agency/.env.example basketball_simulator_agency/.env
```
Edit `.env` with your database credentials and OpenAI API key (if using agency mode).

4. Create PostgreSQL database:
```sql
CREATE DATABASE basketball_sim;
```

## Usage

### Method 1: Using the Agency (Recommended)
If you have an OpenAI API key, you can use the interactive agency mode which provides a natural language interface:

1. Ensure your OpenAI API key is set in `.env`
2. Run the agency:
```bash
python3 agency.py
```
3. Enter commands like:
   - "Scrape the latest NBA data"
   - "Load the data into the database"
   - "Simulate a game between Lakers and Celtics"

### Method 2: Direct Tool Usage
You can also use the tools directly in Python:

1. Initialize the database schemas:
```python
from basketball_simulator_agency.database_agent.tools.CreateSchemasTool import CreateSchemasTool
tool = CreateSchemasTool()
tool.run()
```

2. Scrape current NBA data:
```python
from basketball_simulator_agency.web_scraper_agent.tools.ScrapeTeamsTool import ScrapeTeamsTool
from basketball_simulator_agency.web_scraper_agent.tools.ScrapePlayersTool import ScrapePlayersTool
teams_tool = ScrapeTeamsTool()
players_tool = ScrapePlayersTool()
teams_tool.run()
players_tool.run()
```

3. Load data into database:
```python
from basketball_simulator_agency.database_agent.tools.LoadDataTool import LoadDataTool
tool = LoadDataTool()
tool.run()
```

4. Simulate a game:
```python
from basketball_simulator_agency.game_simulation_agent.tools.SimulateGameTool import SimulateGameTool
game_tool = SimulateGameTool(home_team="Boston Celtics", away_team="Los Angeles Lakers")
print(game_tool.run())
```

## Project Structure

```
basketball_simulator_agency/
├── agency.py                 # Main entry point
├── data/                     # CSV data storage
├── web_scraper_agent/       # Web scraping functionality
├── database_agent/          # Database management
└── game_simulation_agent/   # Game simulation logic
```

## Environment Variables

Required environment variables in `.env`:
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host (default: localhost)
- `OPENAI_API_KEY`: Your OpenAI API key (required for agency mode)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Legal Notice

This is a personal project for educational purposes only. The project:
- Uses the [agency-swarm](https://github.com/VRSEN/agency-swarm) framework - all rights belong to their respective owners
- Accesses publicly available data from ESPN and basketball-reference.com
- Is not affiliated with, endorsed, or sponsored by the NBA, ESPN, or basketball-reference.com
- Should not be used for commercial purposes

## Acknowledgments

- Built using [agency-swarm](https://github.com/VRSEN/agency-swarm) framework
- Data sourced from:
  - ESPN's publicly available data
  - basketball-reference.com
- Inspired by real NBA statistics and gameplay
- This project is for educational purposes only 