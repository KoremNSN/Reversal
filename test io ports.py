from psychopy.hardware.labjacks import U3
import time
from psychopy import visual, core, monitors, event #, data, tools
lj = U3()
'''

for i in range(0,16):
    print(i)
    lj.setFIOState(i,1)
    time.sleep(1)

for i in range(0,16):
    lj.setFIOState(i,0)
    print(i)
    time.sleep(1.5)
    
for i in range(0,16):
    lj.setFIOState(i,1)
    print(i)
    time.sleep(0.5)

for address in range(5000, 7000):
    try:
        lj.setData(0,address=address)
        print(address)
        time.sleep(0.5)
        lj.setData(1,address=address)
    except:
        continue
        
'''

lj.setFIOState(0,1)
lj.setFIOState(6,1)
time.sleep(1)


lj.setFIOState(0,0)
lj.setFIOState(6,0)
time.sleep(1)


lj.setFIOState(0,1)
lj.setFIOState(6,1)
time.sleep(1)

lj.close()