
from setuptools import setup, find_packages

from pip.download import PipSession
from pip.req import parse_requirements

reqs = [
    str(r.req) for r in
    parse_requirements('requirements.txt', session=PipSession())]


setup(
    name="lycheesync",
    version="3.0.9",
    author="Gustave Pate",
    author_email="gustave.pate@fake.com",
    description="Photo synchronization utility for Lychee",
    license="MIT",
    url="http://github.com/GustavePate/lycheesync",
    packages=find_packages(),
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': [
            'lycheesync=lycheesync.sync:main',
        ]
    },
    install_requires=reqs,
)
