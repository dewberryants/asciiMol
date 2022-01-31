from setuptools import setup, find_packages

with open('./README.md') as f:
    readme = f.read()

with open('./LICENSE') as f:
    lic = f.read()

packages = find_packages()

setup(
    name='asciimol',
    version='0.1.6',
    description='An ASCII molecule viewer.',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Dominik Behrens',
    author_email='dewberryants@gmail.com',
    install_requires=['numpy'],
    url='https://github.com/dewberryants/asciimol',
    license=lic,
    packages=find_packages(exclude="docs"),
    package_data={"": ["data/*"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Chemistry"
    ],
    entry_points={"console_scripts": ["asciimol = asciimol:run_asciimol"]}
)
