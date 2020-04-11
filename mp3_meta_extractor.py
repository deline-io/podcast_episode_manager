import os
import yaml
import boto3
import urllib.parse
from mutagen.mp3 import MP3


TMP_DIR = '/tmp'
INPUT_DIR = os.path.join(TMP_DIR, 'input')
OUTPUT_DIR = os.path.join(TMP_DIR, 'output')

s3 = boto3.resource('s3')
s3_cli = boto3.client('s3')


def handle(event, context):
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        s3_event_meta = event['Records'][0]['s3']
        input_bucket = s3_event_meta['bucket']['name']
        s3_input_path = urllib.parse.unquote_plus(
            s3_event_meta['object']['key'], encoding='utf-8')

        input_file_name = os.path.basename(s3_input_path)
        download_path = os.path.join(INPUT_DIR, input_file_name)

        bucket = s3.Bucket(input_bucket)
        bucket.download_file(s3_input_path, download_path)

        output_file_path = os.path.join(OUTPUT_DIR, input_file_name)
        with open(output_file_path, 'w') as f:
            yaml.dump({
                'relative_audio_path': s3_input_path,
                'file_size': s3_event_meta['object']['size'],
                'length': extract_mp3_length(download_path)
            }, f)

        upload_path = s3_input_path.replace(
            'audio', 'audio_meta').replace('.mp3', '.yml')
        bucket.upload_file(output_file_path, upload_path)

    except Exception as e:
        print(e)
        raise e


def extract_mp3_length(path):
    return int(MP3(path).info.length)
