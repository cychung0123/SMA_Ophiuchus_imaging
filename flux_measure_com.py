import sys
import os
import numpy as np
import math
import scipy.optimize as opt

from astropy.io.fits import getdata
from astropy import wcs
from astropy.io import fits
from astropy import units as u
from astropy import constants as con
from astropy.coordinates import SkyCoord

import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib


def Gaussian_2D(xdata_tuple, amp, x0, y0, sigma_x, sigma_y, theta, z0):
    (x, y) = xdata_tuple 
    x0 = float(x0)
    y0 = float(y0)
    a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = (np.sin(2*theta))/(4*sigma_x**2) - (np.sin(2*theta))/(4*sigma_y**2)
    c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    z = z0 + amp*np.exp(-(a*(x-x0)**2+2*b*(x-x0)*(y-y0)+c*(y-y0)**2))
    return z.ravel()

ifband = str(sys.argv[1])
sideband = str(sys.argv[2])
field = str(sys.argv[3])
track = str(sys.argv[4])

def write_to_file(file, field, value):
    txt_file = file
    new_row = 1
    add_line = str(value)+'   '
    try:
        with open(txt_file, 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.split()[0] == field:
                new_line=line[:-1]+add_line+'\n'
                lines[i]=new_line
                new_row = 0
                break
        if new_row == 1:
            with open(txt_file, 'a') as f:
                f.write('\n')
                f.write(''.join(field+'   '+add_line))
        else:
            with open(txt_file, 'w') as f:
                f.writelines(lines)
    except:
        with open(txt_file, 'w') as f:
            f.write(''.join(field+'   '+add_line))

def gaussian_fitting(z, rms):
    x = np.linspace(0, (z.shape[0]-1), (z.shape[0]))
    y = np.linspace(0, (z.shape[1]-1), (z.shape[1]))
    x, y = np.meshgrid(x, y)
    xdata = np.vstack((x.ravel(),y.ravel()))

    # initial guess
    max_x, max_y = np.unravel_index(np.argmax(z, axis=None), z.shape)
    max_pos = hduwcs.wcs_pix2world(max_x, max_y, 0)
    max_flux = z[(max_x, max_y)]
    sigma_x = 10
    sigma_y = 10
    theta = 0
    z0 = rms
    p0= (max_flux, max_x, max_y, sigma_x, sigma_y, theta, z0)

    if (max_flux/rms > 3):
        try:
            # 2D Gaussiam fit
            popt, pcov = opt.curve_fit(Gaussian_2D, xdata, z.ravel(), p0=p0, maxfev=10000)
            peak_flux = popt[0]*1000
            cen = hduwcs.wcs_pix2world(popt[1]+box0, popt[2]+box1, 0)
            fwhm_x = abs(popt[3])*math.sqrt(8*np.log(2))
            fwhm_y = abs(popt[4])*math.sqrt(8*np.log(2))
            major_axis = max(fwhm_x*(abs(cdelt1)), fwhm_y*cdelt2)*3600
            minor_axis = min(fwhm_x*(abs(cdelt1)), fwhm_y*cdelt2)*3600

            # fitted function
            z_fit = Gaussian_2D((x, y), *popt)
            integrated_flux = peak_flux*2*math.pi*(abs(popt[3]))*(abs(popt[4]))
            pix_num = (math.pi*(bmaj/2)*(bmin/2)/(np.log(2))/((abs(cdelt1))*cdelt2))
            total_flux = abs(integrated_flux/pix_num)
            SNR=(popt[0]/rms)
            perr = np.sqrt(np.diag(pcov))
            if perr[3] > 0.3 or perr[4] > 0.3:
                major_axis = 0.000000000000
                minor_axis = 0.000000000000
                total_flux = max_flux*1000
                cen = max_pos
                SNR=max_flux/rms
                return max_flux*1000, major_axis, minor_axis, total_flux, cen, SNR

            elif math.sqrt((hduwcs.wcs_world2pix(cen[0],cen[1],0)[1]-cen_x)**2+(hduwcs.wcs_world2pix(cen[0],cen[1],0)[0]-cen_y)**2) > bmaj*6/cdelt2:
                major_axis = 0.000000000000
                minor_axis = 0.000000000000
                total_flux = 0.000000000000
                cen = (0.0,0.0)
                SNR = 0.0
                return max_flux*1000, major_axis, minor_axis, total_flux, cen, SNR

            else:
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111)
                plt.imshow(z, origin='lower')
                plt.contour(x, y, z_fit.reshape(z.shape), 8, colors='w')
                plt.savefig(field+'_'+track+'.'+ifband+'.fitting.pdf', format='PDF', transparent=True)
                plt.close(fig)

                return max_flux*1000, major_axis, minor_axis, total_flux, cen, SNR

        except:
            major_axis = 0.000000000000
            minor_axis = 0.000000000000
            total_flux = max_flux*1000
            SNR=max_flux/rms
            cen = max_pos

            if math.sqrt((hduwcs.wcs_world2pix(cen[0],cen[1],0)[0]-cen_x)**2+(hduwcs.wcs_world2pix(cen[0],cen[1],0)[1]-cen_y)**2) > bmaj*6/cdelt2:
                major_axis = 0.000000000000
                minor_axis = 0.000000000000
                total_flux = 0.000000000000
                cen = (0.0,0.0)
                SNR = 0.0
                return max_flux*1000, major_axis, minor_axis, total_flux, cen, SNR

            else:
                return max_flux*1000, major_axis, minor_axis, total_flux, cen, SNR    
    else:
        major_axis = 0.000000000000
        minor_axis = 0.000000000000
        total_flux = max_flux*1000
        SNR=max_flux/rms
        cen = max_pos

        if math.sqrt((hduwcs.wcs_world2pix(cen[0],cen[1],0)[0]-cen_x)**2+(hduwcs.wcs_world2pix(cen[0],cen[1],0)[1]-cen_y)**2) > bmaj*6/cdelt2:
                major_axis = 0.000000000000
                minor_axis = 0.000000000000
                total_flux = 0.000000000000
                cen = (0.0,0.0)
                SNR = 0.0
                return max_flux*1000, major_axis, minor_axis, total_flux, cen, SNR
        else:
                return max_flux*1000, major_axis, minor_axis, total_flux, cen, SNR


            
cleanmap = field+'.'+ifband+'.'+track+'.ch0.clean.fits'
if_success = False
try:

    # importing FITS image to a HDU
    chdu   = fits.open(cleanmap)

    # editing the FITS image by multiplying a scaling factor
    clean_img = chdu[0].data[0][0]
    box = eval(sys.argv[5])
    rms = float(sys.argv[6])
    if_success = True

except:
    print('Unable to read the intensity FITS image. Please double check the image file.')

if ( if_success == True ):
      # Reading FITS header
    try:
        naxis1 = chdu[0].header['naxis1']
        naxis2 = chdu[0].header['naxis2']
        crval1 = chdu[0].header['crval1']
        crpix1 = chdu[0].header['crpix1']
        cdelt1 = chdu[0].header['cdelt1']
        crval2 = chdu[0].header['crval2']
        crpix2 = chdu[0].header['crpix2']
        cdelt2 = chdu[0].header['cdelt2']
        hduwcs = wcs.WCS( chdu[0].header)
        hduwcs = hduwcs.dropaxis(dropax=2)
        hduwcs = hduwcs.dropaxis(dropax=2)
    except:
        print( 'Warning. No coordinate headers')
    
    try:
        bmaj = chdu[0].header['bmaj']
        bmin = chdu[0].header['bmin']
        bpa  = chdu[0].header['bpa']
    except:
        print('Warnning. No header for synthesized beam size')

    filename='center_track2_2.txt'
    file = open(filename, 'r')
    lines = file.readlines()
    for i, line in enumerate(lines):
        if line.split()[0] == field:
            for k in range(4):
                if line.split()[k+1] != '(0.0,0.0)':
                    cen_cord = eval(line.split()[k+1])
                    cen_x = hduwcs.wcs_world2pix(cen_cord[0],cen_cord[1],0)[0]
                    cen_y = hduwcs.wcs_world2pix(cen_cord[0],cen_cord[1],0)[1]
                    break
                else:
                    cen_x = naxis1/2
                    cen_y = naxis2/2

    box0 = int(cen_x - 7.5/(cdelt2*3600))
    box1 = int(cen_y - 7.5/(cdelt2*3600))
    box2 = int(cen_x + 7.5/(cdelt2*3600))
    box3 = int(cen_y + 7.5/(cdelt2*3600))


    # select region to fit
#    box_cen = ((box[0]+box[2])/2,(box[1]+box[3])/2)
#    box0 = int(box_cen[0] - 7.5/(cdelt2*3600))
#    box1 = int(box_cen[1] - 7.5/(cdelt2*3600))
#    box2 = int(box_cen[0] + 7.5/(cdelt2*3600))
#    box3 = int(box_cen[1] + 7.5/(cdelt2*3600))

    z = clean_img[box1:box3 , box0:box2]
    peak_flux, major_axis, minor_axis, total_flux, cen, SNR = gaussian_fitting(z, rms)
    sys.stdout.write(str(peak_flux)+'   '+str(major_axis)+'   '+str(minor_axis)+'   '+str(total_flux)+'   ')
    box=(box0,box1,box2,box3)
    
else: 
    box=(0.0, 0.0, 0.0, 0.0)
    peak_flux = 0.000000000000
    major_axis = 0.000000000000
    minor_axis = 0.000000000000
    total_flux = 0.000000000000
    SNR=0.0
    cen=(0.0,0.0)
    sys.stdout.write(str(peak_flux)+'   '+str(major_axis)+'   '+str(minor_axis)+'   '+str(total_flux)+'   ')


write_to_file('axis_FWHM_'+track+'.txt', field, str(major_axis)+' '+str(minor_axis))
write_to_file('flux_'+track+'.txt', field, total_flux)
write_to_file('SNR_'+track+'.txt', field, SNR)
write_to_file('box_'+track+'.txt', field, box)
write_to_file('center_'+track+'.txt', field, '('+str(cen[0])+','+str(cen[1])+')')
