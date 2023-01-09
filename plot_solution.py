import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import math
import datetime as dt
import matplotlib.dates as md

def plot_sol(ant, track, rx, sideband, target, color, zord):
    time = []
    phase = []
    filename = target+'_'+track+'.'+rx+'.'+sideband+'.1p.gain.txt'
    file = open(filename, 'r')
    lines = file.readlines()
    for i in range(int((len(lines)-4)/2)):
        t = lines[i*2+4].split()[1]
        if ant<7:
            pha = float(lines[i*2+4].split()[ant+1])%360
            if pha != 0 or ant == 6:
                phase.append(pha)
                time.append(t)
        else:
            pha = float(lines[i*2+5].split()[ant-7])%360
            if pha != 0 or ant == 6:
                phase.append(pha)
                time.append(t)
    if len(phase)!= 0:
        phase = [phase[i] if phase[i] <180 else phase[i]-360 for i in range(len(phase))]
        time_d = [dt.datetime.strptime(t,'%H:%M:%S') for t in time]
        xfmt = md.DateFormatter('%H:%M:%S')
        if track =='track5':
            ax.set_xlim([dt.datetime.strptime('11:30:00', '%H:%M:%S'), dt.datetime.strptime('20:40:00', '%H:%M:%S')])
        ax.xaxis.set_major_formatter(xfmt)
        ax.scatter(time_d, phase, color=color, zorder=zord)

targets=['DoAr_16','DoAr_33','YLW_8','GSS_39','DoAr_24E','AS_206','GSS_26','WSB_31','VSSG_1','DoAr_25','IRS_37','IRS_41','IRS_51','IRS_39','YLW_47','WSB_60','HBC_266','DoAr_44']
tracks=['track1','track2a','track3b']
rxs=['rx230','rx240','rx345', 'rx400']
sidebands=['lsb', 'usb']
others=['FM_Tau', 'CW_Tau', 'DD_Tau', 'CoKu_Tau_1', 'BP_Tau', 'DE_Tau', 'IP_Tau', 'FV_Tau','DH_Tau', 'IQ_Tau', 'DK_Tau', 'FY_Tau', 'GK_Tau', 'AA_Tau', 'CI_Tau', '04278+2253', 'UX_Tau', 'V710_Tau', 'DM_Tau', 'DQ_Tau', 'Haro_6-37', 'HO_Tau', 'DN_Tau', 'HV_Tau', 'CIDA-7', 'GO_Tau', 'CIDA-7', 'DS_Tau', 'UY_Aur', 'Haro_6-39', 'SU_Aur', 'RW_Aur', 'CIDA-9', 'V836_Tau']
ant = [1, 2, 3, 4, 5, 6, 7, 8]

for track in tracks:
    for rx in rxs:
        for sideband in sidebands:
            fig = plt.figure(figsize=(15, 12))
            l = []
            for i in range(len(ant)):
                ax = fig.add_subplot(421+i)
                colors = cm.turbo(np.linspace(0, 1, len(targets)))

                for target,color in zip(targets,colors):
                    try:
                        plot_sol(ant[i], track, rx, sideband, target, color, 0)
                        l.append(target)
                    except:
                        print('No solutions for '+target+'_'+track+'.'+rx+'.'+sideband+', Ant'+str(ant))

                if (i%2 == 0):
                    plt.ylabel('Phase (deg)', size=10)
                if (ant[i]==7 or ant[i]==8):
                    plt.xlabel('UTC time', size=10)
                if (ant[i]==5):
                    plt.legend(l ,loc=4, prop={'size': 8}, ncol=5, framealpha=0.3)

#                for target in others:
#                    try:
#                        plot_sol(ant[i], track, rx, sideband, target, 'lightgrey', -1)
#                    except:
#                        print('No solutions for '+target+'_'+track+'.'+rx+'.'+sideband+', Ant'+str(ant[i]))


                ax.title.set_text('Ant'+str(ant[i]))
                ax.set_ylim([-180,180])
            fig.tight_layout()
            plt.savefig('selfcal_solution_'+track+'.'+rx+'.'+sideband+'_b.pdf', format='PDF', transparent=True)
            plt.savefig('selfcal_solution_'+track+'.'+rx+'.'+sideband+'_b.png', transparent=True)
            plt.close(fig)



group1=['FM_Tau', 'CW_Tau', '04113+2758', 'CY_Tau', 'DD_Tau', 'V892_Tau', 'CoKu_Tau_1']
group2=['CoKu_Tau_1', 'BP_Tau', 'RY_Tau', 'DE_Tau', 'IP_Tau', 'FT_Tau', 'FV_Tau']
group3=['DH_Tau', 'IQ_Tau', 'DK_Tau', 'UZ_Tau', 'DL_Tau', 'FY_Tau', 'GK_Tau', 'AA_Tau']
group4=['LkCa_15', 'CI_Tau', '04278+2253', 'T_Tau', 'UX_Tau', 'V710_Tau', 'DM_Tau', 'DQ_Tau', 'Haro_6-37', 'DR_Tau']
group5=['HO_Tau', 'DN_Tau', 'DO_Tau', 'HV_Tau', 'IC_2087_IR', 'CIDA-7', 'GO_Tau', 'CIDA-7', 'DS_Tau']
group6=['DS_Tau', 'UY_Aur', 'Haro_6-39', 'GM_Aur', 'AB_Aur', 'SU_Aur', 'RW_Aur', 'CIDA-9', 'V836_Tau']

targets=[group1, group2, group3, group4, group5, group6]

#for track in tracks:
#    for rx in rxs:
#        for sideband in sidebands:
#            for group in targets:
#                fig = plt.figure(figsize=(15, 12))
#                l = []
#                for ant in range(1,9):
#                    ax = fig.add_subplot(420+int(ant))
#                    colors = cm.turbo(np.linspace(0, 1, len(group)))
#                    for target,color in zip(group,colors):
#                        try:
#                            plot_sol(ant[i], track, rx, sideband, target, color, 0)
#                            l.append(target)
#                        except:
#                            print('No solutions for '+target+'_'+track+'.'+rx+'.'+sideband+', Ant'+str(ant))
#                    if (ant%2 == 1):
#                        plt.ylabel('Phase (deg)', size=10)
#                    if (ant==7 or ant==8):
#                        plt.xlabel('UTC time', size=10)
#                    if (ant==6):
#                        plt.legend(l ,loc=2, prop={'size': 8}, ncol=3)
#                    ax.title.set_text('Ant'+str(ant))
#                    ax.set_ylim([-180,180])
#                fig.tight_layout()
#                plt.savefig('selfcal_solution_'+track+'.'+rx+'.'+sideband+'_'+group[0]+'.pdf', format='PDF', transparent=True)
#                plt.close(fig)
