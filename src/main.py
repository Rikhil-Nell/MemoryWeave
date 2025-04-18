import asyncio
from agents import journal_agent

user_input = "Generate a Journal Entry for the Objects"

def generateStory(user_input)-> str:
    response = asyncio.run(journal_agent.run(user_input))
    return response.output



