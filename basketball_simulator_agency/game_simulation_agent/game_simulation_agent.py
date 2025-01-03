from agency_swarm import Agent
from .tools.SimulateGameTool import SimulateGameTool
from .tools.SimulateDailyGamesTool import SimulateDailyGamesTool

class GameSimulationAgent(Agent):
    def __init__(self):
        super().__init__(
            name="GameSimulationAgent",
            description="Agent responsible for simulating basketball games using player statistics",
            instructions="./instructions.md",
            tools=[SimulateGameTool, SimulateDailyGamesTool]
        ) 