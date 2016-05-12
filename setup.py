import re
import sys
from setuptools import setup

# Get version without importing, which avoids dependency issues
def get_version():
    with open('serpextract/__init__.py') as version_file:
        return re.search(r"""__version__\s+=\s+(['"])(?P<version>.+?)\1""",
                         version_file.read()).group('version')

install_requires = [
    'iso3166 >= 0.4',
    'pylru >= 1.0.3',
    'tldextract >= 1.2',
    'chardet==2.3.0'
]

if sys.version_info <= (2,7):
    install_requires.append("argparse >= 1.2.1")

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='serpextract',
    version=get_version(),
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
