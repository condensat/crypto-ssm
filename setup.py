from setuptools import setup

setup(
    name='crypto-ssm',
    version='0.1',
    packages=['core', 'cli'],
    #include_package_data=True,
    install_requires=['Click==7.0'],
    entry_points={
        'console_scripts': [
            'ssm-cli=cli.cli:cli',
        ],
    },
    description='Simple cli tool for the software secured module',
    author='Condensat',
    license='LGPL3',
)
