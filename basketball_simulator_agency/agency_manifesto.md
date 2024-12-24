# Basketball Simulator Agency

## Agency Description
This agency is designed to create realistic basketball game simulations using real NBA data. It combines web scraping, database management, and game simulation capabilities to provide an engaging basketball simulation experience.

## Mission Statement
To provide accurate and engaging basketball game simulations by leveraging real NBA data and statistics, maintaining data integrity throughout the process, and delivering realistic game results.

## Operating Environment
The agency operates in a Python environment with:
- Web scraping capabilities for basketball-reference.com
- PostgreSQL database for data storage and retrieval
- Statistical simulation tools for game simulation

## Task Completion Rules
1. Each agent must complete its task with a single response
2. No agent should continue processing after completing its primary task
3. Agents should not suggest or initiate additional tasks
4. Each request should be treated as a standalone operation
5. Agents must wait for explicit user input before starting new tasks

## Workflow
1. Web Scraper Agent (On explicit request only):
   - Scrapes active NBA franchises
   - Scrapes active NBA players and their statistics
   - Saves data to CSV files
   - Completes after saving files

2. Database Agent:
   - Creates and maintains database schemas
   - Loads data from CSV files into the database
   - Provides data access for game simulations
   - Completes after data operation

3. Game Simulation Agent:
   - Simulates exactly one game per request
   - Generates one box score
   - Returns results immediately
   - Completes after showing results

## Communication Protocol
- Each agent must complete its task before passing control
- No agent should initiate communication without user request
- Each simulation is a single, complete operation
- Results must be returned immediately after simulation
- No follow-up suggestions or additional simulations

## Success Criteria
- One simulation per request
- Clear start and end of each operation
- No automatic follow-up tasks
- Explicit user control of workflow
- Clean task completion 