from agency_swarm import Agent
from .tools.ScrapeTeamsTool import ScrapeTeamsTool
from .tools.ScrapePlayersTool import ScrapePlayersTool
from .tools.ScrapePlayerStatsTool import ScrapePlayerStatsTool

class WebScraperAgent(Agent):
    def __init__(self):
        super().__init__(
            name="WebScraperAgent",
            description="Agent responsible for scraping NBA data from basketball-reference.com and ESPN",
            instructions="./instructions.md",
            tools=[ScrapeTeamsTool, ScrapePlayersTool, ScrapePlayerStatsTool]
        ) 