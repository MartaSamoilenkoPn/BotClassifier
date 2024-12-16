from twikit import Client, TooManyRequests
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import asyncio
import os
from getpass import getpass
from datetime import datetime, timezone
import joblib 
import pandas as pd


async def login():
    """
    Login into Twitter account"""
    # Prompt user for input
    username = input("Enter your username: ").strip()
    email = input("Enter your email: ").strip()
    password = getpass("Enter your password: ")  # Hides the password input

    # Initialize client with user agent and language
    client = Client(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.120 Safari/537.36",
        language="en-US"
    )

    # Perform the login operation
    try:
        await client.login(
            auth_info_1=username,
            auth_info_2=email,
            password=password
        )
        client.save_cookies("cookies.json")
        print("Login successful, cookies saved to cookies.json")
    except Exception as e:
        print(f"Error during login: {e}")

    return client

async def fetch_updated_user_data(username, client):
    """
    Find Twitter user and fetch him data by username
    """
    try:
        # Search for the user by screen_name
        users = await client.search_user(username, count=1)
        if not users:
            print(f"User not found: {username}")
            return None
        user = users[0]
        username = user.screen_name
        # Parse the account creation time
        created_at = datetime.strptime(user.created_at, "%a %b %d %H:%M:%S %z %Y")

        # Calculate derived fields
        current_time = datetime.now(timezone.utc)
        account_age_days = (current_time - created_at).days
        average_tweets_per_day = user.statuses_count / account_age_days if account_age_days > 0 else 0

        # Format the data to match the model's input structure
        user_data = {
            'hour_created': created_at.hour,
            'verified': int(user.is_blue_verified),
            'default_profile': int(user.default_profile),
            'favourites_count': user.favourites_count,
            'followers_count': user.followers_count,
            'friends_count': user.following_count,
            'statuses_count': user.statuses_count,
            'average_tweets_per_day': round(average_tweets_per_day, 2),
            'account_age_days': account_age_days
        }

        # Convert to a DataFrame for prediction
        user_df = pd.DataFrame([user_data])

        return user_df, username

    except Exception as e:
        print(f"Error fetching data for {username}: {e}")
        return None



async def main():
    """
    Function to detect if user in Twitter is real or not
    """
    print("Trying to login into Twitter account...")
    if os.path.exists("cookies.json"):
        print("Login with cookies file...")
        client = Client(language='en-US')
        client.load_cookies('cookies.json')
    else:
        print("Login with credentials")
        client = await login()
    username = input("Enter username you want to detect: ").strip()
    user_data, username_real = await fetch_updated_user_data(username, client)
    knn_from_joblib = joblib.load('knn_bot_detector.pkl')
    twi_pred = knn_from_joblib.predict(user_data)
    twi_pred = ['bot' if pred == -1 else 'user' for pred in twi_pred][0]

    print(f"Twiter account with username - {username_real} is ", twi_pred)

if __name__ == "__main__":
    asyncio.run(main())
