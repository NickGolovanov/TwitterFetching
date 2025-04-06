from unittest.mock import MagicMock

class MockDynamoDB:
    def __init__(self):
        self.tables = {}

    def Table(self, table_name):
        if table_name not in self.tables:
            self.tables[table_name] = MagicMock()
        return self.tables[table_name]

dynamodb = MockDynamoDB()
dynamodb_client = MagicMock()
dynamodb_resource = MockDynamoDB() 