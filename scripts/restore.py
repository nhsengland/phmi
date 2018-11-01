import sys
import datetime
import subprocess
import boto3
import os


def get_bucket(bucket_name, file_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.download_file(file_name, file_name)


def load_file(db_name, db_user, file_name):
    command = "psql -d {} -U {} -f {}".format(
        db_name, db_user, file_name
    )
    subprocess.check_call(command, shell=True)


def main(db_name, db_user, bucket_name, file_name):
    bucket = get_bucket(bucket_name, file_name)
    load_file(db_name, db_user, file_name)
    os.remove(file_name)


if __name__ == '__main__':
    try:
        _, db_name, db_user, bucket_name, file_name = sys.argv
        main(db_name, db_user, bucket_name, file_name)
    except Exception as e:
        print('errored with {}'.format(str(e)))