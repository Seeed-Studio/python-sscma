import setuptools
from setuptools import find_packages
import re

with open("./sscma/__init__.py", 'r') as f:
    content = f.read()
    version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content).group(1)
    
with open("README.md", "r") as fh:
    long_description = fh.read()
    

setuptools.setup(
    name='python-sscma',
    version=version,
    author='Seeed Studio',
    author_email='lht856@foxmail.com',
    description='Python library for sscma',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Seeed-Studio/python-sscma',
    packages=find_packages(),
    package_data={'sscma': ['fonts/*.ttf']},
    install_requires=[
        'pillow',
        'pyserial',
        'paho-mqtt > 2.0.0',
        'xmodem',
        'tqdm',
        'click',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    license='MIT',
    entry_points={
        'console_scripts': [
            'sscma.cli = sscma.cli.cli:main',
        ]
    }
)
