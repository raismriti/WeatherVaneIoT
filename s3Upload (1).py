import boto3
import os
from botocore.exceptions import NoCredentialsError

# Create an S3 access object
s3 = boto3.client("s3")

def upload_to_s3(local_file_path, bucket_name, s3_file_name):
    try:
        # Upload the file
        s3.upload_file(local_file_path, bucket_name, s3_file_name)
        print(f"File '{local_file_path}' uploaded successfully to '{bucket_name}' as '{s3_file_name}'")
    except FileNotFoundError:
        print(f"The file '{local_file_path}' was not found.")
    except NoCredentialsError:
        print("Credentials not available or incorrect.")

def find_and_upload_csv(folder_path, bucket_name, s3_folder_path, csv_filename):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file == csv_filename:
                local_file_path = os.path.join(root, file)
                s3_file_path = os.path.join(s3_folder_path, file)
                upload_to_s3(local_file_path, bucket_name, s3_file_path)

# Example usage
local_folder_path = 'C:/Users/nkp180005/Desktop/Classes/CE4201-IoT/Project'
bucket_name = 'weathersys'
s3_folder_path = 'weatherData/'
csv_filename = 'PassengerSenseTest.csv'

find_and_upload_csv(local_folder_path, bucket_name, s3_folder_path, csv_filename)
