import unittest

try:
    from serpextract import extract
except ImportError:
    import os, sys
    basedir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    sys.path.append(basedir)
    from serpextract import extract


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

    def assertValidSERPs(self, expected_serps):
        for url, engine_name, keyword in expected_serps:
            res = extract(url)
            assert res.keyword == keyword
            assert res.engine_name == engine_name

    def test_google(self):
        serps = (
            ('http://www.google.com/url?sa=t&rct=j&q=hello&source=web&cd=1&ved=0CCoQFjAA&url=http%3A%2F%2Fwww.hellomagazine.ca%2F&ei=MDfSUe-JMob9ygGn24CoCw&usg=AFQjCNF6TQIo1aZe7WI8knqcdZax-lpg-A&bvm=bv.48572450,d.aWc', 'Google', u'hello'),
            ('http://www.google.co.uk/url?sa=t&rct=j&q=hello&source=web&cd=1&ved=0CDMQFjAA&url=http%3A%2F%2Fwww.hellomagazine.com%2F&ei=4TfSUdCLEY2_ywHXp4GADg&usg=AFQjCNE2TScP1sOG-TytWVe-kB0UUbWncg&bvm=bv.48572450,d.aWc', 'Google', u'hello'),
            ('http://www.google.co.in/url?sa=t&rct=j&q=%E0%A4%A8%E0%A4%AE%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A5%87&source=web&cd=1&ved=0CCwQFjAA&url=http%3A%2F%2Fhi.wikipedia.org%2Fwiki%2F%25E0%25A4%25A8%25E0%25A4%25AE%25E0%25A4%25B8%25E0%25A5%258D%25E0%25A4%25A4%25E0%25A5%2587&ei=eTfSUceOJ6i4yAGk6oGoDw&usg=AFQjCNGpYEO70ix-UtllM5iLl8Ywenwbpw&bvm=bv.48572450,d.aWc', 'Google', u'\u0928\u092e\u0938\u094d\u0924\u0947'),
            ('http://www.google.com.ua/url?sa=t&rct=j&q=%D0%BF%D1%80%D0%B8%D0%B2%D1%96%D1%82&source=web&cd=1&ved=0CC0QFjAA&url=http%3A%2F%2Fuk.wiktionary.org%2Fwiki%2F%25D0%25BF%25D1%2580%25D0%25B8%25D0%25B2%25D1%2596%25D1%2582&ei=dTjSUYnYJuSOyAG-rYDoCQ&usg=AFQjCNHloehQAu7UJ6upCqMVCDpNh3sNTg&bvm=bv.48572450,d.aWc', 'Google', u'\u043f\u0440\u0438\u0432\u0456\u0442'),
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


if __name__ == '__main__':
    unittest.main()

        