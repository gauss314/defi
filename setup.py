from setuptools import setup, find_packages


setup(name="defi",
	packages=find_packages() ,
	version="1.0.2", 
	descrription="Tools for use in DeFi", 
	author="Juan Pablo Pisano",
	author_email="jpp.programacion@gmail.com", 
	url="https://github.com/gauss314/defi",
	keywords="defi, impermanent loss, finance, cryptos, bitcoin, liquidity pool, farming, bsc, eth, terra, heco, blockchain " ,
	classifiers=["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: OS Independent"],
	python_requires=">=3.6",
	install_requires=["pandas","matplotlib", "datetime"])