# src/producers/ecommerce_producer.py
from kafka import KafkaProducer
import json
import time
from datetime import datetime
import random

class EcommerceProducer:
    def __init__(self, bootstrap_servers):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
    def generate_ecommerce_data(self):
        events = ['page_view', 'add_to_cart', 'purchase', 'remove_from_cart']
        categories = ['electronics', 'clothing', 'books', 'home']
        
        data = {
            'user_id': random.randint(1000, 9999),
            'event_type': random.choice(events),
            'product_id': random.randint(1, 1000),
            'category': random.choice(categories),
            'timestamp': datetime.now().isoformat(),
            'session_id': f"session_{random.randint(1000, 9999)}",
            'value': round(random.uniform(10, 1000), 2)
        }
        
        return data
    
    def start_producing(self):
        while True:
            data = self.generate_ecommerce_data()
            self.producer.send('ecommerce', value=data)
            time.sleep(0.5)