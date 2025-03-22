#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://issues.apache.org/jira/browse/CAMEL-10597"

def fetch_issue_page(issue_id: str) -> str:
    """Fetch the HTML content of a Jira issue page."""
    url = f"{BASE_URL}{issue_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

def main():
    issue_id = "10597"  # Example issue: CAMEL-10597
    html_content = fetch_issue_page(issue_id)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        with open("temp.html", "w") as file:
            file.write(soup.prettify())

if __name__ == "__main__":
    main()