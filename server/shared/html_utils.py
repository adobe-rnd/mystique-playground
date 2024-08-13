import base64
import hashlib

from bs4 import BeautifulSoup


def compute_unique_hash(input_string):
    encoded_string = input_string.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(encoded_string)
    hex_digest = sha256_hash.hexdigest()
    return hex_digest


def convert_urls_to_hashes(html_string, url_mapping, min_length=0):
    def hash_url(url):
        if url in url_mapping.values():
            return next(k for k, v in url_mapping.items() if v == url)
        # compute unique hash value for long almost identical URLs
        hash_value = f'hash://{compute_unique_hash(url)}'
        url_mapping[hash_value] = url
        return hash_value

    def traverse_and_hash(node):
        if node.name is None:
            return node if node else ''
        attributes = {}
        for attr, value in node.attrs.items():
            if attr in ['href', 'src', 'srcset'] and len(value) > min_length:
                value = f"{hash_url(value)}"
            attributes[attr] = value
        open_tag = f"<{node.name}{' ' + ' '.join([f'{k}=\"{v}\"' for k, v in attributes.items()]) if attributes else ''}>"
        close_tag = f"</{node.name}>"
        children = ''.join([traverse_and_hash(child) for child in node.children if child.name or child.string])
        return f"{open_tag}{children}{close_tag}"

    soup = BeautifulSoup(html_string, 'html.parser')
    body = soup.body or soup
    hashed_html = traverse_and_hash(body)
    return str(BeautifulSoup(hashed_html, 'html.parser')).replace('<!--[document]-->', '').replace('&lt;[document]&gt;', '').strip()


def convert_hashes_to_urls(compressed_html, url_mapping):
    def reconstruct_url(hash_value):
        return url_mapping.get(hash_value)

    soup = BeautifulSoup(compressed_html, 'html.parser')
    for tag in soup.find_all():
        for attr, value in tag.attrs.items():
            if isinstance(value, str) and value.startswith('hash://'):
                original_url = reconstruct_url(value)
                tag[attr] = original_url
    return str(soup)
