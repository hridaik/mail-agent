# tailor-agent v0.1
AI agent to create personalized messages. This agent is currently optimized for reaching out to researchers.
Given a list of researchers/PIs, and your interests, the agent will pick the most relevant papers from the researcher's lab and write a personalized message/email using an example template, mentioning your interest in the researcher's work. Returns a CSV with the most relevant papers and personalized message.

**Note:** tailor-agent is still under development. Groq API key required for LLM access. You can get one for free at https://console.groq.com/keys

## Example Usage
git clone https://github.com/hridaik/mail-agent.git

cd tailor-agent

**Create .env file with GROQ_API_KEY**

python cli.py  --level low --pi_list sample_list.csv 
                --sample_text sample_para.txt --criteria 'AI/ML, mathematical modelling, genomics'
                --search_engine brave --delay 60
                --output_path /mnt/c/Users/hridai/Desktop

Use **python cli.py [-h/--help]** for info on input arguments 

## Requirements
**pip**: phidata, dotenv, pandas, bs4, duckduckgo_search (optional)

**.env file**: GROQ_API_KEY, BRAVE_API_KEY (optional, recommended)

## Options
**--level**: Automation level. **ONLY LOW AVAILABLE RIGHT NOW.** Allowed: low, medium, high
    level 'low': Returns a CSV with the most relevant papers and personalized message for each person in input list.

**--pi_list**: Path to a CSV of people. CSV should include columns: name, affiliation

**--output_path**: Path to save output CSV

**--sample_text**: Path to TXT file with sample text to personalize

**--criteria**: Quotes-enclosed string of topics relevant to you. Example usage: --criteria 'AI/ML, mathematical modelling, genomics'

**--delay**: Time in seconds to wait after processing each row to avoid API timeout. Default: 60s