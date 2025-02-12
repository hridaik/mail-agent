# Mail Agent v0.1
# Author: Hridai Khurana
# Example Usage: cli.py --level low --pi_list sample_list.csv 
#                       --sample_text sample_para.txt --criteria 'AI/ML, mathematical modelling, genomics'
#                       --search_engine brave --delay 60
#                       --output_path /mnt/c/Users/hridai/Desktop
import argparse
import os
from low import low

parser = argparse.ArgumentParser()
parser.add_argument("--level", type=str, help="Automation level. ONLY LOW AVAILABLE RIGHT NOW. Options: low, medium, high")
parser.add_argument("--pi_list", type=str, help="Path to a CSV of people to email. CSV should include columns: name, affiliation")
parser.add_argument("--search_engine", type=str, help="Search engine to use. Options: brave (Brave search), ddg (DuckDuckGo)")
parser.add_argument("--output_path", type=str, help="Path to save output CSV")
parser.add_argument("--sample_text", type=str, help="Path to TXT file with sample text to personalize")
parser.add_argument("--criteria", type=str, help="Quotes-enclosed string of topics relevant to you. Example usage: --criteria 'AI/ML, mathematical modelling, genomics'")
parser.add_argument("--delay", type=int, help="Time in seconds to wait after processing each row to avoid API timeout.")
args = parser.parse_args()

if args.level == 'low':
    print('Low Automation Level Run Starting')
else:
    print(f'Automation level {args.level} not available. Defaulting to low.')

sample_txt = open(args.sample_text, "r")
sample = sample_txt.read()

out_df = low(args.pi_list, args.search_engine, sample=sample, criteria=args.criteria)

save_csv_path = '/mnt/c/users/hridai/Desktop'
outfile = os.path.join(save_csv_path, 'mail_agent.csv')
out_df.to_csv(outfile)
print(f'Output CSV saved to {outfile}')