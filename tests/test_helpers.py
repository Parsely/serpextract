from __future__ import absolute_import

import unittest
from six.moves.urllib.parse import urlparse

from serpextract import serpextract


class TestSERPExtractUtilityFunctions(unittest.TestCase):
    """Test the utility functions used commonly in serpextract."""

    def test_serp_query_string(self):
        serp_query_string = serpextract._serp_query_string
        url = 'http://www.something.com/?a=1#b=2'
        expected = 'a=1&b=2'
        parts = urlparse(url)
        self.assertEqual(serp_query_string(parts), expected)

    def test_is_url_without_path_query_or_fragment(self):
        is_url_without_path_query_or_fragment = \
            serpextract._is_url_without_path_query_or_fragment
        results = (
            ('http://www.something.com', True),
            ('http://www.something.com/', True),
            ('http://www.something.com/path', False),
            ('http://www.something.com/?query=true', False),
            ('http://www.something.com/#fragment', False),
            ('http://www.something.com/path?query=True#fragment', False),
        )

        for url, expected in results:
            parts = urlparse(url)
            actual = is_url_without_path_query_or_fragment(parts)
            self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
