import os
import json
import boto3
import requests
import zipfile
from rss_feed_renderer import render_rss_feed


REPO_ZIP_URL = 'https://github.com/deline-io/podcast_contents/archive/{}.zip'

TMP_DIR = '/tmp'
ZIP_PATH = os.path.join(TMP_DIR, 'podcast_contents.zip')
UNZIP_PATH = os.path.join(TMP_DIR, 'podcast_contents')

CHANNEL_YAML = 'channel.yml'
EPISODES_YAML = 'episodes.yml'

S3_BUCKET = 'deline'
RSS_FEED_PATH = os.path.join(TMP_DIR, 'rss.xml')
S3_RSS_FEED_PATH = 'feed/rss.xml'

s3 = boto3.resource('s3')
s3_cli = boto3.client('s3')


def handle(event, context):
    request_body = json.loads(event['body'])

    target_branch = request_body['ref'].replace('refs/heads/', '')
    if target_branch == 'master':
        render(target_branch)

    return {
        "statusCode": 200,
        "body": ""
    }


def render(target_branch):
    # contents リポジトリを zip 形式でダウンロードする
    res = requests.get(REPO_ZIP_URL.format(target_branch), stream=True)

    # zip ファイルを /tmp に書き込む
    with open(ZIP_PATH, 'wb') as f:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    # zip ファイルを展開する
    with zipfile.ZipFile(ZIP_PATH) as zip:
        root_dir = os.path.join(UNZIP_PATH, zip.namelist()[0])
        zip.extractall(UNZIP_PATH)

    ch_yaml_path = os.path.join(root_dir, CHANNEL_YAML)
    eps_yaml_path = os.path.join(root_dir, EPISODES_YAML)

    with open(RSS_FEED_PATH, 'w', encoding='utf-8') as f:
        f.write(render_rss_feed(ch_yaml_path, eps_yaml_path))

    bucket = s3.Bucket(S3_BUCKET)
    bucket.upload_file(RSS_FEED_PATH, S3_RSS_FEED_PATH)
