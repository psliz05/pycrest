
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
from scipy.fftpack import fftn, ifftn, ifftshift
import starfile
import mrcfile
import sys
import csv
from pathlib import Path
import math
import glob
import matplotlib.pyplot as plt
import weakref
from datetime import timedelta
import random
import mrcfile
import starfile

#import tom.py
import tom

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
from kivy.core.window import Window
Window.size = (900,800)

#importing kivy file
Builder.load_file(os.getcwd() + '/gui.kv')

class Cresta(App):

	def build(self):
		self.icon = 'bin/crestalogo.png'
		self.title = 'CrESTA'
		return Tabs()

#giving buttons functionality
class Tabs(TabbedPanel):
	
	label = Label(text="Sigma")
	label2 = Label(text=" ", size_hint_y=.8)
	sigma = TextInput(text="5", multiline=False, size_hint_x=.12, size_hint_y=1.9, pos_hint={'center_x': .5, 'center_y': .5})

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
		self.ids.mainsubtomo.text = "/".join(self.ids.mainstar.text.split("/")[:-1])
		self.ids.starstatus.text = 'path saved'
		self.ids.starstatus.color = (0,.6,0,1)

	def triggerstar(self):
		self.ids.starstatus.text = 'path not saved'
		self.ids.starstatus.color = (.6,0,0,1)

	def subtomosave(self):
		if self.ids.mainsubtomo.text[0] !=  '/':
			self.ids.mainsubtomo.text = '/' + self.ids.mainsubtomo.text
		if self.ids.mainsubtomo.text[-1] !=  '/':
			self.ids.mainsubtomo.text = self.ids.mainsubtomo.text + '/'
		if self.ids.subtomocheck.active == True:
			if self.ids.maincwd.text in self.ids.mainsubtomo.text:
				self.ids.mainsubtomo.text = self.ids.mainsubtomo.text
			else:
				self.ids.mainsubtomo.text = self.ids.maincwd.text + self.ids.mainsubtomo.text
		else:
			if self.ids.maincwd.text in self.ids.mainsubtomo.text:
				self.ids.mainsubtomo.text = self.ids.mainsubtomo.text.replace(self.ids.maincwd.text, '')
			else:
				self.ids.mainsubtomo.text = self.ids.mainsubtomo.text
		self.ids.subtomostatus.text = 'path saved'
		self.ids.subtomostatus.color = (0,.6,0,1)

	def triggersubtomo(self):
		self.ids.subtomostatus.text = 'path not saved'
		self.ids.subtomostatus.color = (.6,0,0,1)

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
			self.ids['sigma'] = weakref.ref(Tabs.sigma)
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
			file_opt.writelines('Index:' + '\t' + self.ids.index.text + '\n')
			file_opt.writelines('Indall:' + '\t' + self.ids.index2.text + '\n')
			file_opt.writelines('SurfaceLvl:' + '\t' + self.ids.surface_level.text + '\n')
			file_opt.writelines('Defocus:' + '\t' + self.ids.defoc.text + '\n')
			file_opt.writelines('SnrFall:' + '\t' + self.ids.snrval.text + '\n')
			file_opt.writelines('Sigma:' + '\t' + self.ids.sigma.text + '\n')
			file_opt.writelines('Filename:' + '\t' + self.ids.filenameget.text + '\n')
			file_opt.writelines('CoordFile:' + '\t' + self.ids.coordf.text + '\n')
			file_opt.writelines('FirstSuf:' + '\t' + self.ids.suffixt.text + '\n')
			file_opt.writelines('FirstBin:' + '\t' + self.ids.binnt.text + '\n')
			file_opt.writelines('SecondSuf:' + '\t' + self.ids.suffixf.text + '\n')
			file_opt.writelines('SecondBin:' + '\t' + self.ids.binnf.text + '\n')
			file_opt.writelines('MaskPath:' + '\t' + self.ids.maskpath.text + '\n')
			file_opt.writelines('SDThresh:' + '\t' + self.ids.sdrange.text + '\n')
			file_opt.writelines('SDShift:' + '\t' + self.ids.sdshift.text + '\n')
			file_opt.writelines('MaskBlur:' + '\t' + self.ids.blurrate.text + '\n')
			file_opt.writelines('CCCVolone:' + '\t' + self.ids.cccvolone.text + '\n')
			file_opt.writelines('CCCVoltwo:' + '\t' + self.ids.cccvoltwo.text + '\n')
			file_opt.writelines('CCCWedge:' + '\t' + self.ids.cccwedge.text + '\n')
			file_opt.writelines('Volvol:' + '\t' + self.ids.volvol.text + '\n')
			file_opt.writelines('Volwedge:' + '\t' + self.ids.volwedge.text + '\n')
			file_opt.close()
			self.ids.pullpath.text = save
		except IndexError:
			print('Enter a project directory and name')

	def pulldata(self):
		try:
			self.ids['sigma'] = weakref.ref(Tabs.sigma)
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
					if re.search('MaskPath', line):
						self.ids.maskpath.text = yank	
					if re.search('SDThresh', line):
						self.ids.sdrange.text = yank
					if re.search('SDShift', line):
						self.ids.sdshift.text = yank	
					if re.search('MaskBlur', line):
						self.ids.blurrate.text = yank	
					if re.search('CCCVolone', line):
						self.ids.cccvolone.text = yank
					if re.search('CCCVoltwo', line):
						self.ids.cccvoltwo.text = yank
					if re.search('CCCWedge', line):
						self.ids.cccwedge.text = yank
					if re.search('Volvol', line):
						self.ids.volvol.text = yank
					if re.search('Volwedge', line):
						self.ids.volwedge.text = yank
		except FileNotFoundError:
			print('Enter a file path')
		except IsADirectoryError:
			print('Enter a text file')

	def show_screen(self):
		self.ids.first_row_wiener.clear_widgets()
		self.ids.second_row_wiener.clear_widgets()
		self.ids.gaussian_row.clear_widgets()
		
		if self.ids.wienerbutton.active == True:
			self.ids.first_row_wiener.add_widget(self.ids.boxone)
			self.ids.first_row_wiener.add_widget(self.ids.boxtwo)
			self.ids.first_row_wiener.add_widget(self.ids.boxthree)
			self.ids.first_row_wiener.add_widget(self.ids.boxfour)
			self.ids.second_row_wiener.add_widget(self.ids.boxfive)
			self.ids.second_row_wiener.add_widget(self.ids.boxsix)
			self.ids.second_row_wiener.add_widget(self.ids.boxseven)
			self.ids.second_row_wiener.add_widget(self.ids.boxeight)

		if self.ids.gaussianbutton.active == True:
			self.ids.gaussian_row.add_widget(Tabs.label)
			self.ids.gaussian_row.add_widget(Tabs.label2)
			self.ids.gaussian_row.add_widget(Tabs.sigma)

		if not(self.ids.wienerbutton.active) and not(self.ids.gaussianbutton.active):
			text = Label(text="Please select a filter")
			self.ids.gaussian_row.add_widget(text)
	

	plt.ion()

	def filter_vol(self):
		try:
			self.ids['sigma'] = weakref.ref(Tabs.sigma)
			direct = self.ids.mainmrc.text
			if self.ids.mainmrc.text[-1] != '/':
				direct = self.ids.mainmrc.text + '/'
			wienerbutton = self.ids.wienerbutton.active
			gaussianbutton = self.ids.gaussianbutton.active
			angpix = float(self.ids.A1.text)
			defoc = float(self.ids.defoc.text)
			snrratio = float(self.ids.snrval.text)
			highpassnyquist = float(self.ids.highpass.text)
			if gaussianbutton == True:
				sigval = float(self.ids.sigma.text)
			voltage = float(self.ids.voltage.text)
			cs = float(self.ids.cs.text)
			envelope = float(self.ids.envelope.text)
			bfactor = float(self.ids.bfactor.text)
			phasebutton = self.ids.phaseflip.active
			starf = self.ids.mainstar.text
			subtomodir = self.ids.mainsubtomo.text
			mrcButton = self.ids.mrcfilter.active
			starButton = self.ids.starfilter.active

			if wienerbutton == False and gaussianbutton == False:
				print("At least one option needs to be selected.")
			imageFileNames = starfile.read(starf)["particles"]["rlnImageName"]
		#	wiener
			if wienerbutton == True:
				if starButton:
					for fileName in imageFileNames:
						# create folder
						folderPath = "/".join(fileName.split("/")[:-1]) + "/"
						filterout = subtomodir + folderPath + 'filtered/'
						if os.path.exists(filterout) == False:
							os.mkdir(filterout)

						print('Now filtering ' + fileName)
						fullFilePath = subtomodir + fileName

						# read .mrc file and apply filter
						mrc = mrcfile.read(fullFilePath)
						
						subtomo_filt = tom.deconv_tomo(mrc, angpix, defoc, snrratio, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton)
						subtomo_filt = subtomo_filt.astype('float32')

						# write filtered .mrc file
						baseFileName = fullFilePath.split("/")[-1].split(".")[0]
						newFileName = os.path.join(filterout, baseFileName + '_wiener.mrc')
						print('Now writing ' + newFileName)
						mrcfile.new(newFileName, subtomo_filt, overwrite = True)
						with mrcfile.open(newFileName, 'r+') as mrc:
							header = mrc.header
						header.cella = (angpix, angpix, angpix)

					#constructs star file
					star_data = starfile.read(starf)
					df = pd.DataFrame.from_dict(star_data["particles"])

					def replaceName(s):
						s = s.split("/")
						s.insert(-1, 'filtered')
						s = '/'.join(s)
						return s
					
					def addWiener(s):
						s = s.split("/")
						s[-1] = s[-1].split(".")[0] + "_wiener.mrc"
						s = '/'.join(s)
						return s
			
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: replaceName(x))
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: addWiener(x))
					star_data["particles"] = df
					starfile.write(star_data, subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered' + ".star", overwrite=True)

				elif mrcButton:
					# create folder
					filterout = direct + 'filtered/'
					if os.path.exists(filterout) == False:
						os.mkdir(filterout)
					# apply filter to all .mrc files in the folder
					myFiles = [f for f in os.listdir(direct) if f.endswith(".mrc")]
					for f in myFiles:
						fullFileName = os.path.join(direct, f)
						print('Now filtering ' + fullFileName)

						# read .mrc file and apply filter
						mrc = mrcfile.read(fullFileName)
						
						subtomo_filt = tom.deconv_tomo(mrc, angpix, defoc, snrratio, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton)
						subtomo_filt = subtomo_filt.astype('float32')

						# write filtered .mrc file
						baseFileName, extension = os.path.splitext(f)
						newFileName = os.path.join(filterout, baseFileName + '_wiener.mrc')
						print('Now writing ' + newFileName)
						mrcfile.new(newFileName, subtomo_filt, overwrite = True)

				plt.show(block=False)

		#	gaussian
			if gaussianbutton == True:
				from scipy.ndimage import gaussian_filter
				if starButton:
					for fileName in imageFileNames:
						# create folder
						folderPath = "/".join(fileName.split("/")[:-1]) + "/"
						filterout = subtomodir + folderPath + 'filtered/'
						if os.path.exists(filterout) == False:
							os.mkdir(filterout)
						
						print('Now filtering ' + fileName)
						fullFilePath = subtomodir + fileName

						# read .mrc file and apply filter
						mrc = mrcfile.read(fullFilePath)
						subtomo_filt = gaussian_filter(mrc, sigma=sigval)

						# write filtered .mrc file
						baseFileName = fullFilePath.split("/")[-1].split(".")[0]
						newFileName = os.path.join(filterout, baseFileName + '_gauss.mrc')
						print('Now writing ' + newFileName)
						mrcfile.new(newFileName, subtomo_filt, overwrite = True)

					#constructs star file
					star_data = starfile.read(starf)
					df = pd.DataFrame.from_dict(star_data["particles"])

					def replaceName(s):
						s = s.split("/")
						s.insert(-1, 'filtered')
						s = '/'.join(s)
						return s
					
					def addGaussian(s):
						s = s.split("/")
						s[-1] = s[-1].split(".")[0] + "_gauss.mrc"
						s = '/'.join(s)
						return s
			
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: replaceName(x))
					df.loc[:, "rlnImageName"] = df.loc[:, "rlnImageName"].apply(lambda x: addGaussian(x))
					star_data["particles"] = df
					starfile.write(star_data, subtomodir + starf.split("/")[-1].split(".")[0] + '_filtered' + ".star", overwrite=True)
				elif mrcButton:
					# create folder
					filterout = direct + 'filtered/'
					if os.path.exists(filterout) == False:
						os.mkdir(filterout)
					# apply filter to all .mrc files in the folder
					myFiles = [f for f in os.listdir(direct) if f.endswith(".mrc")]
					for f in myFiles:
						fullFileName = os.path.join(direct, f)
						print('Now filtering ' + fullFileName)

						# read .mrc file and apply filter
						mrc = mrcfile.read(fullFileName)
						subtomo_filt = gaussian_filter(mrc, sigma=sigval)

						# write filtered .mrc file
						baseFileName, extension = os.path.splitext(f)
						newFileName = os.path.join(filterout, baseFileName + '_gauss.mrc')
						print('Now writing ' + newFileName)
						mrcfile.new(newFileName, subtomo_filt, overwrite = True)

		except FileNotFoundError:
			print("This directory does not exist")

	def pick_coord(self):
		try:
			# initialize variables
			ChimeraX_dir = self.ids.chimera_path.text
			listName = self.ids.mainstar.text
			direct = self.ids.mainsubtomo.text
			if self.ids.mainsubtomo.text[-1] != '/':
				direct = self.ids.mainsubtomo.text + '/'
			levels = self.ids.surface_level.text
			pxsz = float(self.ids.A1.text)
			curindex = int(self.ids.index.text)
			self.ids.pickcoordtext.text = 'Please wait. Opening ChimeraX.'
		#	Find the filename and tomogram name for the current index
			imageNames = starfile.read(listName)["particles"]["rlnImageName"]
			folderNames = starfile.read(listName)["particles"]["rlnMicrographName"]
			starfinal = imageNames[curindex - 1]
			tomoName = folderNames[curindex - 1]
			tomoName = tomoName.split('/')[0] + '/' + tomoName.split('/')[1]
			# set total index value
			self.ids.index2.text = str(len(imageNames))

			# create cmm_files folder inside subtomogram directory specified on master key
			cmmdir = direct + 'cmm_files'
			if os.path.isdir(cmmdir) == False:
				os.mkdir(cmmdir)

			# create and run python script to open ChimeraX
			chim3 = direct + 'chimcoord.py'
			tmpflnam = direct + starfinal
			file_opt = open(chim3, 'w')
			file_opt.writelines(("import subprocess" + "\n" + "from chimerax.core.commands import run" + "\n" + "run(session, \"cd " + cmmdir + "\")" + "\n" + "run(session, \"open " + tmpflnam + "\")" + "\n" + "run(session, \"set bgColor white;volume #1 level " + levels + ";\")" + "\n" + "run(session, \"color radial #1.1 palette #ff0000:#ff7f7f:#ffffff:#7f7fff:#0000ff center 127.5,127.5,127.5;\")" + "\n" + "run(session, \"ui mousemode right \'mark point\'\")" + "\n" + "run(session, \"ui tool show \'Side View\'\")"))
			file_opt.close()
			print(subprocess.getstatusoutput(ChimeraX_dir + '/chimerax ' + chim3))

			# create .cmm file inside of respective tomogram directory
			cmmflip = starfinal.replace('.mrc', '.cmm')
			endfile = os.path.split(cmmflip)
			endcmm = endfile[1]
			self.ids.filenameget.text = starfinal
			if os.path.exists(cmmdir + '/' + tomoName) == False:
				os.makedirs(cmmdir + '/' + tomoName)
			if os.path.exists(cmmdir + '/coord.cmm') == True:
				shutil.move(cmmdir + '/coord.cmm', (cmmdir + '/' + tomoName + '/' + endcmm))
				statstat = 1
			else:
				statstat = 0

			# signify whether coordinates have been saved or not
			if statstat == 1:
				self.ids.pickcoordtext.text = 'Coords saved.'
			else:
				self.ids.pickcoordtext.text = 'No coords selected.'

			self.ids.notecoord.text = ""
			self.ids.notesave.text = ""
			os.remove(chim3)

		except FileNotFoundError:
			print("This directory does not exist")
			self.ids.pickcoordtext.text = 'Click above to begin.'

		return

	def right_pick(self):
		starf = self.ids.mainstar.text
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			self.ids.index2.text = str(len(imageNames))
		except FileNotFoundError:
			print("This star file does not exist")
			return
		self.ids.pickcoordtext.text = 'Press Pick Coordinates'
		# increase index by one
		if int(self.ids.index.text) == int(self.ids.index2.text):
			print('Outside of index bounds')
			return
		self.ids.index.text = str((int(self.ids.index.text) + 1))
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			starfinal = imageNames[int(self.ids.index.text) - 1]
			self.ids.filenameget.text = starfinal
		except FileNotFoundError:
			print("This star file does not exist")
			self.ids.index.text = str((int(self.ids.index.text) - 1))
			self.ids.pickcoordtext.text = 'Click above to begin.'
			return
		return

	def left_pick(self):
		try:
			starf = self.ids.mainstar.text
			self.ids.pickcoordtext.text = 'Press Pick Coordinates'
			# decrease index by one
			if int(self.ids.index.text) == 1:
				print('Outside of index bounds')
				self.ids.pickcoordtext.text = 'Click above to begin.'
				return
			self.ids.index.text = str((int(self.ids.index.text) - 1))
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			starfinal = imageNames[int(self.ids.index.text) - 1]
			self.ids.filenameget.text = starfinal
		except FileNotFoundError:
			print("This star file does not exist")
			self.ids.index.text = str((int(self.ids.index.text) + 1))
			self.ids.pickcoordtext.text = 'Click above to begin.'
		return

	def note(self):
		# create note
		starf = self.ids.mainstar.text
		direct = "/".join(starf.split("/")[:-1]) + '/'
		filename = self.ids.filenameget.text
		subtom = filename.split('/')[-2]
		file_path = "coordnote" + subtom + ".txt" 
		coordFile = open(direct + file_path, "a")

		coordFile.writelines(self.ids.index.text + ' ' + self.ids.filenameget.text + ': ' + self.ids.notecoord.text + '\n')
		coordFile.close()
		self.ids.notesave.text = 'Saved'
		print('Saved to ' + direct + file_path)
		return

	def create_coords(self):
		# initialize variables
		starf = self.ids.mainstar.text
		direct = self.ids.mainsubtomo.text
		imgToCmmCor = {}
		if self.ids.mainsubtomo.text[-1] != '/':
				direct = self.ids.mainsubtomo.text + '/'
		boxsize = float(self.ids.px1.text)
		boxsize = boxsize / 2

		# set directory path
		directory = direct + 'cmm_files/'

		# check that /cmm_files/ folder exists
		if os.path.exists(directory) == False:
			print(directory + ' does not exist. Please save coordinates first.')
			return

		# iterate through each folder in directory
		for file1 in os.listdir(directory):
			folder1 = directory + file1
			if folder1[-1] != '/':
				folder1 = folder1 + '/'
			if os.path.isdir(folder1) == True:
				for file in os.listdir(folder1):
					folder = folder1 + file
					# iterate through each .cmm file
					if os.path.isdir(folder) == True:
						for filename in os.listdir(folder):
							if filename.endswith('.cmm'):
								name = filename.replace('.cmm', '')
								with open(folder + '/' + filename) as ftomo:
									for line in ftomo:
										# finding selected .cmm coordinates and shifting based on box size
										if re.search('x', line):
											xmid = re.search(' x="(.*)" y', line)
											x_coord = xmid.group(1)
											cmmX = round(boxsize - float(x_coord))
											ymid = re.search(' y="(.*)" z', line)
											y_coord = ymid.group(1)
											cmmY = round(boxsize - float(y_coord))
											zmid = re.search(' z="(.*)" r=', line)
											z_coord = zmid.group(1)
											cmmZ = round(boxsize - float(z_coord))
											# add coords to dictionary
											imgToCmmCor[name] = [x_coord, y_coord, z_coord]
											# read star file and extract original x, y, z coordinates
											star_data = starfile.read(starf)
											df = pd.DataFrame.from_dict(star_data['particles'])
											row = df[df['rlnImageName'].str.contains(name)]
											xCor = float(row['rlnCoordinateX'].iloc[0])
											yCor = float(row['rlnCoordinateY'].iloc[0])
											zCor = float(row['rlnCoordinateZ'].iloc[0])
											# calculate final x, y, z coordinates
											finalx = str(round(xCor) - int(cmmX))
											finaly = str(round(yCor) - int(cmmY))
											finalz = str(round(zCor) - int(cmmZ))
											# create files
											eman = name[::-1]
											cutName = re.sub('\d{6}','', eman)
											cutName = cutName[::-1]
											file_opt = open(folder + '/' + cutName + '.coordsnew', 'a')
											file_opt.writelines(finalx + ' ' + finaly + ' ' + finalz + '\n')
											file_opt.close()
											file_opt = open(folder + '/' + 'NameCoord.txt', 'a')
											file_opt.writelines(row['rlnImageName'].iloc[0] + '\n')
											file_opt.close()
											file_opt = open(folder + '/' + cutName + '.shift', 'a')
											file_opt.writelines(finalx + ' ' + finaly + ' ' + finalz + '\t' + row['rlnImageName'].iloc[0] + '\n')
											file_opt.close()
			else:
				# files not in folder
				return
		
		# add cmm coordinates to star file
		star_data = starfile.read(starf)
		df = pd.DataFrame.from_dict(star_data['particles'])
		df["rlnCmmX"] = np.zeros(df.shape[0])
		df["rlnCmmY"] = np.zeros(df.shape[0])
		df["rlnCmmZ"] = np.zeros(df.shape[0])
		for file1 in os.listdir(directory):
			folder1 = directory + file1
			if folder1[-1] != '/':
				folder1 = folder1 + '/'
			if os.path.isdir(folder1) == True:
				for file in os.listdir(folder1):
					folder = folder1 + file
					# iterate through each .cmm file
					if os.path.isdir(folder) == True:
						for name in os.listdir(folder):
							if name.endswith('.cmm'):
								name = name.replace('.cmm', '')
								df.loc[df['rlnImageName'].str.contains(name), "rlnCmmX"] = imgToCmmCor[name][0]
								df.loc[df['rlnImageName'].str.contains(name), "rlnCmmY"] = imgToCmmCor[name][1]
								df.loc[df['rlnImageName'].str.contains(name), "rlnCmmZ"] = imgToCmmCor[name][2]
		starfile.write(df, directory + '/' + starf.split("/")[-1].split(".")[0] + '_cmm.star')

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
		self.ids.cmmf.text = '/cmm_files'
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
		try:
			import mrcfile
			direct = self.ids.mainmrc.text
			box = int(self.ids.px1.text)
			rad = float(self.ids.radius.text)
			height = float(self.ids.height.text)
			vertshift = float(self.ids.vertical.text)
			maskmrc = self.ids.maskname.text
			masktype = self.ids.spinner.text

			if masktype == 'Sphere':
				sphere = tom.spheremask(np.ones([box, box, box], np.float32), rad, [box, box, box], 1, [round(box/2), round(box/2), round(box/2)])
				sphere = sphere.astype('float32')
				newMask = os.path.join(direct, maskmrc)
				print('Now writing ' + newMask)
				mrcfile.new(newMask, sphere)

			if masktype == 'Cylinder':
				curve = 9649
				cylinder = tom.cylindermask(np.ones([box, box, box], np.float32), rad, 1, [round(box/2), round(box/2)])
				sph_top = (tom.spheremask(np.ones([box, box, box], np.float32), curve, [box, box, box], 1, [round(box/2),round(box/2),round(box/2)+vertshift-round(height/2)-curve])-1) * -1
				sph_bot = (tom.spheremask(np.ones([box, box, box], np.float32), curve, [box, box, box], 1, [round(box/2),round(box/2),round(box/2)+vertshift+round(height/2)+curve])-1) * -1
				mask_final = cylinder * sph_top * sph_bot

				mask_final = mask_final.astype('float32')
				newMask = os.path.join(direct, maskmrc)
				print('Now writing ' + newMask)
				mrcfile.new(newMask, mask_final)
			self.ids.maskwarning.text = ''
		except ValueError:
			self.ids.maskwarning.text = 'Filename already exists'

		return

	def reextract(self):
		mask = self.ids.maskpath.text
		starf = self.ids.mainstar.text
		if self.ids.mainsubtomo.text[-1] != '/':
			direc = self.ids.mainsubtomo.text + '/'
		else:
			direc = self.ids.mainsubtomo.text
		boxsize = float(self.ids.px1.text)
		pxsz = float(self.ids.A1.text)
		filter = self.ids.filterbackground.active
		grow = float(self.ids.blurrate.text)
		normalizeit = self.ids.normalized.active
		sdrange = float(self.ids.sdrange.text)
		sdshift = float(self.ids.sdshift.text)
		blackdust = self.ids.blackdust.active
		whitedust = self.ids.whitedust.active
		shiftfil = self.ids.shiftbysd.active
		randfilt = self.ids.randnoise.active
		permutebg = self.ids.permutebg.active
		
		def cut_part_and_movefunc(maskname, listName, direc, boxsize, pxsz, filter, grow, normalizeit, sdrange, sdshift, blackdust, whitedust, shiftfil, randfilt, permutebg):
			offSetCenter = [0, 0 ,0]
			boxsize = [boxsize, boxsize, boxsize]
			fileNames, angles, shifts, list_length, pickPos, new_star_name = tom.readList(listName, pxsz, 'masked', [])
			fileNames = [direc + name for name in fileNames]
			maskh1 = mrcfile.read(maskname)
			posNew = []
			aa = time.perf_counter()
			for i in range(len(fileNames)):
				mrcName = fileNames[i].split('/')[-1]
				mrcDirec = "/".join(fileNames[i].split('/')[:-1])
				reextractDir = mrcDirec + '/masked/'
				print("Now re-extracting " + mrcName)
				a = time.perf_counter()
				outH1, posNew[:i] = tom.processParticle(fileNames[i], angles[:,i].conj().transpose(), shifts[:,i], maskh1, pickPos[:,i].conj().transpose(), offSetCenter, boxsize, filter, grow, normalizeit, sdrange, sdshift,blackdust,whitedust,shiftfil,randfilt,permutebg)
				if os.path.exists(reextractDir) == False:
					os.mkdir(reextractDir)
				mrcfile.write(reextractDir + mrcName, outH1, True)
				b = time.perf_counter()
				t1 = str(timedelta(seconds = b-a)).split(":")
				if int(t1[1]) > 0:
					print(f"Re-extraction complete for {mrcName} in {t1[1]} minutes and {t1[2]} seconds" )
				else:
					print(f"Re-extraction complete for {mrcName} in {t1[2]} seconds" )
			bb = time.perf_counter()
			t2 = str(timedelta(seconds = bb-aa)).split(":")
			print(f'Total re-extraction time: {t2[1]} minutes and {t2[2]} seconds')
			print('New starfile created: ' + new_star_name + '\n')

		cut_part_and_movefunc(mask, starf, direc, boxsize, pxsz, filter, grow, normalizeit, sdrange, sdshift, blackdust, whitedust, shiftfil, randfilt, permutebg)
		return

	def calculate_ccc(self):
		cccVol1 = self.ids.cccvolone.text
		cccVol2 = self.ids.cccvoltwo.text
		wedge = self.ids.cccwedge.text
		star = self.ids.mainstar.text
		zoom = 40
		boxsize = float(self.ids.px1.text)
		boxsize = [boxsize, boxsize, boxsize]
		ccc = tom.ccc_calc(star, cccVol1, cccVol2, boxsize, zoom, wedge)
		print(ccc)
		return

	def filter_ccc(self):
		volume = self.ids.volvol.text
		star = self.ids.mainstar.text
		wedge = self.ids.volwedge.text
		cccthresh = float(self.ids.cccthresh.text)
		boxsize = float(self.ids.px1.text)
		boxsize = [boxsize, boxsize, boxsize]
		zoom = float(self.ids.zoomrange.text)
		tom.ccc_loop(star, volume, cccthresh, boxsize, zoom, wedge)
		return
	
	def randFlip(self):
		self.ids.randaxis.text = ""
		starf = self.ids.mainstar.text
		xflip = self.ids.xflip.active
		yflip = self.ids.yflip.active
		zflip = self.ids.zflip.active
		if xflip or yflip or zflip:
			if xflip == True:
				axis = 0
			if yflip == True:
				axis = 1
			if zflip == True:
				axis = 2
		else:
			self.ids.randaxis.text = "Axis of rotation not specified"
			return
		
		randPercent = float(self.ids.percentflip.text)
		_, ext = os.path.splitext(starf)
		if ext == '.star':
			star_data = starfile.read(starf)["particles"]
			new_star = starfile.read(starf)
			
			df = pd.DataFrame.from_dict(new_star["particles"])
			numFiles = len(star_data['rlnImageName'])
			randIdx = random.sample(range(numFiles), round(numFiles*randPercent/100))
			if axis == 0:
				df.loc[randIdx, "rlnAngleRot"] += 180
			if axis == 1:
				df.loc[randIdx, "rlnAngleTilt"] += 180
			if axis == 2:
				df.loc[randIdx, "rlnAnglePsi"] += 180
			flipped = np.zeros((numFiles,), dtype=int)
			for i in range(numFiles):
				if i in randIdx:
					flipped[i] = 1
			df["Flipped"] = flipped
			new_star["particles"] = df
			starfile.write(new_star, _ + "_randFlip" + ".star", overwrite=True)

		else:
			raise ValueError("Unsupported file extension.")
		return

	def rotate_subtomos(self, listName, dir, pxsz, boxsize, shifton, ownAngs):
		boxsize = [boxsize, boxsize, boxsize]
		fileNames, angles, shifts, list_length, pickPos, new_star_name = tom.readList(listName, pxsz, 'rottrans', ownAngs)
		fileNames = [dir + name for name in fileNames]
		for i in range(len(fileNames)):
			mrcName = fileNames[i].split('/')[-1]
			mrcDirec = "/".join(fileNames[i].split('/')[:-1])
			rotDir = mrcDirec + '/rottrans/'
			if len(ownAngs) != 3:
				outH1 = tom.processParticler(fileNames[i], angles[:,i].conj().transpose() * -1, boxsize, shifts[:,i].conj().transpose() * -1, shifton)
			else:
				outH1 = tom.processParticler(fileNames[i], ownAngs * -1, boxsize, shifts[:,i].conj().transpose() * -1, shifton)
			outH1 = outH1.astype(np.float32)
			if os.path.exists(rotDir) == False:
				os.mkdir(rotDir)
			mrcfile.write(rotDir + mrcName, outH1, True)
		return
	
	def rotate(self):
		starf = self.ids.mainstar.text
		if self.ids.mainsubtomo.text[-1] != '/':
			dir = self.ids.mainsubtomo.text + '/'
		else:
			dir = self.ids.mainsubtomo.text
		boxsize = float(self.ids.px1.text)
		pxsz = float(self.ids.A1.text)
		shifton = self.ids.applyTranslations.active
		ownAngs = []

		self.rotate_subtomos(starf, dir, pxsz, boxsize, shifton, ownAngs)
		return
	
	def manualrotate(self):
		self.ids.noaxis.text = " "
		starf = self.ids.mainstar.text
		if self.ids.mainsubtomo.text[-1] != '/':
			dir = self.ids.mainsubtomo.text + '/'
		else:
			dir = self.ids.mainsubtomo.text
		boxsize = float(self.ids.px1.text)
		pxsz = float(self.ids.A1.text)
		shifton = False
		xaxis = self.ids.xaxis.active
		yaxis = self.ids.yaxis.active
		zaxis = self.ids.zaxis.active
		anglerotate = float(self.ids.anglerotation.text)

		# X-axis  corresponds to  phi=0     psi=0   theta=alpha
        # Y-axis  corresponds to  phi=270   psi=90  theta=alpha
        # Z-axis  corresponds to  phi=alpha psi=0   theta=0

		ownAngs = []
		if xaxis or yaxis or zaxis:
			ownAngs = [0,0,0]
			if xaxis == True:
				ownAngs[2] = anglerotate
			if yaxis == True:
				ownAngs[0] = 270
				ownAngs[1] = 90
				ownAngs[2] = anglerotate
			if zaxis == True:
				ownAngs[0] = anglerotate
			ownAngs = np.array(ownAngs)
		else:
			self.ids.noaxis.text = "Axis of rotation not specified"
			return
		
		self.rotate_subtomos(starf, dir, pxsz, boxsize, shifton, ownAngs)

	# used to store a subtomogram's accepted/rejected status
	indexToVal = {}

	def visualize(self):
		# view current subtomogram
		starf = self.ids.mainstar.text
		subtomodir = self.ids.mainsubtomo.text
		chimeraDir = self.ids.chimera_path.text
		index = int(self.ids.visind1.text)
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
		except FileNotFoundError:
			print('Star file not found')
			return
		self.ids.visind2.text = str(len(imageNames))
		name = imageNames[index - 1]
		self.ids.visualizestep.text = 'Currently on file ' + name.split("/")[-1]
		fileName = subtomodir + name
		# run ChimeraX
		vis = subtomodir + 'visualize.py'
		file_opt = open(vis, 'w')
		file_opt.writelines(("import subprocess" + "\n" + "from chimerax.core.commands import run" + "\n" + "run(session, \"cd " + subtomodir + "\")" + "\n" + "run(session, \"open " + fileName + "\")" + "\n" + "run(session, \"set bgColor white;volume #1 level " + '0.5' + ";\")" + "\n" + "run(session, \"color radial #1.1 palette #ff0000:#ff7f7f:#ffffff:#7f7fff:#0000ff center 127.5,127.5,127.5;\")" + "\n" + "run(session, \"ui mousemode right \'mark point\'\")" + "\n" + "run(session, \"ui tool show \'Side View\'\")"))
		file_opt.close()
		print(subprocess.getstatusoutput(chimeraDir + '/chimerax ' + vis))
		os.remove(vis)
		self.ids.visualizefeedback.text = 'Accept or Reject the Subtomogram'
		self.ids.visualizefeedback.color = (.6,0,0,1)
		return

	def right_visualize(self):
		starf = self.ids.mainstar.text
		# set index max
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			self.ids.visind2.text = str(len(imageNames))
		except FileNotFoundError:
			print('Star file not found')
			return
		# check if index limit reached
		if int(self.ids.visind1.text) == int(self.ids.visind2.text):
			print('Outside of index bounds')
			return
		# increase index by one
		self.ids.visind1.text = str(int(self.ids.visind1.text) + 1)
		# set current filename
		name = imageNames[int(self.ids.visind1.text) - 1]
		self.ids.visualizestep.text = 'Currently on file ' + name.split("/")[-1]
		try:
			if self.indexToVal[int(self.ids.visind1.text)] == "accepted":
				self.ids.visualizefeedback.text = "Subtomogram Accepted"
				self.ids.visualizefeedback.color = (0,.3,0,1)
			elif self.indexToVal[int(self.ids.visind1.text)] == "rejected":
				self.ids.visualizefeedback.text = "Subtomogram Rejected"
				self.ids.visualizefeedback.color = (0,.3,0,1)
		except KeyError:
			self.ids.visualizefeedback.text = "View subtomogram"
			self.ids.visualizefeedback.color = (250, 250, 31, 1)
			return

		
	def left_visualize(self):
		starf = self.ids.mainstar.text
		# check if index limit reached
		if int(self.ids.visind1.text) == 1:
			print('Outside of index bounds')
			return
		# decrease index by one
		self.ids.visind1.text = str(int(self.ids.visind1.text) - 1)
		# set current filename
		try:
			imageNames = starfile.read(starf)["particles"]["rlnImageName"]
			name = imageNames[int(self.ids.visind1.text) - 1]
			self.ids.visualizestep.text = 'Currently on file ' + name.split("/")[-1]
		except FileNotFoundError:
			print('Star file not found')
			self.ids.visind1.text = str(int(self.ids.visind1.text) + 1)
			return
		try:
			if self.indexToVal[int(self.ids.visind1.text)] == "accepted":
				self.ids.visualizefeedback.text = "Subtomogram Accepted"
				self.ids.visualizefeedback.color = (0,.3,0,1)
			elif self.indexToVal[int(self.ids.visind1.text)] == "rejected":
				self.ids.visualizefeedback.text = "Subtomogram Rejected"
				self.ids.visualizefeedback.color = (0,.3,0,1)
		except KeyError:
			self.ids.visualizefeedback.text = "View subtomogram"
			self.ids.visualizefeedback.color = (250, 250, 31, 1)
			return

	def saveVisual(self):
		index = int(self.ids.visind1.text) - 1
		self.indexToVal[index + 1] = "accepted"
		starf = self.ids.mainstar.text
		subtomodir = self.ids.mainsubtomo.text
		# create visualize.star file if does not exist
		if not(os.path.exists(subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star")):
			star_data = starfile.read(starf)
			df = pd.DataFrame.from_dict(star_data["particles"])
			df = df.drop(df.index)
			star_data["particles"] = df
			starfile.write(star_data, subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star")
		# isolate current index image name
		row = pd.DataFrame.from_dict(starfile.read(starf)["particles"]).iloc[[index]]
		starA = starfile.read(subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star")
		df = pd.DataFrame.from_dict(starA["particles"])
		df = df.dropna(how="all")
		original = row["rlnImageName"].values[0]
		# add 'accepted' folder to image name path in accepted.star
		if "accepted" in row["rlnImageName"].values[0].split("/"):
			newRowName = row["rlnImageName"].values[0]
		else:
			rowName = row["rlnImageName"].values[0].split("/")
			rowName.insert(-1, "accepted")
			newRowName = "/".join(rowName)
		if df[df["rlnImageName"] == newRowName].shape[0] == 0:
			def replaceName(s):
				s = s.split("/")
				s.insert(-1, 'accepted')
				s = '/'.join(s)
				return s
			row.loc[:, "rlnImageName"] = row.loc[:, "rlnImageName"].apply(lambda x: replaceName(x))
			df = pd.concat([df, row])
			starA["particles"] = df
			starfile.write(starA, subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star", overwrite=True)
			# create accepted folder and copy in the accepted files
			folderPath = "/".join(newRowName.split("/")[:-1]) + "/"
			savedout = subtomodir + folderPath + '/'
			if os.path.exists(savedout) == False:
				os.mkdir(savedout)
			shutil.copy(subtomodir + original, savedout)
		# remove .mrc files from _reject.star
		starR_path = subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star"
		if os.path.exists(starR_path):
			row = pd.DataFrame.from_dict(starfile.read(starf)["particles"]).iloc[[index]]
			starR = starfile.read(starR_path)
			df = pd.DataFrame.from_dict(starR["particles"])
			df = df.dropna(how="all")
			rowName = row["rlnImageName"].values[0]
			df = df[df["rlnImageName"] != rowName]
			starR["particles"] = df
			starfile.write(starR, subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star", overwrite=True)
		self.ids.visualizefeedback.text = 'Subtomogram Accepted'
		self.ids.visualizefeedback.color = (0,.3,0,1)


	def noSaveVisual(self):
		index = int(self.ids.visind1.text) - 1
		self.indexToVal[index + 1] = "rejected"
		starf = self.ids.mainstar.text
		subtomodir = self.ids.mainsubtomo.text
		# create _rejected.star if it does not exist
		if not(os.path.exists(subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star")):
			star_data = starfile.read(starf)
			df = pd.DataFrame.from_dict(star_data["particles"])
			df = df.drop(df.index)
			star_data["particles"] = df
			starfile.write(star_data, subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star")
		# isolate current index image name
		row = pd.DataFrame.from_dict(starfile.read(starf)["particles"]).iloc[[index]]
		starR = starfile.read(subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star")
		df = pd.DataFrame.from_dict(starR["particles"])
		df = df.dropna(how="all")
		rowName = row["rlnImageName"].values[0]
		# add mrc file path to _rejected.star
		if df[df["rlnImageName"] == rowName].shape[0] == 0: # if file not in _rejected.star
			df = pd.concat([df, row])
			starR["particles"] = df
			starfile.write(starR, subtomodir + starf.split("/")[-1].split(".")[0] + "_rejected.star", overwrite=True)
		# check if accepted.star exists
		if os.path.exists(subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star"):
			row = pd.DataFrame.from_dict(starfile.read(starf)["particles"]).iloc[[index]]
			starA = starfile.read(subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star")
			df = pd.DataFrame.from_dict(starA["particles"])
			df = df.dropna(how="all")
		else:
			return
		if "accepted" in row["rlnImageName"].values[0].split("/"):
			newRowName = row["rlnImageName"].values[0]
		else:
			rowName = row["rlnImageName"].values[0].split("/")
			rowName.insert(-1, "accepted")
			newRowName = "/".join(rowName)
		# remove .mrc files in both accepted.star and accepted folder if they were previously accepted
		if df[df["rlnImageName"] == newRowName].shape[0] == 1:
			df = df[df["rlnImageName"] != newRowName]
			starA["particles"] = df
			starfile.write(starA, subtomodir + starf.split("/")[-1].split(".")[0] + "_accepted.star", overwrite=True)
			os.remove(subtomodir + newRowName)
		self.ids.visualizefeedback.text = 'Subtomogram Rejected'
		self.ids.visualizefeedback.color = (0,.3,0,1)

	def plottedBack(self):
		starf = self.ids.mainstar.text
		refPath = self.ids.refPath.text
		refBasename = self.ids.refBasename.text
		minParticleNum = float(self.ids.minParticleNum.text)
		boxsize = float(self.ids.px1.text)
		boxsize = [boxsize, boxsize, boxsize]
		folderPath = "/".join(starf.split("/")[:-1]) + "/"
		plotOut = folderPath + 'plotted'
		if os.path.exists(plotOut) == False:
			os.mkdir(plotOut)
		tom.plotBack(starf, refPath, refBasename, plotOut, boxsize, minParticleNum)

	pass

#run CrESTA
Cresta().run()