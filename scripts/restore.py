import os
import subprocess
import sys

import boto3


def get_bucket(bucket_name, file_name):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    bucket.download_file(file_name, file_name)


def load_file(db_name, db_user, file_name):
    command = f"psql -d {db_name} -U {db_user} -f {file_name}"
    subprocess.check_call(command, shell=True)


def main(db_name, db_user, bucket_name, file_name):
    get_bucket(bucket_name, file_name)
    load_file(db_name, db_user, file_name)
    os.remove(file_name)


if __name__ == "__main__":
    try:
        _, db_name, db_user, bucket_name, file_name = sys.argv
        main(db_name, db_user, bucket_name, file_name)
    except Exception as e:
        print(f"errored with {str(e)}")
