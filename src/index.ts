import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import axios from 'axios';
import { APIGatewayEvent } from 'aws-lambda';

const s3 = new S3Client({ region: 'us-east-2' }); // e.g., 'us-east-1'
const BUCKET_NAME = 'my-weather-data-650';

export const handler = async (event:APIGatewayEvent) => {
    try {
        // Step 1: Fetch data from the JSONPlaceholder API
        const response = await axios.get('https://jsonplaceholder.typicode.com/posts');
        const data = response.data;

        // Step 2: Prepare data for S3
        const objectKey = `data/posts-${Date.now()}.json`; // Generate a unique key
        const params = {
            Bucket: BUCKET_NAME,
            Key: objectKey,
            Body: JSON.stringify(data),
            ContentType: 'application/json'
        };

        // Step 3: Upload data to S3
        await s3.send(new PutObjectCommand(params));
        
        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Data uploaded to S3 successfully', objectKey }),
        };
    } catch (error) {
        console.error('Error fetching data or uploading to S3:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Failed to fetch data or upload to S3' }),
        };
    }
};
