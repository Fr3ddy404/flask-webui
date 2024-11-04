import re
from bs4 import BeautifulSoup

def process_message(message):
    return {
        "messages": [
            {
                "content": format_message(message.get('content')),
                "actor": message.get('actor')
            }, {
                "content": format_message(message.get('content')),
                "actor": 2
            }
        ]}


def format_message(message):
    soup = BeautifulSoup(message, 'html.parser')
    
    # Define a regex pattern to match content inside square brackets
    pattern1 = re.compile(r'\[([\t\f\v]*)\]')
    pattern2 = re.compile(r'\[([^\[\]\n]+)\]')
    
    # Find all text nodes that match the pattern
    for tag in soup.find_all(text=pattern1):
        new_html_snipped = pattern1.sub(lambda match: f"['{match.group(1)}']", tag)
        new_soup = BeautifulSoup(new_html_snipped, 'html.parser')
        tag.replace_with(new_soup)
   
    # Find all text nodes that match the pattern
    for tag in soup.find_all(text=pattern2):
        new_html_snipped = pattern2.sub(lambda match: f'<span class="spoiler" onclick="toggleSpoiler(this)">{match.group(1)}</span>', tag)
        new_soup = BeautifulSoup(new_html_snipped, 'html.parser')
        tag.replace_with(new_soup)
   
    message = str(soup)
    return message
