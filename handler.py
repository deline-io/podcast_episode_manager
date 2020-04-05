import os
import json
import requests
import zipfile

REPO_ZIP_URL = 'https://github.com/deline-io/podcast_contents/archive/master.zip'

DIR = '/tmp'
ZIP_PATH = os.path.join(DIR, 'podcast_contents.zip')
UNZIP_PATH = os.path.join(DIR, 'podcast_contents')

CHANNEL_YAML = 'README.md'
EPISODES_YAML = 'LICENSE'


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

    # チャンネルの情報を読みとる
    with open(os.path.join(root_dir, CHANNEL_YAML)) as f:
        print(f.read())

    # エピソードの情報を読み取る
    with open(os.path.join(root_dir, EPISODES_YAML)) as f:
        print(f.read())

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": os.listdir(UNZIP_PATH)
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
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


if __name__ == '__main__':
    lambda_handler(None, None)
