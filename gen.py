import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = './templates'
RSS_FEED_TEMPLATE_NAME = 'rss_feed.xml'


def render_rss_feed(ch_yaml_path, eps_yaml_path):
    ch = load_channel_info(ch_yaml_path)
    eps = load_episodes_info(eps_yaml_path)
    rss_tmpl = load_rss_feed_template()

    return rss_tmpl.render(ch=ch, eps=eps)


def load_channel_info(path):
    with open(path) as f:
        return yaml.safe_load(f)


def load_episodes_info(path):
    with open(path) as f:
        return yaml.safe_load(f)


def load_rss_feed_template():
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR, encoding='utf8'),
        autoescape=select_autoescape(['xml'])
    ).get_template(RSS_FEED_TEMPLATE_NAME)
