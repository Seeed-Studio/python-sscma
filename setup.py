import setuptools
from setuptools import find_packages
import re

with open("./sscma/__init__.py", 'r') as f:
    content = f.read()
    # from https://www.py4u.net/discuss/139845
    version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content).group(1)
    
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='python-sscma',
    version=version,
    author='Seeed Studio',
    author_email='lht856@foxmail.com',
    description='<INSERT_DESCRIPTION>',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Seeed-Studio/python-sscma',
    packages=find_packages(),
    package_data={'sscma': ['fonts/*.ttf']},
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
