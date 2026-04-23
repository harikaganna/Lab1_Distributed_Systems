import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.database import get_db
from shared.kafka_consumer import create_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user_worker")


def process_user_created(data):
    logger.info(f"Processed user.created: {data.get('user_id')} - {data.get('email')}")


def process_user_updated(data):
    logger.info(f"Processed user.updated: {data.get('user_id')}")


HANDLERS = {
    "user.created": process_user_created,
    "user.updated": process_user_updated,
}


def main():
    logger.info("User Worker starting...")
    consumer = create_consumer(
        topics=["user.created", "user.updated"],
        group_id="user-worker-group",
    )
    logger.info("User Worker listening for events...")
    for message in consumer:
        topic = message.topic
        data = message.value
        logger.info(f"Received {topic}: {data}")
        handler = HANDLERS.get(topic)
        if handler:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error processing {topic}: {e}")


if __name__ == "__main__":
    main()
