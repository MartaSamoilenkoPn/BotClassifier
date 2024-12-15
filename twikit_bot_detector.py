from twikit import Client, TooManyRequests
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import asyncio
import os


async def login():
    config = ConfigParser()
    config.read('config.ini')
    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']

    client = Client(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.120 Safari/537.36", language='en-US')

    await client.login(
        auth_info_1=username,
        auth_info_2=email,
        password=password
    )
    client.save_cookies("cookies.json")

    return client



async def main():
    if os.path.exists("cookies.json"):
        client = Client(language='en-US')
        client.load_cookies('cookies.json')
    else:
        client = await login()
    
    with open('tweets.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes'])

    tweets = await client.search_tweet('python', 'Latest')

    for tweet in tweets:
        print(
            vars(tweet)
        )

if __name__ == "__main__":
    asyncio.run(main())
