"""Setup for filestorage XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='xblock-filestorage',
    version='0.5',
    description='FileStorage XBlock for adding external documents to courseware',
    packages=[
        'filestorage',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'filestorage = filestorage:FileStorageXBlock',
        ]
    },
    package_data=package_data("filestorage", ["static", "public"]),
)
