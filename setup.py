from setuptools import setup, find_packages

with open('./README.md') as f:
    readme = f.read()

with open('./LICENSE') as f:
    lic = f.read()

packages = find_packages()

setup(
    name='asciimol',
    version='0.1.1',
    description='An ASCII molecule viewer.',
    long_description=readme,
    author='Dominik Behrens',
    author_email='dewberryants@gmail.com',
    url='https://github.com/dewberryants/asciimol',
    license=lic,
    packages=find_packages(exclude="docs"),
    package_data={"": ["data/*"]}
)
