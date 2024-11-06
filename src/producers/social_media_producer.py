# src/producers/social_media_producer.py
from kafka import KafkaProducer
import json
import time
from datetime import datetime
import random
from textblob import TextBlob

class SocialMediaProducer:
    def __init__(self, bootstrap_servers):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
    def generate_social_media_data(self):
        platforms = ['twitter', 'facebook', 'instagram']
        sentiments = ['positive', 'negative', 'neutral']
        
        data = {
            'platform': random.choice(platforms),
            'user_id': random.randint(1000, 9999),
            'text': f"Sample social media post {random.randint(1, 1000)}",
            'timestamp': datetime.now().isoformat(),
            'engagement': random.randint(0, 1000)
        }
        
        # Perform sentiment analysis
        blob = TextBlob(data['text'])
        data['sentiment_score'] = blob.sentiment.polarity
        
        return data
    
    def start_producing(self):
        while True:
            data = self.generate_social_media_data()
            self.producer.send('social_media', value=data)
            time.sleep(1)