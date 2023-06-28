-> Make sure that you don't execute the SBGrid shell script otherwise some python programs get installed in the SBGrid path!
---------------------------------------------------------------------------
Install Homebrew:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

-Note on Apple Silicon, insert the following line in the .bash_profile file: 
eval "$(/opt/homebrew/bin/brew shellenv)"
------------------------
run:
brew doctor
to make sure that the installation is OK.

If it says that command line tools are outdated, run:

sudo rm -rf /Library/Developer/CommandLineTools
sudo xcode-select --install
------------------------
Install sld2 packages:

brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer 
------------------------
Install python:

brew install python
------------------------
Install virtualenv:

python3 -m pip install --upgrade pip setuptools virtualenv
  -Note: some machines may need to add '--users' to end of above command
------------------------------------------------
Install kivy:

python3 -m pip install "kivy[base] @ https://github.com/kivy/kivy/archive/master.zip"
------------------------
Install pandas:

pip3 install pandas
------------------------
Install scipy:

pip3 install scipy
------------------------
Install scikit-image:

pip3 install scikit-image
------------------------
Install mrcfile and starfile:

pip3 install mrcfile
pip3 install starfile
------------------------
Install matplotlib:

pip3 install matplotlib
------------------------
then 'cd' to the pycrest directory
cc -fPIC -shared -o rot3d.so rot3d.c (enter this in the command line)

enter 'source bin/activate' in pycrest directory
enter 'python3 cresta.py' to open
------------------------
change ChimeraX path to the latest version:

/opt/sbgrid/i386-mac/chimerax/1.5/ChimeraX.app/Contents/bin
---------------------------------------------------------------------------
Use Test_Data and Results folders to confirm that everything works.