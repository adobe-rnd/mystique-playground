import base64
from bs4 import BeautifulSoup

def compress_html(html_string, replace_urls=False, existing_url_mapping=None):
    non_essential_tags = ['script', 'style', 'meta', 'link', 'head', 'title']
    non_essential_attributes = ['onclick', 'onload']
    non_essential_styles = []

    # Use the provided existing_url_mapping or create a new one
    url_mapping = existing_url_mapping if existing_url_mapping is not None else {}

    def is_non_essential_tag(tag):
        return tag in non_essential_tags

    def is_non_essential_attribute(attr):
        return attr in non_essential_attributes or attr.startswith('data-')

    def is_non_essential_style(style):
        return style in non_essential_styles

    def extract_styles(element):
        style = element.get('style', '')
        styles = {}
        for s in style.split(';'):
            if ':' in s:
                key, value = s.split(':', 1)
                key = key.strip()
                value = value.strip()
                if not is_non_essential_style(key):
                    styles[key] = value
        return styles

    def hash_url(url):
        if url in url_mapping.values():
            for k, v in url_mapping.items():
                if v == url:
                    return k
        hash_value = base64.urlsafe_b64encode(url.encode()).decode()[:8]
        url_mapping[hash_value] = url
        return hash_value

    def traverse_and_compress(node):
        if node.name is None:
            return node if node else ''
        if is_non_essential_tag(node.name):
            return ''
        attributes = []
        for attr, value in node.attrs.items():
            if not is_non_essential_attribute(attr):
                if isinstance(value, list):
                    value = ' '.join(value)
                if replace_urls and attr in ['href', 'src', 'srcset'] and len(value) > 30:
                    value = f"hash:{hash_url(value)}"
                attributes.append(f'{attr}="{value}"')
        styles = extract_styles(node)
        style_string = '; '.join([f'{k}: {v}' for k, v in styles.items()])
        if style_string:
            attributes.append(f'style="{style_string}"')
        open_tag = f"<{node.name}{' ' + ' '.join(attributes) if attributes else ''}>"
        close_tag = f"</{node.name}>"
        children = ''.join([traverse_and_compress(child) for child in node.children if child.name or child.string])
        return f"{open_tag}{children}{close_tag}"

    soup = BeautifulSoup(html_string, 'html.parser')
    body = soup.body or soup
    compressed_html = traverse_and_compress(body)
    compressed_html = str(BeautifulSoup(compressed_html, 'html.parser')).replace('<!--[document]-->', '').replace('&lt;[document]&gt;', '').strip()
    original_size = len(html_string)
    compressed_size = len(compressed_html)
    compression_ratio = 100 - (compressed_size / original_size * 100)

    return {
        'compressed_html': compressed_html,
        'url_mapping': url_mapping,
        'compression_ratio': compression_ratio
    }

def decompress_html(compressed_html, url_mapping):
    def reconstruct_url(hash_value):
        return url_mapping.get(hash_value, hash_value)

    soup = BeautifulSoup(compressed_html, 'html.parser')
    for tag in soup.find_all():
        for attr, value in tag.attrs.items():
            if isinstance(value, str) and value.startswith('hash:'):
                original_url = reconstruct_url(value[5:])
                tag[attr] = original_url
    return str(soup)

