import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='termination',
    version='0.0.1',
    author='Chris Bouchard',
    author_email='chris@upliftinglemma.net',
    description='A library for first-order term-rewriting',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cbouchard/termination',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
