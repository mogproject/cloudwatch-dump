from setuptools import setup, find_packages

SRC_DIR = 'src'


def get_version():
    import sys

    sys.path[:0] = [SRC_DIR]
    return __import__('cloudwatch_dump.cloudwatch_dump').__version__


setup(
    name='cloudwatch-dump',
    version=get_version(),
    description='AWS CloudWatch metrics dumper',
    author='mogproject',
    author_email='mogproj@gmail.com',
    url='https://github.com/mogproject/cloudwatch-dump',
    install_requires=[
        'pytz',
        'python-dateutil',
        'boto',
    ],
    tests_require=[
        'moto',
    ],
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    test_suite='tests',
    entry_points="""
    [console_scripts]
    cloudwatch-dump = cloudwatch_dump.cloudwatch_dump:main
    """,
)
