import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
from dotenv import load_dotenv
from datetime import datetime

# Load the .env file
load_dotenv()

# Access the variables as environment variables
weibo_url = os.getenv('WEIBO_URL')
message_webhook_url = os.getenv('MESSAGE_WEBHOOK_URL')
status_webhook_url = os.getenv('STATUS_WEBHOOK_URL')

# To store last parsed post
last_post = None

def send_message(url, content):
    # This is a basic structure of a discord embed, adjust according to your needs
    data = {
        "embeds": [
            {
                "title": "New Weibo Post",
                "description": content['text'],
                "image": {"url": content['img']}
            }
        ]
    }
    response = requests.post(url, json=data)
    return response.status_code

def send_status():
    data = {"content": f"Script is running - {datetime.now().isoformat()}"}
    response = requests.post(status_webhook_url, json=data)
    return response.status_code

def parse_weibo():
    global last_post
    page = requests.get(weibo_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Adjust the below line according to the structure of your Weibo page
    posts = soup.find_all('div', class_='weibo_post')

    for post in posts:
        # Again, this is dependent on the structure of the Weibo page
        text = post.find('div', class_='weibo_text').get_text()
        img = post.find('img')['src']
        
        if post != last_post:
            send_message(message_webhook_url, {'text': text, 'img': img})
            last_post = post
        else:
            break

# Scheduling tasks
schedule.every(10).minutes.do(parse_weibo)  # replace X with the desired interval
schedule.every(1).hours.do(send_status)

while True:
    schedule.run_pending()
    time.sleep(1)
