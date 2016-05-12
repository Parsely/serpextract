# -*- coding=utf-8 -*-
from __future__ import absolute_import

import unittest
from six.moves.urllib.parse import urlparse

from serpextract import (SearchEngineParser, extract, is_serp,
                         get_all_query_params, add_custom_parser)


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

    def setUp(self):
        self.custom_serp_url = 'http://search.piccshare.com/search.php?cat=web&channel=main&hl=en&q=test'
        self.custom_parser = SearchEngineParser(u'PiccShare', u'q',
                                                u'/search.php?q={k}',u'utf-8')

    def assertInvalidSERP(self, url, **kwargs):
        self.assertIsNone(extract(url, **kwargs))
        self.assertFalse(is_serp(url, **kwargs))

    def assertValidSERP(self, url, expected_engine_name, expected_keyword, **kwargs):
        # Test both the URL and a parsed URL version
        for url in (url, urlparse(url)):
            res = extract(url, **kwargs)
            self.assertEqual(res.keyword, expected_keyword)
            self.assertEqual(res.engine_name, expected_engine_name)
            self.assertTrue(is_serp(url, **kwargs))

    def assertValidSERPs(self, expected_serps, **kwargs):
        for url, engine_name, keyword in expected_serps:
            self.assertValidSERP(url, engine_name, keyword, **kwargs)

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
            ('https://www.google.it', 'Google', u''),
            # TODO: More google edge cases
        )
        self.assertValidSERPs(serps)

    def test_baidu(self):
        # TODO: More tests for Baidu
        serps = (
            ('http://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD&rsv_bp=0&ch=&tn=baidu&bar=&rsv_spt=3&ie=utf-8&rsv_n=2&rsv_sug3=1&rsv_sug=0&rsv_sug1=1&rsv_sug4=352&inputT=1295', 'Baidu', u'\u4f60\u597d'),
            ('http://www.baidu.com/s?wd=baidu', 'Baidu', u'baidu'),

            ('http://m.baidu.com/s?tn=zbios&pu=sz%401320_480%2Ccuid%40la2si_O62i_OaH8sgu2BalajHiYgaH8IgOSu808Cva8Ca-8gYPvli_uqv8_Ea2tWA%2Ccua%40_PvjhYa6vhIDJEjPkJAiC_CVBhxVGNGoC%2Ccut%405kSYMltqeC_kavNkJavjh_h02IgUNvikyf3NuDhwWexZB%2Cosname%40baiduboxapp%2Cctv%402%2Ccfrom%40100027o%2Ccen%40cuid_cua_cut%2Ccsrc%40app_mainbox_txt&bd_page_type=1&word=JA%2Fp%2B5L7M%7AbPQiXwy%2FwNvsehkuDQ7MkKYlc7KBr%396F3%2FK7nn%7AIyc4bEsILLktNREw4av3%7Au6LK8evDN0J1%39N6Q%3D%3D&cki=1&from=100027o&pkgname=com.baidu.searchbox&network=1_0&bdna=0&rq=ia32CwEEkD5%2BrODe7teev%7AxDEeFDnwewm1g0b6lDp%5AL2gR28C3QFsgSf7rt%2F5ccYQAi6YdcJuSOBWUtroCOnDw%3D%3D&ckirq=1&sa=ikb&ss=110', 'Baidu', u'美洽'),
            ('http://www.baidu.com/s?wd=%CD%E2%CE%A7%C4%A3%CC%D8%C9%CC%CE%F1%BB%E1', 'Baidu', u'外围模特商务会'),
        )
        self.assertValidSERPs(serps)

    def test_yahoo(self):
        serps = (
            ('http://ca.search.yahoo.com/search;_ylt=At9vKXZDJTDsQ6o7bDQPLBUt17V_;_ylc=X1MDMjE0MjYyMzUzMwRfcgMyBGZyA3lmcC10LTcxNQRuX2dwcwMxMARvcmlnaW4DY2EueWFob28uY29tBHF1ZXJ5A2hlbGxvBHNhbwMx?p=hello&toggle=1&cop=mss&ei=UTF-8&fr=yfp-t-715', 'Yahoo!', u'hello'),
            ('http://search.yahoo.com/search;_ylt=AnQcoCW29caK.8RLkGgSiqGbvZx4?p=united+states&toggle=1&cop=mss&ei=UTF-8&fr=yfp-t-900', 'Yahoo!', u'united states'),
            ('http://r.search.yahoo.com/_ylt=A0LEVy5UeJBUUzgAR2FXNyoA;_ylu=X3oDMTEzaGpsYTZuBHNlYwNzcgRwb3MDMgRjb2xvA2JmMQR2dGlkA1ZJUDU1OF8x/RV=2/RE=1418782933/RO=10/RU=http%3a%2f%2fen.wikipedia.org%2fwiki%2fToronto/RK=0/RS=cUOWJ12k59iqbScMA1r6sQedikc-', 'Yahoo!', u''),
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

    def test_custom_parser_explicit(self):
        self.assertInvalidSERP(self.custom_serp_url)
        self.assertValidSERP(self.custom_serp_url,
                             self.custom_parser.engine_name,
                             u'test',
                             parser=self.custom_parser)

    def test_custom_parser_implicit(self):
        from serpextract.serpextract import _get_search_engines, _engines
        self.assertInvalidSERP(self.custom_serp_url)
        add_custom_parser(u'search.piccshare.com', self.custom_parser)
        self.assertValidSERP(self.custom_serp_url,
                             self.custom_parser.engine_name,
                             u'test')
        del _engines[u'search.piccshare.com']

    def test_naive_detection(self):
        self.assertInvalidSERP(self.custom_serp_url)
        self.assertValidSERP(self.custom_serp_url, u'piccshare', u'test', use_naive_method=True)
        url = 'http://www.yahoo.com/#/%C2%BF??;%C2%AB99555$&&&4&'
        urlp = urlparse(url)
        self.assertInvalidSERP(urlparse(url), use_naive_method=True)
        self.assertInvalidSERP(url, use_naive_method=True)

    def test_get_all_query_params(self):
        """Ensure that get_all_query_params is a non-empty list."""
        params = get_all_query_params()
        self.assertIsInstance(params, list)
        self.assertGreater(len(params), 0)

    def test_invalid_serps(self):
        invalid_serps = (
            'http://www.google.com/reader',
            'http://www.google.com/ig',
            'http://plus.url.google.com/url?sa=z&n=1374157226744&url=http%3A%2F%2Ftgam.ca%2FDsyz&usg=CSc5XfUHV6imxjYmxocn-G-rPyg',
            'http://news.google.com/',
            'http://www.yahoo.com/',
            'http://www.something.com/',
            'http://www.reddit.com/',
        )
        for url in invalid_serps:
            self.assertInvalidSERP(url)


if __name__ == '__main__':
    unittest.main()
