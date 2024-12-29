from setuptools import setup, find_packages

setup(
    name="basketball_simulator_agency",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask>=2.0.1',
        'requests>=2.26.0',
        'beautifulsoup4>=4.9.3',
        'psycopg2-binary>=2.9.1',
        'python-dotenv>=0.19.0',
        'agency-swarm>=0.1.0',
        'pydantic>=1.10.13',
        'gunicorn>=20.1.0',
    ],
) 