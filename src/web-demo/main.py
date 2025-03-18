import datetime
from typing import Any
from flask import Flask, render_template, request
import tweepy
import os
from dotenv import load_dotenv
import time

from db import connect_to_dynamodb_table, insert_data, make_post_item

load_dotenv()

app = Flask(__name__)

bearer_token = os.environ.get("TWITTER_API_BEARER")
consumer_key = os.environ.get("TWITTER_CLEINT_ID")
consumer_secret = os.environ.get("TWITTER_CLIENT_SECRET")
access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
access_secret = os.environ.get("TWITTER_ACCESS_SECRET_TOKEN")

client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_secret,
)


def get_example_tweets():
    return [
        {
            "id": 1897951629413917183,
            "text": "A beautiful sunny morning in Amsterdam 😎 https://t.co/68gzlpEQJY",
            "created_at": datetime.datetime(
                2025, 3, 7, 10, 5, 5, tzinfo=datetime.timezone.utc
            ),
            "username": "paxtondom",
        },
        {
            "id": 1897933285747003820,
            "text": "Amsterdam with good weather is such a beautiful city🫶",
            "created_at": datetime.datetime(
                2025, 3, 7, 8, 52, 11, tzinfo=datetime.timezone.utc
            ),
            "username": "coralaespa_m",
        },
        {
            "id": 1897916520656748904,
            "text": "loving Amsterdam’s weather for now.",
            "created_at": datetime.datetime(
                2025, 3, 7, 7, 45, 34, tzinfo=datetime.timezone.utc
            ),
            "username": "trvpsxxl_",
        },
        {
            "id": 1897905376403898511,
            "text": "Solar panels blind pilots approaching Amsterdam Schiphol; runway closed for two hours when sunny https://t.co/VxABZcf0Nk via @aviation24_be",
            "created_at": datetime.datetime(
                2025, 3, 7, 7, 1, 17, tzinfo=datetime.timezone.utc
            ),
            "username": "ranchette1",
        },
        {
            "id": 1897861700315234806,
            "text": "˚₊‧꒰ა ☆ ໒꒱ ‧₊˚ AESPA takes Paris by storm! The highly anticipated 2024-25 AESPA LIVE TOUR – SYNK : PARALLEL LINE – in Paris and Amsterdam delivers an electrifying night filled with breathtaking performances, stunning visuals, and unparalleled energy. https://t.co/MNar1w3GzE",
            "created_at": datetime.datetime(
                2025, 3, 7, 4, 7, 44, tzinfo=datetime.timezone.utc
            ),
            "username": "wirntr",
        },
        {
            "id": 1897800182957584649,
            "text": "i have 5 picks:\n\n1. london n2 for castles crumbling w/ hayley\n\n2. amsterdam n3 for the sweeter than fiction x holy ground and mary's song\n\n3. edinburgh n2 for crazier\n\n4. whichever nashville night was the rain show with wcs and mine\n\n5. the london night with holly humberstone https://t.co/xKpr07uGLQ",
            "created_at": datetime.datetime(
                2025, 3, 7, 0, 3, 17, tzinfo=datetime.timezone.utc
            ),
            "username": "laurathestork_",
        },
        {
            "id": 1897733497726325038,
            "text": "Huidig weer in Rotterdam https://t.co/ZcjBBTGoc9",
            "created_at": datetime.datetime(
                2025, 3, 6, 19, 38, 18, tzinfo=datetime.timezone.utc
            ),
            "username": "Piet_Heyn",
            "country": "Nederland",
            "country_code": "NL",
            "full_name": "Rotterdam, Nederland",
            "name": "Rotterdam",
            "place_type": "city",
        },
        {
            "id": 1897730441756786752,
            "text": "https://t.co/vwWRkCDTDM",
            "created_at": datetime.datetime(
                2025, 3, 6, 19, 26, 10, tzinfo=datetime.timezone.utc
            ),
            "username": "NickBackman4",
        },
        {
            "id": 1897662710189277540,
            "text": "The weather in Amsterdam is gorgeous 👍🇱🇺☘️🥝💚 https://t.co/GMk71WP40B",
            "created_at": datetime.datetime(
                2025, 3, 6, 14, 57, 1, tzinfo=datetime.timezone.utc
            ),
            "username": "smuWhite",
        },
    ]


def get_twitter_responce(query, max_results=5):
    try:
        tweets: Any = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            expansions=["geo.place_id", "author_id"],
            tweet_fields=["id", "text", "created_at", "geo"],
            user_fields=["username"],
            place_fields=["country", "country_code", "full_name", "name", "place_type"],
        )

        print("Tweets: ", tweets)

        return tweets

    except tweepy.TooManyRequests as e:
        reset_time = int(e.response.headers.get("x-rate-limit-reset", time.time()))
        current_time = int(time.time())
        wait_time = reset_time - current_time

        print(
            f"{datetime.datetime.now()} Rate limit exceeded. Try again in {wait_time} seconds."
        )
        return None


def process_twitter_responce(response):
    print("Response: ", response)

    try:
        tweets = response.data if response.data else []

        includes = response.includes if response.includes else {}

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
        print(f"Error processing response: {e}, {response}")
        return []


@app.route("/", methods=["GET", "POST"])
def home():
    USE_EXAMPLE_TWEETS = False

    tweets = []

    if USE_EXAMPLE_TWEETS:
        tweets = get_example_tweets()

    queries = [
        "(weather OR forecast OR rain OR sunny OR storm OR temperature) (Amsterdam OR Rotterdam) -is:retweet -is:reply",
        "(storm OR snow OR heatwave OR flood OR wind OR hail) (Amsterdam OR Rotterdam) -is:retweet -is:reply",
        "(cold OR hot OR freezing OR warm OR 'bad weather' OR 'good weather') (Amsterdam OR Rotterdam) -is:retweet -is:reply",
    ]
    # query = "weather Netherlands -is:retweet -is:reply -has:links"

    if request.method == "POST":
        query = request.form.get("query")
        response = get_twitter_responce(query, max_results=10) or []

        tweets = process_twitter_responce(response)

        print("Tweets: ", tweets)

        table = connect_to_dynamodb_table("posts")

        insert_data(
            table,
            items=[
                make_post_item(
                    int(tweet["id"]),
                    tweet["text"],
                    tweet["created_at"],
                    str(tweet["id"]),
                )
                for tweet in tweets
            ],
        )

    tweets = [
        f"https://twitter.com/{tweet["username"]}/status/{tweet["id"]}"
        for tweet in tweets
    ]

    return render_template("index.html", tweets=tweets, queries=queries)


@app.route("/db", methods=["GET"])
def db():
    try:
        table = connect_to_dynamodb_table("posts")

        if table is None:
            return render_template("db.html", posts=[])

        response = table.scan()

        items = response.get("Items", [])
    except Exception as e:
        items = []
        print(f"Error fetching data: {e}")

    return render_template("db.html", posts=items)


if __name__ == "__main__":
    app.run(port=3333, debug=True)
