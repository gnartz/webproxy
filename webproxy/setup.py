from setuptools import setup, find_packages

setup(
    name='webproxy',
    version='0.1.0',
    author='Jimmy Allen',
    author_email='allenjsomb@gmail.com',
    description='A simple async web proxy.',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    python_requires='>=3.10',
)
