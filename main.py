import requests    
import datetime     
import logging      
import os           

from urllib.parse import quote
from typing import Dict


MD_DIR = "docs"
CONTENT_DIR = os.path.join(MD_DIR, "index.md")
DATE_FORMAT = "%Y-%m-%d"
TITLE_FORMAT = "{date}_{title}.md"
DATA_URL = "https://xkcd.com/{page_no}/info.0.json"
MARKDOWN_FORMAT = """
# XKCD Comic for day {date}

## {title}

![{title}]({img_url} "{alt}")

[Visit the original page](https://xkcd.com/{num}/)
"""
CONTENT_PAGE_SPLIT = f"| {'-'*10} | {'-'*50} | {'-'*142} |"


def generate_file_name(title: str, date: str) -> str:
    """Generate the file name for the markdown file to be written"""
    return TITLE_FORMAT.format(date=date, title=title)


def generate_markdown(title: str, img_url: str, alt: str, num: int, date: str) -> str:
    """Generate the markdown content"""
    return MARKDOWN_FORMAT.format(date=date, title=title, img_url=img_url, alt=alt, num=num)


def generate_content_line(title: str, date: str, url_path: str) -> str:
    """Generate the content line for the content page"""
    link_format = f"[Link](./{quote(url_path)} \"{title}\")"
    return f"| {date:10} | {title:50} | {link_format:142} |"



def insert_to_content_page(title: str, date: str, file_name: str):
    """Insert the markdown content at the beginning of the content page"""

    

    new_line = generate_content_line(title, date, file_name)

    with open(CONTENT_DIR, "r+") as file:
        content = file.read()

    # Check if CONTENT_PAGE_SPLIT is already in the file
    if CONTENT_PAGE_SPLIT not in content:
        # If not, append it to the end of the file
        with open('index.md', 'a') as file:
            file.write('\n' + CONTENT_PAGE_SPLIT)

        # Check if the new line is already present
        if new_line in content:  # Exact match
            return  # Skip if the line already exists

        # Find the position of the split
        split_pos = content.find(CONTENT_PAGE_SPLIT)
        if split_pos == -1:
            raise ValueError(f"Could not find split '{CONTENT_PAGE_SPLIT}' in index.md")

        # Insert the new line after the split
        new_content = (
            content[:split_pos + len(CONTENT_PAGE_SPLIT)] + "\n" + new_line + content[split_pos + len(CONTENT_PAGE_SPLIT):]
        )
        
        # Rewrite the file with the new content
        file.seek(0)
        file.write(new_content)


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    current_time = datetime.datetime.now()
    project_start_date = datetime.datetime(2024, 3, 17)
    day_since_creation = current_time - project_start_date

    # Call the api
    with requests.Session() as session:
        response = session.get(
            DATA_URL.format(page_no=day_since_creation.days),
        )

        if response.status_code >= 400:
            logger.critical(f"Failed to get the data from the API. Status code: {response.status_code}")
            exit(1)

        data: Dict[str, str] = response.json()

    # Extract information
    title = data.get("title", "No title")
    img_url = data.get("img", "No image")
    alt = data.get("alt", "No alt")
    num = data.get("num", "1")

    # Create the file
    date_str = current_time.strftime(DATE_FORMAT)
    file_name = generate_file_name(title, date_str)

    with open(os.path.join(MD_DIR, file_name), "w") as file:
        file.write(
            generate_markdown(title, img_url, alt, int(num), date_str),
        )

    # print(data)
    # Update the content page
    insert_to_content_page(title, date_str, file_name.strip(".md"))