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
            "id": 1897362946738806855,
            "text": "https://t.co/VJOfR9slWj",
            "created_at": datetime.datetime(
                2025, 3, 5, 19, 5, 52, tzinfo=datetime.timezone.utc
            ),
            "username": "TaWeststrate",
            "country": "Nederland",
            "country_code": "NL",
            "full_name": "Rotterdam, Nederland",
            "name": "Rotterdam",
            "place_type": "city",
        },
        {
            "id": 1897299418052956288,
            "text": "https://t.co/uBldDMfLsp",
            "created_at": datetime.datetime(
                2025, 3, 5, 14, 53, 26, tzinfo=datetime.timezone.utc
            ),
            "username": "CASTAeroSafe",
        },
        {
            "id": 1897296691981963289,
            "text": "That how I’m #unpack my boat every time when it’s a good weather in Amsterdam. https://t.co/PA2Wvq8t6x",
            "created_at": datetime.datetime(
                2025, 3, 5, 14, 42, 36, tzinfo=datetime.timezone.utc
            ),
            "username": "CryptoYDao",
        },
        {
            "id": 1897290780831846469,
            "text": "That how I’m #unpack my boat Avery time when it’s a good weather in Amsterdam. https://t.co/tEuikmd6UX",
            "created_at": datetime.datetime(
                2025, 3, 5, 14, 19, 6, tzinfo=datetime.timezone.utc
            ),
            "username": "CryptoYDao",
        },
        {
            "id": 1897288350072983565,
            "text": "Even the birds seem happy that the weather is improving in Amsterdam's Red Light District. \n\nExciting times ahead: 3 million tourists from around the world are expected to visit this district, eager to discover what lies behind Amsterdam's \"red\" windows.\n\nI’ll need to find a new… https://t.co/SyAn5GBkSx https://t.co/T05sVVbJGG",
            "created_at": datetime.datetime(
                2025, 3, 5, 14, 9, 27, tzinfo=datetime.timezone.utc
            ),
            "username": "PascalMurasira",
        },
        {
            "id": 1897282901794021517,
            "text": "A beautiful sunny day in Amsterdam https://t.co/qLfk88g02q",
            "created_at": datetime.datetime(
                2025, 3, 5, 13, 47, 48, tzinfo=datetime.timezone.utc
            ),
            "username": "paxtondom",
        },
        {
            "id": 1897274227398729996,
            "text": "Quick boat tour in Amsterdam before catching my flight this evening! Decent weather for it too. https://t.co/cnzIeZcgEb",
            "created_at": datetime.datetime(
                2025, 3, 5, 13, 13, 20, tzinfo=datetime.timezone.utc
            ),
            "username": "Mosh108",
        },
        {
            "id": 1897236579598655499,
            "text": "I expected it to be a windy &amp; rainy night in Rotterdam …. but it’s sunny, 12 degrees and very little wind at kickoff today. Forza Inter!!",
            "created_at": datetime.datetime(
                2025, 3, 5, 10, 43, 44, tzinfo=datetime.timezone.utc
            ),
            "username": "ArnautovicArmy",
        },
        {
            "id": 1897229839670898852,
            "text": "Peep the pic. Whole room looks plugged into X through headphones 😅 Secret meetup? Gonzo mode on. In sunny Amsterdam with crypto mom @cryptocanal &amp; frens—building the agent-powered future. https://t.co/iqOdRISpy0",
            "created_at": datetime.datetime(
                2025, 3, 5, 10, 16, 57, tzinfo=datetime.timezone.utc
            ),
            "username": "leealabs",
        },
        {
            "id": 1897041565367066661,
            "text": "Netherlands: Runway at Amsterdam Schiphol Airport to close two hours on sunny mornings amid solar panel issues https://t.co/WgwKglooGt",
            "created_at": datetime.datetime(
                2025, 3, 4, 21, 48, 49, tzinfo=datetime.timezone.utc
            ),
            "username": "avsec_pro",
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
    USE_EXAMPLE_TWEETS = True

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
    app.run(debug=True)
