from setuptools import setup, find_packages

setup(
    name='koftipy',
    version='0.0.1',
    author='Ovunc Cetin',
    author_email='ovunccetin@gmail.com',
    description='A library bringing functional features to Python',
    license='Apache',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License v2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
