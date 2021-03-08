# build file used to generate and install the whl package in a test python environment

installation_python_env="build-env/bin/activate"
version_file="../fastHistory/config/default_version.txt"


# note: manually create $HOME/.pypirc based on the pyirc_template
# https://pypi.org/manage/account/token/
# https://test.pypi.org/manage/account/token/
pypi_upload=false
pypi_domain="pypi.org"
pypi_repo="pypi"

pypi_test_upload=false
pypi_test_domain="test.pypi.org"
pypi_test_repo="testpypi"


if [ -f setup.py ]; then	
	if [ -f $installation_python_env ]; then
		
		source $installation_python_env
		if [ $? -eq 0 ]; then
			echo "the build environment is OK"
		else
			echo "Error: the build environment cannot be used"
			return
		fi

		read -p "Do you wish to upload it to test.pypi.org?[y/N] " YN
		if [[ $YN == "y" || $YN == "Y" ]]; then
			pypi_test_upload=true
			read -p "Upload also to pypi.org ?[y/N] " YN
			if [[ "$YN" == "y" || $YN == "Y" ]]; then
				pypi_upload=true
			fi

			# update version 
			# note: we assume the test pypi always has the more updated version
			version_pypi=$(wget -qO- https://$pypi_domain/pypi/fastHistory/json | python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])")
			regex="([0-9]+).([0-9]+).([0-9]+)"
			if [[ $version_pypi =~ $regex ]]; then
				major="${BASH_REMATCH[1]}"
				minor="${BASH_REMATCH[2]}"
				build="${BASH_REMATCH[3]}"

			  	echo "$pypi_repo current version: ${major}.${minor}.${build}"
				read -p "Is a [M]ajor, [F]eature or [B]UG update?[m/f/B] " C
				if [[ "$C" == "m" || $C == "M" ]]; then
				  major=$(echo $major + 1 | bc)
				  minor=0
				  build=0
				elif [[ "$C" == "f" || $C == "F" ]]; then
				  minor=$(echo $minor + 1 | bc)
				  build=0
				elif [[ "$C" == "b" || $C == "B" || $C == "" ]]; then
				  build=$(echo $build + 1 | bc)
				else
				  echo "wrong input"
				  exit -1
				fi
				echo "new version: ${major}.${minor}.${build}"
				echo -n ${major}.${minor}.${build} > $version_file
			else
				echo "$pypi_repo not found, i will try to use the following local version"
				cat $version_file
			fi
			
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
			echo ""
			# upload
			if $pypi_test_upload; then 
				python3 -m twine upload --repository $pypi_test_repo dist/*.whl
				if $pypi_upload; then
					python3 -m twine upload --repository $pypi_repo dist/*.whl		
				fi
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






