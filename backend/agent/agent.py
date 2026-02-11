from google.adk.agents import LlmAgent
from agent.prompt import *
from agent.tools import get_cars, update_car_by_name,delete_car_by_name,log_update,get_last_updated_car,create_booking,get_customer_with_most_rentals,get_most_rented_model,introduce_booking_model
from constants import AGENT_NAME, AGENT_DESCRIPTION, AGENT_MODEL

root_agent = LlmAgent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    description=AGENT_DESCRIPTION, 
    instruction=ROOT_AGENT_PROMPT,
    tools= [
    get_cars,update_car_by_name,delete_car_by_name,log_update,get_last_updated_car,create_booking,get_customer_with_most_rentals,get_most_rented_model,introduce_booking_model]
)