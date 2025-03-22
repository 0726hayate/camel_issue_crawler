#!/usr/bin/env python3
from bs4 import BeautifulSoup #for reading and searching HTML
import time
from typing import Dict, List
from selenium import webdriver # control bowser to get dyanmic content i.e. comments
from selenium.webdriver.chrome.options import Options
import csv

BASE_URL = "https://issues.apache.org/jira/browse/CAMEL-"

def fetch_issue_page(issue_id: str) -> str:
    """Fetch the HTML content of a Jira issue page with Selenium.

    Args:
        issue_id: The Jira issue ID (e.g., "10597" for CAMEL-10597).

    Returns:
        String containing the full HTML content of the page, or empty string if fetch fails.
    """
    url = f"{BASE_URL}{issue_id}" #build full URL
    options = Options()
    options.headless = True  # Run bowser without showing the window
    driver = webdriver.Chrome(options=options)  # open chrome
    try:
        driver.get(url) # open url in chrome
        time.sleep(2)  # Wait for dynamic content (comments) to load
        html_content = driver.page_source
        #save HTML to full_page.html for parsing and debugging
        with open("full_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        return html_content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""
    finally:
        driver.quit() #close bowser

def parse_details(soup: BeautifulSoup) -> Dict[str, str]:
    """Parse the 'Details' section of the issue page.

    Args:
        soup: BeautifulSoup object containing the parsed HTML of the Jira issue page.

    Returns:
        Dictionary mapping detail labels (e.g., "Type:") to their values (e.g., "Bug").
    """
    details = {} # to store details
    detail_section = soup.find("ul", id="issuedetails") #look for ul tag with id issuedetails
    if detail_section: #check to see if section is found
        for item in detail_section.find_all("li", class_="item"): #get all list items in the section
            label_elem = item.find("strong", class_="name") #to find each lable/subheader (type, status, priority...) under details
            if label_elem:
                label = label_elem.text.strip()
                value_elem = item.find("span", class_="value") or item.find("div", class_="value") # to get values of each label/subheader
                if value_elem:
                    value = " ".join(value_elem.get_text(strip=True).split()) #clean up text
                    details[label] = value
                else:
                    details[label] = "" #add label/subheader:value to details
    return details

def parse_people(soup: BeautifulSoup) -> Dict[str, str]:
    """Parse the 'People' section of the issue page.

    Args:
        soup: BeautifulSoup object containing the parsed HTML of the Jira issue page.

    Returns:
        Dictionary mapping people labels (e.g., "Assignee:") to their values (e.g., "Claus Ibsen").
    """
    people = {}
    people_section = soup.find("div", id="peoplemodule") #look for people section
    if people_section:
        for item in people_section.find_all("dd"): #get values
            label = item.find_previous_sibling("dt").text.strip() #get labels/subjeaders
            value = item.text.strip()
            people[label] = value #put labels/subheaders and values together
    return people

def parse_dates(soup: BeautifulSoup) -> Dict[str, str]:
    """Parse the 'Dates' section of the issue page.

    Args:
        soup: BeautifulSoup object containing the parsed HTML of the Jira issue page.

    Returns:
        Dictionary mapping date labels (e.g., "Created:") to their values (e.g., "2016-12-14T14:42:08+0000"),
        including "Created Epoch" with the epoch timestamp.
    """
    dates = {}
    dates_section = soup.find("div", id="datesmodule") #look for dates section
    if dates_section:
        for item in dates_section.find_all("dd"): #get values
            label = item.find_previous_sibling("dt").text.strip() #get label/subheader
            value = item.find("time")["datetime"] if item.find("time") else item.text.strip()
            dates[label] = value
            if label == "Created:" and item.find("time"): #convert time to proper format
                epoch = int(time.mktime(time.strptime(value, "%Y-%m-%dT%H:%M:%S%z")))
                dates["Created Epoch"] = str(epoch)
    return dates

def parse_description(soup: BeautifulSoup) -> str:
    """Parse the 'Description' section of the issue page.

    Args:
        soup: BeautifulSoup object containing the parsed HTML of the Jira issue page.

    Returns:
        String containing the issue description text, or empty string if not found.
    """
    desc_section = soup.find("div", id="descriptionmodule") #find description section
    if desc_section:
        desc = desc_section.find("div", class_="user-content-block") #get actual description
        return desc.text.strip() if desc else ""
    return ""

def parse_comments(soup: BeautifulSoup) -> List[str]:
    """Parse the 'Comments' section of the issue page.

    Args:
        soup: BeautifulSoup object containing the parsed HTML of the Jira issue page.

    Returns:
        List of strings, each representing a comment in the format "author:epoch:timestamp:text".
    """
    comments = []
    comment_section = soup.find("div", id="activitymodule") #find comment section (webpage is opened with the activity section already in the comment section )
    if comment_section: #loop through each comment to get author, time stamp, the actual comment
        #print("Found activitymodule:")
        for comment_block in comment_section.find_all("div", class_="issue-data-block"):
            print(f"Comment: {comment_block.prettify()}")
            author_elem = comment_block.find("a", class_="user-hover")
            time_elem = comment_block.find("time", class_="livestamp")
            body_elem = comment_block.find("div", class_="action-body")
            print(f"Author: {author_elem}, Time: {time_elem}, Body: {body_elem}")
            if author_elem and time_elem and body_elem:
                author = author_elem.text.strip()
                timestamp = time_elem["datetime"]
                epoch = int(time.mktime(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")))
                text = body_elem.text.strip()
                comments.append(f"{author}:{epoch}:{timestamp}:{text}") #combine author, time stamp, actual comment into a string
    else:
        print("Warning: No activitymodule found")
    return comments

def parse_issue(html_content: str) -> Dict:
    """Parse all required fields from the issue HTML.

    Args:
        html_content: String containing the full HTML content of the Jira issue page.

    Returns:
        Dictionary containing all parsed issue data (details, people, dates, description, comments).
    """
    soup = BeautifulSoup(html_content, "html.parser") #turn HTML into objext
    data = {}#create dictionary and enter the results from each section
    data.update(parse_details(soup))
    data.update(parse_people(soup))
    data.update(parse_dates(soup))
    data["Description"] = parse_description(soup)
    data["Comments"] = "; ".join(parse_comments(soup)) #join comments with ;into 1 string
    return data

def write_to_csv(issue_data: Dict, filename: str = "camel_issues.csv"):
    """Write issue data to a CSV file.

    Args:
        issue_data: Dictionary containing parsed issue data.
        filename: Optional string specifying the output CSV file name (default: "camel_issues.csv").

    Returns:
        None (writes data to the specified CSV file).
    """
    headers = [
        "Type", "Assignee", "Created", "Created Epoch", "Description", "Comments"
    ]  
    data_row = {
        "Type": issue_data.get("Type:", ""),
        "Assignee": issue_data.get("Assignee:", ""),
        "Created": issue_data.get("Created:", ""),
        "Created Epoch": issue_data.get("Created Epoch", ""),
        "Description": issue_data.get("Description", ""),
        "Comments": issue_data.get("Comments", "")
    }
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerow(data_row)

def main():
    
    issue_id = "10597"
    html_content = fetch_issue_page(issue_id)
    if html_content:
        issue_data = parse_issue(html_content)
        write_to_csv(issue_data)
        print(f"Data written to camel_issues.csv")

if __name__ == "__main__":
    main()