import json
import boto3
import requests
import urllib.parse
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError

# Initialize DynamoDB client
# this is a new comment
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('weather_data_table')  # Replace with your actual DynamoDB table name

def get_secret():

    secret_name = "WEATHER_API_KEY"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret_string = get_secret_value_response['SecretString']
    if secret_string:
        # Parse the secret value (assuming it's a JSON string)
        secret = json.loads(secret_string)
        return secret['API_KEY']  # Assuming your secret is stored as {"apiKey": "your-api-key"}
    else:
        raise ValueError("SecretString is empty or not found")
    

def lambda_handler(event, context):
    print("Starting Lambda function...")  # Debug log
    
    api_key = get_secret()
    
    # Define the API URL
    api_url = f'https://api.tomorrow.io/v4/weather/realtime?location=College%20park&units=metric&apikey={api_key}'
    
    try:
        # Call the weather API
        print("Calling weather API...")  # Debug log
        response = requests.get(api_url)
        data = response.json()
        print("API call successful, data received.")  # Debug log
        
        # Generate a unique timestamp
        timestamp = datetime.now().isoformat()  # ISO format for unique timestamp
        
        # Extract relevant fields from the API response
        values = data['data']['values']  # Ensure this is defined correctly
        
        # Helper function to convert float to Decimal for DynamoDB compatibility
        def to_decimal(value):
            return Decimal(str(value)) if isinstance(value, float) else value

        # Prepare the item dictionary with Decimal conversion for float values
        item = {
            'timestamp': timestamp,
            'temperature': to_decimal(values.get('temperature')),
            'temperature_si': to_decimal(values.get('temperature-si')),
            'temperature_us': to_decimal(values.get('temperature-us')),
            'temperature_apparent': to_decimal(values.get('temperatureApparent')),
            'dew_point': to_decimal(values.get('dewPoint')),
            'dew_point_si': to_decimal(values.get('dewpoint-si')),
            'dew_point_us': to_decimal(values.get('dewpoint-us')),
            'humidity': to_decimal(values.get('humidity')),
            'wind_speed': to_decimal(values.get('windSpeed')),
            'wind_speed_si': to_decimal(values.get('wind-speed-si')),
            'wind_speed_us': to_decimal(values.get('wind-speed-us')),
            'wind_direction': to_decimal(values.get('windDirection')),
            'wind_gust': to_decimal(values.get('windGust')),
            'pressure_surface_level': to_decimal(values.get('pressureSurfaceLevel')),
            'pressure_sea_level': to_decimal(values.get('pressureSeaLevel')),
            'precipitation_intensity': to_decimal(values.get('precipitationIntensity')),
            'precipitation_si': to_decimal(values.get('precip-si')),
            'precipitation_us': to_decimal(values.get('precip-us')),
            'rain_intensity': to_decimal(values.get('rainIntensity')),
            'freezing_rain_intensity': to_decimal(values.get('freezingRainIntensity')),
            'snow_intensity': to_decimal(values.get('snowIntensity')),
            'sleet_intensity': to_decimal(values.get('sleetIntensity')),
            'precipitation_probability': to_decimal(values.get('precipitationProbability')),
            'precipitation_type': to_decimal(values.get('precipitationType')),
            'rain_accumulation': to_decimal(values.get('rainAccumulation')),
            'snow_accumulation': to_decimal(values.get('snowAccumulation')),
            'snow_accumulation_lwe': to_decimal(values.get('snowAccumulationLwe')),
            'snow_depth': to_decimal(values.get('snowDepth')),
            'sleet_accumulation': to_decimal(values.get('sleetAccumulation')),
            'sleet_accumulation_lwe': to_decimal(values.get('sleetAccumulationLwe')),
            'ice_accumulation': to_decimal(values.get('iceAccumulation')),
            'ice_accumulation_lwe': to_decimal(values.get('iceAccumulationLwe')),
            'sunrise_time': values.get('sunriseTime'),
            'sunset_time': values.get('sunsetTime'),
            'visibility': to_decimal(values.get('visibility')),
            'visibility_si': to_decimal(values.get('visibility-si')),
            'visibility_us': to_decimal(values.get('visibility-us')),
            'cloud_cover': to_decimal(values.get('cloudCover')),
            'cloud_base': to_decimal(values.get('cloudBase')),
            'cloud_ceiling': to_decimal(values.get('cloudCeiling')),
            'moon_phase': to_decimal(values.get('moonPhase')),
            'uv_index': to_decimal(values.get('uvIndex')),
            'uv_health_concern': to_decimal(values.get('uvHealthConcern')),
            'gdd_10_to_30': to_decimal(values.get('gdd10To30')),
            'gdd_10_to_31': to_decimal(values.get('gdd10To31')),
            'gdd_08_to_30': to_decimal(values.get('gdd08To30')),
            'gdd_03_to_25': to_decimal(values.get('gdd03To25')),
            'evapotranspiration': to_decimal(values.get('evapotranspiration')),
            'weather_code_full_day': values.get('weatherCodeFullDay'),
            'weather_code_day': values.get('weatherCodeDay'),
            'weather_code_night': values.get('weatherCodeNight'),
            'weather_code': values.get('weatherCode'),
            'thunderstorm_probability': to_decimal(values.get('thunderstormProbability')),
            'ez_heat_stress_index': to_decimal(values.get('ezHeatStressIndex'))
        }
        
        # Store data in DynamoDB
        table.put_item(Item=item)
        print("Data successfully saved to DynamoDB.")  # Debug log
        
        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps('Data saved to DynamoDB successfully')
        }
    
    except Exception as e:
        print("Error occurred:", e)  # Debug log for error
        return {
            'statusCode': 500,
            'body': json.dumps('Error saving data')
        }
