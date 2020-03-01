# build file used to generate and install the whl package in a test python environment

installation_python_env="build-env/bin/activate"


if [ -f setup.py ]; then	
	if [ -f $installation_python_env ]; then
		
		source $installation_python_env
		if [ $? -eq 0 ]; then
			echo "the build environment is OK"
		else
			echo "Error: the build environment cannot be used"
			return
		fi
		# clean old dist folder
		rm -f -r dist/*.whl

		# build
		python3 setup.py bdist_wheel

		# clean build folder
		rm -f -r "build"
		rm -f -r ../*.egg-info

		# install from dist folder.
		if [ -f dist/*.whl ]; then
			pip3 install -I dist/*.whl
			echo "Package installed correctly in the local test environment"
			# exit from test env
			#exec $SHELL -l
			# upload 
			# you need to have configured the ".pypirc" file
			echo ""
			read -p "Do you wish to upload it to the test pypi?[Y/n] " YN
			if [[ $YN == "y" || $YN == "Y" || $YN == "" ]]; then
				python3 -m twine upload --repository testpypi dist/*.whl
			else
				echo "Upload skipped"
			fi
		else
			echo "Error: installation stopped, whl file cannot be found"
		fi
	else
		echo "Error: build-env not found. Creation of build-env.."
		DIR=build-env; python3 -m venv $DIR;
		source $installation_python_env
		if [ $? -eq 0 ]; then
			echo OK
			pip3 install setuptools
			pip3 install wheel
			pip3 install twine
			echo "Please try now to run the build again"
		else
			echo "Error: the build environment cannot be created automatically"
		fi
	fi
else
	echo "Error: setup.py file not found. Please execute the build.sh script from the build folder"
fi






