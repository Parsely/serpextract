import unittest
from urlparse import urlparse

try:
    from serpextract import extract, is_serp, get_all_query_params
except ImportError:
    import os, sys
    basedir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    sys.path.append(basedir)
    from serpextract import extract, is_serp, get_all_query_params


class TestSERPs(unittest.TestCase):
    """Most popular search engines to really worry about until we have full on
    test coverage are:
        - Google
        - Baidu
        - Yahoo
        - Yandex
        - Microsoft (Bing)

    We test these engines, and for each we ensure we try to cover the multiple
    country case and the keywords with crazy characters case.
    """

    def assertValidSERP(self, url, expected_engine_name, expected_keyword):
        # Test both the URL and a parsed URL version
        for url in (url, urlparse(url)):
            res = extract(url)
            self.assertEqual(res.keyword, expected_keyword)
            self.assertEqual(res.engine_name, expected_engine_name)
            self.assertTrue(is_serp(url))

    def assertValidSERPs(self, expected_serps):
        for url, engine_name, keyword in expected_serps:
            self.assertValidSERP(url, engine_name, keyword)

    def test_google(self):
        serps = (
            ('http://www.google.com/url?sa=t&rct=j&q=hello&source=web&cd=1&ved=0CCoQFjAA&url=http%3A%2F%2Fwww.hellomagazine.ca%2F&ei=MDfSUe-JMob9ygGn24CoCw&usg=AFQjCNF6TQIo1aZe7WI8knqcdZax-lpg-A&bvm=bv.48572450,d.aWc', 'Google', u'hello'),
            ('http://www.google.co.uk/url?sa=t&rct=j&q=hello&source=web&cd=1&ved=0CDMQFjAA&url=http%3A%2F%2Fwww.hellomagazine.com%2F&ei=4TfSUdCLEY2_ywHXp4GADg&usg=AFQjCNE2TScP1sOG-TytWVe-kB0UUbWncg&bvm=bv.48572450,d.aWc', 'Google', u'hello'),
            ('http://www.google.co.in/url?sa=t&rct=j&q=%E0%A4%A8%E0%A4%AE%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A5%87&source=web&cd=1&ved=0CCwQFjAA&url=http%3A%2F%2Fhi.wikipedia.org%2Fwiki%2F%25E0%25A4%25A8%25E0%25A4%25AE%25E0%25A4%25B8%25E0%25A5%258D%25E0%25A4%25A4%25E0%25A5%2587&ei=eTfSUceOJ6i4yAGk6oGoDw&usg=AFQjCNGpYEO70ix-UtllM5iLl8Ywenwbpw&bvm=bv.48572450,d.aWc', 'Google', u'\u0928\u092e\u0938\u094d\u0924\u0947'),
            ('http://www.google.com.ua/url?sa=t&rct=j&q=%D0%BF%D1%80%D0%B8%D0%B2%D1%96%D1%82&source=web&cd=1&ved=0CC0QFjAA&url=http%3A%2F%2Fuk.wiktionary.org%2Fwiki%2F%25D0%25BF%25D1%2580%25D0%25B8%25D0%25B2%25D1%2596%25D1%2582&ei=dTjSUYnYJuSOyAG-rYDoCQ&usg=AFQjCNHloehQAu7UJ6upCqMVCDpNh3sNTg&bvm=bv.48572450,d.aWc', 'Google', u'\u043f\u0440\u0438\u0432\u0456\u0442'),
            ('http://www.google.ca/url?sa=i&rct=j&q=%22justin+timberlake%22&source=images&cd=&docid=mPgs-1UiH9v_-M&tbnid=Zkq86Kfj5IWYxM:&ved=0CAEQjxw&url=http%3A%2F%2Fwww.salon.com%2F2013%2F01%2F10%2Fis_justin_timberlake_releasing_a_new_album%2F&ei=ZuDmUaOlEaTk4AOE_4GgCQ&bvm=bv.49405654,d.dmg&psig=AFQjCNEX5ylDUbWb68msE2VIYZw-ObWtNg&ust=1374171617895913', 'Google', u'"justin timberlake"'),
            ('https://www.google.com/', 'Google', u''),
            ('https://www.google.co.uk', 'Google', u''),
            ('http://www.google.ca/search?hl=en&site=imghp&tbm=isch&source=hp&biw=1436&bih=508&q=lenovo&oq=lenovo&gs_l=img.3..0l10.2042.2539.0.2755.6.5.0.1.1.0.99.382.5.5.0....0.0..1ac.1.20.img.zuc4SkaG3pk#q=lenovo&hl=en&site=imghp&tbs=isz:l,qdr:d,itp:photo&tbm=isch&source=lnt&sa=X&ei=chbnUcwB88fgA9GdgdgD&ved=0CD0QpwUoAg&bav=on.2,or.r_qf.&bvm=bv.49405654%2Cd.dmg%2Cpv.xjs.s.en_US.QXiTEk6XjhM.O&fp=74e28ccdf351cc74&biw=1436&bih=508&facrc=_&imgdii=_&imgrc=PWcY9IoUsS8fqM%3A%3BLXHKDtPubm1b_M%3Bhttp%253A%252F%252Fmy.kyozou.com%252Fpictures%252F_15%252F14595%252F14594417.jpg%3Bhttp%253A%252F%252Fwww.ebay.com%252Fitm%252FLENOVO-X200-LAPTOP-CORE-2-DUO-1-86GHz-4GB-160GB-WIRELESS-%252F221252458890%253Fpt%253DLaptops_Nov05%2526hash%253Ditem3383ac998a%3B1600%3B1200', 'Google Images', u'lenovo'),
            # TODO: More google edge cases
        )
        self.assertValidSERPs(serps)

    def test_baidu(self):
        # TODO: More tests for Baidu
        serps = (
            ('http://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD&rsv_bp=0&ch=&tn=baidu&bar=&rsv_spt=3&ie=utf-8&rsv_n=2&rsv_sug3=1&rsv_sug=0&rsv_sug1=1&rsv_sug4=352&inputT=1295', 'Baidu', u'\u4f60\u597d'),
        )
        self.assertValidSERPs(serps)

    def test_yahoo(self):
        serps = (
            ('http://ca.search.yahoo.com/search;_ylt=At9vKXZDJTDsQ6o7bDQPLBUt17V_;_ylc=X1MDMjE0MjYyMzUzMwRfcgMyBGZyA3lmcC10LTcxNQRuX2dwcwMxMARvcmlnaW4DY2EueWFob28uY29tBHF1ZXJ5A2hlbGxvBHNhbwMx?p=hello&toggle=1&cop=mss&ei=UTF-8&fr=yfp-t-715', 'Yahoo!', u'hello'),
            ('http://search.yahoo.com/search;_ylt=AnQcoCW29caK.8RLkGgSiqGbvZx4?p=united+states&toggle=1&cop=mss&ei=UTF-8&fr=yfp-t-900', 'Yahoo!', u'united states'),
        )
        self.assertValidSERPs(serps)

    def test_yandex(self):
        serps = (
            ('http://www.yandex.com/yandsearch?text=%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82&lr=87', 'Yandex', u'\u043f\u0440\u0438\u0432\u0435\u0442'),
            ('http://yandex.ru/yandsearch?lr=10115&text=%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82', 'Yandex', u'\u043f\u0440\u0438\u0432\u0435\u0442'),
        )
        self.assertValidSERPs(serps)

    def test_bing(self):
        serps = (
            ('http://www.bing.com/search?q=united+states&go=&qs=n&form=QBLH&filt=all&pq=united+states&sc=8-13&sp=-1&sk=', 'Bing', u'united states'),
        )
        self.assertValidSERPs(serps)

    def test_path_engines(self):
        """Tests for search engines that contain keywords within their paths
        and require regex extraction."""
        serps = (
            ('http://www.123people.ca/s/michael+sukmanowsky', '123people', u'michael sukmanowsky'),
            ('http://www.1.cz/s/ars-technica/', '1.cz', u'ars-technica'),  # These guys do not properly URL encode their keywords
        )

    def test_get_all_query_params(self):
        """Ensure that get_all_query_params is a non-empty list."""
        params = get_all_query_params()
        self.assertIsInstance(params, list)
        assert len(params) > 0

    def test_invalid_serps(self):
        invalid_serps = (
            'http://www.google.com/reader',
            'http://www.yahoo.com/',
            'http://www.something.com/',
        )
        for url in invalid_serps:
            self.assertIsNone(extract(url))
            self.assertFalse(is_serp(url))


if __name__ == '__main__':
    unittest.main()