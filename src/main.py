import os
from dotenv import load_dotenv

from data import process_x_posts, retrieve_x_posts
from db import dynamodb_client, create_main_tables_if_not_exist

load_dotenv()


# main application loop
def main():
    # create_main_tables_if_not_exist(dynamodb_client)

    x_posts_unprocessed = retrieve_x_posts()

    print("=====================================")

    print("unprocessed: ", x_posts_unprocessed)

    print("=====================================")

    x_posts = process_x_posts(x_posts_unprocessed)

    print("processed: ", x_posts)

    print("=====================================")


# entry point for the application
if __name__ == "__main__":
    main()
