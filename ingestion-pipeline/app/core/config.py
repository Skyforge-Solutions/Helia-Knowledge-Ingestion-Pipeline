from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# RabbitMQ Configuration
RABBIT_USER = os.getenv("RABBIT_USER", "myuser")
RABBIT_PASS = os.getenv("RABBIT_PASS", "mysecurepassword")
RABBIT_HOST = os.getenv("RABBIT_HOST", "34.47.190.56")
RABBIT_PORT = os.getenv("RABBIT_PORT", "5672")

# Construct Broker URL
BROKER_URL = f"amqp://{RABBIT_USER}:{RABBIT_PASS}@{RABBIT_HOST}:{RABBIT_PORT}//"

# Print configuration for verification (remove in production)
if __name__ == "__main__":
    print(f"RabbitMQ Configuration:")
    print(f"User: {RABBIT_USER}")
    print(f"Host: {RABBIT_HOST}")
    print(f"Port: {RABBIT_PORT}")
    print(f"Broker URL: {BROKER_URL}")
