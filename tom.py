#matlab tom functions converted into python

import ctypes
from ctypes import *
so_file = "/Users/patricksliz/Documents/GitHub/pycrest/rot3d.so"
rot_function = CDLL(so_file)
import os
from subprocess import call
import pandas as pd
import numpy as np
import math
from scipy.fftpack import fftn, ifftn, ifftshift, fftshift
from scipy.ndimage import label, binary_opening
from skimage.morphology import remove_small_objects
import starfile
import mrcfile
import emfile
from pathlib import Path
import matplotlib.pyplot as plt
import warnings

#Wiener filter functions
def deconv_tomo(vol, angpix, defocus, snrfalloff, highpassnyquist, voltage, cs, envelope, bfactor, phasebutton):
    highpass = np.arange(0, 1 + 1 / 2047, 1 / 2047)
    highpass = np.minimum(1, highpass / highpassnyquist) * np.pi
    highpass = 1 - np.cos(highpass)

    snr = np.exp((np.arange(0, -1 - (1/2047), -1 / 2047)) * snrfalloff * 100 / angpix) * 1000 * highpass
    if phasebutton == True:
        ctf = np.abs(ctf1d(2048, angpix * 1e-10, voltage, cs, -defocus * 1e-6, envelope, 0, bfactor))
    else:
        ctf = (ctf1d(2048, angpix * 1e-10, voltage, cs, -defocus * 1e-6, envelope, 0, bfactor))

    wiener = []
    for c, s in zip(ctf, snr):
        if s == 0:
            v = 0
        else:
            v = c / (c * c + 1 / s)
        wiener.append(v)

    plt.close()
    plt.plot(np.arange(0, 1 + 1 / 2047, 1 / 2047), wiener)
    plt.grid(True)
    plt.title('Wiener Function')
    plt.ylabel('Wiener Filter Function')

    s1 = -np.floor(vol.shape[0] / 2)
    f1 = s1 + vol.shape[0] - 1
    s2 = -np.floor(vol.shape[1] / 2)
    f2 = s2 + vol.shape[1] - 1
    s3 = -np.floor(vol.shape[2] / 2)
    f3 = s3 + vol.shape[2] - 1

    x, y, z = np.mgrid[s1:f1+1, s2:f2+1, s3:f3+1]
    x = x / np.abs(s1)
    y = y / np.abs(s2)
    z = z / max(1, np.abs(s3))
    r = np.sqrt(x**2 + y**2 + z**2)
    r = np.minimum(1, r)
    r = np.fft.ifftshift(r)
    x = np.arange(0, 1 + 1/2047, 1 / 2047)

    ramp = np.interp(r, x, wiener)
    deconv = np.real(np.fft.ifftn(np.fft.fftn(vol.astype(np.float32)) * ramp))
    return deconv

def ctf1d(length, pixelsize, voltage, cs, defocus, amplitude_contrast, phase_shift, bfactor):
    ny = 1 / (pixelsize)
    lambda_ = 12.2643247 / np.sqrt(voltage * (1.0 + voltage * 0.978466e-6)) * 1e-10
    lambda2 = lambda_ * 2

    points = np.arange(0, length)
    points = points / (2 * length) * ny
    k2 = points ** 2
    term1 = lambda_**3 * cs * k2**2

    w = np.pi / 2 * (term1 + lambda2 * defocus * k2) - phase_shift

    acurve = np.cos(w) * amplitude_contrast
    pcurve = -np.sqrt(1 - amplitude_contrast**2) * np.sin(w)
    bfactor_term = np.exp(-bfactor * k2 * 0.25)

    ctf = (pcurve + acurve) * (bfactor_term)

    return ctf


#Create mask functions
def spheremask(vol, radius, sigma=0, center=None):
    if center == None:
        #	maybe no +1
        center = [np.floor(vol.shape[0] / 2) + 1, np.floor(vol.shape[1] / 2) + 1, np.floor(vol.shape[2] / 2) + 1]
    x, y, z = np.mgrid[0:vol.shape[0], 0:vol.shape[1], 0:vol.shape[2]]
    x = np.sqrt((x + 1 - center[0])**2 + (y + 1 - center[1])**2 + (z + 1 - center[2])**2)
    ind = np.where(x >= radius)
    mask = np.ones(vol.shape, dtype=np.float32)
    mask[ind] = 0

    if sigma > 0:
        mask[ind] = np.exp(-((x[ind] - radius) / sigma)**2)
        ind = np.where(mask < np.exp(-2))
        mask[ind] = 0

    vol = vol * mask
    return vol

def cylindermask(vol, radius, sigma, center):
    x, y = np.mgrid[0:vol.shape[0], 0:vol.shape[1]]
    x = np.sqrt((x + 1 - center[0])**2 + (y + 1 - center[1])**2)
    ind = np.where(x >= radius)
    mask = np.ones((vol.shape[0], vol.shape[1]), dtype=np.float32)
    mask[ind] = 0

    if sigma > 0:
        mask[ind] = np.exp(-((x[ind] - radius) / sigma)**2)
        ind = np.where(mask < np.exp(-2))
        mask[ind] = 0

    for iz in range(vol.shape[2]):
        vol[:, :, iz] = vol[:, :, iz] * mask
    return vol


#3D Signal Subtraction Functions
def readList(listName, pxsz):
    _, ext = os.path.splitext(listName)
    if ext == '.star':
        star_data = starfile.read(listName)["particles"]
        list_length = len(star_data)
        # fileNames = [star_data[i]['rlnImageName'] for i in range(list_length)]
        # PickPos = np.zeros((3, list_length))
        # shifts = np.zeros((3, list_length))
        # angles = np.zeros((3, list_length))
        Align = allocAlign(list_length)
        fileNames = []
        PickPos = np.empty(shape=(3, list_length))
        shifts = np.empty(shape=(3, list_length))
        angles = np.empty(shape=(3, list_length))
        for i in range(list_length):
            fileNames.append(star_data['rlnImageName'][i])
            PickPos[:,i] = [star_data['rlnCoordinateX'][i], star_data['rlnCoordinateY'][i], star_data['rlnCoordinateZ'][i]]
            shifts[:,i] = [-float(star_data['rlnOriginXAngst'][i]) / pxsz, -float(star_data['rlnOriginYAngst'][i]) / pxsz, -float(star_data['rlnOriginZAngst'][i]) / pxsz]
            euler_angles = eulerconvert_xmipp(star_data['rlnAngleRot'][i], star_data['rlnAngleTilt'][i], star_data['rlnAnglePsi'][i])
            angles[:,i] = [euler_angles[0], euler_angles[1], euler_angles[2]]
            
            Align[i]["Filename"] = fileNames[i]
            Align[i]["Angle"]["Phi"] = angles[0, i]
            Align[i]["Angle"]["Psi"] = angles[1, i]
            Align[i]["Angle"]["Theta"] = angles[2, i]
            Align[i]["Shift"]["X"] = shifts[0, i]
            Align[i]["Shift"]["Y"] = shifts[1, i]
            Align[i]["Shift"]["Z"] = shifts[2, i]
    else:
        raise ValueError("Unsupported file extension.")
    
    return fileNames, angles, shifts, list_length, PickPos

def allocAlign(num_of_entries):
    Align = []
    for i in range(num_of_entries):
        align_entry = {
            'Filename': '',
            'Tomogram': {
                'Filename': '',
                'Header': '',
                'Position': {
                    'X': -1,
                    'Y': -1,
                    'Z': -1
                },
                'Regfile': '',
                'Offset': [0, 0, 0],
                'Binning': 0,
                'AngleMin': 0,
                'AngleMax': 0
            },
            'Shift': {
                'X': 0,
                'Y': 0,
                'Z': 0
            },
            'Angle': {
                'Phi': 0,
                'Psi': 0,
                'Theta': 0,
                'Rotmatrix': []
            },
            'CCC': -1,
            'Class': -1,
            'ProjectionClass': 0,
            'NormFlag': 0,
            'Filter': [0, 0]
        }
        Align.append(align_entry)
    return Align

def eulerconvert_xmipp(rot, tilt, psi):
    rot2 = -psi * np.pi / 180
    tilt = -tilt * np.pi / 180
    psi = -rot * np.pi / 180
    rot = rot2

    rotmatrix = np.dot(
        np.dot(
            np.array([[np.cos(rot), -np.sin(rot), 0],
                      [np.sin(rot), np.cos(rot), 0],
                      [0, 0, 1]]),
            np.array([[np.cos(tilt), 0, np.sin(tilt)],
                      [0, 1, 0],
                      [-np.sin(tilt), 0, np.cos(tilt)]])),
        np.array([[np.cos(psi), -np.sin(psi), 0],
                  [np.sin(psi), np.cos(psi), 0],
                  [0, 0, 1]])
    )

    euler_out = np.zeros(3)
    euler_out[0] = np.arctan2(rotmatrix[2, 0], rotmatrix[2, 1]) * 180 / np.pi
    euler_out[1] = np.arctan2(rotmatrix[0, 2], -rotmatrix[1, 2]) * 180 / np.pi
    euler_out[2] = np.arccos(rotmatrix[2, 2]) * 180 / np.pi
    euler_out[euler_out < 0] += 360

    if -(rotmatrix[2, 2] - 1) < 10e-8:
        euler_out[2] = 0
        euler_out[1] = 0
        euler_out[0] = np.arctan2(rotmatrix[1, 0], rotmatrix[0, 0]) * 180 / np.pi
    return euler_out

def processParticle(filename,tmpAng,tmpShift,maskh1,PickPos,offSetCenter,boxsize,filter,grow,normalizeit, sdRange, sdShift,blackdust,whitedust,shiftfil,randfilt,permutebg):
    volTmp = mrcfile.read(filename)
    maskh1Trans = shift(rotate(maskh1, tmpAng), tmpShift.conj().transpose())
    maskh1Trans = maskh1Trans > 0.14
    vectTrans = pointrotate(offSetCenter,tmpAng[0],tmpAng[1],tmpAng[2])+tmpShift.conj().transpose()
    posNew=(np.round(vectTrans)+PickPos).conj().transpose()

    outH1 = volTmp
    if filter == True:
        if shiftfil == True:
            outH1 = maskWithFil(outH1,maskh1Trans, sdRange, sdShift,blackdust,whitedust)
        elif randfilt == True:
            outH1 = randnoise_filt(outH1,maskh1Trans,'', 0, sdRange,blackdust,whitedust)
    if permutebg == True:
        outH1 = permute_bg(outH1,maskh1Trans,'',grow,5,3)
        print(outH1)

    if normalizeit == True:
        input = outH1
        inmax = np.max(input)
        inmin = np.min(input)
        range = inmax - inmin
        input = ((input-inmin) / range - .5) * 2
        indd = np.where(maskh1Trans < 0.1)
        ind_rand = np.random.permutation(len(indd[0]))
        input[indd] = input[indd[ind_rand]]
        outH1 = input

    return outH1, posNew

def shift(im, delta):
    dimx, dimy, dimz = im.shape
    if delta.ndim > 1:
        delta = delta.flatten()

    x, y, z = np.mgrid[-np.floor(dimx/2):-np.floor(dimx/2)+dimx,
                       -np.floor(dimy/2):-np.floor(dimy/2)+dimy,
                       -np.floor(dimz/2):-np.floor(dimz/2)+dimz]
    
    indx = np.where([dimx, dimy, dimz] == 1)[0]
    delta[indx] = 0
    delta /= [dimx, dimy, dimz]
    x = delta[0] * x + delta[1] * y + delta[2] * z
    
    im = np.fft.fftn(im)
    im = np.real(np.fft.ifftn(im * np.exp(-2j * np.pi * np.fft.ifftshift(x))))
    return im

def rotate(*args):
    nargin = len(args)
    if nargin == 5:
        taper = args[4]
        center = args[3]
        ip = args[2]
    elif nargin == 4:
        if not isinstance(args[3], int):
            taper = args[3]
            center = np.ceil(np.array(args[0].shape) / 2)
        else:
            taper = 'no'
            center = args[3]
        ip = args[2]
    elif nargin == 3:
        ip = args[2]
        center = np.ceil(np.array(args[0].shape) / 2)
        taper = 'no'
    elif nargin == 2:
        center = np.ceil(np.array(args[0].shape) / 2)
        ip = 'l'
        taper = 'no'
    else:
        print('Wrong number of arguments')
        return -1
    
    in_array = args[0]
    in_array = in_array.astype(np.float32)
    euler_angles = np.array(args[1])
    euler_angles = euler_angles.astype(np.float32)
    px = float(center[0])
    py = float(center[1])
    pz = float(center[2])
    
    if taper != 'taper':
        out = np.zeros_like(in_array, dtype=np.float32)
        pointer_in = np.ctypeslib.ndpointer(shape = in_array.shape, dtype = np.float32)
        pointer_out = np.ctypeslib.ndpointer(shape = out.shape, dtype = np.float32)
        pointer_ang = np.ctypeslib.ndpointer(shape = euler_angles.shape, dtype = np.float32)
        rot_function.rot3d.argtypes = (pointer_in, pointer_out, ctypes.c_long, ctypes.c_long, ctypes.c_long, pointer_ang, ctypes.c_wchar, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_int)
        rot_function.rot3d.restype = None
        rot_function.rot3d(in_array, out, 256, 256, 256, euler_angles, ip, px, py, pz, 1)
        out = out.astype(np.float64)
    
    return out

def tom_taper(in_data, new_size):
    if len(new_size) == 2:
        new_size.append(1)

    out = np.zeros(new_size)
    out = paste(out, in_data, np.round(((np.array(out.shape) - np.array(in_data.shape)) / 2) + 1))

    for z in range(1, new_size[2] + 1):
        diff_z = np.round((new_size[2] - in_data.shape[2]) / 2)
        if z > diff_z and z <= in_data.shape[2] + diff_z:
            im = in_data[:, :, z - diff_z - 1]
            out_sl = out[:, :, z - 1]

            a = im[:, 0]
            b = im[:, im.shape[1] - 1]
            c = im[0, :]
            d = im[im.shape[0] - 1, :]

            diff_hor = np.round((new_size[0] - im.shape[0]) / 2)
            diff_vert = np.round((new_size[1] - im.shape[1]) / 2)
            stop_up = diff_vert
            start_down = out.shape[1] - diff_vert

            for i in range(1, new_size[0] + 1):
                if i <= diff_hor or i > (im.shape[0] + diff_hor):
                    if i < diff_hor:
                        val_up = a[0]
                        val_low = b[0]
                    else:
                        val_up = a[a.shape[0] - 1]
                        val_low = b[b.shape[0] - 1]
                else:
                    val_up = a[i - diff_hor - 1]
                    val_low = b[i - diff_hor - 1]

                out_sl[i - 1, :stop_up] = val_up
                out_sl[i - 1, start_down:] = val_low

            stop_left = diff_hor
            start_right = out.shape[0] - diff_hor

            for i in range(1, new_size[1] + 1):
                if i > diff_vert and i <= (im.shape[1] + diff_vert):
                    out_sl[:stop_left, i - 1] = c[i - diff_vert - 1]
                    out_sl[start_right:, i - 1] = d[i - diff_vert - 1]

            out[:, :, z - 1] = out_sl

    if new_size[2] == 1:
        return out
    for z in range(1, new_size[2] + 1):
        diff_z = np.round((new_size[2] - in_data.shape[2]) / 2)
        if z <= diff_z or z >= in_data.shape[2] + diff_z:
            if z <= diff_z:
                out[:, :, z - 1] = out[:, :, diff_z]
            else:
                out[:, :, z - 1] = out[:, :, diff_z + in_data.shape[2] - 1]
    return out
    
def paste(a, b, coord):
    dims = b.shape
    s1, s2, s3 = a.shape
    
    if s3 == 1:
        if coord[0] > s1 or coord[1] > s2:
            raise ValueError('Improper Selection of Starting Pixel')
        elif coord[0] <= 0 or coord[1] <= 0:
            if coord[0] <= 0 and coord[1] > 0:
                if coord[0] + dims[0] - 1 < 1:
                    raise ValueError('Improper Selection of Starting Pixel')
                elif coord[1] + dims[1] - 1 > s2:
                    a[0:(coord[0] + dims[0] - 1), coord[1]:s2] = b[(abs(coord[0]) + 1):dims[0], 0:(s2 - coord[1] + 1)]
                else:
                    a[0:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1)] = b[(abs(coord[0]) + 1):dims[0], 0:dims[1]]
            elif coord[0] > 0 and coord[1] <= 0:
                if coord[1] + dims[1] - 1 < 1:
                    raise ValueError('Improper Selection of Starting Pixel')
                elif coord[0] + dims[0] - 1 > s1:
                    a[coord[0]:s1, 0:(coord[1] + dims[1] - 1)] = b[0:(s1 - coord[0] + 1), (abs(coord[1]) + 1):dims[1]]
                else:
                    a[coord[0]:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1)] = b[0:dims[0], (abs(coord[1]) + 1):dims[1]]
            elif coord[0] <= 0 and coord[1] <= 0:
                if coord[0] + dims[0] - 1 < 1 or coord[1] + dims[1] - 1 < 1:
                    raise ValueError('Improper Selection of Starting Pixel')
                else:
                    a[0:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1)] = b[(abs(coord[0]) + 1):dims[0], (abs(coord[1]) + 1):dims[1]]
        else:
            if (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) <= s2:
                a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1)] = b
            elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) <= s2:
                a[coord[0]:s1, coord[1]:(coord[1] + dims[1] - 1)] = b[0:(1 + s1 - coord[0]), 0:dims[1]]
            elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) > s2:
                a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:s2] = b[0:dims[0], 0:(s2 - coord[1] + 1)]
            elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) > s2:
                a[coord[0]:s1, coord[1]:s2] = b[0:(s1 - coord[0] + 1), 0:(s2 - coord[1] + 1)]
    else:
        if coord[0] > s1 or coord[1] > s2 or coord[2] > s3:
            raise ValueError('Improper Selection of Starting Pixel')
        elif coord[0] <= 0 or coord[1] <= 0 or coord[2] <= 0:
            if (coord[0] + dims[0] - 1) < 1 or (coord[1] + dims[1] - 1) < 1 or (coord[2] + dims[2] - 1) < 1:
                raise ValueError('Improper Selection of Starting Pixel')
        
        if coord[2] <= 0 and ((coord[2] + dims[2] - 1) <= s3):
            ad = abs(coord[2]) + 1
            for i in range(coord[2], coord[2] + dims[2]):
                if i <= 0:
                    continue
                else:
                    if coord[0] <= 0 and coord[1] > 0:
                        if (coord[1] + dims[1] - 1) > s2:
                            a[0:(coord[0] + dims[0] - 1), coord[1]:s2, i] = b[(abs(coord[0]) + 1):dims[0], 0:(s2 - coord[1] + 1), (i + ad)]
                        else:
                            a[0:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1), i] = b[(abs(coord[0]) + 1):dims[0], 0:dims[1], (i + ad)]
                    elif coord[0] > 0 and coord[1] <= 0:
                        if (coord[0] + dims[0] - 1) > s1:
                            a[coord[0]:s1, 0:(coord[1] + dims[1] - 1), i] = b[0:(s1 - coord[0] + 1), (abs(coord[1]) + 1):dims[1], (i + ad)]
                        else:
                            a[coord[0]:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1), i] = b[0:dims[0], (abs(coord[1]) + 1):dims[1], (i + ad)]
                    elif coord[0] <= 0 and coord[1] <= 0:
                        a[0:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1), i] = b[(abs(coord[0]) + 1):dims[0], (abs(coord[1]) + 1):dims[1], (i + ad)]
                    elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) <= s2:
                        a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1), i] = b[:, :, (i + ad)]
                    elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) <= s2:
                        a[coord[0]:s1, coord[1]:(coord[1] + dims[1] - 1), i] = b[0:(s1 - coord[0] + 1), 0:dims[1], (i + ad)]
                    elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) > s2:
                        a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:s2, i] = b[0:dims[0], 0:(s2 - coord[1] + 1), (i + ad)]
                    elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) > s2:
                        a[coord[0]:s1, coord[1]:s2, i] = b[0:(s1 - coord[0] + 1), 0:(s2 - coord[1] + 1), (i + ad)]
        elif coord[2] >= 1:
            ad = coord[2] - 1
            for i in range(coord[2], coord[2] + dims[2]):
                if i > s3:
                    continue
                else:
                    if coord[0] <= 0 and coord[1] > 0:
                        if (coord[1] + dims[1] - 1) > s2:
                            a[0:(coord[0] + dims[0] - 1), coord[1]:s2, i] = b[(abs(coord[0]) + 1):dims[0], 0:(s2 - coord[1] + 1), (i - ad)]
                        else:
                            a[0:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1), i] = b[(abs(coord[0]) + 1):dims[0], 0:dims[1], (i - ad)]
                    elif coord[0] > 0 and coord[1] <= 0:
                        if (coord[0] + dims[0] - 1) > s1:
                            a[coord[0]:s1, 0:(coord[1] + dims[1] - 1), i] = b[0:(s1 - coord[0] + 1), (abs(coord[1]) + 1):dims[1], (i - ad)]
                        else:
                            a[coord[0]:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1), i] = b[0:dims[0], (abs(coord[1]) + 1):dims[1], (i - ad)]
                    elif coord[0] <= 0 and coord[1] <= 0:
                        a[0:(coord[0] + dims[0] - 1), 0:(coord[1] + dims[1] - 1), i] = b[(abs(coord[0]) + 1):dims[0], (abs(coord[1]) + 1):dims[1], (i - ad)]
                    elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) <= s2:
                        a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:(coord[1] + dims[1] - 1), i] = b[:, :, (i - ad)]
                    elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) <= s2:
                        a[coord[0]:s1, coord[1]:(coord[1] + dims[1] - 1), i] = b[0:(s1 - coord[0] + 1), 0:dims[1], (i - ad)]
                    elif (coord[0] + dims[0] - 1) <= s1 and (coord[1] + dims[1] - 1) > s2:
                        a[coord[0]:(coord[0] + dims[0] - 1), coord[1]:s2, i] = b[0:dims[0], 0:(s2 - coord[1] + 1), (i - ad)]
                    elif (coord[0] + dims[0] - 1) > s1 and (coord[1] + dims[1] - 1) > s2:
                        a[coord[0]:s1, coord[1]:s2, i] = b[0:(s1 - coord[0] + 1), 0:(s2 - coord[1] + 1), (i - ad)]
    return a

def cut_out(in_data, pos, size_c, fill_flag='no-fill'):
    if fill_flag != 'fill':
        fill_flag = 'no-fill'
    
    # Kick out values < 1
    if not isinstance(pos, np.ndarray):
        pos = np.floor((np.array(in_data.shape) - np.array(size_c)) / 2) + 1
    
    pos = np.where(pos > 0, pos, 1)
    
    num_of_dim = in_data.ndim
    if in_data.shape[0] == 1:
        in_size = in_data.shape[1]
        num_of_dim = 1
    else:
        in_size = in_data.shape
        num_of_dim = in_data.ndim
    
    bound = np.zeros(3)
    
    if (pos[0] + size_c[0]) <= in_size[0]:
        bound[0] = pos[0] + size_c[0] - 1
    else:
        bound[0] = in_size[0]
    
    if num_of_dim > 1:
        if (pos[1] + size_c[1]) <= in_size[1]:
            bound[1] = pos[1] + size_c[1] - 1
        else:
            bound[1] = in_size[1]
    else:
        pos[1] = 0
        bound[1] = 0
    
    if num_of_dim > 2:
        if (pos[2] + size_c[2]) <= in_size[2]:
            bound[2] = pos[2] + size_c[2] - 1
        else:
            bound[2] = in_size[2]
    else:
        pos[2] = 0
        bound[2] = 0
    
    pos = np.round(pos).astype(int)
    bound = np.round(bound).astype(int)
    
    # Cut it
    if num_of_dim > 1:
        out = in_data[pos[0]:bound[0], pos[1]:bound[1], pos[2]:bound[2]]
    else:
        out = in_data[pos[0]:bound[0]]
    
    return out
    
def pointrotate(r, phi, psi, the):
    phi = phi / 180 * np.pi
    psi = psi / 180 * np.pi
    the = the / 180 * np.pi

    matr = np.array([[np.cos(psi), -np.sin(psi), 0],
                     [np.sin(psi), np.cos(psi), 0],
                     [0, 0, 1]])

    matr = matr @ np.array([[1, 0, 0],
                            [0, np.cos(the), -np.sin(the)],
                            [0, np.sin(the), np.cos(the)]])

    matr = matr @ np.array([[np.cos(phi), -np.sin(phi), 0],
                            [np.sin(phi), np.cos(phi), 0],
                            [0, 0, 1]])

    r = matr @ r
    r = r.flatten()
    return r

def maskWithFil(input, mask, std2fil, std2shift, blackdust, whitedust):

    indd = np.where(mask < 0.1)
    ind_mean = np.mean(input[indd])
    ind_std = np.std(input[indd])

    if whitedust == True:
        for idx in np.nditer(indd):
            if input[idx] > (ind_mean + std2fil * ind_std):
                input[idx] -= std2shift * ind_std
        # indd2 = np.where(input[indd] > (ind_mean + std2fil * ind_std))
        # input[indd[indd2]] -= std2shift * ind_std

    if blackdust == True:
        for idx in np.nditer(indd):
            if input[idx] > (ind_mean + std2fil * ind_std):
                input[idx] += std2shift * ind_std
        # indd2 = np.where(input[indd] < (ind_mean - std2fil * ind_std))
        # input[indd[0][indd2]] += std2shift * ind_std

    return input

def randnoise_filt(input, mask, outputname, grow_rate, sdrange, blackdust, whitedust):

    if grow_rate == 0:
        outmask = np.where(mask < 0.1)
        outsmall = np.where(input[outmask] < -sdrange)
        outlarge = np.where(input[outmask] > sdrange)

        if whitedust == True:
            for i in range(len(outlarge[0])):
                input[outmask[0][outlarge[0][i]]] = np.random.normal(0, 1)

        if blackdust == True:
            for i in range(len(outsmall[0])):
                input[outmask[0][outsmall[0][i]]] = np.random.normal(0, 1)

    '''else:
        mask_tmp = mask
        smooth_ch = np.arange(100/num_of_steps, 100, 100/num_of_steps)
        std_ch = np.arange(4/num_of_steps, 4, 4/num_of_steps)
        filt_ch = np.arange(2, -2/num_of_steps, -2/num_of_steps)

        for i in range(num_of_steps):
            mask_old = mask_tmp
            mask_tmp = tom_grow_mask(mask_tmp, grow_rate, max_error, filt_cer)
            mask_diff = mask_tmp - mask_old
            indd = np.where(mask_diff > 0.1)
            ind_rand = np.random.permutation(len(indd[0]))
            ind_rand2 = np.random.permutation(len(indd[0]))
            cut_len = round(len(ind_rand) * (smooth_ch[i] / 100))
            tmp_vox = input[indd[0][ind_rand[:cut_len]]]
            tmp_vox = clean_stat(tmp_vox, std_ch[i])
            input[indd[0][ind_rand2[:cut_len]]] = tmp_vox

            if filt_ch[i] == 0:
                in_f = input
            else:
                in_f = tom_filter(input, filt_ch[i])

            tmp_vox = in_f[indd[0][ind_rand[:cut_len]]]
            tmp_vox = clean_stat(tmp_vox, std_ch[i])
            input[indd[0][ind_rand2[:cut_len]]] = tmp_vox
    '''

    return input

def permute_bg(input, mask, outputname='', grow_rate=0, num_of_steps=10, filt_cer=10, max_error=10):

    if grow_rate == 0:
        indd = np.where(mask < 0.1)
        ind_rand = np.random.permutation(len(indd[0]))
        input[indd] = input[indd[ind_rand]]

    else:
        mask_tmp = mask
        smooth_ch = np.arange(100/num_of_steps, 100 + 100/num_of_steps, 100/num_of_steps)
        std_ch = np.arange(4/num_of_steps, 4 + 4/num_of_steps, 4/num_of_steps)
        filt_ch = np.round(np.arange(2, 0 - (2/num_of_steps), -(2/num_of_steps)))

        for i in range(num_of_steps):
            mask_old = mask_tmp
            mask_tmp = tom_grow_mask(mask_tmp, grow_rate, max_error, filt_cer)
            mask_old = mask_old.astype(int)
            mask_tmp = mask_tmp.astype(int)
            mask_diff = mask_tmp - mask_old

            indd = np.flatnonzero(mask_diff)
            ind_rand = np.random.permutation(len(indd))
            ind_rand2 = np.random.permutation(len(indd))
            cut_len = int(np.round(len(ind_rand) * (smooth_ch[i] / 100)))
        #   tmp_vox = input[indd[0][ind_rand[:cut_len]]]
            tmp_vox = []
            inputshape = input.shape
            input = input.flatten()
            for ii in range(cut_len):
                index = indd[ind_rand[ii]]
                tmp_vox.append(input[index])

            tmp_vox = np.array(tmp_vox)
            tmp_vox = clean_stat(tmp_vox, std_ch[i])
            
            #input[indd[0][ind_rand2[:cut_len]]] = tmp_vox
            input[indd[ind_rand2[:cut_len]]] = tmp_vox
            # for ii in range(cut_len):
            #     index = indd[ind_rand2[ii]]
            #     input[index].append(tmp_vox)

            if filt_ch[i] == 0:
                in_f = input
            else:
                input.reshape(inputshape)
                in_f = tom_filter(input, filt_ch[i])

            tmp_vox = in_f[indd[ind_rand[:cut_len]]]
            tmp_vox = clean_stat(tmp_vox, std_ch[i])
            input[indd[ind_rand2[:cut_len]]] = tmp_vox

#    indd = np.array(np.where(mask_tmp < 0.1))
    indd = np.array(np.where(mask_tmp < 0.1, mask_tmp, 0))
    indd.reshape((256,256,256))
    ind_rand = np.random.permutation(indd)
    #input[indd] = input[indd[ind_rand]]
    for i in range(indd.shape[0]):
        for j in range(indd.shape[1]):
            for k in range(indd.shape[2]):
                input[indd[i, j, k]] = input[indd[i, j, k]][ind_rand[i, j, k]]

    return input

def tom_grow_mask(mask, factor, max_error=2, filter_cer=None):

    thr_inc = 0.1
    thr_tmp = 0.4

    org_num_of_vox = np.sum(mask > 0)
    dust_size = int(round(org_num_of_vox - (0.3 * org_num_of_vox)))

    max_itr = 1000

    mask_filt = tom_filter(mask, filter_cer)

    for ii in range(1, 31):
        thr_inc /= ii
        thr_start = thr_tmp
        for i in range(1, max_itr + 1):
            thr_tmp = thr_start - (thr_inc * i)
            new_num = np.sum(remove_small_objects(mask_filt > thr_tmp, min_size = dust_size, connectivity=6))
            if new_num > (org_num_of_vox * factor):
                break
        act_error = ((new_num - (org_num_of_vox * factor)) / org_num_of_vox) * 100
        thr_tmp = thr_start - (thr_inc * (i - 1))
        if act_error < max_error:
            break
    new_mask = remove_small_objects(mask_filt > (thr_start - (thr_inc * i)), min_size = dust_size, connectivity = 6)
    
    return new_mask

def clean_stat(vox, nstd):
    mea_out = np.mean(vox)
    std_out = np.std(vox)

    idx = np.where((vox > (mea_out + (nstd * std_out))) + (vox < (mea_out - (nstd * std_out))))

    out = vox.copy()
    out[idx] = mea_out

    return out


def tom_filter(im, radius, flag='circ'):
    if flag.lower() == 'circ':
        mask = np.ones_like(im)
        mask = spheremask(mask, radius)

    npix = np.sum(mask)
    mask = mask.astype(np.float32)
    im = im.astype(np.float32)
    im = np.real(np.fft.fftshift(np.fft.ifftn(np.fft.fftn(mask) * np.fft.fftn(im)) / npix))
    # im = np.real(np.fft.fftshift(np.fft.ifftn((np.fft.fftn(mask) * np.fft.fftn(im))) / npix))
    
    return im

def writeParticle(filename, outH1, output):
    nameLeft = filename.replace(output.findWhat, output.rplaceWith[0])
    pFoldLeft = os.path.dirname(nameLeft)
    warnings.filterwarnings("ignore")  # Turn off warnings
    os.makedirs(pFoldLeft, exist_ok=True)  # Create directory (ignore if it already exists)
    warnings.filterwarnings("default") 
    if nameLeft == filename:
        raise ValueError("Check output find what: " + filename + " == " + nameLeft)
    mrcfile.write(nameLeft, outH1)