-> Make sure that you don't execute the SBGrid shell script otherwise some python programs get installed in the SBGrid path!
---------------------------------------------------------------------------
Install Homebrew:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
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
  -Note: on Apple Silicon, virtualenv gets installed in /Users/<username>/Library/Python...
------------------------------------------------
Install kivy:

python3 -m pip install "kivy[base] @ https://github.com/kivy/kivy/archive/master.zip"
  -Note: on Apple Silicon, kivy gets installed in /Users/<username>/Library/Python...
------------------------
Install pandas:

pip3 install pandas
  -Note: on Apple Silicon, some pandas scripts get installed in /Users/<username>/Library/Python...
------------------------
Install mrcfile:

pip3 install mrcfile
  -Note: on Apple Silicon, some mrcfile scripts get installed in /Users/<username>/Library/Python...
------------------------
then 'cd' to the pycrest directory
use 'source bin/activate' in pycrest directory
enter 'python3 cresta.py' to open
------------------------
change ChimeraX path to the latest version:

/opt/sbgrid/i386-mac/chimerax/1.5/ChimeraX.app/Contents/bin
---------------------------------------------------------------------------
Use Test_Data and Results folders to confirm that everything works.