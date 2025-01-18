import tweepy
import schedule
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from flask import Flask
import logging
from threading import Thread

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Twitter API v2 client
twitter_client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)

# Initialize Flask app
app = Flask(__name__)

# Define the start date of Trump's presidency
TRUMP_START_DATE = datetime(2017, 1, 20)

# Function to calculate the day count of Trump's presidency
def calculate_presidency_day():
    today = datetime.utcnow().date()
    return (today - TRUMP_START_DATE.date()).days + 1

# Function to post a daily update
def post_daily_update():
    try:
        day_count = calculate_presidency_day()
        tweet_text = f"Day {day_count} of Trump's Presidency."

        # Optionally add other random facts or content here
        additional_content = get_random_addition()
        if additional_content:
            tweet_text += f"\n\n{additional_content}"

        # Post the tweet
        twitter_client.create_tweet(text=tweet_text)
        logger.info(f"Successfully posted tweet: {tweet_text}")
    except Exception as e:
        logger.error(f"Error posting daily update: {e}")

# Function to get additional random content
def get_random_addition():
    content_options = [
        "Fun Fact: The White House has 132 rooms, including 35 bathrooms.",
        "This Day in History: In 1789, George Washington was unanimously elected as the first U.S. President.",
        "Quote of the Day: \"Make America Great Again!\" - Donald Trump",
        "Did you know? The U.S. President earns $400,000 annually during their term.",
        "Trivia: James Buchanan was the only U.S. president never to marry."
    ]
    return random.choice(content_options)

# Flask route for health checks
@app.route('/')
def home():
    return "Trump Presidency Bot is running"

# Function to schedule and run the bot
def run_bot():
    logger.info("Starting Trump Presidency Bot...")

    # Schedule daily posts at a specific time (e.g., 12:00 PM UTC)
    schedule.every().day.at("12:00").do(post_daily_update)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        # Start the bot in a separate thread
        bot_thread = Thread(target=run_bot)
        bot_thread.start()

        # Run Flask app for health checks
        port = int(os.environ.get("PORT", 8080))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
