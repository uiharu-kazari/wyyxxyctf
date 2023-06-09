from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os
import json
import sqlite3
from dotenv import load_dotenv
import requests
from datetime import datetime
import schedule
import pytz
import random
import platform

# Load the .env file
load_dotenv()

# Access the variables as environment variables
weibo_url = os.getenv('WEIBO_URL')
message_webhook_url = os.getenv('MESSAGE_WEBHOOK_URL')
status_webhook_url = os.getenv('STATUS_WEBHOOK_URL')


class WeiboScrapper:
    def __init__(self):
        # Setup driver
        # add headless
        self.driver = self.new_driver()
        # create a sqlite database to store id
        # change to mongodb later
        self.db = sqlite3.connect('weibo.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS weibo (id INTEGER PRIMARY KEY)''')
        self.db.commit()
        with open('kawaii_content.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.kawaii_emojis = data['kawaii_emojis']
        self.kawaii_texts = data['kawaii_texts']
        self.kawaii_titles = data['kawaii_titles']

    
    def new_driver(self):
        # Setup driver
        # add headless
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(\
            service=Service(ChromeDriverManager().install())\
                ,options=options)
        return driver


    def start(self):
        # Run the scan immediately and then every 10 minutes
        self.scan()
        schedule.every(10).minutes.do(self.scan)

        # Run send_status immediately and then every hour
        self.send_status()
        schedule.every(1).hour.do(self.send_status)

        while True:
            schedule.run_pending()
            time.sleep(1)

        
    def get_weibo_content_once(self):
        # check if the driver is alive
        if self.driver.service.is_connectable():
            pass
        else:
            self.driver.quit()
            self.driver = self.new_driver()

        try:
            self.driver.get(os.getenv('WEIBO_URL'))
            # Wait for the dynamic content to load
            time.sleep(10)
            self.driver.implicitly_wait(20)
            pre_tag = self.driver.find_element(By.TAG_NAME, 'pre')
            json_text = pre_tag.text
        except Exception as e:
            print(e)
            return None
        content = json.loads(json_text) # content is a dictionary
        return content['data']['list']
    
    def check_id(self,item):
        # if id is not in the database, return True
        # else return False
        weibo_item_id=item['id']
        self.cursor.execute('''SELECT * FROM weibo WHERE id=?''',(weibo_item_id,))
        if self.cursor.fetchone() is None:
            #write the id to the database
            self.cursor.execute('''INSERT INTO weibo (id) VALUES (?)''',(weibo_item_id,))
            self.db.commit()
            return True
        else:
            return False       

    def get_weibo_content_loop(self):
        i=0
        print(f'getting weibo content... @ {datetime.now()}')
        while True:
            content = self.get_weibo_content_once()
            if content:
                break   
            print('retrying...')
            time.sleep(60)
            i+=1
            print(i)
            if i>10:
                print('failed')
                return None
        return content

    def scan(self):
        content = self.get_weibo_content_loop()
        if content:
            for item in content:
                if self.check_id(item):
                    self.parse_item(item)
                    time.sleep(5)
        else:
            print('failed to get content')
            return None

    def parse_item(self,item):
        # parse item and store it in the database
        # send text_raw to discord
        # add separator to text_raw
        text_raw = item['text_raw']
        created_at = item['created_at']
        # use discord embed to display the content
        # "embed_color": 16738740
        dt = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
        # Convert to UTC
        # use GMT+8
        timezone = pytz.timezone('Etc/GMT-8')
        dt = dt.astimezone(timezone)
        # Format as required by Discord
        discord_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        message ={
            "embeds": [{
                "title": "塔菲の新微博喵~",
                "url": "https://weibo.com/7618923072?refer_flag=1001030103_",
                "description": text_raw,
                "color": 16738740,
                "timestamp": discord_timestamp
            },
            ]
        }
        response = requests.post(message_webhook_url, json=message)
        return response.status_code

    def send_status(self):
        # send status to discord, say that the script is running, add some random kawaii emoji and text
        # use discord embed to display the content
        embed_color = 16738740
        emoji = random.choice(self.kawaii_emojis)
        text = random.choice(self.kawaii_texts)
        title = random.choice(self.kawaii_titles)
        if platform.system() == 'Windows':
            machine_info = f"{platform.node()} {platform.machine()}"
        else:
            machine_info = f"{os.uname().nodename} {os.uname().machine}"
        # TODO: use chatgpt to generate random text
        # get current time, up to seconds, timezone GMT+9
        timezone = pytz.timezone('Etc/GMT-9')
        # Get current time up to seconds in GMT+9
        time_now = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S %Z')

        message = {
            "embeds": [
                {
                    "title": title,
                    "description": f"{emoji} {text} @ {time_now} -- {machine_info}",
                    "color": embed_color
                }
            ]
        }
        response = requests.post(status_webhook_url, json=message)
        return response.status_code
    

if __name__ == "__main__":
    weibo_scrapper = WeiboScrapper()
    weibo_scrapper.start()