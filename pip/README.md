# requirements

```
sudo apt install python3 python3-pip python3-venv
```

## automatic build mode

### run build script 

```
./build.sh 
```

you may need to run this twice the first time

## manual build mode

### create the build environemnt

```
DIR=build-env; python3 -m venv $DIR;
source build-env/bin/activate
pip3 install setuptools
pip3 install wheel
pip3 install twine
```

### install with local user


```
python3 setup.py bdist_wheel
pip3 install -I dist/*.whl
```

### install for all users

```
python3 setup.py bdist_wheel
sudo pip3 install -I dist/*.whl
```

### uninstall for local user

```
pip3 uninstall fastHistory
```

### uninstall for all users

```
sudo pip3 uninstall fastHistory
```
