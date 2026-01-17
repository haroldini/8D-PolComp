
import os
import logging

from application import create_app
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)


app = create_app()


# Run the application
if __name__ == "__main__":
    debug = (os.getenv("ENVIRONMENT", "DEV") == "DEV")
    app.run(
        host = "127.0.0.1",
        port = 5001,
        debug = debug
        )
