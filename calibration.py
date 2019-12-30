from psychopy.hardware.labjacks import U3
import time
from psychopy import visual, core, monitors, event #, data, tools

win = visual.Window(color=[0,0,0], screen = 1, fullscr=True, mouseVisible = False)
Text = visual.TextStim(win,text="US", pos=(0,0), font='Courier New', alignHoriz = 'center', alignVert = 'center', color = 'black',units = 'norm')
lj = U3()

while True:
    lj.setFIOState(6,1)
    Text.text = 'get ready'
    Text.draw()
    win.flip()
    time.sleep(1)
    lj.setFIOState(6,0)
    Text.text = 'did you fill it?'
    Text.draw()
    win.flip()
    buttonPress=event.waitKeys()
         
    if buttonPress == ['5']:
        break
    
win.close()

lj.close()