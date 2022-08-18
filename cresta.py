#kivy needed for app
import kivy
kivy.require('2.1.0')

#python packages
import os, subprocess
from subprocess import call
import re
import shutil
import time
import pandas as pd
import numpy as np
import sys
import csv
from pathlib import Path
import math
import glob

#disabling multi-touch kivy emulation
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
#importing necessary kivy features
from kivy.app import App
from kivy.graphics import Canvas, Color
from kivy.lang import Builder
from kivy.properties import ColorProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooser
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput

#importing kivy file
Builder.load_file(os.getcwd() + '/gui.kv')

class Cresta(App):

	def build(self):
		return Tabs()

#giving buttons functionality
class Tabs(TabbedPanel):

	def cwd(self):
		self.ids.maincwd.text = os.getcwd()

	def cwdempty(self):
		if self.ids.maincwd.text == '':
			self.ids.maincwd.text = os.getcwd()

	def starsave(self):
		if self.ids.mainstar.text[0] !=  '/':
			self.ids.mainstar.text = '/' + self.ids.mainstar.text
		if self.ids.starcheck.active == True:
			if self.ids.maincwd.text in self.ids.mainstar.text:
				self.ids.mainstar.text = self.ids.mainstar.text
			else:
				self.ids.mainstar.text = self.ids.maincwd.text + self.ids.mainstar.text
		else:
			if self.ids.maincwd.text in self.ids.mainstar.text:
				self.ids.mainstar.text = self.ids.mainstar.text.replace(self.ids.maincwd.text, '')
			else:
				self.ids.mainstar.text = self.ids.mainstar.text
		self.ids.starstatus.text = 'path saved'
		self.ids.starstatus.color = (0,.6,0,1)

	def triggerstar(self):
		self.ids.starstatus.text = 'path not saved'
		self.ids.starstatus.color = (.6,0,0,1)

	def mrcsave(self):
		if self.ids.mainmrc.text[0] !=  '/':
			self.ids.mainmrc.text = '/' + self.ids.mainmrc.text
		if self.ids.mainmrc.text[-1] !=  '/':
			self.ids.mainmrc.text = self.ids.mainmrc.text + '/'
		if self.ids.mrccheck.active == True:
			if self.ids.maincwd.text in self.ids.mainmrc.text:
				self.ids.mainmrc.text = self.ids.mainmrc.text
			else:
				self.ids.mainmrc.text = self.ids.maincwd.text + self.ids.mainmrc.text
		else:
			if self.ids.maincwd.text in self.ids.mainmrc.text:
				self.ids.mainmrc.text = self.ids.mainmrc.text.replace(self.ids.maincwd.text, '')
			else:
				self.ids.mainmrc.text = self.ids.mainmrc.text
		self.ids.mrcstatus.text = 'path saved'
		self.ids.mrcstatus.color = (0,.6,0,1)

	def triggermrc(self):
		self.ids.mrcstatus.text = 'path not saved'
		self.ids.mrcstatus.color = (.6,0,0,1)

	def savedata(self):
		try:
			if self.ids.save.text[-1] != '/':
				self.ids.save.text = self.ids.save.text + '/'
	#	create text file with saved project data and text inputs
			save = self.ids.save.text + self.ids.savename.text + '.txt'
			file_opt = open(save, 'w')
			file_opt.writelines('Project ' + self.ids.savename.text + '\n')
			file_opt.writelines('Cwd:' + '\t' + self.ids.maincwd.text + '\n')
			file_opt.writelines('StarFile:' + '\t' + self.ids.mainstar.text + '\n')
			file_opt.writelines('StarCheck:' + '\t' + str(self.ids.starcheck.active) + '\n')
			file_opt.writelines('MrcPath:' + '\t' + self.ids.mainmrc.text + '\n')
			file_opt.writelines('MrcCheck:' + '\t' + str(self.ids.mrccheck.active) + '\n')
			file_opt.writelines('BoxSize:' + '\t' + self.ids.px1.text + '\n')
			file_opt.writelines('PxSize:' + '\t' + self.ids.A1.text + '\n')
			file_opt.writelines('ChimeraX:' + '\t' + self.ids.chimera_path.text + '\n')
			file_opt.writelines('ChimeraOutput:' + '\t' + self.ids.chimera_out.text + '\n')
			file_opt.writelines('Index:' + '\t' + self.ids.index.text + '\n')
			file_opt.writelines('Indall:' + '\t' + self.ids.index2.text + '\n')
			file_opt.writelines('SurfaceLvl:' + '\t' + self.ids.surface_level.text + '\n')
			file_opt.writelines('Defocus:' + '\t' + self.ids.defoc.text + '\n')
			file_opt.writelines('SnrFall:' + '\t' + self.ids.snrval.text + '\n')
			file_opt.writelines('Sigma:' + '\t' + self.ids.sigma.text + '\n')
			file_opt.writelines('Filename:' + '\t' + self.ids.filenameget.text + '\n')
			file_opt.writelines('CmmFile:' + '\t' + self.ids.cmmf.text + '\n')
			file_opt.writelines('CoordFile:' + '\t' + self.ids.coordf.text + '\n')
			file_opt.writelines('FirstSuf:' + '\t' + self.ids.suffixt.text + '\n')
			file_opt.writelines('FirstBin:' + '\t' + self.ids.binnt.text + '\n')
			file_opt.writelines('SecondSuf:' + '\t' + self.ids.suffixf.text + '\n')
			file_opt.writelines('SecondBin:' + '\t' + self.ids.binnf.text + '\n')
			file_opt.close()
			self.ids.pullpath.text = save
		except IndexError:
			print('Enter a project directory and name')
	def pulldata(self):
		try:
			load = self.ids.pullpath.text
		#	load existing project information
			with open(load) as pull:
				direct, proj = os.path.split(load)
				self.ids.save.text = direct
				self.ids.savename.text = proj.replace('.txt', '')
				for line in pull:
					pinfo = line.split()
					try:
						yank = pinfo[1]
					except IndexError:
						yank = ''
					if re.search('Cwd', line):
						self.ids.maincwd.text = yank
					if re.search('StarFile', line):
						self.ids.mainstar.text = yank
					if re.search('StarCheck', line):
						self.ids.starcheck.active = eval(yank)
					if re.search('MrcPath', line):
						self.ids.mainmrc.text = yank
					if re.search('MrcCheck', line):
						self.ids.mrccheck.active = eval(yank)
					if re.search('BoxSize', line):
						self.ids.px1.text = yank
					if re.search('PxSize', line):
						self.ids.A1.text = yank
					if re.search('ChimeraX', line):
						self.ids.chimera_path.text = yank
					if re.search('ChimeraOut', line):
						self.ids.chimera_out.text = yank
					if re.search('Index', line):
						self.ids.index.text = yank
					if re.search('Indall', line):
						self.ids.index2.text = yank
					if re.search('SurfaceLvl', line):
						self.ids.surface_level.text = yank
					if re.search('Defocus', line):
						self.ids.defoc.text = yank
					if re.search('SnrFall', line):
						self.ids.snrval.text = yank
					if re.search('Sigma', line):
						self.ids.sigma.text = yank
					if re.search('Filename', line):
						self.ids.filenameget.text = yank
					if re.search('CmmFile', line):
						self.ids.cmmf.text = yank
					if re.search('CoordFile', line):
						self.ids.coordf.text = yank
					if re.search('FirstSuf', line):
						self.ids.suffixt.text = yank
					if re.search('FirstBin', line):
						self.ids.binnt.text = yank
					if re.search('SecondSuf', line):
						self.ids.suffixf.text = yank
					if re.search('SecondBin', line):
						self.ids.binnf.text = yank	
		except FileNotFoundError:
			print('Enter a file path')
		except IsADirectoryError:
			print('Enter a text file')


	def filter_vol(self):
		listName = self.ids.mainstar.text
		direct = self.ids.mainmrc.text
		if self.ids.mainmrc.text[-1] != '/':
			direct = self.ids.mainmrc.text + '/'
		angpix = float(self.ids.A1.text)
		defocus = float(self.ids.defoc.text)
		snrratio = float(self.ids.snrval.text)
		sigval = float(self.ids.sigma.text)
	#	if os.path.exists(listName) == False:
	#		sys.exit('Star file not found')
		filttypebutton = self.ids.wienerbutton.active
	#	set up for filtering
		mySubDirs = os.fsencode(direct)
		for file in os.listdir(mySubDirs):
			filename = os.fsdecode(file)
			if filename.endswith('filt.mrc'):
				os.remove(direct + filename)
		for file in os.listdir(mySubDirs):
			filename = os.fsdecode(file)
			if filename.endswith('.mrc'):
				baseFileName = Path(filename).stem
				fullFileName = direct + filename
				print('Now filtering ' + fullFileName + '\n')
				#new_sub = tom_mrcread(fullFileName)
			#	fopen('/Volumes/atbimac23/20210403MPI/T04/T04_ali.mrc')
			#	wiener button
				if filttypebutton == True:
					highpass = np.linspace(0, 1, 2048)
					highpass2 = []
					for num in highpass:
						low = float(num)/.01
						highpass2.append(min(1, low) * np.pi)
					highpass3 = []
					for num in highpass2:
						highpass3.append(1-math.cos(float(num)))

					ex = np.linspace(0, -1, 2048) * snrratio * 100 / angpix
					ext = []
					for num in ex:
						ext.append(math.exp(float(num)) * 1000)

			#	gaussian button
				#else:
					#subtomo_filt = imgaussfilt3()
				newFileName = direct + baseFileName + '_filt.mrc'
				print('Now writing ' + newFileName + '\n')
			#	tom_mrcwrite()



	def rotate(self):
		print("rotated")

	def zoomcut(self):
		print("zoomed")

	def align(self):
		print("aligned")

	'''def stack(self):
		alignin = self.ids.aligninput.text
		import matlab.engine
		eng = matlab.engine.start_matlab()
		eng.tom_av3_stackbrowser_2(nargout=0)
		# os.system("/Users/psliz05/kivy_venv/tom_av3_stackbrowser_2.fig")
		return'''

	def pick_coord(self):
		ChimeraX_dir = self.ids.chimera_path.text
		listName = self.ids.mainstar.text
		cwd = self.ids.maincwd.text
		direct = self.ids.mainmrc.text
		levels = self.ids.surface_level.text
		pxsz = float(self.ids.A1.text)
		curindex = int(self.ids.index.text)
		self.ids.pickcoordtext.text = 'Please wait. Opening ChimeraX.'
	#	Find the filename for the current index
		pat = '.mrc'
		img = 'ImageName'
		fnlength = 0
		stardom = []
		statstat = 0
		fileNames = open(listName, 'r')
		for line in fileNames:
			if re.search(img, line):
				for m in line:
					if m.isdigit():
						columnstar = int(m) - 1
			if re.search(pat, line):
				fnlength += 1 
				starline = line.split()
				stardex = starline[columnstar]
				stardom.append(stardex)
		flength = str(fnlength)
		self.ids.index2.text = flength
		if curindex < 1 or curindex > fnlength:
			print('The index is outside of the file limits.')
			self.ids.filenameget.text = ""
		else:
			if self.ids.chimera_out.text[0] != '/':
				self.ids.chimera_out.text = '/' + self.ids.chimera_out.text
			if self.ids.chimera_out.text[-1] == '/':
				self.ids.chimera_out.text = self.ids.chimera_out.text.rstrip(self.ids.chimera_out.text[-1])
			if self.ids.codcheck.active == True:
				cmmdir = cwd + self.ids.chimera_out.text
			else:
				cmmdir = self.ids.chimera_out.text
			if os.path.isdir(cmmdir) == False:
				os.mkdir(cmmdir)
			starind = curindex - 1
			starfinal = stardom[starind]
			chim3 = cwd + '/chimcoord.py'
			tmpflnam = direct + starfinal
		#	Creates the script to run Chimera with proper parameters
			file_opt = open(chim3, 'w')
			file_opt.writelines(("import subprocess" + "\n" + "from chimerax.core.commands import run" + "\n" + "run(session, \"cd " + cmmdir + "\")" + "\n" + "run(session, \"open " + tmpflnam + "\")" + "\n" + "run(session, \"set bgColor white;volume #1 level " + levels + ";\")" + "\n" + "run(session, \"color radial #1.1 palette #ff0000:#ff7f7f:#ffffff:#7f7fff:#0000ff center 127.5,127.5,127.5;\")" + "\n" + "run(session, \"ui mousemode right \'mark point\'\")"))
			file_opt.close()
			print(subprocess.getstatusoutput(ChimeraX_dir + '/chimerax chimcoord.py'))
			cmmflip = starfinal.replace('.mrc', '.cmm')
			endfile = os.path.split(cmmflip)
			endcmm = endfile[1]
			self.ids.filenameget.text = starfinal
			if os.path.exists(cmmdir + '/coord.cmm') == True:
				shutil.move(cmmdir + '/coord.cmm', (cmmdir + '/' + endcmm))
				statstat = 1
			else:
				statstat = 0

		if statstat == 1:
			self.ids.pickcoordtext.text = 'Coords saved.'
		else:
			self.ids.pickcoordtext.text = 'No coords selected.'

		self.ids.notecoord.text = ""
		self.ids.notesave.text = ""
		os.remove(chim3)
		return

	def right_pick(self):
		self.ids.index.text = str((int(self.ids.index.text) + 1))
		self.pick_coord()
		return

	def left_pick(self):
		self.ids.index.text = str((int(self.ids.index.text) - 1))
		self.pick_coord()
		return

	def filename(self):
		ChimeraX_dir = self.ids.chimera_path.text
		listName = self.ids.mainstar.text
		cwd = self.ids.maincwd.text
		direct = self.ids.mainmrc.text
		levels = self.ids.surface_level.text
		pxsz = float(self.ids.A1.text)
		curindex = int(self.ids.index.text)
		cmmdir = self.ids.chimera_out.text
		pat = 'Extract'
		img = 'ImageName'
		fnlength = 0
		stardom = []
		fileNames = open(listName, 'r')
		for line in fileNames:
			if re.search(img, line):
				for m in line:
					if m.isdigit():
						columnstar = int(m) - 1
			if re.search(pat, line):
				fnlength += 1 
				starline = line.split()
				stardex = starline[columnstar]
				stardom.append(stardex)
		flength = str(fnlength)
		starind = curindex - 1
		if curindex < 1 or curindex > fnlength:
			print('The index is outside of the file limits.')
			self.ids.filenameget.text = ""
		else:
			starfinal = stardom[starind]
			self.ids.filenameget.text = starfinal
		return

	def note(self):
		cwd = self.ids.maincwd.text
		coordnote = cwd + '/coordpickernote.txt'

		while os.path.exists(cwd + '/coordpickernote.txt') == False:
			file_opt = open(coordnote, 'w')
			file_opt.writelines('index$filename$note')
			file_opt.close()

		file_opt = open(coordnote, 'a')
		file_opt.writelines("\n" + self.ids.index.text + '$' + self.ids.filenameget.text + '$' + self.ids.notecoord.text)
		file_opt.close()
		notedata = pd.read_csv(coordnote, delimiter = '$')
		notedata.to_csv(cwd + '/coordpickernote.csv', index=None)
		self.ids.notesave.text = 'Saved to /coordpickernote.csv'
		return

	def create_coords(self):
		self.cwdempty()
		direct = self.ids.maincwd.text
		boxsize = float(self.ids.px1.text)
		boxsize = boxsize / 2
		pxsz = float(self.ids.A1.text)
		listName = self.ids.mainstar.text
		if self.ids.chimera_coord.text == '':
			self.ids.chimera_coord.text = self.ids.chimera_out.text
		if self.ids.chimera_coord.text[0] !=  '/':
			self.ids.chimera_coord.text = '/' + self.ids.chimera_coord.text
		if self.ids.chimera_coord.text[-1] != '/':
			self.ids.chimera_coord.text = self.ids.chimera_coord.text + '/'
		if self.ids.direcheck.active == True:
			directory = direct + self.ids.chimera_coord.text
		else:
			directory = self.ids.chimera_coord.text
		if self.ids.codcheck.active == True:
			cmmdir = direct + self.ids.chimera_out.text
		else:
			cmmdir = self.ids.chimera_out.text
		if cmmdir[-1] != '/':
			cmmdir = cmmdir + '/'
		if os.path.exists(directory) == False:
			os.mkdir(directory)
		slash, star = os.path.split(listName)
		if os.path.exists(directory + star) == False:
			shutil.copy2((listName),directory)
		if directory[-1] != '/':
			directory = directory + '/'
		directoread = os.fsencode(directory)
		cmmdread = os.fsencode(cmmdir)
		tomoname = directory + 'TomoName.txt'
		file_opt = open(tomoname, 'w')
		file_opt.writelines('')
		file_opt.close()
	#	Removes string of numbers at end of file name
		for file in os.listdir(cmmdread):
			filename = os.fsdecode(file)
			if filename.endswith(".cmm"):
				emanelif = filename[::-1]
				filenam = re.sub('[0-9][0-9][0-9][0-9][0-9][0-9]','',emanelif)
				filenam = filenam[::-1]
				filebase = os.path.splitext(filenam)[0]
				file_opt = open(tomoname, 'a')
				file_opt.writelines(filebase + "\n")
				file_opt.close()
	#	finding all unique tomograms
		lines_seen = set()
		with open(tomoname, 'r+') as tomb:
			d = tomb.readlines()
			tomb.seek(0)
			for i in d:
				if i not in lines_seen:
					tomb.write(i)
					lines_seen.add(i)
			tomb.truncate()
		with open(tomoname) as tom:
			for line in tom:
			#	Makes directory for each different tomogram
				bucket = line.strip()
				if os.path.exists(directory + bucket) == False:
					os.mkdir(directory + bucket)
				Tomo = directory + bucket
				filerun = sorted(os.listdir(cmmdread))
				for file in filerun:
					filename = os.fsdecode(file)
					#	Move each cmm file into the proper tomogram folder
					if filename.endswith(".cmm"):
						if filename[0:3] == bucket[0:3]:
							shutil.move((cmmdir + filename), Tomo)
							with open(Tomo + '/' + filename) as ftomo:
								for line in ftomo:
								#	finding selected coordinates and shifting based on box size
									if re.search('x', line):
										xmid = re.search(' x="(.*)" y', line)
										x_coord = xmid.group(1)
										x_cor = round(boxsize - float(x_coord))
										ymid = re.search(' y="(.*)" z', line)
										y_coord = ymid.group(1)
										y_cor = round(boxsize - float(y_coord))
										zmid = re.search(' z="(.*)" r=', line)
										z_coord = zmid.group(1)
										z_cor = round(boxsize - float(z_coord))
										corx = '_rlnCoordinateX'
										cory = '_rlnCoordinateY'
										corz = '_rlnCoordinateZ'
										Namepos = '_rlnImageName'
										filenoend = filename.replace('.cmm', '')
										fileNames = open(listName, 'r')
									#	finding correct column indexes
										for line in fileNames:
											if re.search(corx, line):
												for m in line:
													if m.isdigit():
														colux = int(m) - 1	
											if re.search(cory, line):
												for m in line:
													if m.isdigit():
														coluy = int(m) - 1		
											if re.search(corz, line):
												for m in line:
													if m.isdigit():
														coluz = int(m) - 1
											if re.search(Namepos, line):
												for m in line:
													if m.isdigit():
														imagefile = int(m) - 1
											if re.search(bucket, line):
												if re.search(filenoend, line):
													starline = line.split()
													roots = starline[imagefile]
													nameroots = roots.replace('.mrc', '.cmm')
													ogx = float(starline[colux])
													ogy = float(starline[coluy])
													ogz = float(starline[coluz])
													finalx = str(round(ogx) - int(x_cor))
													finaly = str(round(ogy) - int(y_cor))
													finalz = str(round(ogz) - int(z_cor))
													if re.search('_filt', line):
														bucket = bucket.replace('_filt', '')
												#	creating files
													file_opt = open(Tomo + '/' + bucket + '.coordsnew', 'a')
													file_opt.writelines(finalx + ' ' + finaly + ' ' + finalz + '\n')
													file_opt.close()
													file_opt = open(Tomo + '/' + 'NameCoord.txt', 'a')
													file_opt.writelines(nameroots + '\n')
													file_opt.close()
													file_opt = open(Tomo + '/' + bucket + '.shift', 'a')
													file_opt.writelines(finalx + ' ' + finaly + ' ' + finalz + '\t' + 'filename' + '\n')
													file_opt.close()
		os.remove(tomoname)
		return

	def parse(self):
		self.cwdempty()
		if self.ids.parscheck.active == True:
			starpar = self.ids.maincwd.text + self.ids.restar.text
		else:
			starpar = self.ids.restar.text
		if self.ids.reout.text[-1] != '/':
			self.ids.reout.text = self.ids.reout.text + '/'
		if self.ids.parsoutcheck.active == True:
			outpar = self.ids.maincwd.text + self.ids.reout.text
		else:
			outpar = self.ids.reout.text
		if os.path.exists(outpar) == False:
			os.mkdir(outpar)
		xstar = '_rlnCoordinateX'
		ystar = '_rlnCoordinateY'
		zstar = '_rlnCoordinateZ'
		microstar = '_rlnMicrographName'
		micronames = outpar + 'microname.txt'
		file_opt = open(micronames, 'w')
		file_opt.write('')
		file_opt.close()
	#	finding correct column indexes
		with open(starpar) as par:
			for line in par:
				if re.search(xstar, line):
					xcol = re.findall(r'\d+', line)
					xcol = int(xcol[0]) - 1
				if re.search(ystar, line):
					ycol = re.findall(r'\d+', line)
					ycol = int(ycol[0]) - 1	
				if re.search(zstar, line):
					zcol = re.findall(r'\d+', line)
					zcol = int(zcol[0]) - 1
				if re.search(microstar, line):
					microcol = re.findall(r'\d+', line)
					microcol = int(microcol[0]) - 1
				if re.search('.mrc', line):
					fold = line.split()
					unique = fold[microcol]
					file_opt = open(micronames, 'a')
					file_opt.write(unique + '\n')
					file_opt.close()
	#	searching for unique tomograms
		lines_seen = set()
		with open(micronames, 'r+') as tomb:
			d = tomb.readlines()
			tomb.seek(0)
			for i in d:
				if i not in lines_seen:
					tomb.write(i)
					lines_seen.add(i)
			tomb.truncate()
		with open(micronames) as stap:
			for line in stap:
				tine = line.strip()
				fine = tine.replace('\n', '')
				ending = fine.rsplit('/', 1)[-1]
				vine = ending.replace('.mrc', '')
				if re.search('_filt', vine):
					vine = vine.replace('_filt', '')
				edge = outpar + vine + '_subcoord.coord'
				file_opt = open(edge, 'w')
				file_opt.writelines('')
				file_opt.close()
				with open(starpar) as rats:
					for line in rats:
						if re.search(fine, line):
							sline = line.split()
						#	extracting the correct values
							xst = str(int(float(sline[xcol])))
							yst = str(int(float(sline[ycol])))
							zst = str(int(float(sline[zcol])))
							allcooc = xst + '\t' + yst + '\t' + zst + '\t'
							if int(xst) < 800 and int(yst) < 800 and int(zst) < 800:
								print('WARNING: Double check that files in ' + vine + ' are binned!')
						#	create the coord file
							file_opt = open(edge, 'a')
							if self.ids.cooc.active == True:
								file_opt.writelines(allcooc)
							if self.ids.othercols.text != '':
								other = self.ids.othercols.text
								parts = other.split(',')
								for item in parts:
									if len(item) > 0:
										spot = int(item)
										spod = spot - 1
										info = sline[spod]
										file_opt.writelines(info + '\t')
							file_opt.writelines('\n')
							file_opt.close()
		os.remove(micronames)
		return



	def path_1(self):
		self.ids.cmmf.text = self.ids.chimera_out.text
		if self.ids.cmmf.text[0] !=  '/':
			self.ids.cmmf.text = '/' + self.ids.cmmf.text
		return

	def calculate_ang(self):
		self.cwdempty()
		star = self.ids.mainstar.text
		self.ids.coordf.text = self.ids.coordf.text.strip()
		if self.ids.coordf.text[-1] != '/':
			self.ids.coordf.text = self.ids.coordf.text + '/'
		CoordDir = self.ids.coordf.text
		Suffix = self.ids.suffixf.text
		Bin = self.ids.binnf.text
		Suffixt = self.ids.suffixt.text
		Bint = self.ids.binnt.text
		head, tail = os.path.split(star)
		if head[-1] != '/':
			head = head + '/'
		if self.ids.calcoutcheck.active == True:
			Out = self.ids.maincwd.text + self.ids.outputp.text
		else:
			Out = self.ids.outputp.text
		cwd = self.ids.maincwd.text
		if self.ids.dircmmcheck.active == True:
			CMMDir = self.ids.maincwd.text + self.ids.cmmf.text
		else:
			CMMDir = self.ids.cmmf.text
		Cresta_dir = cwd + '/CRESTA_files'
		if os.path.exists(Out) == False:
			os.mkdir(Out)
		tempo = Out
		if os.path.exists(tempo + '/temp') == False:
			os.mkdir(tempo + '/temp')
		tempy = tempo + '/temp'
		starfile = star
	#	This gets the positions of micrograph name, and original x y and z coordinates from the star file
		with open(starfile) as bigstar:
			corx = '_rlnCoordinateX'
			cory = '_rlnCoordinateY'
			corz = '_rlnCoordinateZ'
			image = '_rlnImageName'
			micrograph = '_rlnMicrographName'
			optics = '_rlnOpticsGroup'
			groupno = '_rlnGroupNumber'
			anglerot = '_rlnAngleRot'
			angletil = '_rlnAngleTilt'
			anglepsi = '_rlnAnglePsi'
			for line in bigstar:
				if re.search(corx, line):
					Xpos = re.findall(r'\d+', line)
					Xpos = int(Xpos[0]) - 1	
				if re.search(cory, line):
					Ypos = re.findall(r'\d+', line)
					Ypos = int(Ypos[0]) - 1		
				if re.search(corz, line):
					Zpos = re.findall(r'\d+', line)
					Zpos = int(Zpos[0]) - 1
				if re.search(image, line):
					Namepos = re.findall(r'\d+', line)
					Namepos = int(Namepos[0]) - 1
				if re.search(micrograph, line):
					Micropos = re.findall(r'\d+', line)
					Micropos = int(Micropos[0]) - 1
				if re.search(optics, line):
					Opticspos = re.findall(r'\d+', line)
					Opticspos = int(Opticspos[0]) - 1
				if re.search(groupno, line):
					Groupnopos = re.findall(r'\d+', line)
					Groupnopos = int(Groupnopos[0]) - 1
				if re.search(anglerot, line):
					Rotpos = re.findall(r'\d+', line)
					Rotpos = int(Rotpos[0]) - 1
				if re.search(angletil, line):
					Tilpos = re.findall(r'\d+', line)
					Tilpos = int(Tilpos[0]) - 1
				if re.search(anglepsi, line):
					Psipos = re.findall(r'\d+', line)
					Psipos = int(Psipos[0]) - 1
	#	Makes new file without headers called decapitated.txt
		line_length = 0
		with open(starfile) as bigstar:
			for line in bigstar:
				if (len(line) > line_length):
					line_length = len(line)
		line_length = line_length - 5
		smallstar = tempy + '/decapitated.txt'
		file_opt = open(smallstar, 'w')
		file_opt.writelines('')
		file_opt.close()
		with open(starfile) as bigstar:
			for line in bigstar:
				if len(line) >= line_length:
					file_opt = open(smallstar, 'a')
					file_opt.writelines(line)
					file_opt.close()
	#	break txt into just the lines regarding our specific file
		smalleststar = tempy + '/capped.txt'
		file_opt = open(smalleststar, 'w')
		file_opt.writelines('')
		file_opt.close()
		openup = CMMDir
		back, actual = os.path.split(openup)
		for line in open(smallstar, 'r'):
			if re.search(actual, line):
				file_opt = open(smalleststar, 'a')
				file_opt.writelines(line)
				file_opt.close()	
	#	find which line numbers we are focusing on
		numbers = []
		findcmm = os.fsencode(openup)
		for file in os.listdir(findcmm):
			filename = os.fsdecode(file)
			if filename.endswith('.cmm'):
				filenoend = filename.replace('.cmm', '')
				with open(smalleststar) as cap:
					for num, line in enumerate(cap, 1):
						if filenoend in line:
							numbers.append(num)
		if self.ids.otherdir.active == False:
	#	create a file with the original coords
			tinystar = tempy + '/ogcor.txt'
			file_opt = open(tinystar, 'w')
			file_opt.writelines('')
			file_opt.close()
			with open(smalleststar) as cap:
				for line in cap:
					capsplit = line.split()
					XCor = capsplit[Xpos]
					YCor = capsplit[Ypos]
					ZCor = capsplit[Zpos]
					file_opt = open(tinystar, 'a')
					file_opt.writelines(XCor + '$' + YCor + '$' + ZCor + '\n')
					file_opt.close()
		else:
			tinystar = tempy + '/ogcor.txt'
			file_opt = open(tinystar, 'w')
			file_opt.writelines('')
			file_opt.close()
			firstact = actual[0:3]
			suffixfolder = os.fsencode(CoordDir)
			for file in os.listdir(suffixfolder):
				filename = os.fsdecode(file)
				if re.search(firstact, filename):
					if re.search(Suffix, filename):
						with open(CoordDir + filename, 'r') as suffixtext:
							for line in suffixtext:
								capsplit = line.split()
								XCor = str(round(float(capsplit[0]) * float(Bint)))
								YCor = str(round(float(capsplit[1]) * float(Bint)))
								ZCor = str(round(float(capsplit[2]) * float(Bint)))
								file_opt = open(tinystar, 'a')
								file_opt.writelines(XCor + '$' + YCor + '$' + ZCor + '\n')
								file_opt.close()
	#	get the suffix file coords binned
		allbinned = tempy + '/bincor.txt'
		file_opt = open(allbinned, 'w')
		file_opt.writelines('')
		file_opt.close()
		firstact = actual[0:3]
		suffixfolder = os.fsencode(CoordDir)
		for file in os.listdir(suffixfolder):
			filename = os.fsdecode(file)
			if re.search(firstact, filename):
				if re.search(Suffix, filename):
					with open(CoordDir + filename, 'r') as suffixtext:
						for line in suffixtext:
							diffchar = line.split()
							getbinned = str(round(float(diffchar[0]) * float(Bin)))
							getbinned1 = str(round(float(diffchar[1]) * float(Bin)))
							getbinned2 = str(round(float(diffchar[2]) * float(Bin)))
							file_opt = open(allbinned, 'a')
							file_opt.writelines(getbinned + '$' + getbinned1 + '$' + getbinned2 + '\n')
							file_opt.close()
	#	narrow down coords to our files
		final = tempy + '/final.txt'
		file_opt = open(final, 'w')
		file_opt.writelines('')
		file_opt.close()
		for item in numbers:
			with open(smalleststar) as cap:
				eachcap = cap.readlines()
				savecap = eachcap[item - 1]
				savecap = savecap.split()
				Tomname = savecap[Namepos]
			with open(tinystar) as og:
				eachog = og.readlines()
				Tomog = eachog[item - 1]
				Tomog = Tomog.replace('\n', '')
			with open(allbinned) as binn:
				eachbin = binn.readlines()
				Tombin = eachbin[item - 1]
				Tombin = Tombin.replace('\n', '')
			file_opt = open(final, 'a')
			file_opt.writelines(Tomname + '$' + Tomog + '$' + Tombin + '\n')
			file_opt.close()
	#	make the data into csv file
		centers2data = pd.read_csv(final, delimiter = '$')
		centers2data.to_csv(tempo + '/centers2data.csv', index=None)
	#	get euler angles script
		print(subprocess.getstatusoutput('python3 ' + cwd + '/transform_project_JL.py ' + 'calcangles --csv ' + tempo + '/centers2data.csv ' + '--outdir ' + tempo))
		nounds = tempo + '/neweulerangs_round.csv'
		nanc = tempo + '/neweulerangs.csv'
		nangnames = 0
		with open(nanc, 'r') as nangs, open(nounds, 'w') as nound:
			reader = csv.reader(nangs, delimiter = ',')
			writer = csv.writer(nound, delimiter = ',')
			for row in reader:
				with open(smalleststar) as cap:
					rownum = numbers[nangnames]
					eachcap = cap.readlines()
					savecap = eachcap[rownum - 1]
					savecap = savecap.split()
					Tomname = savecap[Namepos]
				colValues = []
				for col in row:
					colValues.append(round(float(col), 2))
				colValues.append(Tomname)
				writer.writerow(colValues)
				nangnames = nangnames + 1
		os.rename(nounds, nanc)
		AllTomo = os.fsencode(openup)
		Tomo = actual
		if re.search('_filt', Tomo):
			Tomo = Tomo.replace('_filt', '')
		if os.path.exists(tempy + '/' + Tomo + '_expanded.txt'):
			os.remove(tempy + '/' + Tomo + '_expanded.txt')
		expanded = tempy + '/' + Tomo + '_expanded.txt'
	#	make file names unique based on having multiple coordinates
		with open(openup + '/NameCoord.txt') as names:
			seenline = set()
			rep = 1
			iteratesh = 0
			for line in names:
				line = line.replace('\n', '')
				if line in seenline:
					rep = rep + 1
				else:
					rep = 1
				swap = re.sub('.cmm', '.mrc', line)
				expand = re.sub('_filt', '_' + str(rep) + '_filt', swap)
				seenline.add(line)
				with open(openup + '/' + Tomo + '.shift') as shiftfile:
					focus = shiftfile.readlines()
					theline = focus[iteratesh]
					expund = theline.replace('filename', expand)
					expund = expund.replace('\n', '')
					with open(starfile) as starry:
						for line in starry:
							if re.search(swap, line):
								fract = line.split()
								microname = fract[Micropos]
								optic = fract[Opticspos]
					with open(nanc) as findang:
						for line in findang:
							if re.search(swap, line):
								broke = line.split(',')
								Rot = broke[0]
								Tilt = broke[1]
								Psi = broke[2]
								angle = Rot + '\t' + Tilt + ' \t' + Psi
					file_opt = open(expanded, 'a')
					file_opt.writelines(expund + '\t' + microname + '\t' + optic + '\t' + angle + '\n')
					file_opt.close()
					iteratesh = iteratesh + 1
		newstar = tempo + '/' + Tomo + '_Newstar.star'
		file_opt = open(newstar, 'w')
		file_opt.writelines('')
		file_opt.close()
	#	get rid of all temp files
		os.rename(expanded, newstar)
		os.remove(nanc)
		os.remove(tempo + '/centers2data.csv')
		os.remove(smallstar)
		os.remove(smalleststar)
		os.remove(tinystar)
		os.remove(allbinned)
		os.remove(final)
		os.rmdir(tempy)
		return

	def mask(self):
		return

	def volume(self):
		return

	def reextract(self):
		return

	def calculate_ccc(self):
		return

	def filter_ccc(self):


		return

	pass


#run CrESTA
Cresta().run()
