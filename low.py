# Tailor Agent v0.1
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
from time import sleep

# Init
dotenv.load_dotenv()

example_criteria = 'AI/ML, mathematical modelling, genomics'
example_para = "I find the ways the brain captures, encodes, and processes information to be extremely fascinating, and your lab's work on elucidating the mechanisms of memory and learning has been a significant inspiration. I'm particularly interested in your projects combining genetics with neuroscience, and thoroughly enjoyed reading your paper on how neuronal ensemble dynamics in the hippocampus underlie episodic memory formation, as well as your work on the role of synaptic plasticity in the retrosplenial cortex in contextual learning, especially its insights into activity-dependent transcriptional and epigenetic programs critical for memory retrieval and consolidation."

def low(pi_list_path, search_engine, sample=example_para, criteria=example_criteria, delay=60, max_retries=3):
    """
    Processes the list of PIs from the CSV file at `pi_list_path` and, for each, performs web search and language model 
    operations to extract a Google Scholar URL, retrieve publication details, extract the top three relevant papers, and 
    personalize an email paragraph. If any step fails, the function will either retry (waiting for `delay` seconds between 
    attempts) or, after `max_retries` attempts, skip that row (logging an error message).
    """
    pi_list = pd.read_csv(pi_list_path, skipinitialspace=True)
    last_idx = pi_list.index[-1]
    output_rows = []

    for index, row in pi_list.iterrows():
        pi_name = row['pi_name']
        affiliation = row['affiliation']
        print(f"Processing {pi_name}")
        
        attempt = 0
        success = False
        while attempt < max_retries and not success:
            try:
                # Initialize the first agent (for web search and extraction)
                agent = Agent(
                    model=Groq(id="llama-3.3-70b-versatile"),
                    add_chat_history_to_messages=False,
                    # num_history_responses=5,
                    tools=[],
                    markdown=True
                )

                # Get Google Scholar Link using the chosen search engine
                print("Finding Google Scholar link...")
                query = f"{pi_name} {affiliation} Google Scholar"
                if search_engine == 'brave':
                    search_result = brave_search(query=query)
                else:
                    search_result = ddg_search(query=query)
                
                gs_task = (f"Provided below are top web search results for the Google Scholar webpage of {pi_name}, {affiliation}. "
                           "Decide which of the results looks like it is the official Google Scholar page and provide ONLY the link "
                           "to the Google Scholar page, and nothing else in your response. If none of the results look like the correct "
                           "person's Google Scholar webpage, respond with only '0'")
                gs_prompt = f"{gs_task} \n<WEB RESULTS START>\n{search_result}\n<WEB RESULTS END>"
                
                gs_run = agent.run(gs_prompt)
                
                # If the agent response is '0', consider it a failure for this row.
                if gs_run.content.strip() == '0':
                    raise ValueError("No valid Google Scholar page found")
                else:
                    scholar_url = gs_run.content.strip() + "&view_op=list_works&sortby=pubdate"

                # Read publication list on Google Scholar
                scholar_page = requests.get(scholar_url, headers={'User-agent': 'mail-agentv0.1'})
                if not str(scholar_page.status_code).startswith('2'):
                    raise Exception(f"Error fetching scholar page, status code: {scholar_page.status_code}")

                soup = BeautifulSoup(scholar_page.text, 'html.parser')
                publist = soup.find_all(id='gsc_a_t')[0]
                gs_html = publist.prettify()

                # Extract most relevant papers based on criteria
                print("Picking most relevant papers...")
                extr_task = (f"Provided below is the Google Scholar HTML Table of {pi_name}'s publication list sorted by most recent. "
                             f"From this, pick the 3 most relevant to the criteria: {criteria}. Your response should contain only the "
                             "publication names listed from 1 to 3.")
                extr_prompt = f"{extr_task}\n<HTML TABLE STARTS>\n{gs_html}\n<HTML TABLE ENDS>"
                extr_run = agent.run(extr_prompt)
                top_papers = extr_run.content.strip()

                # Personalize email paragraph using a second agent
                print("Personalizing text...")
                models = ["gemma2-9b-it", "llama3-70b-8192"] 
                para_agent = Agent(
                    model=Groq(id=models[1]),
                    tools=[],
                    markdown=True
                )
                personalize_task = ("Now, given the chosen most relevant papers (given below), talk about my interest in them in a short paragraph "
                                    "that mimics the example paragraph given below. The paragraph should talk about my interest in the papers, "
                                    "not plainly highlighting what the paper is talking about, and sound natural and human. Respond with only the paragraph and nothing else.")
                personalize_prompt = (f"{personalize_task}\n<EXAMPLE PARAGRAPH STARTS>\n{sample}\n<EXAMPLE PARAGRAPH ENDS>\n"
                                      f"RELEVANT PAPERS: {top_papers}")
                personalize_run = para_agent.run(personalize_prompt)
                personalized_para = personalize_run.content.strip()

                # Save successful row output
                row_output = [pi_name, affiliation, scholar_url, top_papers, personalized_para]
                output_rows.append(row_output)
                success = True

            except Exception as e:
                attempt += 1
                print(f"Error processing {pi_name} on attempt {attempt}/{max_retries}: {e}")
                if attempt < max_retries:
                    print(f"Retrying {pi_name} after waiting {delay} seconds...")
                    sleep(delay)
                else:
                    print(f"Skipping {pi_name} after {max_retries} attempts.")
                    # Append a row indicating that processing for this PI failed.
                    error_message = f"Error: {e}"
                    row_output = [pi_name, affiliation, None, None, error_message]
                    output_rows.append(row_output)
        
        # Wait before processing the next row (if not the last one)
        if index != last_idx:
            print(f"Processing for {pi_name} complete. Waiting for {delay}s before moving to the next.")
            sleep(delay)
        else:
            print(f"Processing complete for file {pi_list_path}")

    cols = ['PI_NAME', 'AFFILIATION', 'GS_URL', 'PAPERS', 'PARAGRAPH']
    output = pd.DataFrame(data=output_rows, columns=cols)
    return output