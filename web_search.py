import re
import requests
import os
import pandas as pd
from duckduckgo_search import DDGS

def remove_html_tags(text):
    return re.sub(r"</?strong>", "", text)


def brave_search(query, api_key='BSAKiixseKVtNfNdfy0NKTIatrmReBV'):
    search_url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    params = {"q": query, "count": 10}
    response = requests.get(search_url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code == 200:
        results = response.json()

    filtered_results = [
        {"title": item["title"], "url": item["url"], "description": item.get("description", "No description available")}
        for item in results["web"]["results"]
    ]

    formatted_results = "\n".join(
        f"Title: {remove_html_tags(res['title'])}\n"
        f"URL: {res['url']}\n"
        f"Description: {remove_html_tags(res['description'])}\n"
        for res in filtered_results
    )

    return formatted_results

def ddg_search(query):
    results = DDGS().text(
        keywords=query
    )
    # results_df = pd.DataFrame(results)
    search_result = str(results)
    return search_result



