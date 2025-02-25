import tweepy
import pandas as pd
import os
from dotenv import load_dotenv

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
    wait_on_rate_limit=True
)

# api = tweepy.API(auth, wait_on_rate_limit=True)

search_query = "Elon Musk fired -is:retweet -is:reply -has:links"
# search_query = "point_radius:[4.895168 53.370216 25km]"
no_of_tweets = 100

try:
    # Fetch tweets
    tweets = client.search_recent_tweets(query=search_query, max_results=no_of_tweets, tweet_fields=["created_at", "author_id"])

    # Process and store tweets
    if tweets.data:
        attributes_container = [[tweet.author_id, tweet.created_at, tweet.text] for tweet in tweets.data]

        columns = ["User ID", "Date Created", "Tweet"]
        tweets_df = pd.DataFrame(attributes_container, columns=columns)

        print(tweets_df)
    else:
        print("No tweets found.")

except Exception as e:
    print("❌ Status Failed On:", str(e))