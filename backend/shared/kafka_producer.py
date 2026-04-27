import json
import logging
from kafka import KafkaProducer
from .config import KAFKA_BOOTSTRAP_SERVERS

logger = logging.getLogger(__name__)
_producer = None


def get_producer():
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                retries=3,
            )
        except Exception as e:
            logger.error(f"Kafka producer init failed: {e}")
            return None
    return _producer


def publish_event(topic: str, data: dict):
    producer = get_producer()
    if producer:
        try:
            producer.send(topic, value=data)
            producer.flush(timeout=3)
            logger.info(f"Published to {topic}: {data.get('action', 'unknown')}")
        except Exception as e:
            logger.error(f"Kafka publish failed: {e}")
    else:
        logger.warning(f"Kafka unavailable, skipping event: {topic}")
