from dotenv import load_dotenv

from data import (
    data_pipeline,
)
from db import create_main_tables_if_not_exist, dynamodb_client


load_dotenv()


# main application loop
def main():
    create_main_tables_if_not_exist(dynamodb_client)

    data_pipeline()


# entry point for the application
if __name__ == "__main__":
    main()
