import numpy as np
import matplotlib.pyplot as plt
# plt.rcParams.update({'font.size': 15})

names_Cellular= ['Time','U','I1','I2','D','Ve','IFNe']
names_Plaque= ['Time','avgI1rd','avgI2rd','avgDrd']
t = 480
replicate = 20
parameter = 'k31'
# p = [1.0,5.0,10.0, 50.0, 100.0]
p = [1.0, 3.98, 5.0, 6.31, 7.94, 10.0, 12.59, 15.85, 19.95, 25.12, 39.81, 50.0, 63.10, 79.43, 100.0, 125.89]
dt = 1.666667e-01

VeAUC = []
IFNeAUC = []
GrowthRate = []
for i in range(len(p)):
    iVeAUC = []
    iIFNeAUC = []
    iGrowthRate = []
    for r in range(1,replicate+1):
        f = np.genfromtxt('Data/FullModelCellular_%s_%.2f_%i.txt' % (parameter,p[i],r),
                          skip_header=1, delimiter=',',
                          names=names_Cellular,
                          max_rows=t)
        iVeAUC.append(np.log10(np.trapz(f['Ve'], dx = dt)))
        iIFNeAUC.append(np.log10(np.trapz(f['IFNe'],dx = dt)))
        f = np.genfromtxt('Data/PlaqueAssay_%s_%.2f_%i.txt' % (parameter, p[i], r),
                          skip_header=1,
                          delimiter=',',
                          names=names_Plaque,
                          max_rows=t)
        [mI1, y0I1] = np.polyfit(f['Time'][-10:],f['avgI1rd'][-10:], 1)
        iGrowthRate.append(mI1)
    VeAUC.append(iVeAUC)
    IFNeAUC.append(iIFNeAUC)
    GrowthRate.append(iGrowthRate)

## No Outliers Plots
plt.boxplot(VeAUC,
            sym = '',
            labels=p,
            patch_artist=True,
            boxprops = {'facecolor':'#666699','alpha':0.75},
            medianprops={'color':'black'})
plt.title('Virus AUC')
plt.ylabel(r'PFU hr/ml')
plt.xlabel('Parameter Multiplier')
plt.xticks(rotation=270)
plt.tight_layout()
plt.gca().set_aspect(1.0 / plt.gca().get_data_ratio() * 1.0)
plt.tight_layout()
plt.savefig('Fig.BoxNoOutliers.Virus_AUC_%s.pdf' % parameter,transparent=True)
plt.clf()

plt.boxplot(IFNeAUC,
            sym = '',
            labels=p,
            patch_artist=True,
            boxprops = {'facecolor':'#993300','alpha':0.75},
            medianprops={'color':'black'})
plt.title('IFN AUC')
plt.ylabel(r'$\mu$M hr')
plt.xlabel('Parameter Multiplier')
plt.xticks(rotation=270)
plt.gca().set_aspect(1.0 / plt.gca().get_data_ratio() * 1.0)
plt.tight_layout()
plt.savefig('Fig.BoxNoOutliers.IFNe_AUC_%s.pdf' % parameter,transparent=True)
plt.clf()

plt.boxplot(GrowthRate,
            sym = '',
            labels=p,
            patch_artist=True,
            boxprops = {'facecolor':'black','alpha':0.50},
            medianprops={'color':'black'})
plt.title('Plaque Growth Rate')
plt.ylabel('Plaque Growth Rate (cell diameter/hrs)')
plt.xlabel('Parameter Multiplier')
plt.xticks(rotation=270)
plt.gca().set_aspect(1.0 / plt.gca().get_data_ratio() * 1.0)
plt.tight_layout()
plt.savefig('Fig.BoxNoOutliers.Growth_Rate_%s.pdf' % parameter, transparent=True)
plt.clf()

## Filtered Plots
plt.boxplot(VeAUC,
            labels=p,
            patch_artist=True,
            boxprops = {'facecolor':'#666699','alpha':0.75},
            medianprops={'color':'black'})
plt.title('Virus AUC')
plt.ylabel(r'PFU hr/ml')
plt.xlabel('Parameter Multiplier')
plt.xticks(rotation=270)
plt.gca().set_aspect(1.0 / plt.gca().get_data_ratio() * 1.0)
plt.tight_layout()
plt.savefig('Fig.BoxFiltered.Virus_AUC_%s.pdf' % parameter,transparent=True)
plt.clf()

plt.boxplot(IFNeAUC,
            labels=p,
            patch_artist=True,
            boxprops = {'facecolor':'#993300','alpha':0.75},
            medianprops={'color':'black'})
plt.title('IFN AUC')
plt.ylabel(r'$\mu$M hr')
plt.xlabel('Parameter Multiplier')
plt.xticks(rotation=270)
plt.gca().set_aspect(1.0 / plt.gca().get_data_ratio() * 1.0)
plt.tight_layout()
plt.savefig('Fig.BoxFiltered.IFNe_AUC_%s.pdf' % parameter,transparent=True)
plt.clf()

plt.boxplot(GrowthRate,
            labels=p,
            patch_artist=True,
            boxprops = {'facecolor':'black','alpha':0.75},
            medianprops={'color':'black'})
plt.title('Plaque Growth Rate')
plt.ylabel('Plaque Growth Rate (cell diameter/hrs)')
plt.xlabel('Parameter Multiplier')
plt.xticks(rotation=270)
plt.gca().set_aspect(1.0 / plt.gca().get_data_ratio() * 1.0)
plt.tight_layout()
plt.savefig('Fig.BoxFiltered.Growth_Rate_%s.pdf' % parameter, transparent=True)
plt.clf()

## All Outliers Plots
plt.boxplot(VeAUC,
            labels=p,
            patch_artist=True,
            boxprops = {'facecolor':'#666699','alpha':0.75},
            medianprops={'color':'black'})
plt.title('Virus AUC')
plt.ylabel(r'PFU hr/ml')
plt.xlabel('Parameter Multiplier')
plt.xticks(rotation=270)
plt.gca().set_aspect(1.0 / plt.gca().get_data_ratio() * 1.0)
plt.tight_layout()
plt.savefig('Fig.BoxAllOutliers.Virus_AUC_%s.pdf' % parameter,transparent=True)
plt.clf()

plt.boxplot(IFNeAUC,
            labels=p,
            patch_artist=True,
            boxprops = {'facecolor':'#993300','alpha':0.75},
            medianprops={'color':'black'})
plt.title('IFN AUC')
plt.ylabel(r'$\mu$M hr')
plt.xlabel('Parameter Multiplier')
plt.xticks(rotation=270)
plt.gca().set_aspect(1.0 / plt.gca().get_data_ratio() * 1.0)
plt.tight_layout()
plt.savefig('Fig.BoxAllOutliers.IFNe_AUC_%s.pdf' % parameter,transparent=True)
plt.clf()

plt.boxplot(GrowthRate,
            labels=p,
            patch_artist=True,
            boxprops = {'facecolor':'black','alpha':0.50},
            medianprops={'color':'black'})
plt.title('Plaque Growth Rate')
plt.ylabel('Plaque Growth Rate (cell diameter/hrs)')
plt.xlabel('Parameter Multiplier')
plt.xticks(rotation=270)
plt.gca().set_aspect(1.0 / plt.gca().get_data_ratio() * 1.0)
plt.tight_layout()
plt.savefig('Fig.BoxAllOutliers.Growth_Rate_%s.pdf' % parameter, transparent=True)
plt.clf()