from google.adk.agents import LlmAgent
from agent.prompt import *
from agent.tools import *
from constants import AGENT_NAME, AGENT_DESCRIPTION, AGENT_MODEL

root_agent = LlmAgent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    description=AGENT_DESCRIPTION, 
    instruction=ROOT_AGENT_PROMPT,
    tools= [
    get_cars]
)