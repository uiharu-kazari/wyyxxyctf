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
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(\
            service=Service(ChromeDriverManager().install())\
                ,options=options)
        # create a sqlite database to store id
        # change to mongodb later
        self.db = sqlite3.connect('weibo.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS weibo (id INTEGER PRIMARY KEY)''')
        self.db.commit()


    def start(self):
        # Run the scan immediately and then every 10 minutes
        self.scan()
        schedule.every(10).minutes.do(self.scan)

        # Run send_status immediately and then every hour
        schedule.every(1).hour.do(self.send_status)

        while True:
            schedule.run_pending()
            time.sleep(1)

        
    def get_weibo_content_once(self):
        try:
            self.driver.get(os.getenv('WEIBO_URL'))
            # Wait for the dynamic content to load
            time.sleep(5)
            self.driver.implicitly_wait(5)
            pre_tag = self.driver.find_element(By.TAG_NAME, 'pre')
            json_text = pre_tag.text
            self.driver.quit()
        except Exception as e:
            print(e)
            self.driver.quit()
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
        print('getting weibo content...')
        while True:
            content = self.get_weibo_content_once()
            if content:
                break   
            print('retrying...')
            time.sleep(5)
            i+=1
            print(i)
            if i>50:
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
        # use discord embed to display the content
        # "embed_color": 16738740
        
        message ={
            "embeds": [{
                "title": "塔菲の新微博喵~",
                "description": text_raw,
                "color": 16738740
            },
            ]
        }
        response = requests.post(message_webhook_url, json=message)
        return response.status_code

    def send_status():
        data = {"content": f"Script is running - {datetime.now().isoformat()}"}
        response = requests.post(status_webhook_url, json=data)
        return response.status_code
    

if __name__ == "__main__":
    weibo_scrapper = WeiboScrapper()
    weibo_scrapper.start()