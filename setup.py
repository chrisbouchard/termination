import re
import sys

from setuptools import find_packages, setup

with open('src/termination/__init__.py', 'r') as fh:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fh.read(),
        re.MULTILINE
    ).group(1)

with open('README.md', 'r') as fh:
    long_description = fh.read()

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name='termination',
    url='https://github.com/chrisbouchard/termination',
    author='Chris Bouchard',
    author_email='chris@upliftinglemma.net',
    description='A library for first-order term-rewriting',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages('src'),
    package_dir={
        '': 'src'
    },
    test_suite='nose.collector',
    install_requires=[
        'anytree>=2.4,<2.5'
    ],
    setup_requires=[
        "flake8"
    ],
    tests_require=[
        'nose'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
    ],
)
