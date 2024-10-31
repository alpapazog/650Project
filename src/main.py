import os
import json
import boto3
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("WEATHERSTACK_API_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
s3_client = boto3.client('s3')

def respond_json(body, status_code):
    return {
        'statusCode': status_code,
        'body': json.dumps(body)
    }

def lambda_handler(event, context):
    city = event['pathParameters']['city']
    endpoint = 'http://api.weatherstack.com/current'
    
    try:
        response = requests.get(endpoint, params={'access_key': API_KEY, 'query': city})
        data = response.json()
        
        if 'error' in data:
            return respond_json({'error': data['error']['info']}, 400)

        weather_data = {
            'city': data['location']['name'],
            'temperature': data['current']['temperature'],
            'textWeather': data['current']['weather_descriptions'],
        }

        # Store weather data in S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"weather_data/{city}.json",
            Body=json.dumps(weather_data)
        )

        return respond_json(weather_data, 200)
    
    except Exception as e:
        print(e)
        return respond_json({'error': 'An error occurred while fetching weather data.'}, 500)
