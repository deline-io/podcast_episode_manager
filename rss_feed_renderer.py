from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = './templates'
RSS_FEED_TEMPLATE_NAME = 'rss_feed.xml'


def render_rss_feed(ch, eps):
    return load_rss_feed_template().render(ch=ch, eps=eps)


def load_rss_feed_template():
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR, encoding='utf8'),
        autoescape=select_autoescape(['xml'])
    ).get_template(RSS_FEED_TEMPLATE_NAME)
