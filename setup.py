from setuptools import setup, find_packages


setup(name="juanpy",
	packages=find_packages() ,
	version="1.0.0", 
	descrription="Paquete de pruebas curso Ullua", 
	author="Juan Pablo Pisano",
	author_email="jpp.programacion@gmail.com", 
	url="https://github.com/gauss314/juanpy",
	keywords="Ullua, El taco no, manteca" ,
	classifiers=["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: OS Independent"],
	python_requires=">=3.6",
	install_requires=["pandas","matplotlib", "yfinance", "datetime"])