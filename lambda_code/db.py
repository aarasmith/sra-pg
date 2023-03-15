import psycopg2
import boto3
import json

def get_connection(search_path, secret_id):
    
    client = boto3.client('secretsmanager')
    connect_creds = json.loads(client.get_secret_value(SecretId=secret_id)['SecretString'])
    
    return psycopg2.connect(
            host=connect_creds['host'],
            database=connect_creds['database'],
            user=connect_creds['username'],
            password=connect_creds['password'],
            port=connect_creds['port'],
            options=f"-c search_path={search_path}"
        )
