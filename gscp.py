#!/usr/bin/env python3

# Imports the Google Cloud client library
import os
import sys
import argparse
from urllib import parse
from typing import List, Dict, Optional, Union, Tuple

from google.cloud import storage
from google.api_core.exceptions import NotFound

STORAGE_CLIENT = storage.Client()


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


def validate_bucket_url(url: str) -> bool:
    """ Just simple validation which only checks if the bucket url has a url schema 'gs://' """

    if url.startswith('gs://'):
        return True
    return False


def get_bucket_name_from_url(url: str) -> Union[str, bool]:
    """
    If the bucket url is valid, and the bucket is exist, return the bucket name. In the other case return False.
    """

    if not validate_bucket_url(url):
        return False

    bucket_name = parse.urlparse(url).netloc

    if not STORAGE_CLIENT.get_bucket(bucket_name):
        return False

    return bucket_name


def _upload_to_bucket(bucket: storage.bucket.Bucket, src_path: str, dst_path: str) -> bool:
    pass


def copy_files(src_path: str, dst_path: str) -> bool:
    src_path_is_bucket = ''
    pass


def get_bucket_options(bucket_url: str) -> Tuple[str, str]:
    """
    Get bucket name and path from the bucket url
    """

    parsed_bucket_url = parse.urlparse(bucket_url)
    return parsed_bucket_url.netloc, parsed_bucket_url.path


def get_bucket(bucket_name: str) -> storage.bucket.Bucket:
    """
    Get the bucket object and bucket path if the given bucket exists.
    """

    try:
        return STORAGE_CLIENT.get_bucket(bucket_name)
    except NotFound:
        pass

    print(
        f"Bucket '{bucket_name}' does not exist.",
        "Try to use an absolute path to the files."
    )
    sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--recursive", help="Download files recursively", action="store_true")
    parser.add_argument("-m", "--parallel", help="Run copying in parallel. Provide the number of the threads", type=int)
    parser.add_argument("src_url", help="Bucket path, what do we have to copy", type=str)
    parser.add_argument("dst_url", help="Local path, where do we have to save copied", type=str)
    args = parser.parse_args()

    bucket_name, bucket_path = get_bucket_options(args.src_url)
    print(bucket_name, bucket_path)
    bucket = get_bucket(bucket_name)

    print(bucket.blob)

    if args.recursive:
        "TODO: verify that src_url is a dir"
        pass

    if args.parallel:
        pass

    # Instantiates a client
    # storage_client = storage.Client()
    #
    # # The name for the new bucket
    # bucket_name = "online-infra-engineer-test"
    # bucket = storage_client.get_bucket(bucket_name)
    # blobs_list = bucket.list_blobs()
    # blobs = []
    # local_path = '/tmp'
    # for blob in blobs_list:
    #     download_path = os.path.join(local_path, blob.name)
    #     if not os.path.exists(os.path.dirname(download_path)):
    #         os.makedirs(os.path.dirname(download_path))
    #     blob = bucket.blob(blob.name)
    #     blob.download_to_filename(download_path)
