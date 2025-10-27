from setuptools import setup

with open("README.md", "r") as fh: 
	description = fh.read() 

setup( 
	name="pyv2x", 
	version="1.2.1", 
	author="Edoardo Torrini", 
	author_email="edoardo.torrini@gmail.com", 
	packages=[
		"pyv2x",
		"pyv2x.v2x_utils",
		"pyv2x.v2x_network",
	    "pyv2x.v2x_msg"	
	], 
	description="Python package to communicate using v2x", 
	long_description=description, 
	long_description_content_type="text/markdown", 
	url="https://github.com/EdoardoTorrini/pyv2x", 
	license='MIT', 
	python_requires='>=3.8', 
	install_requires=[],
	include_package_data=True,
	package_data={
		"pyv2x": ["etsi_its_header.asn"]
	}
) 
