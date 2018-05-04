from setuptools import setup

setup(
    name='snips_wa',
    version='1.0.3',
    description='Wolfram Alpha skill for Snips',
    author='Hugh Cole-Baker',
    url='https://github.com/sigmaris/snips-skill-wolframalpha',
    download_url='',
    license='MIT',
    install_requires=['wolframalpha'],
    test_suite="tests",
    keywords=['snips', 'wolfram alpha'],
    py_modules=['snips_wa'],
    entry_points={
        'console_scripts': ['snipswolfram=snips_wa:main'],
    }
)
