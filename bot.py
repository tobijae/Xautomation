import tweepy
import requests
import openai
from datetime import datetime
import schedule
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize clients
twitter_client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)
openai.api_key = OPENAI_API_KEY

def get_crypto_data():
    """Fetch detailed crypto data including price, volume, and market cap"""
    coins = ['bitcoin', 'ethereum', 'solana']
    all_data = {}
    
    for coin in coins:
        url = f'https://api.coingecko.com/api/v3/coins/{coin}'
        response = requests.get(url)
        data = response.json()
        
        all_data[coin] = {
            'price': data['market_data']['current_price']['usd'],
            'change_24h': data['market_data']['price_change_percentage_24h'],
            'volume': data['market_data']['total_volume']['usd'],
            'market_cap': data['market_data']['market_cap']['usd']
        }
    
    return all_data

def get_ai_analysis(market_data):
    """Generate AI analysis of market conditions"""
    prompt = f"""
    Analyze these crypto market conditions and provide a brief, technical market summary in 150 characters or less:
    
    BTC: ${market_data['bitcoin']['price']:,.0f} ({market_data['bitcoin']['change_24h']:.1f}%)
    ETH: ${market_data['ethereum']['price']:,.0f} ({market_data['ethereum']['change_24h']:.1f}%)
    SOL: ${market_data['solana']['price']:,.0f} ({market_data['solana']['change_24h']:.1f}%)
    
    Include: key support/resistance levels, trend direction, or notable pattern formations.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Updated to use gpt-4o-mini
        messages=[
            {"role": "system", "content": "You are a crypto technical analyst. Focus on key technicals and potential setups. Be concise and specific."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.7
    )
    
    return response.choices[0].message['content']

def should_post(market_data):
    """Determine if market conditions warrant a post"""
    # Post if any coin has moved more than 2% in either direction
    for coin_data in market_data.values():
        if abs(coin_data['change_24h']) > 2:
            return True
    return False

def create_market_tweet():
    """Create and format tweet with market data and AI analysis"""
    try:
        # Get market data
        market_data = get_crypto_data()
        
        # Only post if there's significant movement
        if not should_post(market_data):
            print("No significant market movement. Skipping post.")
            return None
            
        # Get AI analysis
        analysis = get_ai_analysis(market_data)
        
        # Format tweet
        time_now = datetime.now().strftime('%H:%M UTC')
        tweet = f"Market Update ({time_now})\n\n"
        
        # Add price data
        for coin, data in market_data.items():
            symbol = coin[:3].upper()
            arrow = "↗️" if data['change_24h'] > 0 else "↘️"
            tweet += f"{symbol}: ${data['price']:,.0f} {arrow} {data['change_24h']:.1f}%\n"
        
        # Add AI analysis
        tweet += f"\nAnalysis:\n{analysis}"
        
        return tweet
    
    except Exception as e:
        print(f"Error creating tweet: {e}")
        return None

def post_update():
    """Post market update to Twitter"""
    tweet = create_market_tweet()
    if tweet:
        try:
            twitter_client.create_tweet(text=tweet)
            print(f"Tweet posted successfully at {datetime.now()}")
        except Exception as e:
            print(f"Error posting tweet: {e}")

def main():
    """Main function to schedule and run the bot"""
    # Schedule 3 posts during market hours
    schedule.every().day.at("13:30").do(post_update)  # 9:30 AM EST
    schedule.every().day.at("18:00").do(post_update)  # 2:00 PM EST
    schedule.every().day.at("20:00").do(post_update)  # 4:00 PM EST
    
    print("Bot started. Posts scheduled for 9:30 AM, 2:00 PM, and 4:00 PM EST")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
