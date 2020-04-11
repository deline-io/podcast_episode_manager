import os
import requests
import zipfile

from gen import render_rss_feed
from mp3_meta_extractor import store_mp3_meta

REPO_ZIP_URL = 'https://github.com/deline-io/podcast_contents/archive/develop.zip'

DIR = '/tmp'
ZIP_PATH = os.path.join(DIR, 'podcast_contents.zip')
UNZIP_PATH = os.path.join(DIR, 'podcast_contents')

CHANNEL_YAML = 'channel.yml'
EPISODES_YAML = 'episodes.yml'


def lambda_handler(event, context):
    # contents リポジトリを zip 形式でダウンロードする
    res = requests.get(REPO_ZIP_URL, stream=True)

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
    xml = render_rss_feed(ch_yaml_path, eps_yaml_path)

    response = {
        "statusCode": 200,
        "body": xml
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """


def lambda_mp3_meta_extractor(event, context):
    store_mp3_meta(event, context)


if __name__ == '__main__':
    lambda_handler(None, None)
