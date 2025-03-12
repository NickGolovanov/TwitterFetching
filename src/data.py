from typing import List

import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_API_BEARER")
CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")


client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
)

SEARCH_QUERY = "(weather OR forecast OR rain OR sunny OR storm OR temperature) (Amsterdam OR Rotterdam) -is:retweet -is:reply"
MAX_RESULTS = 100


def retrieve_x_posts(
    search_query: str = SEARCH_QUERY, max_result: str = MAX_RESULTS
) -> List:
    """
    Retrieves a list of tweets based on the search query and maximum results.
    """

    try:
        response = client.search_recent_tweets(
            query=search_query,
            max_results=max_result,
            expansions=["geo.place_id", "author_id"],
            tweet_fields=["id", "text", "created_at", "geo"],
            user_fields=["username"],
            place_fields=["country", "country_code", "full_name", "name", "place_type"],
        )

        return response

    except tweepy.TooManyRequests as e:
        print("Rate Limit Exceeded:", str(e))

    except Exception as e:
        print("Status Failed On:", str(e))


def process_x_posts(x_posts: List) -> List:
    """
    Processes the retrieved tweets to extract relevant information.
    """
    try:
        tweets = x_posts.data if x_posts.data else []

        includes = x_posts.includes if x_posts.includes else {}

        places = {place["id"]: place for place in includes.get("places", [])}
        users = {user["id"]: user for user in includes.get("users", [])}

        processed_tweets = []

        if tweets:
            for tweet in tweets:
                tweet_data = {
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "username": users.get(tweet.author_id, {}).get(
                        "username", "Unknown"
                    ),
                }
                geo = tweet.get("geo", {})
                if geo and "place_id" in geo:
                    place = places.get(tweet.geo["place_id"], {})
                    tweet_data.update(
                        {
                            "country": place.get("country"),
                            "country_code": place.get("country_code"),
                            "full_name": place.get("full_name"),
                            "name": place.get("name"),
                            "place_type": place.get("place_type"),
                        }
                    )

                processed_tweets.append(tweet_data)

        return processed_tweets
    except Exception as e:
        print(f"Error processing X posts: {e}, {x_posts}")
        return []


def validate_x_posts(x_posts: List) -> List:
    """
    Validates the processed tweets for any errors or inconsistencies.
    """
    validated_tweets = []

    return validated_tweets


def store_x_posts(x_posts: List) -> None:
    """
    Stores the validated tweets in a database or file for further analysis.
    """
    pass


def retrieve_geo_data() -> List: ...


def process_geo_data(geo_data: List) -> List: ...


def store_geo_data(geo_data: List) -> None: ...
