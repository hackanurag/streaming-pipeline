# src/utils/helpers.py
import logging
from datetime import datetime
import json

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def parse_timestamp(timestamp_str):
    return datetime.fromisoformat(timestamp_str)

def serialize_to_json(data):
    return json.dumps(data, default=str)

def deserialize_from_json(json_str):
    return json.loads(json_str)