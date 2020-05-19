from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from distutils.command.install_data import install_data

project_name = "fastHistory"
project_path = "../"
license_file="LICENSE"
license="GPLv3+"
description="A python tool connected to your terminal to store important commands and search them in a new and faster way"
url_project="http://github.com/mkcn/fasthistory"
author="Mirko Conti"
author_email="mirko.conti29@gmail.com"
keywords="bash history search fast"
version_file = project_path + project_name + "/config/default_version.txt"
readme_file = project_path + "README.md"

try:
	f = open(version_file, "r")
	version = f.read()
	f.close()

	f = open(readme_file, "r")
	readme = f.read()
	f.close()

	setup(name=project_name,
		version=version,
		# set relative working folder
		package_dir={'':project_path},
		description=description,
		long_description=readme,
		long_description_content_type="text/markdown",
		url=url_project,
		author=author,
		keywords=keywords,
		author_email=author_email,
		license=license,
		platforms='OS-independent',
		# dependeces
		install_requires=[
			"bashlex>=0.14",
			"pyperclip>=1.7.0"
		],
		# all data files to include 
		package_data={
			'': [ 
				'bash/*.sh',
				'config/default_fastHistory.conf', 
				'config/default_version.txt',
			],
		},
		# all python files to include
		packages=find_packages(where=project_path, exclude=["*unitTests"]),
		entry_points={
			'console_scripts': [
				'f=fastHistory:f',
			]
		},
		# https://pypi.org/classifiers/
		classifiers=[
			'Development Status :: 5 - Production/Stable',
			'Intended Audience :: Developers',
			'Intended Audience :: System Administrators',
			'Intended Audience :: End Users/Desktop',
			'Natural Language :: English',
			'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
			'Operating System :: OS Independent',
			'Programming Language :: Python',
			'Programming Language :: Python :: 3',
		    ],
		#scripts=[project_path + '/bash/setup'],
		#setup_requires=['setup'],
		#license_file=license_file_path,
	)

except OSError:
	print("version file not found; " + version_file)
except ValueError:
	print("version is not a valid float. Fix your version file: " + version_file)


