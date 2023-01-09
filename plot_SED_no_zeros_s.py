from astropy.io import ascii
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import math

def SED_fit(freq, flux, idx):
    freq_log = []
    flux_log = []
    for k in range(len(flux)):
        freq_t = freq[k][idx]
        flux_t = flux[k][idx].ravel()
        zero_idx=np.where(flux_t<0)[0]
        freq_t = np.delete(freq_t,zero_idx)
        flux_t = np.delete(flux_t,zero_idx)
        freq_log.extend(np.log(freq_t).tolist())
        flux_log.extend(np.log(flux_t).tolist())
    
    z, cov = np.polyfit(freq_log, flux_log, 1, cov=True)
    p = np.poly1d(z)
    xp = np.linspace(np.log(freq[0][idx][0]), np.log(freq[-1][idx][-1]), 10)
    ax.plot(np.exp(xp), np.exp(p(xp)),'-', color='grey')
    return round(z[0],2)

tracks = ['track3b','track2a','track1']
colors = cm.jet([0.2, 0.5, 0.8])
freq1 = [199, 219, 228, 248]
freq2 = [260, 280, 292, 312]
freq3 = [337, 357, 397.5, 417.5]
freq = []
flux = []
rms = []
flux_sel = []
rms_sel = []
others=['DoAr_16', 'DoAr_33', 'YLW_8', 'GSS_39', 'DoAr_24E', 'AS_206', 'GSS_26', 'WSB_31', 'VSSG_1', 'DoAr_25', 'IRS_37', 'IRS_41', 'IRS_51', 'IRS_39', 'YLW_47', 'WSB_60', 'HBC_266', 'DoAr_44']


Ophidict = {
    "DoAr 16": "DoAr 16, HBC 257",
    "YLW 47": "IRS 49, GY 308",
    "IRS 39": "IRS 39, WL 4",
    "DoAr 33": "DoAr 33, WSB 53",
    "IRS 37": "IRS 37, GY 244",
    "IRS 41": "IRS 41, WL 3",
    "HBC 266": "SR 13, HBC 266",
    "AS 206": "SR 4, AS 206",
    "WSB 60": "WSB 60, YLW 58",
    "DoAr 24E": "DoAr 24E, GSS 31",
    "IRS 51": "IRS 51, GY 315",
    "DoAr 44": "DoAr 44, HBC 268",
    "VSSG 1": "EL 20, VSSG 1",
    "YLW 8": "SR 21, EL 30",
    "GSS 26": "GSS 26",
    "DoAr 25": "DoAr 25, WSB 29",
    "GSS 39": "EL 27, GSS 39",
    "WSB 31": "EL 24, WSB 31"
}

target = []
spidx = []
freq_q = []
Flux_q = []
Flux_e_q = []
freq_l_q = []
Flux_l_e_q = []
Flux_l_q = []
table = ascii.read('datafile1.txt')

filename='flux_'+tracks[0]+'.txt'
file = open(filename, 'r')
lines = file.readlines()
for i in range(len(lines)):
    if lines[i].split()[0] in others:
        name=""
        for j in range(len(lines[i].split()[0].split('_'))):
            name = name + ' ' + lines[i].split()[0].split('_')[j]
        target.append(name[1:])
        idx=np.where(table['Name'] == Ophidict[name[1:]])[0]
        tempf = []
        tempF = []
        tempF_e = []
        tempf_l = []
        tempF_l = []
        tempF_l_e = []

        if len(idx) != 0:
            spidx.append(table['Sp+Index'][idx][0])
            if table['l_F850'][idx][0] == '<':
                tempf_l.append(353)
                tempF_l.append(table['F850'][idx][0])
                tempF_l_e.append(table['e_F850'][idx][0])
            else:
                tempf.append(353)
                tempF.append(table['F850'][idx][0])
                tempF_e.append(table['e_F850'][idx][0])

            if table['l_F1.3'][idx][0] == '<':
                tempf_l.append(231)
                tempF_l.append(table['F1.3'][idx][0])
                tempF_l_e.append(table['e_F1.3'][idx][0])
            else:
                tempf.append(231)
                tempF.append(table['F1.3'][idx][0])
                tempF_e.append(table['e_F1.3'][idx][0])

        else:
            spidx.append(np.nan)
        freq_q.append(tempf)
        Flux_q.append(tempF)
        Flux_e_q.append(tempF_e)
        freq_l_q.append(tempf_l)
        Flux_l_q.append(tempF_l)
        Flux_l_e_q.append(tempF_l_e)



for track in tracks:
    filename='flux_'+track+'.txt'
    file = open(filename, 'r')
    lines = file.readlines()
    temp = []
    tempf = []
    a = 0
    for i in range(len(lines)):
        if lines[i].split()[0] in others:
            a = 1
            temp.append(lines[i].split()[1:])
            if track =='track3b':
                tempf.append(freq1)
            elif track == 'track2a':
                tempf.append(freq2)
            else:
                tempf.append(freq3)
    if a == 1:
        flux.append(temp)
        freq.append(tempf)

for track in tracks:
    filename='rms_'+track+'.txt'
    file = open(filename, 'r')
    lines = file.readlines()
    temp = []
    a = 0
    for i in range(len(lines)):
        if lines[i].split()[0] in others:
            a = 1
            temp.append(lines[i].split()[1:])
    if a == 1:
        rms.append(temp)



# for track in tracks:
#    filename='flux_'+track+'.sel.txt'
#    file = open(filename, 'r')
#    lines = file.readlines()
#    temp = []
#    for i in range(len(lines)):
#        temp.append(lines[i].split()[1:])
#    flux_sel.append(temp)

#for track in tracks:
#    filename='rms_'+track+'.sel.txt'
#    file = open(filename, 'r')
#    lines = file.readlines()
#    temp = []
#    for i in range(len(lines)):
#        temp.append(lines[i].split()[1:])
#    rms_sel.append(temp)


flux=np.array(flux).astype(float) 
rms=np.array(rms).astype(float)*1000
#flux_sel=np.array(flux_sel).astype(float)
#rms_sel=np.array(rms_sel).astype(float)*1000

flux_c=np.zeros(flux.shape)
cal_ratio=[[1, 1, 11.057/10.507,1],[10.383/9.511, 9.985/9.153, 9.780/10.366, 9.444/9.470],[9.077/8.180, 8.767/8.199, 8.322/7.599, 8.092/7.490]]

for i in range(3):
    for j in range(len(target)):
        for k in range(4):
            flux_c[i][j][k] = flux[i][j][k]*cal_ratio[i][k]

def get_idx(target, flux_0, rank):
    # index [:,0] for 345 GHz lsb
    flux_0_s = sorted(flux_0[:,0], reverse = True)
    idx_l= list(np.where(flux_0[:,0]==flux_0_s[rank])[0])
    return idx_l

flux=np.where(flux==0.0,-100,flux)
flux_c=np.where(flux_c==0.0,-100,flux_c)

num = 6
num_sel = 3

num_figure= int((len(target))/num)
times = 1
for i in range(num_figure):
    fig = plt.figure(figsize=(15, 12))
    for j in range(num):
#        ax = fig.add_subplot(322+j*2)
#        rank = 3*i+j
        # index[1] for track 5
#        idx_l = get_idx(target, flux_sel[1], rank)
#        if len(idx_l) > times:
#            idx = idx_l[times-1]
#            times += 1
#        elif len(idx_l) == times and times > 1:
#            idx = idx_l[times-1]
#            times = 1
#        else:
#            idx = idx_l[0]
#            times = 1
#        if_zero = 0
#        flux_max = 0
#        for k in range(len(flux)):
#            ax.errorbar(freq3[0:4], flux_sel[k][idx][0:4], yerr=rms_sel[k][idx][0:4], fmt='o', color=colors[k])
#            if_zero+=flux_sel[k][idx].tolist().count(0.0)
#            flux_max = max(flux_max, max(flux_sel[k][idx]))

#        plt.ylim([0, flux_max*1.25])
#        plt.legend(['track4', 'track5', 'track6'])
#        if (j==5):
#            plt.xlabel('Frequency [GHz]', size=14)
#        if (if_zero>0):
#            ax.title.set_text(target[idx])
#        else:
#            alpha  = SED_fit(freq3, flux_sel, idx)
#            ax.title.set_text(target[idx]+', \u03B1='+str(alpha))


        ax = fig.add_subplot(321+j)
        rank = num*i+j
        idx_l = get_idx(target, flux[tracks.index('track1')], rank)
        if len(idx_l) > times:
            idx = idx_l[times-1]
            times += 1
        elif len(idx_l) == times and times > 1:
            idx = idx_l[times-1]
            times = 1
        else:
            idx = idx_l[0]
            times = 1
        if_zero = 0
        flux_max = 0
        for k in range(len(flux)):
            ax.errorbar(freq[k][idx][0:4], flux[k][idx][0:4], yerr=rms[k][idx][0:4], fmt='o', color=colors[k])
            if_zero+=flux[k][idx].tolist().count(-100)
            flux_max = max(flux_max, max(flux[k][idx]))

#            ax.errorbar(freq[k][idx][0:4], flux_c[k][idx][0:4], yerr=rms[k][idx][0:4], fmt='o', color='brown',ms=4)
#            if_zero+=flux_c[k][idx].tolist().count(-100)
#            flux_max = max(flux_max, max(flux_c[k][idx]))

        if len(Flux_q[idx]) > 0:
            ax.errorbar(freq_q[idx], Flux_q[idx], yerr=Flux_e_q[idx], fmt='D', color='grey',alpha=0.5)
            flux_max = max(flux_max, max(Flux_q[idx]))

        if len(Flux_l_q[idx]) > 0:
            ax.errorbar(freq_l_q[idx], Flux_l_q[idx], yerr=Flux_l_e_q[idx], fmt='v', color='grey',alpha=0.5)
            flux_max = max(flux_max, max(Flux_l_q[idx]))

        try:
            freq_a, flux_a, flux_e_a = np.loadtxt('flux_quote_'+target[idx]+'.txt', dtype='float',usecols=range(3), unpack=True)            
            ax.errorbar(freq_a, flux_a, yerr=flux_e_a, fmt='o', color='brown',alpha=0.5)
            flux_max = max(flux_max, max(flux_a))

        except:
            flux_max = flux_max

        plt.ylim([0, flux_max*1.25])
        plt.legend(['0606 230 GHz-3b','0523 270 GHz-2a','0524 400 GHz-1','A&W(2007)','A&W(2007)'])
        if (j%2==0):
            plt.ylabel('Flux density [mJy]', size=14)
        if (j==4 or j==5):
            plt.xlabel('Frequency [GHz]', size=14) 
#        if (if_zero>0):
#            ax.title.set_text(target[idx])
#        else:
        alpha = SED_fit(freq, flux, idx)
        ax.title.set_text(target[idx]+', \u03B1='+str(alpha)+', ['+str(spidx[idx])+']')

    fig.tight_layout()
    plt.savefig('flux_measurement_0_'+str(i)+'.pdf', format='PDF', transparent=True)
    plt.close(fig) 

i = num_figure
fig = plt.figure(figsize=(15, 12))
for j in range(len(target)%num):
        ax = fig.add_subplot(321+j)
        rank = num*i+j
        idx_l = get_idx(target, flux[tracks.index('track1')], rank)
        if len(idx_l) > times:
            idx = idx_l[times-1]
            times += 1
        elif len(idx_l) == times and times > 1:
            idx = idx_l[times-1]
            times = 1
        else:
            idx = idx_l[0]
            times = 1
        if_zero = 0
        flux_max = 0
        for k in range(len(flux)):
            ax.errorbar(freq[k][idx][0:4], flux[k][idx][0:4], yerr=rms[k][idx][0:4], fmt='o', color=colors[k])
            if_zero+=flux[k][idx].tolist().count(-100)
            flux_max = max(flux_max, max(flux[k][idx]))

        for k in range(len(flux_c)):
            ax.errorbar(freq[k][idx][0:4], flux_c[k][idx][0:4], yerr=rms[k][idx][0:4], fmt='o', color='brown')
            if_zero+=flux_c[k][idx].tolist().count(-100)
            flux_max = max(flux_max, max(flux_c[k][idx]))

        if len(Flux_q[idx]) > 0:
            ax.errorbar(freq_q[idx], Flux_q[idx], yerr=Flux_e_q[idx], fmt='D', color='grey',alpha=0.5)
            flux_max = max(flux_max, max(Flux_q[idx]))

        if len(Flux_l_q[idx]) > 0:
            ax.errorbar(freq_l_q[idx], Flux_l_q[idx], yerr=Flux_l_e_q[idx], fmt='v', color='grey',alpha=0.5)
            flux_max = max(flux_max, max(Flux_l_q[idx]))


        plt.ylim([0, flux_max*1.25])
        plt.legend(['0606 230 GHz-3b','0523 270 GHz-2a','0524 400 GHz-1','A&W(2007)','A&W(2007)'])
        if (j%2==0):
            plt.ylabel('Flux density [mJy]', size=14)
        if (j==4 or j==5):
            plt.xlabel('Frequency [GHz]', size=14)
#        if (if_zero>0):
#            ax.title.set_text(target[idx])
#        else:
        alpha = SED_fit(freq, flux, idx)
        ax.title.set_text(target[idx]+', \u03B1='+str(alpha)+', ['+str(spidx[idx])+']')

fig.tight_layout()
plt.savefig('flux_measurement_0_'+str(i)+'.pdf', format='PDF', transparent=True)
plt.close(fig)



#flux = []
#rms = []


#for track in tracks:
#    filename='flux_'+track+'.sel.txt'
#    file = open(filename, 'r')
#    lines = file.readlines()
#    temp = []
#    for i in range(len(lines)):
#        temp.append(lines[i].split()[1:])
#    flux.append(temp)

#for track in tracks:
#    filename='rms_'+track+'.sel.txt'
#    file = open(filename, 'r')
#    lines = file.readlines()
#    temp = []
#    for i in range(len(lines)):
#        temp.append(lines[i].split()[1:])
#    rms.append(temp)

#flux=np.array(flux).astype(float)  
#rms=np.array(rms).astype(float)*1000
#num_figure= int((len(target))/6)

#for i in range(num_figure):
#    fig = plt.figure(figsize=(15, 12))
#    for j in range(6):
#        ax = fig.add_subplot(320+j+1)
#        idx = 6*i+j
#        ax.errorbar(freq3[0:4], flux[0][idx][0:4], yerr=rms[0][idx][0:4], fmt='o', color='tab:green')
#        ax.errorbar(freq3[0:4], flux[1][idx][0:4], yerr=rms[1][idx][0:4], fmt='o', color='tab:blue')
#        ax.errorbar(freq3[0:4], flux[2][idx][0:4], yerr=rms[2][idx][0:4], fmt='o', color='tab:orange')
#        plt.ylim([0, None])
#        if (j%2 == 0):
#            plt.ylabel('Flux density [mJy]', size=14)
#        if (j==4 or j==5):
#            plt.xlabel('Frequency [GHz]', size=14)
#        if (flux[0][idx].tolist().count(0.0)+flux[1][idx].tolist().count(0.0)+flux[2][idx].tolist().count(0.0)>0):
#            ax.title.set_text(target[idx])
#        else:
#       	    alpha = SED_fit(freq3, flux[0][idx], flux[1][idx], flux[2][idx])
#       	    ax.title.set_text(target[idx]+', \u03B1='+str(alpha))
#        ax.title.set_text(target[idx])
#    plt.savefig('flux_measurement_'+str(i)+'.sel.pdf', format='PDF', transparent=True)
#    plt.close(fig)

#fig = plt.figure(figsize=(15, 12))
#for j in range(len(target)%6):
#    ax = fig.add_subplot(320+j+1)
#    idx = 6*num_figure+j
#    ax.errorbar(freq3[0:4], flux[0][idx][0:4], yerr=rms[0][idx][0:4], fmt='o', color='tab:green')
#    ax.errorbar(freq3[0:4], flux[1][idx][0:4], yerr=rms[1][idx][0:4], fmt='o', color='tab:blue')
#    ax.errorbar(freq3[0:4], flux[2][idx][0:4], yerr=rms[2][idx][0:4], fmt='o', color='tab:orange')
#    plt.ylim([0, None])
#    if (j%2 == 0):
#        plt.ylabel('Flux density [mJy]', size=14)
#    if (j==4 or j==5):
#        plt.xlabel('Frequency [GHz]', size=14)
#    if (flux[0][idx].tolist().count(0.0)+flux[1][idx].tolist().count(0.0)+flux[2][idx].tolist().count(0.0)>0):
#        ax.title.set_text(target[idx])
#    else:
#        alpha = SED_fit(freq3, flux[0][idx], flux[1][idx], flux[2][idx])
#        ax.title.set_text(target[idx]+', \u03B1='+str(alpha))
#    ax.title.set_text(target[idx])
#plt.savefig('flux_measurement_'+str(num_figure)+'.sel.pdf', format='PDF', transparent=True)
#plt.close(fig)

