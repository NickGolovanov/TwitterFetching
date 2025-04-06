from cryptography.fernet import Fernet

AWS_REGION = "us-east-1"
HASHING_SECRET = Fernet.generate_key() 