import boto3
import os
import threading
import sys
from datetime import datetime
from pathlib import Path

class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()
    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

base_path = "./deploy/"
space_name = 'raspbian-store'

key_id = os.environ.get('boto_id')
key_secret = os.environ.get('boto_secret')

# Generate filenames for uploading
today = datetime.today()
file_date = today.strftime('%Y-%m-%d') # 2019-01-03
file_base_name = f'image_{file_date}-Raspbian'
lite_file_name = f'{file_base_name}-lite.zip'
norm_file_name = f'{file_base_name}.zip'
full_file_name = f'{file_base_name}-full.zip'

# check that all files exist

files = []

for file_name in [lite_file_name, norm_file_name, full_file_name]:
    file_path = f'{base_path}{file_name}'
    file = Path(file_path)

    # if the file exists
    if Path(file_path).is_file():
        files.append({
            'name': file_name,
            'path': file_path
            }) # add it to the path
    else:
        raise Exception(f'{file_path} doesn\'t exist')

session = boto3.session.Session()
client = session.client('s3',
                        region_name='sfo2',
                        endpoint_url='https://sfo2.digitaloceanspaces.com',
                        aws_access_key_id=key_id,
                        aws_secret_access_key=key_secret)

for file in files:
    file_path = file.get('path', "")
    file_name = file.get('name', "")
    print(f"Uploading {file_name}...")
    client.upload_file(
        file_path,
        space_name,
        file_name,
        Callback=ProgressPercentage(file_path)
    )