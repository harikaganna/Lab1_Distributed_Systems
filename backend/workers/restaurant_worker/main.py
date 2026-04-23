import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.database import get_db
from shared.kafka_consumer import create_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("restaurant_worker")


def process_restaurant_created(data):
    logger.info(f"Processed restaurant.created: {data.get('restaurant_id')} - {data.get('name')}")


def process_restaurant_updated(data):
    logger.info(f"Processed restaurant.updated: {data.get('restaurant_id')}")


def process_restaurant_claimed(data):
    logger.info(f"Processed restaurant.claimed: {data.get('restaurant_id')} by owner {data.get('owner_id')}")


HANDLERS = {
    "restaurant.created": process_restaurant_created,
    "restaurant.updated": process_restaurant_updated,
    "restaurant.claimed": process_restaurant_claimed,
}


def main():
    logger.info("Restaurant Worker starting...")
    consumer = create_consumer(
        topics=["restaurant.created", "restaurant.updated", "restaurant.claimed"],
        group_id="restaurant-worker-group",
    )
    logger.info("Restaurant Worker listening for events...")
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
