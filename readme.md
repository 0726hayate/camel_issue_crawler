# Camel Issue Crawler

## Overview
This Python script fetches and extracts details from Apache Camel Jira issue pages. It retrieves issue metadata, description, and comments, then saves the data into a CSV file.

## Prerequisites
Before running the script, ensure you have the following installed:

- Python 3.x
- Google Chrome
- Chrome WebDriver
- Required Python libraries:
  ```bash
  pip install beautifulsoup4 selenium
  ```

## Usage
1. **Modify the Issue ID:**
   - Change the `issue_id` variable inside the `main()` function to the desired Jira issue number.

2. **Run the script:**
   ```bash
   python src/crawler.py
   ```
   - The script fetches the specified Jira issue page, extracts relevant details, and saves them to `camel_issues.csv`.

## Output
- The script creates a CSV file named `camel_issues.csv` containing:
  - Issue Type
  - Assignee
  - Created Date
  - Created Epoch Time
  - Description
  - Comments

## License
This script is free to use and modify as needed.

