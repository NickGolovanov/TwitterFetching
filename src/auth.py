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


client = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_secret)

# api = tweepy.API(auth, wait_on_rate_limit=True)

search_query = "Elon Musk fired -filter:retweets AND -filter:replies AND -filter:links"
# search_query = "point_radius:[4.895168 53.370216 25km]"
no_of_tweets = 100

try:
    #The number of tweets we want to retrieved from the search
    # tweets = api.search_tweets(q=search_query, lang="en", count=no_of_tweets, tweet_mode ='extended')
    
    tweets = client.search_recent_tweets(query=search_query, max_results=no_of_tweets)

    attributes_container = [[tweet.user.name, tweet.created_at, tweet.favorite_count, tweet.source, tweet.full_text] for tweet in tweets]

    columns = ["User", "Date Created", "Number of Likes", "Source of Tweet", "Tweet"]
    
    tweets_df = pd.DataFrame(attributes_container, columns=columns)
except BaseException as e:
    print('Status Failed On,',str(e))