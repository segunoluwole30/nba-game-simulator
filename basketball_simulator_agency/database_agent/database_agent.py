from agency_swarm import Agent
from .tools.CreateSchemasTool import CreateSchemasTool
from .tools.LoadDataTool import LoadDataTool
from .tools.QueryPlayerStatsTool import QueryPlayerStatsTool

class DatabaseAgent(Agent):
    def __init__(self):
        super().__init__(
            name="DatabaseAgent",
            description="Agent responsible for managing the PostgreSQL database operations",
            instructions="./instructions.md",
            tools=[CreateSchemasTool, LoadDataTool, QueryPlayerStatsTool]
        ) 