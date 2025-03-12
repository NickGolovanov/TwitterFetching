import tweepy
import pandas as pd
import os
from dotenv import load_dotenv
import json

load_dotenv()

bearer_token = os.environ.get("TWITTER_API_BEARER")
consumer_key = os.environ.get("TWITTER_CLEINT_ID")
consumer_secret = os.environ.get("TWITTER_CLIENT_SECRET")
access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
access_secret = os.environ.get("TWITTER_ACCESS_SECRET_TOKEN")

# auth = tweepy.OAuth2BearerHandler(bearer_token)

# auth = tweepy.OAuth1UserHandler(
#     consumer_key, consumer_secret,
#     access_token, access_secret
# )


client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_secret,
    wait_on_rate_limit=True,
)

search_query = "Elon Musk fired -is:retweet -is:reply -has:links"
no_of_tweets = 100

try:

    response = client.search_recent_tweets(
        query=search_query,
        max_results=no_of_tweets,
        tweet_fields=["created_at", "author_id"],
    )

    # Process and store tweets
    if response.data:
        tweet_list = [
            {
                "User ID": tweet.author_id,
                "Date Created": tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Tweet": tweet.text,
            }
            for tweet in response.data
        ]

        tweets_json = json.dumps(tweet_list, indent=4)

        print(tweets_json)
    else:
        print("No tweets found.")

except Exception as e:
    print("❌ Status Failed On:", str(e))
