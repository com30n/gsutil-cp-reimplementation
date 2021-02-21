# Imports the Google Cloud client library
import os
from typing import List

from google.cloud import storage


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


def get_bucket_files_list(bucket_name: str, storage_client: storage.Client, bucket_path: str = '') -> List[str]:
    bucket_path = bucket_path.lstrip('/')
    return [x.name for x in storage_client.list_blobs(bucket_or_name=bucket_name, prefix=bucket_path)]


def download_files_from_bucket(bucket_name: str, storage_client: storage.Client, bucket_path: str = '',
                               local_path: str = '/tmp') -> List[str]:
    remote_files_list = get_bucket_files_list(bucket_name, storage_client, bucket_path)
    print(remote_files_list)
    for file_name in remote_files_list:
        file_name = os.path.join(local_path, file_name)
        # file_content =
        with open(file_name, 'wb') as f:
            f.write()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Instantiates a client
    storage_client = storage.Client()

    # The name for the new bucket
    bucket_name = "online-infra-engineer-test"
    bucket = storage_client.get_bucket(bucket_name)
    blobs_list = bucket.list_blobs()
    blobs = []
    local_path = '/tmp'
    for blob in blobs_list:
        download_path = os.path.join(local_path, blob.name)
        if not os.path.exists(os.path.dirname(download_path)):
            os.makedirs(os.path.dirname(download_path))
        blob = bucket.blob(blob.name)
        blob.download_to_filename(download_path)
