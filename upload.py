import boto3
import os
import threading
import sys

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


session = boto3.session.Session()
client = session.client('s3',
                        region_name='sfo2',
                        endpoint_url='https://sfo2.digitaloceanspaces.com',
                        aws_access_key_id=key_id,
                        aws_secret_access_key=key_secret)

client.upload_file('./deploy/image_2018-12-31-Raspbian-lite.zip',  # Path to local file
                   space_name,  # Name of Space
                   'image_2018-12-31-Raspbian-lite.zip', # Name for remote file
                   Callback=ProgressPercentage("./deploy/image_2018-12-31-Raspbian-lite.zip"))


