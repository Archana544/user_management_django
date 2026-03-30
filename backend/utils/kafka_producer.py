import json
import os
from confluent_kafka import Producer
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

_producer = None

def get_producer():
    global _producer
    if _producer is None:
        _producer = Producer({
            'bootstrap.servers': settings.KAFKA_BROKER,
            'client.id': 'ai-doc-platform',
        })
    return _producer


def publish_event(topic: str, event: dict):
    """
    Publish any event to a Kafka topic.
    Call this wherever you need to emit events.
    """
    try:
        producer = get_producer()
        producer.produce(
            topic=topic,
            value=json.dumps(event).encode('utf-8'),
            callback=_delivery_callback
        )
        producer.flush()
        logger.info(f"Event published to {topic}: {event}")

    except Exception as e:
        logger.error(f"Kafka publish failed: {str(e)}")



def _delivery_callback(err, msg):
    if err:
        logger.error(f"Kafka delivery failed: {err}")
    else:
        logger.info(f"Delivered to {msg.topic()} [{msg.partition()}]")

def publish_document_uploaded(document_id: int, user_id: int):
    publish_event(settings.KAFKA_TOPIC_DOCUMENTS, {
        'event_type': 'DOCUMENT_UPLOADED',
        'document_id': document_id,
        'user_id': user_id,
    })

def publish_document_processed(document_id: int, user_id: int):
    publish_event(settings.KAFKA_TOPIC_DOCUMENTS, {
        'event_type': 'DOCUMENT_PROCESSED',
        'document_id': document_id,
        'user_id': user_id,
    })

def publish_document_failed(document_id: int, user_id: int, error: str):
    publish_event(settings.KAFKA_TOPIC_DOCUMENTS, {
        'event_type': 'DOCUMENT_FAILED',
        'document_id': document_id,
        'user_id': user_id,
        'error': error
    })