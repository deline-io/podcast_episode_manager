import os
import json
import boto3
import requests
import zipfile
from rss_feed_renderer import render_rss_feed
from web_json_renderer import render_list_json, render_single_jsons
from meta_loader import load_channel_info, load_episodes_info


REPO_ZIP_URL = 'https://github.com/deline-io/podcast_contents/archive/{}.zip'

TMP_DIR = '/tmp'
ZIP_PATH = os.path.join(TMP_DIR, 'podcast_contents.zip')
UNZIP_PATH = os.path.join(TMP_DIR, 'podcast_contents')

CHANNEL_YAML = 'channel.yml'
EPISODES_DIR_NAME = 'episodes'

S3_BUCKET = os.environ.get('S3_BUCKET', 'deline')
RSS_FEED_PATH = os.path.join(TMP_DIR, 'rss.xml')
LIST_JSON_PATH = os.path.join(TMP_DIR, 'list.json')
SINGLE_JSON_PATH_BASE = os.path.join(TMP_DIR, '{id}.json')
S3_RSS_FEED_PATH = 'feed/rss.xml'
S3_META_DIR = 'meta'
S3_LIST_JSON_PATH = os.path.join(S3_META_DIR, 'list.json')
S3_SINGLE_JSON_DIR = os.path.join(S3_META_DIR, 'episodes')

s3 = boto3.resource('s3')
s3_cli = boto3.client('s3')

TARGET_BRANCH = os.environ.get('TARGET_BRANCH', 'master')


def handle(event, context):
    print(TARGET_BRANCH)
    print(S3_BUCKET)

    request_body = json.loads(event['body'])

    target_branch = request_body['ref'].replace('refs/heads/', '')
    if target_branch == TARGET_BRANCH:
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
    eps_md = os.path.join(root_dir, EPISODES_DIR_NAME)

    ch = load_channel_info(ch_yaml_path)
    eps = load_episodes_info(eps_md)

    with open(RSS_FEED_PATH, 'w', encoding='utf-8') as f:
        f.write(render_rss_feed(ch, [ep[-1] for ep in eps]))

    single_json_path_list = []
    for id, meta in render_single_jsons(eps):
        path = SINGLE_JSON_PATH_BASE.format(id=id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(meta, f)
        single_json_path_list.append(path)

    with open(LIST_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(render_list_json(eps), f)

    bucket = s3.Bucket(S3_BUCKET)
    bucket.upload_file(RSS_FEED_PATH, S3_RSS_FEED_PATH)
    bucket.upload_file(LIST_JSON_PATH, S3_LIST_JSON_PATH)
    for path in single_json_path_list:
        fname = os.path.basename(path)
        bucket.upload_file(path, os.path.join(S3_SINGLE_JSON_DIR, fname))


if __name__ == '__main__':
    render('develop')
