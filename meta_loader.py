import os
import yaml
import markdown
import requests

__all__ = ['load_channel_info', 'load_episodes_info']

HOST = 'https://deline.s3-ap-northeast-1.amazonaws.com'
AUDIO_META_DIR = os.path.join(HOST, 'audio_meta')


def load_channel_info(path):
    with open(path) as f:
        return yaml.safe_load(f)


def load_episodes_info(dir):
    def filter_invalid_file(path):
        return path.endswith('.md')

    children = [os.path.join(dir, name) for name in os.listdir(dir)]
    children.sort(reverse=True)

    eps = []
    for ep_md in filter(filter_invalid_file, children):
        with open(ep_md) as f:
            audio_meta = load_audio_meta(ep_md)
            id_str, _ = os.path.splitext(os.path.basename(ep_md))
            md_txt = f.read()
            md = markdown.Markdown(extensions=['full_yaml_metadata'])
            html = md.convert(md_txt)

            md.Meta.update(audio_meta)

            relative_audio_path = audio_meta['relative_audio_path']
            md.Meta.update({
                'id': int(id_str),
                'file_url': os.path.join(HOST, relative_audio_path)
            })

            # md['id'] = int(id_str)
            # relative_audio_path = audio_meta['relative_audio_path']
            # md['file_url'] = os.path.join(HOST, relative_audio_path)
            # md['duration_sec'] = audio_meta['duration_sec']
            # md['file_size'] = audio_meta['file_size']

            eps.append((html, md.Meta))

    return eps


def load_audio_meta(path):
    name, _ = os.path.splitext(os.path.basename(path))
    audio_meta_path = os.path.join(AUDIO_META_DIR, f'{name}.json')
    res = requests.get(audio_meta_path)

    return res.json()
