import os
import yaml
import markdown

__all__ = ['load_channel_info', 'load_episodes_info']


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
            md_txt = f.read()
            md = markdown.Markdown(extensions=['full_yaml_metadata'])
            html = md.convert(md_txt)
            eps.append((html, md.Meta))

    return eps
