553# -*- coding: utf-8 -*-
"""
Spyder Editor

Reversal learinging in fMRI with labjack and eyelink 21.11.2019
Nachshon Korem, Yale

"""
### import packages
import datetime, os, random, time
from psychopy import visual, core, monitors, event #, data, tools
from psychopy.hardware.labjacks import U3
import pylink as pl


# %% create a subject object
class subject:
    
    def __init__(self, sub_n):
        self.subjectID = sub_n # get subject number
        
        # create a time stamp at the bigining of the run
        date=datetime.datetime.now()
        self.time_stamp = str(date.day) + str(date.month) + str(date.year) + str(date.hour) + str(date.minute) + str(date.second)
        
        # create file and folder for the run
        cwd = os.getcwd()
        fileName = cwd + '/data/cb1Reversal_' + str(self.subjectID) + '_' + str(self.time_stamp)
        if not os.path.isdir('data/'):
           os.makedirs('data/')
        self.dataFile = open(fileName+'.csv', 'w')
        
        #writes headers for the output file
        self.dataFile.write('Sub,Group,time,Trial_n,Condition,color,US,FixationOnset,StimulusOnset,USOnset,reversal\n')

        # create a window object
        self.win = visual.Window(color=[0,0,0], screen = 1, fullscr=True, mouseVisible = False)
        #initiate a trial counter
        self.trial_n = 0
        self.lj = U3()
        self.lj.setFIOState(6,1)
        self.lj.setFIOState(0,0)
        self.reversed=False

        # creates the visual objects for the experiment
        self.fixation=visual.Circle(self.win, radius=10, fillColor='black',lineColor='black',units = 'pix')
        self.rect = visual.Rect(self.win,units="norm",width=0.5,height=0.5,fillColor='black',lineColor='Grey',pos=(0,0))
        self.Text = visual.TextStim(self.win,text="US", pos=(0,0), font='Courier New',
            alignHoriz = 'center', alignVert = 'center', color = 'black',units = 'norm')
        
        # base on subject number subjects are divided to group A and B (%2) and color order (%4<=1)
        if self.subjectID % 2 == 0:
            self.group = "A"
        else:
            self.group = "B"
            
        if self.subjectID % 4 <= 1:
            self.stim = {"CSplus":"blue","CSminus":"yellow"}
        else:
            self.stim={"CSplus":"yellow","CSminus":"blue"}
            
            
 # %% initaite the eyelink module and run calibration
       
    def setup_eyelink(self):
        
        '''Thank you very much
        
        '''
        # call for eyelink
        self.eyelink_tracker = pl.EyeLink("100.1.1.1")
        
        #parameters for eyelink
        self.monitor = monitors.Monitor('testMonitor')
        self.winSize = self.monitor.getSizePix()
        self.foreground = (250,250,250)
        self.background = (127,127,127)
        
        # create file
        self.edfFileName = "cbConfig" + str(self.subjectID)
        if len(self.edfFileName) > 8:
            self.edfFileName = self.edfFileName[0:8]
        pl.getEYELINK().openDataFile(self.edfFileName)
        pl.getEYELINK().setOfflineMode()
    
        #Eyelink - Gets the display surface and sends a mesage to EDF file;
        pl.getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d"%(self.winSize[0]-1, self.winSize[1]-1))
        pl.getEYELINK().sendMessage("Resolution %d %d" %((self.winSize[0]-1, self.winSize[1]-1)))
        pl.getEYELINK().sendMessage("EyeToScreen %d" %(self.monitor.getDistance()))
        pl.getEYELINK().sendMessage("MonitorWidth %d" %(self.monitor.getWidth()))
    
        #EyeLink - Set data file contents
        pl.getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT")
        pl.getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET,INPUT")
    
        #EyeLink - Set Filter contents
        pl.getEYELINK().sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT")
        pl.getEYELINK().sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,INPUT")
    
        #EyeLink - Set Calibration Environment
        pl.setCalibrationColors(self.foreground, self.background);  	#Sets the calibration target and background color  - background color should match testing background        
        
        pl.flushGetkeyQueue()
        pl.getEYELINK().setOfflineMode()
        winX = int(self.winSize[0])
        winY = int(self.winSize[1])
        pl.openGraphics((winX,winY),32)
        pl.getEYELINK().doTrackerSetup()
        pl.closeGraphics()
        pl.setCalibrationSounds("", "", "");
        pl.setDriftCorrectSounds("", "off", "off");
        
        # close configuration file
        event.clearEvents()
        pl.getEYELINK().closeDataFile()
        transferFileName = self.edfFileName + '.edf' # fileName
        pl.getEYELINK().receiveDataFile(self.edfFileName, transferFileName)

# %%
    def two_min(self):
        
        
        self.edfFileName = "cb2M" + str(self.subjectID)
        if len(self.edfFileName) > 8:
            self.edfFileName = self.edfFileName[0:8]
        pl.getEYELINK().openDataFile(self.edfFileName)
        pl.getEYELINK().setOfflineMode()
        
        event.clearEvents()
        self.Text.text = 'Please Relax "7" to continue'
        self.Text.draw()
        pl.getEYELINK().sendMessage('WaitForRestingState')
        self.win.flip()
        
        pl.getEYELINK().sendMessage('WaitForExptrStart')
        event.waitKeys(keyList = ['7'])
        
        event.clearEvents()
        self.Text.text = 'Waiting for the scanner to start...'
        self.Text.draw()
        pl.getEYELINK().sendMessage('WaitForExptrStart')
        self.win.flip()
        
        pl.getEYELINK().sendMessage('WaitForScanner')
        event.waitKeys(keyList = ['5'])
                
        # get a start point  
        pl.getEYELINK().startRecording(1,1,1,1)
        self.Text.text = ""
        self.Text.draw()
        self.win.flip()
        pl.getEYELINK().sendMessage('resting')
        time.sleep(120)
        
        # close and transfer file
        pl.getEYELINK().closeDataFile()
        transferFileName = self.edfFileName + '.edf' # fileName
        pl.getEYELINK().receiveDataFile(self.edfFileName, transferFileName) 
        
# %%
    def shock_calibration(self):
        
        self.Text.text = 'shock intensity calibration'
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        
        while True:
            self.lj.setFIOState(6,1)
            self.Text.text = 'get ready'
            self.Text.draw()
            self.win.flip()
            time.sleep(1)
            for i in range(3,7):
                self.lj.setFIOState(i,1)
            for i in range(3,7):
                self.lj.setFIOState(i,0)
            for i in range(3,7):
                self.lj.setFIOState(i,1)
             
            self.Text.text = 'did you feel it? "5" to accept'
            self.Text.draw()
            self.win.flip()
            buttonPress=event.waitKeys()
                 
            if buttonPress == ['5']:
                break
# %%
    def resting_state(self, resttime):
        
        self.edfFileName = "cbRS" + str(self.subjectID)
        if len(self.edfFileName) > 8:
            self.edfFileName = self.edfFileName[0:8]
        pl.getEYELINK().openDataFile(self.edfFileName)
        pl.getEYELINK().setOfflineMode()
        
        event.clearEvents()
        self.Text.text = 'Please Relax "7" to continue'
        self.Text.draw()
        pl.getEYELINK().sendMessage('WaitForRestingState')
        self.win.flip()
        
        pl.getEYELINK().sendMessage('WaitForExptrStart')
        event.waitKeys(keyList = ['7'])
        
        event.clearEvents()
        self.Text.text = 'Waiting for the scanner to start...'
        self.Text.draw()
        pl.getEYELINK().sendMessage('WaitForExptrStart')
        self.win.flip()
        
        pl.getEYELINK().sendMessage('WaitForScanner')
        event.waitKeys(keyList = ['5'])
                
        # get a start point  
        pl.getEYELINK().startRecording(1,1,1,1)
        self.Text.text = ""
        self.Text.draw()
        self.win.flip()
        pl.getEYELINK().sendMessage('resting')
        time.sleep(resttime)
        
        # close and transfer file
        pl.getEYELINK().closeDataFile()
        transferFileName = self.edfFileName + '.edf' # fileName
        pl.getEYELINK().receiveDataFile(self.edfFileName, transferFileName)            
            

# %%
    def init_experiment(self):
        
        # create file
        self.edfFileName = "cbEL" + str(self.subjectID)
        if len(self.edfFileName) > 8:
            self.edfFileName = self.edfFileName[0:8]
        pl.getEYELINK().openDataFile(self.edfFileName)
        pl.getEYELINK().setOfflineMode()
        
        event.clearEvents()
        self.Text.text = 'Experiment start'
        self.Text.draw()
        pl.getEYELINK().sendMessage('WaitForExptrStart')
        self.win.flip()
        
        pl.getEYELINK().sendMessage('WaitForExptrStart press 7')
        event.waitKeys(keyList = ['7'])
        
        event.clearEvents()
        self.Text.text = 'Waiting for the scanner to start...'
        self.Text.draw()
        pl.getEYELINK().sendMessage('WaitForExptrStart')
        self.win.flip()
        
        pl.getEYELINK().sendMessage('WaitForScanner')
        event.waitKeys(keyList = ['5'])
        
        #get a start point  
        self.globTime = core.Clock()
        self.Text.text = "Ready"
        self.Text.draw()
        self.win.flip()
        pl.getEYELINK().sendMessage('ReadyScreen')
        time.sleep(5)            
            
            
        self.fixation.draw()
        self.win.flip()
        pl.getEYELINK().sendMessage('ReadyITI')
        time.sleep(2)
        event.clearEvents()

# %% run the experiment        
    def seq_order(self):
   
        if self.group == "A": # group A order based on the e-prime
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.reversed=True
            pl.getEYELINK().sendMessage('Reversed')
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            
        else: #group B order based on the e-prime
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.reversed=True
            pl.getEYELINK().sendMessage('Reversed')
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"], True)
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSminus"])
            self.trial(self.stim["CSplus"])
            self.trial(self.stim["CSminus"])

# %% close date file, window and exit experiment
    def exp_end(self):
        
        event.clearEvents()
        pl.getEYELINK().closeDataFile()
        transferFileName = self.edfFileName + '.edf' # fileName
        pl.getEYELINK().receiveDataFile(self.edfFileName, transferFileName)
        pl.getEYELINK().close()
        self.lj.close()
        self.dataFile.close()
        self.win.close()
        core.quit()
              
# %% trail sequence        
    def trial(self, color, US=False):

        '''
        trial procedure
        input   string - color - box color to display
                boolian - US - True for shock
        '''
        event.clearEvents()
        pl.getEYELINK().startRecording(1,1,1,1)
        fixTime = random.randint(10,15)
        stimTime = 4-0.3*US 
        self.trial_n += 1

        self.rect.fillColor = color
        if color == self.stim["CSplus"]:
            condition = "CSplus"
        else:
            condition = "CSminus"
        
        clock = core.Clock()
        trialClock = clock.getLastResetTime() - self.globTime.getLastResetTime()
        
        pl.getEYELINK().sendMessage('TRIALID %d'%(self.trial_n))
        pl.getEYELINK().sendMessage(condition + str(US))
        
        # initate trial display
        fixStart = trialClock + clock.getTime()
        self.fixation.draw()
        pl.getEYELINK().sendMessage('fixation')
        self.win.flip()
        time.sleep(fixTime)
        
        self.rect.draw()
        stimStart = trialClock + clock.getTime()
        self.lj.setFIOState(0,1)
        pl.getEYELINK().sendMessage('stimuli')
        self.win.flip()       
        time.sleep(stimTime)
                 
        # initate shock procedure if US = True
        usStart = trialClock + clock.getTime()
        if US:
            pl.getEYELINK().sendMessage("shock")
            for i in range(3,7):
                self.lj.setFIOState(i,1)
            for i in range(3,7):
                self.lj.setFIOState(i,0)
            for i in range(3,7):
                self.lj.setFIOState(i,1)
            time.sleep(0.3)
            condition = condition+"US"   
        self.lj.setFIOState(0,0)
        pl.getEYELINK().sendMessage('Trial end')
        # write to file trial properties
        self.dataFile.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n'.format(self.subjectID,self.group,self.time_stamp,self.trial_n,condition,color,US,fixStart,stimStart,usStart,self.reversed))
        
        
# %% main budy of experiment   
        
def main():        
    event.globalKeys.add(key='q',modifiers = ['ctrl'], func = core.quit)
    sub = subject(1575)
    sub.setup_eyelink()
    sub.shock_calibration()
    sub.two_min()
    sub.init_experiment()
    sub.seq_order()
    sub.resting_state(480)
    sub.exp_end()
    


if __name__ == '__main__':
    main()
