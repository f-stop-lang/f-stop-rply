import re

from setuptools import setup

with open("fstop/__init__.py") as init:
    content = init.read()
    
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', 
        content, re.MULTILINE,
    ).group(1)

    author = re.search(
        r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]', 
        content, re.MULTILINE,
    ).group(1)

    name = re.search(
        r'^__title__\s*=\s*[\'"]([^\'"]*)[\'"]', 
        content, re.MULTILINE,
    ).group(1)

    license = re.search(
        r'^__license__\s*=\s*[\'"]([^\'"]*)[\'"]', 
        content, re.MULTILINE,
    ).group(1)

with open('requirements.txt') as requirements:
    deps = requirements.read().splitlines()

with open("README.md") as readme:
    readme = readme.read()

setup(
    name = name, 
    author = author,
    version = version, 
    description = "An unoffical API wrapper for tio.run",
    long_description = readme,
    long_description_content_type = "text/markdown",
    license = license,
    url     = "https://github.com/f-stop-lang/f-stop-rply/tree/iteration",
    project_urls = {
        "Repository"   : "https://github.com/f-stop-lang/f-stop-rply/tree/iteration",
        "Issue tracker": "https://github.com/f-stop-lang/f-stop-rply/issues",
    },
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
    ],
    include_package_data = True,
    packages         = ['fstop'],
    install_requires = deps,
    zip_safe = True,
    python_requires = '>=3.8'
)