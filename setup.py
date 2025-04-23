from setuptools import setup
from simpweb import server

setup(
    name='simpweb',
    packages=['simpweb'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)