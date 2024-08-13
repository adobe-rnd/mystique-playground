import unittest
from server.shared.html_utils import convert_urls_to_hashes, convert_hashes_to_urls, compute_unique_hash
import base64


class TestHTMLUtils(unittest.TestCase):

    def test_convert_urls_to_hashes(self):
        html_string = '''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="https://example.com/some/very/long/path/to/resource">Link</a>
                <img src="https://example.com/some/very/long/path/to/image.jpg" />
            </body>
        </html>
        '''
        url_mapping = {}
        hashed_html = convert_urls_to_hashes(html_string, url_mapping)

        # Check if URLs are hashed and are unique
        self.assertIn('hash://', hashed_html)
        self.assertEqual(len(url_mapping), 2)

        # Validate the mapping for each URL
        for original_url in ['https://example.com/some/very/long/path/to/resource',
                             'https://example.com/some/very/long/path/to/image.jpg']:
            expected_hash = f'hash://{compute_unique_hash(original_url)}'
            self.assertIn(expected_hash, url_mapping)
            self.assertEqual(url_mapping[expected_hash], original_url)

    def test_convert_hashes_to_urls(self):
        compressed_html = '''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="hash://aHR0cHM6">Link</a>
                <img src="hash://aHR0cHM7" />
            </body>
        </html>
        '''
        url_mapping = {
            'hash://aHR0cHM6': 'https://example.com/some/very/long/path/to/resource',
            'hash://aHR0cHM7': 'https://example.com/some/very/long/path/to/image.jpg'
        }
        result_html = convert_hashes_to_urls(compressed_html, url_mapping)

        # Check if hashes are replaced with original URLs
        self.assertIn('https://example.com/some/very/long/path/to/resource', result_html)
        self.assertIn('https://example.com/some/very/long/path/to/image.jpg', result_html)
        self.assertNotIn('hash://', result_html)


if __name__ == '__main__':
    unittest.main(verbosity=0)
