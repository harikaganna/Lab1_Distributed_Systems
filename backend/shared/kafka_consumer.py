import json
import logging
from kafka import KafkaConsumer
from .config import KAFKA_BOOTSTRAP_SERVERS

logger = logging.getLogger(__name__)


def create_consumer(topics: list, group_id: str):
    return KafkaConsumer(
        *topics,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
