from setuptools import setup, find_packages

setup(
    name='cloudwatch-dump',
    version='0.0.1',
    description='AWS CloudWatch metrics dumper',
    author='mogproject',
    author_email='mogproj@gmail.com',
    url='http://about.me/mogproject',
    install_requires=[
        'pytz',
        'python-dateutil',
        'boto',
    ],
    tests_require=[
        'moto',
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    test_suite='tests',
    entry_points="""
    [console_scripts]
    cloudwatch-dump = cloudwatchdump.cloudwatchdump:main
    """,
)
