from typing import Any, Dict, List, Optional, Tuple

import re
import tweepy
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key, Attr

from .models.social_media import insert_social_media, insert_log_to_social_media
from .models.post import insert_post
from .models.types import LogType
from .db import dynamodb_resource
from services.email_service import send_email
from services.post_service import encrypt_data

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_API_BEARER")
CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")

SEARCH_QUERY: str = (
    "(weather OR storm OR rain OR sunny OR snow OR wind OR fog OR temperature OR forecast OR thunder OR lightning OR hail OR drizzle OR humidity OR cloudy OR heatwave OR cold OR freezing OR ice OR weer OR regen OR zonnig OR sneeuw OR wind OR mist OR temperatuur OR voorspelling OR onweer OR bliksem OR hagel OR motregen OR vochtigheid OR bewolkt OR hittegolf OR kou OR vriezen OR ijs) \
    (Amsterdam OR Haarlem OR Amstelveen OR Zaandam OR Almere OR Hoofddorp OR Diemen) \
    (lang:nl OR lang:en) -is:retweet"
)
MAX_RESULTS: int = 10


WEATHER_KEYWORDS = {
    "en": [
        "weather",
        "rain",
        "snow",
        "sunny",
        "cloudy",
        "storm",
        "wind",
        "fog",
        "temperature",
        "humidity",
        "forecast",
        "hail",
        "thunder",
        "lightning",
        "drizzle",
        "shower",
        "breeze",
        "heatwave",
        "cold",
        "hot",
        "warm",
        "freezing",
        "chilly",
        "climate",
        "conditions",
    ],
    "nl": [
        "weer",
        "regen",
        "sneeuw",
        "zonnig",
        "bewolkt",
        "storm",
        "wind",
        "mist",
        "temperatuur",
        "vochtigheid",
        "voorspelling",
        "hagel",
        "donder",
        "bliksem",
        "motregen",
        "bui",
        "bries",
        "hittegolf",
        "koud",
        "heet",
        "warm",
        "vriezen",
        "kil",
        "klimaat",
        "omstandigheden",
    ],
}


def retrieve_x_posts(
    search_query: str = SEARCH_QUERY, max_result: int = MAX_RESULTS
) -> Tuple[int, Any]:
    """
    Retrieves a list of tweets based on the search query and maximum results.
    Returns the social media ID and the list of tweets.
    """

    social_media = insert_social_media(
        search_query=search_query,
        start_time=datetime.now().isoformat(),
        end_time=(datetime.now() + timedelta(minutes=15)).isoformat(),
        logs=[],
    )

    social_media_id = social_media["social_media_id"]

    try:
        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Started retrieving X posts",
                "type": str(LogType.INFO),
            },
        )

        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=CLIENT_ID,
            consumer_secret=CLIENT_SECRET,
        )

        response: Any = client.search_recent_tweets(
            query=search_query,
            max_results=max_result,
            expansions=["geo.place_id", "author_id"],
            tweet_fields=["id", "text", "created_at", "geo"],
            user_fields=["username"],
            place_fields=[
                "geo",
                "country",
                "country_code",
                "full_name",
                "name",
                "place_type",
            ],
        )

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Retrieved X posts",
                "type": str(LogType.INFO),
            },
        )

        return social_media_id, response

    except tweepy.TooManyRequests as e:
        print("Rate Limit Exceeded:", str(e))

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": f"Rate Limit Exceeded: {str(e)}",
                "type": str(LogType.ERROR),
            },
        )

        return social_media_id, None

    except Exception as e:
        print(f"Error retrieving X posts: {e}")

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": f"Critical retrieving error: {str(e)}",
                "type": str(LogType.ERROR),
            },
        )

        return social_media_id, None


def process_x_posts(social_media_id: int, x_posts: Any) -> Optional[List]:
    """
    Processes the retrieved tweets to extract relevant information.
    """
    try:
        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Started processing X posts",
                "type": str(LogType.INFO),
            },
        )

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

                    if "geometry" in place.get("geo"):
                        if place.get("geo").get("geometry").get("type") == "Point":
                            coordinates = (
                                place.get("geo").get("geometry").get("coordinates")
                            )
                        elif place.get("geo").get("geometry").get("type") == "Polygon":
                            coordinates = (
                                place.get("geo")
                                .get("geometry")
                                .get("coordinates")[0][0]
                            )

                    elif "bbox" in place.get("geo"):
                        coordinates = [
                            (
                                place.get("geo").get("bbox")[1]
                                + place.get("geo").get("bbox")[3]
                            )
                            / 2,
                            (
                                place.get("geo").get("bbox")[0]
                                + place.get("geo").get("bbox")[2]
                            )
                            / 2,
                        ]

                    else:
                        coordinates = None

                    tweet_data.update(
                        {
                            "country": place.get("country"),
                            "country_code": place.get("country_code"),
                            "full_name": place.get("full_name"),
                            "name": place.get("name"),
                            "place_type": place.get("place_type"),
                            "coordinates": (
                                ",".join(map(str, coordinates)) if coordinates else None
                            ),
                        }
                    )

                processed_tweets.append(tweet_data)

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Processed X posts",
                "type": str(LogType.INFO),
            },
        )

        return processed_tweets

    except Exception as e:
        print(f"Error processing X posts: {e}, {x_posts}")

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": f"Critical processing error: {str(e)}",
                "type": str(LogType.ERROR),
            },
        )

        return None


def validate_x_posts(social_media_id: int, x_posts: List) -> Optional[List]:
    """
    Validates the processed tweets for any errors or inconsistencies.
    """

    def contains_weather_data(text: str) -> bool:
        """
        Checks if the text contains weather-related keywords in Dutch and English languages.
        """
        for _, keywords in WEATHER_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text.lower():
                    return True
        return False

    def filter_duplicate_posts(tweets: List[Dict]) -> List[Dict]:
        """
        Filters out tweets that already exist in the Post table by checking
        tweet IDs and text content using batch queries.
        """
        try:
            if not tweets:
                return []

            tweets_by_id = {}
            for tweet in tweets:
                tweet_id = tweet.get("id")
                tweet_text = tweet.get("text")
                if tweet_id not in tweets_by_id:
                    tweets_by_id[tweet_id] = set()
                tweets_by_id[tweet_id].add(tweet_text)

            duplicates = set()

            table = dynamodb_resource.Table("Post")
            index_name = "id-description-index"

            for tweet_id, descriptions in tweets_by_id.items():
                key_expr = Key("id").eq(tweet_id)

                if len(descriptions) > 1:
                    desc_list = list(descriptions)
                    filter_expr = Attr("description").is_in(desc_list)
                    response = table.query(
                        IndexName=index_name,
                        KeyConditionExpression=key_expr,
                        FilterExpression=filter_expr,
                    )
                else:
                    response = table.query(
                        IndexName=index_name, KeyConditionExpression=key_expr
                    )

                items = response.get("Items", [])
                for item in items:
                    duplicates.add((item.get("id"), item.get("description")))

            non_duplicates = [
                tweet
                for tweet in tweets
                if (tweet.get("id"), tweet.get("text")) not in duplicates
            ]

            return non_duplicates

        except Exception as e:
            print(f"Error filtering duplicate posts: {e}")
            return tweets

    try:
        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Started validation of X posts",
                "type": str(LogType.INFO),
            },
        )

        validated_tweets = []

        try:
            for tweet in x_posts:
                try:
                    if contains_weather_data(tweet["text"]):
                        validated_tweets.append(tweet)
                except KeyError as e:
                    print(f"Error processing tweet: Missing key {e}")
                except Exception as e:
                    print(f"Unexpected error processing tweet: {e}")
                    continue

            validated_tweets = filter_duplicate_posts(validated_tweets)
        except Exception as e:
            print(f"Error during tweet validation process: {e}")

            insert_log_to_social_media(
                social_media_id=social_media_id,
                log={
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Error during validation: {str(e)}",
                    "type": str(LogType.ERROR),
                },
            )

            return None

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Validation of X posts finished",
                "type": str(LogType.INFO),
            },
        )

        return validated_tweets

    except Exception as e:
        print(f"Critical error in validate_x_posts: {e}")

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": f"Critical validation error: {str(e)}",
                "type": str(LogType.ERROR),
            },
        )

        return None


def store_x_posts(social_media_id: int, x_posts: List) -> List:
    """
    Stores the validated tweets in a database or file for further analysis.
    """
    try:
        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Started storing X posts",
                "type": str(LogType.INFO),
            },
        )

        posts = []

        for tweet in x_posts:
            try:
                if tweet.get("full_name") is None or tweet.get("coordinates") is None:
                    location = None
                else:
                    location = {
                        "city": tweet.get("full_name", "Unknown"),
                        "longitude_latitude": tweet.get("coordinates", "Unknown"),
                    }

                post_item = insert_post(
                    social_media_id=social_media_id,
                    location=location,  # type: ignore
                    description=tweet.get("text", ""),
                    severity=tweet.get("severity", "unknown"),
                    weather_type=tweet.get("weather_type", "unknown"),
                    date=tweet.get("created_at", datetime.now()).isoformat(),
                    id=tweet["id"],
                )

                posts.append(post_item)

            except Exception as e:
                print(f"Error storing tweet {tweet['id']}: {e}")
                insert_log_to_social_media(
                    social_media_id=social_media_id,
                    log={
                        "timestamp": datetime.now().isoformat(),
                        "message": f"Error storing tweet {tweet['id']}: {str(e)}",
                        "type": str(LogType.ERROR),
                    },
                )

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Finished storing X posts",
                "type": str(LogType.INFO),
            },
        )

        return posts

    except Exception as e:
        print(f"Critical error in store_x_posts: {e}")

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": f"Critical storing error: {str(e)}",
                "type": str(LogType.ERROR),
            },
        )

        return None


def notify_x_posts(social_media_id: int, posts: List) -> None:
    """
    Notifies the user about the weather-related tweets.
    """
    try:
        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Started notifying X posts",
                "type": str(LogType.INFO),
            },
        )

        def extract_severity(tweet: Dict) -> Tuple[str, int]:
            """
            Extracts the severity score and category from the tweet.
            """
            pattern = r"(\w+)\s*\((\d+)/\d+\)"
            match = re.search(pattern, tweet["severity"])

            if not match:
                return "unknown", 0

            severity_label = match.group(1)
            severity_score = int(match.group(2))

            return severity_label, severity_score

        severe_tweets = []

        # Here is basic checking of the severity of the weather
        # In future it should be extended to more complex analysis
        for post in posts:
            label, score = extract_severity(post)

            if label == "unknown" and score == 0 or post["weather_type"] == "unknown":
                continue

            if score > 5 or label == "high" or label == "extreme":
                severe_tweets.append(post)

        if len(severe_tweets) == 0:
            print("No severe weather tweets found.")
            return None

        severe_tweets = sorted(
            severe_tweets, key=lambda x: extract_severity(x)[1], reverse=True
        )

        link_part = ",".join([str(post["post_id"]) for post in posts])

        hashed_link_part = encrypt_data(link_part).decode()

        print(severe_tweets)

        print(severe_tweets[0].get("weather_type"), hashed_link_part)

        # Send email to user
        send_email(
            weather_type=severe_tweets[0].get("weather_type"),
            date_time=datetime.now().isoformat(),
            location="Amsterdam",
            tweet_link=f"http://localhost:5500/link.html?data={hashed_link_part}",
        )

        print(f"http://localhost:5500/link.html?data={hashed_link_part}")

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": "Finished notifying X posts",
                "type": str(LogType.INFO),
            },
        )

        return None

    except Exception as e:
        print(f"Critical error in notify_x_posts: {e}")

        insert_log_to_social_media(
            social_media_id=social_media_id,
            log={
                "timestamp": datetime.now().isoformat(),
                "message": f"Critical notification error: {str(e)}",
                "type": str(LogType.ERROR),
            },
        )

        return None
