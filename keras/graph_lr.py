import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy

folder = 'learning_rate/'
spec = '-50epoch30batch'
model = 'model06'

name = [
        model + '-10epoch30batch',
        model + '-10epoch50batch',
        model + '-10epoch100batch',
        model + '-20epoch30batch',
        model + '-20epoch50batch',
        model + '-20epoch100batch',
        model + '-30epoch30batch',
        model + '-30epoch50batch',
        model + '-30epoch100batch',
        model + '-40epoch30batch',
        model + '-40epoch50batch',
        model + '-40epoch100batch',
        model + '-50epoch30batch',
        model + '-50epoch50batch',
        model + '-50epoch100batch'
        ]
# ---------

n = len(name)
mod = []
for i in range(n):
    mod.append(numpy.load(folder + name[i] + '.npy'))



fig = plt.figure(figsize=(10,5))
ax1 = fig.add_subplot(111)
axHandles=[]
for i in range(n):        
    l, = ax1.plot(range(10,101,10), mod[i][:,0], linestyle='-', lw=2, label=name[i])
    axHandles.append(l)

ax1.set_xlabel('% trenovaci mnoziny')
ax1.set_ylabel('Loss')
plt.legend(handles=axHandles)
plt.show()

#fig.savefig(modelname + '.png')

fig = plt.figure(figsize=(10,5))
ax1 = fig.add_subplot(111)
axHandles=[]
for i in range(n):        
    l, = ax1.plot(range(10,101,10), mod[i][:,1], linestyle='-', lw=2, label=name[i])
    axHandles.append(l)

ax1.set_xlabel('% trenovaci mnoziny')
ax1.set_ylabel('MAE')
plt.legend(handles=axHandles)
plt.show()



fig = plt.figure(figsize=(10,5))
ax1 = fig.add_subplot(111)
axHandles=[]
for i in range(n):        
    l, = ax1.plot(range(10,101,10), mod[i][:,2], linestyle='-', lw=2, label=name[i])
    axHandles.append(l)

ax1.set_xlabel('% trenovaci mnoziny')
ax1.set_ylabel('RMSE')
plt.legend(handles=axHandles)
plt.show()








