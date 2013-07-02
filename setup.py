import sys
from setuptools import setup

import serpextract


install_requires = ['iso3166 >= 0.4']
if sys.version_info <= (2,7):
    install_requires.append("argparse >= 1.2.1")

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='serpextract',
    version=serpextract.__version__,
    author='Mike Sukmanowsky',
    author_email='mike@parsely.com',
    packages=['serpextract',],
    url='http://github.com/Parsely/serpextract/',
    license='LICENSE.txt',
    keywords='search engines keyword extract',
    description='Easy extraction of keywords from search engine results pages (SERPs).',
    long_description=long_description,
    install_requires=install_requires,
    include_package_data=True,
    platforms='any',
    classifiers=[
        # Taken from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'serpextract = serpextract.serpextract:main',
        ]
    },
)