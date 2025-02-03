# Mail Agent v0.1
# Author: Hridai Khurana
# High Automation Level
# Description

from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
import dotenv
from phi.tools.duckduckgo import DuckDuckGo
from duckduckgo_search import DDGS
import pandas as pd
import requests
from bs4 import BeautifulSoup 

dotenv.load_dotenv()

from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
import dotenv
from phi.tools.duckduckgo import DuckDuckGo
from duckduckgo_search import DDGS
import pandas as pd

# Init
dotenv.load_dotenv()

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    add_chat_history_to_messages=True,
    num_history_responses=5,
    tools=[],
    markdown=True
)


pi_name = "Ibrahim Cisse"
affiliation = ''

# Get lab link
query = pi_name + " " + affiliation + " " + "lab"

results = DDGS().text(
    keywords=query
)
results_df = pd.DataFrame(results)
search_result = str(results) 

link_task = f"Provided below are a json of top web search for the laboratory webpage of {pi_name}, {affiliation}. Decide which of the results looks like it is the official lab webpage and provide ONLY the link (from href column), and nothing else in your response. If none of the results look like the official webpage, respond with only '0'"
link_prompt = f"{link_task} \n<WEB RESULTS START>\n{search_result}\n<WEB RESULTS END>"

# agent.print_response(prompt, stream=True)
link_run = agent.run(link_prompt)
# pprint([m.model_dump(include={"role", "content"}) for m in agent.memory.messages])
# print(link_run.content)
if link_run.content != '0':
    lab_url = link_run.content

# Read lab webpage
lab_page = requests.get(lab_url)

if str(lab_page.status_code).startswith('2'):
    soup = BeautifulSoup(lab_page.text, 'html.parser')
    lab_html = soup.prettify()