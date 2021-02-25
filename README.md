## gsutil cp reimplementation
The project was created for fun and practice with google storage api.

### Prerequisites:
before using the `gscp.py` util you have to provide your google credentials
with environment variable `GOOGLE_APPLICATION_CREDENTIALS`. 

For example:
`export GOOGLE_APPLICATION_CREDENTIALS=~/google-credentials.json`

See more info about google credentials: https://cloud.google.com/docs/authentication/getting-started

### Requirements:
- python = "^3.9"
- poetry = "^0.1.0"

### Installation:
```bash
git clone https://github.com/com30n/gsutil-cp-reimplementation.git
cd gsutil-cp-reimplementation
poetry install
poetry shell 
```

### Usage:

```bazaar
usage: gscp.py [-h] [-r] [-m PARALLEL] [--debug] src_url dst_url

positional arguments:
  src_url               Bucket path, what do we have to copy
  dst_url               Local path, where do we have to save copied

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive       Download files recursively
  -m PARALLEL, --parallel PARALLEL
                        Run copying in parallel. Provide the number of the threads
  --debug               Show debug info
```

#### Examples:
Download all the files from bucket in parallel:
```bash
./gscp.py -m 10 -r gs://my-own-bucket/ /tmp/test
```

Download the only one file from the bucket:
```bash
./gscp.py gs://my-own-bucket/mydir/a/1.txt /tmp/test
```

Download some files from bucket recursively:
```bash
./gscp.py -r gs://my-own-bucket/mydir/ /tmp/test
```


### Contribution:
Before push the commit, please check it with `make fmt` command that will reformat the code and run syntax and linters test

### TODO:
Just add some unit tests
