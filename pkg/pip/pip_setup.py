from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from distutils.command.install_data import install_data

project_name = "fastHistory"
project_path = "."
license_file="LICENSE"
license="GPLv3+"
description="A python tool connected to your terminal to store important commands and search them in a new and faster way"
url_project="http://github.com/mkcn/fasthistory"
author="Mirko Conti"
author_email="mirko.conti29@gmail.com"
keywords="bash history search fast"
version_file = project_name + "/config/default_version.txt"
readme_file = "README.md"
log_intro="[pip_setup.py]"

try:
	try:
		f = open(version_file, "r")
		version = f.read()
		f.close()
		print("%s version file ok: %s" % (log_intro, version_file))
	except IOError:
		print("%s version file NOT ok: %s" % (log_intro, version_file))
		exit()
		
	try:
		f = open(readme_file, "r")
		readme = f.read()
		f.close()
		print("%s README file ok: %s" % (log_intro, readme_file))
	except IOError:
		print("%s README file NOT ok: %s" % (log_intro, readme_file))
		exit()

	setup(name=project_name,
		version=version,
		# set relative working folder
		#package_dir={'':project_path},
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
			"bashlex>=0.15",
			"pyperclip>=1.8.2"
		],
		package_data={
			'': [ 
				'bash/*.sh',
				#'bin/*',
				'config/default_fastHistory.conf', 
				'config/default_version.txt',
			],
		},
		# all python files to include
		packages=find_packages(where=project_path, exclude=["*unitTests"]),
		entry_points={
			'console_scripts': [
				'f=fastHistory:f',
				'fasthistory=fastHistory:f',
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
	)
	print("%s build done" % (log_intro))

except OSError as e:
	print("OS error: " + e)
except ValueError as e:
	print("Value error: " + e)
except Exception() as e:
	print("Generic error: " + e)

