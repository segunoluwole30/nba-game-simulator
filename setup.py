from setuptools import setup, find_packages

setup(
    name="basketball_simulator_agency",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'agency-swarm>=0.4.2',
        'openai>=1.6.1',
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.2',
        'pandas>=2.1.1',
        'numpy>=1.26.2',
        'psycopg2-binary>=2.9.9',
        'python-dotenv>=1.0.1',
        'instructor>=0.4.5',
        'rich>=13.7.1',
        'termcolor>=2.4.0',
        'docstring_parser>=0.16'
    ]
) 