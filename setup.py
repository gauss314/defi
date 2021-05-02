from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name="defi",
	packages=find_packages() ,
	version="1.0.15", 
	descrription="Tools for use in DeFi", 
	long_description = long_description,
	long_description_content_type = "text/markdown",
	author="Juan Pablo Pisano",
	author_email="jpp.programacion@gmail.com", 
	url="https://github.com/gauss314/defi",
	keywords="defi, impermanent loss, finance, cryptos, bitcoin, liquidity pool, farming, bsc, eth, terra, heco, blockchain " ,
	classifiers=["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: OS Independent"],
	python_requires=">=3.6",
	install_requires=["pandas","matplotlib", "datetime","requests","scipy","numpy"])
