import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.database import get_db
from shared.kafka_consumer import create_consumer
from shared.kafka_producer import publish_event
from bson import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("review_worker")


def process_review_created(data):
    db = get_db()
    review_id = data.get("review_id")
    if not review_id:
        return
    # Mark review as processed
    db.reviews.update_one(
        {"_id": ObjectId(review_id)},
        {"$set": {"status": "processed"}},
    )
    logger.info(f"Processed review.created: {review_id}")
    publish_event("booking.status", {
        "action": "review_processed", "review_id": review_id, "status": "completed",
    })


def process_review_updated(data):
    review_id = data.get("review_id")
    logger.info(f"Processed review.updated: {review_id}")
    publish_event("booking.status", {
        "action": "review_updated", "review_id": review_id, "status": "completed",
    })


def process_review_deleted(data):
    review_id = data.get("review_id")
    logger.info(f"Processed review.deleted: {review_id}")
    publish_event("booking.status", {
        "action": "review_deleted", "review_id": review_id, "status": "completed",
    })


HANDLERS = {
    "review.created": process_review_created,
    "review.updated": process_review_updated,
    "review.deleted": process_review_deleted,
}


def main():
    logger.info("Review Worker starting...")
    consumer = create_consumer(
        topics=["review.created", "review.updated", "review.deleted"],
        group_id="review-worker-group",
    )
    logger.info("Review Worker listening for events...")
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
