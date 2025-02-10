# Mail Agent v0.1
# Author: Hridai Khurana
# Low Automation Level
# Takes name, affiliation, returns personalized paragraph from publication list  

from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
import dotenv
import pandas as pd
import requests
from bs4 import BeautifulSoup
from web_search import brave_search, ddg_search
import os

# Init
dotenv.load_dotenv()

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    add_chat_history_to_messages=True,
    num_history_responses=5,
    tools=[],
    markdown=True
)

search_engine = 'brave' # brave or ddg
pi_name = "Ibrahim Cisse"
affiliation = ''

# Get Google Scholar Link
query = pi_name + " " + affiliation + " " + "Google Scholar"

if search_engine == 'brave':
    search_result = brave_search(query=query)
else:
    search_result = ddg_search(query=query)

gs_task = f"Provided below are top web search results for the Google Scholar webpage of {pi_name}, {affiliation}. Decide which of the results looks like it is the official Google Scholar page and provide ONLY the link to the Google Scholar page, and nothing else in your response. If none of the results look like the correct person's Google Scholar webpage, respond with only '0'"
gs_prompt = f"{gs_task} \n<WEB RESULTS START>\n{search_result}\n<WEB RESULTS END>"

# agent.print_response(prompt, stream=True)
gs_run = agent.run(gs_prompt)
# pprint([m.model_dump(include={"role", "content"}) for m in agent.memory.messages])
# print(gs_run.content)
if gs_run.content != '0':
    scholar_url = gs_run.content + "&view_op=list_works&sortby=pubdate"

# Read publication list on Google Scholar
scholar_page = requests.get(scholar_url, headers={'User-agent': 'mail-agentv0.1'})

if str(scholar_page.status_code).startswith('2'):
    soup = BeautifulSoup(scholar_page.text, 'html.parser')
    publist = soup.find_all(id='gsc_a_t')[0]
    gs_html = publist.prettify()

# Extract most relevant papers
extr_task = f"Provided below is the Google Scholar HTML Table of {pi_name}'s publication list sorted by most recent. From this, pick the 3 most relevant to the criteria: AI/ML, mathematical modelling, genomics. Your response should contain only the publication names listed from 1 to 3."
extr_prompt = f'{extr_task}\n<HTML TABLE STARTS>\n{gs_html}\n<HTML TABLE ENDS>'
extr_run = agent.run(extr_prompt)
top_papers = extr_run.content

# Personalize email
para_agent = Agent(
    model=Groq(id="gemma2-9b-it"),
    # add_chat_history_to_messages=True,
    # num_history_responses=5,
    tools=[],
    markdown=True
)

example_para = "I find the ways the brain captures, encodes, and processes information to be extremely fascinating, and your lab's work on elucidating the mechanisms of memory and learning has been a significant inspiration. I'm particularly interested in your projects combining genetics with neuroscience, and thoroughly enjoyed reading your paper on how neuronal ensemble dynamics in the hippocampus underlie episodic memory formation, as well as your work on the role of synaptic plasticity in the retrosplenial cortex in contextual learning, especially its insights into activity-dependent transcriptional and epigenetic programs critical for memory retrieval and consolidation."
personalize_task = "Now, given the chosen most relevant papers (given below), talk about my interest in them in a short paragraph that mimics the example paragraph given below. The paragraph should talk about my interest in the papers, not plainly highlighting what the paper is talking about. Respond with only the paragraph and nothing else."
personalize_prompt = f'{personalize_task}\n<EXAMPLE PARAGRAPH STARTS>\n{example_para}\n<EXAMPLE PARAGRAPH ENDS>\nRELEVANT PAPERS: {top_papers}'
personalize_run = agent.run(personalize_prompt)

personalized_para = personalize_run.content

# Save paragraph, other info => Google Sheets
cols = ['PI_NAME', 'AFFILIATION', 'GS_URL', 'PAPERS', 'PARAGRAPH']
row = [pi_name, affiliation, scholar_url, top_papers, personalized_para]
output = pd.DataFrame(data=row, columns=cols)

save_csv_path = '/mnt/c/users/hridai/Desktop'
output.to_csv(os.path.join(save_csv_path, f'{pi_name}.csv'))
print(output)