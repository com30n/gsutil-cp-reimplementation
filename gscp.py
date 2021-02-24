#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import threading
from functools import partial
from multiprocessing.pool import ThreadPool as Pool
from time import time as timer
from typing import List, Tuple
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
    """  """
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
    """
    Get bucket name and path from the bucket url
    """

    parsed_bucket_url = parse.urlparse(bucket_url)
    bucket_name = parsed_bucket_url.netloc
    bucket_path = parsed_bucket_url.path.lstrip("/")
    return bucket_name, bucket_path


def get_bucket(bucket_name: str) -> Bucket:
    """ Get the bucket object and bucket path if the given bucket exists. """

    try:
        LOG.debug(f'Verifying connect to the bucket "{bucket_name}"...')
        bucket = STORAGE_CLIENT.get_bucket(bucket_name)
        LOG.debug("Connection verified")
        return bucket
    except NotFound:
        pass

    LOG.error(
        f"Bucket '{bucket_name}' does not exist.",
        "Try to use an absolute path to the files.",
    )
    sys.exit(1)


def _download_blob(blob: Blob, dst_url: str) -> None:
    """ Download and save one blob to the local filesystem. """

    download_path = os.path.join(dst_url, blob.name)
    if not os.path.exists(os.path.dirname(download_path)):
        try:
            os.makedirs(os.path.dirname(download_path))
        except FileExistsError:
            pass
    LOG.info(f'Downloading "{blob.name}" to "{download_path}"')
    blob.download_to_filename(download_path)


def download_blobs(blobs: List[Blob], dst_url: str) -> None:
    """ Download and save the blobs to the local filesystem. """
    if not blobs:
        LOG.info("No files was found in bucket by provided path")
        sys.exit(1)

    download_func = partial(_download_blob, dst_url=dst_url)
    for blob in blobs:
        download_func(blob)


def parallel_download_blobs(blobs: List[Blob], dst_url: str, parallel: int) -> None:
    """ Download and save the blobs to the local filesystem in parallel. """
    if not blobs:
        LOG.info("No files was found in bucket by provided path")
        sys.exit(1)

    download_func = partial(_download_blob, dst_url=dst_url)
    download = Pool(parallel).map(download_func, blobs)

    for _ in download:
        # just download a files
        pass


def parallel_download_blobs2(blobs: List[Blob], dst_url: str, parallel: int) -> None:
    """ Download and save the blobs to the local filesystem in parallel. """
    if not blobs:
        LOG.info("No files was found in bucket by provided path")
        sys.exit(1)

    download_func = partial(_download_blob, dst_url=dst_url)
    threads = [threading.Thread(target=download_func, args=(blob,)) for blob in blobs]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def get_blobs(
    bucket: Bucket, blob_path: str = "", recursive: bool = False
) -> List[Blob]:
    """
    Get the blobs list via given blob path.

    If you provide "recursive" option the function will return the list
    with all matched blobs by provided blob path.

    It has an one side effect: if you have a bucket structure mydir/1.txt, mydir2/2.txt
    and you provide only /myd path to the tool with --recursive option
    the tool will download and mydir/ and mydir2/ dirs.
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
    if parallel:
        parallel_download_blobs2(blobs=blobs, dst_url=dst_url, parallel=parallel)
    else:
        download_blobs(blobs=blobs, dst_url=dst_url)
    LOG.debug(f"Downloading time: {timer() - start}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", "--recursive", help="Download files recursively", action="store_true"
    )
    parser.add_argument(
        "-m",
        "--parallel",
        help="Run copying in parallel. Provide the number of the threads",
        type=int,
    )
    parser.add_argument("--debug", help="Show debug info", action="store_true")
    parser.add_argument(
        "src_url", help="Bucket path, what do we have to copy", type=str
    )
    parser.add_argument(
        "dst_url", help="Local path, where do we have to save copied", type=str
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
