#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import threading
from functools import partial
from time import time as timer
from typing import Callable, List, Tuple
from urllib import parse

from google.api_core.exceptions import NotFound
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket

LOG = logging.getLogger()

try:
    STORAGE_CLIENT = storage.Client()
except DefaultCredentialsError as e:
    LOG.error(e)
    sys.exit(1)


def get_logging_handler(log_level: int = logging.INFO) -> logging.Handler:
    """
    Sets the stdout handler to add the ability to view tool logs.
    It can also add a debug formatter if you use the --debug option.
    """
    handler = logging.StreamHandler(sys.stdout)
    if log_level == logging.DEBUG:
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s %(name)s - "%(message)s"'
        )
        handler.setFormatter(formatter)
    return handler


# Setup default logging
LOG.addHandler(get_logging_handler())


def get_bucket_options(bucket_url: str) -> Tuple[str, str]:
    """ Gets the bucket name and path from the bucket URL. """

    parsed_bucket_url = parse.urlparse(bucket_url)
    bucket_name = parsed_bucket_url.netloc
    bucket_path = parsed_bucket_url.path.lstrip("/")
    return bucket_name, bucket_path


def get_bucket(bucket_name: str) -> Bucket:
    """ Gets the bucket object to the bucket, if the bucket exists. """

    try:
        LOG.debug(f'Verifying connect to the bucket "{bucket_name}"...')
        bucket = STORAGE_CLIENT.get_bucket(bucket_name)
        LOG.debug("Connection verified")
        return bucket
    except NotFound:
        pass

    LOG.error(
        f"Bucket '{bucket_name}' does not exist.",
        "Try set an absolute path.",
    )
    sys.exit(1)


def _download_blob(blob: Blob, dst_url: str) -> None:
    """ Downloads and saves a single large binary object to the local file system. """

    download_path = os.path.join(dst_url, blob.name)
    if not os.path.exists(os.path.dirname(download_path)):
        try:
            os.makedirs(os.path.dirname(download_path))
        except FileExistsError:
            # It just only need to prevent an error with parallel download
            # When makedirs could be called a several times
            pass
    LOG.info(f'Downloading "{blob.name}" to "{download_path}"')
    blob.download_to_filename(download_path)


def _parallel_download_blobs(
    blobs: List[Blob], download_func: Callable, parallel: int
) -> None:
    """ Downloads and saves multiple blobs to the local file system in parallel. """

    threads = [threading.Thread(target=download_func, args=(blob,)) for blob in blobs]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def download_blobs(blobs: List[Blob], dst_url: str, parallel: int = 0) -> None:
    """ Downloads and saves multiple blobs to the local file system. """
    if not blobs:
        LOG.info("No files were found in the bucket at the specified path.")
        sys.exit(1)
    download_func = partial(_download_blob, dst_url=dst_url)
    if parallel:
        _parallel_download_blobs(
            blobs=blobs, download_func=download_func, parallel=parallel
        )
    else:
        for blob in blobs:
            download_func(blob)


def get_blobs(
    bucket: Bucket, blob_path: str = "", recursive: bool = False
) -> List[Blob]:
    """
    Gets the blobs list via given blob path.

    If you pass the "recursive" option, the function returns
    a list with all matching blobs along the specified path to the blob.

    It has one side effect: if you have a bucket structure mydir/1.txt, mydir2/2.txt
    and you only provide the / myd path to the tool with the --recursive parameter,
    this function will load both mydir/ and mydir2/ dirs.
    """

    if recursive:
        blobs = [x for x in bucket.list_blobs() if x.name.startswith(blob_path)]
    else:
        blobs = [x for x in bucket.list_blobs() if x.name == blob_path]

    return blobs


def main(src_url: str, dst_url: str, recursive: bool, parallel: bool):
    bucket_name, blob_path = get_bucket_options(src_url)
    LOG.debug(f'Got bucket name: "{blob_path}", got blob path: "{bucket_name}"')
    bucket = get_bucket(bucket_name)

    blobs = get_blobs(bucket=bucket, blob_path=blob_path, recursive=recursive)

    start = timer()
    download_blobs(blobs=blobs, dst_url=dst_url, parallel=parallel)
    LOG.debug(f"Downloading time: {timer() - start}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", "--recursive", help="Download files recursively", action="store_true"
    )
    parser.add_argument(
        "-m",
        "--parallel",
        help="Start copying in parallel. Specify the number of threads",
        type=int,
    )
    parser.add_argument("--debug", help="Show debug info", action="store_true")
    parser.add_argument(
        "src_url",
        help="The whole bucket path with the schema gs://, what do we have to copy",
        type=str,
    )
    parser.add_argument(
        "dst_url", help="The local path where we should save the copied file", type=str
    )
    args = parser.parse_args()

    # Setup logging
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    LOG.addHandler(get_logging_handler(log_level))
    LOG.setLevel(log_level)

    LOG.debug(f"Got cli parameters: {args}")

    main(
        src_url=args.src_url,
        dst_url=args.dst_url,
        recursive=args.recursive,
        parallel=args.parallel,
    )
