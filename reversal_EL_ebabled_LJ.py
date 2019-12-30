# -*- coding: utf-8 -*-
"""
Spyder Editor

Reversal learinging in fMRI with labjack and eyelink 21.11.2019
Nachshon Korem, Yale

"""
### import packages
import datetime, os, random
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
        self.dataFile.write('Sub,Group,time,Trial_n,Condition,color,US,FixationOnset,StimulusOnset,USOnset\n')


# %% create an experemental object input is a subject object
class exp:
    
    def __init__(self, sub):
        # create a window object
        self.win = visual.Window(color=[0,0,0], screen = 1, fullscr=True, mouseVisible = False)
        #initiate a trial counter
        self.trial_n = 0
        self.lj = U3()
        self.lj.setFIOState(3,0)
        self.lj.setFIOState(0,0)

        
                    
        # creates the visual objects for the experiment
        self.fixation=visual.Circle(self.win, radius=10, fillColor='black',lineColor='black',units = 'pix')
        self.rect = visual.Rect(self.win,units="norm",width=0.5,height=0.5,fillColor='black',lineColor='Grey',pos=(0,0))
        self.Text = visual.TextStim(self.win,text="US", pos=(1,0), font='Courier New',
            alignHoriz = 'center', alignVert = 'center', color = 'black',units = 'norm')
        
        # base on subject number subjects are divided to group A and B (%2) and color order (%4<=1)
        if sub.subjectID % 2 == 0:
            self.group = "A"
        else:
            self.group = "B"
            
        if sub.subjectID % 4 <= 1:
            self.stim = {"CSplus":"blue","CSminus":"yellow"}
        else:
            self.stim={"CSplus":"yellow","CSminus":"blue"}
            
            
 # %% initaite the eyelink module and run calibration
       
    def setup_eyelink(self):
        '''Thank you very much
        
        '''
        #parameters for eyelink
        self.monitor = monitors.Monitor('testMonitor')
        self.winSize = self.monitor.getSizePix()
        self.foreground = (250,250,250)
        self.background = (127,127,127)
        
        # call for eyelink
        self.eyelink_tracker = pl.EyeLink("100.1.1.1")
        
        self.edfFileName = "cbEL" + str(sub.subjectID)
        if len(self.edfFileName) > 8:
            self.edfFileName = self.edfFileName[0:8]
        pl.getEYELINK().openDataFile(self.edfFileName)
        

        pl.flushGetkeyQueue()
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
        #getEYELINK().sendCommand("button_function 5 'accept_target_fixation'");
        pl.setCalibrationColors(self.foreground, self.background);  	#Sets the calibration target and background color  - background color should match testing background
        #setTargetSize(int(win.size[0]/20), int(win.size[0]/100));	#select best size for calibration target
        
        
        #self.Text.text = "calibration press 7"
        #self.Text.draw()
        #self.win.flip()
        #while True: 
        #    buttonPress=event.waitKeys(keyList = ['7']) 
        #    if buttonPress == ['5']:
        #        break
        
        pl.getEYELINK().setOfflineMode()
        winX = int(self.winSize[0])
        winY = int(self.winSize[1])
        pl.openGraphics((winX,winY),32)
        pl.getEYELINK().doTrackerSetup()
        pl.setCalibrationSounds("", "", "");
        pl.setDriftCorrectSounds("", "off", "off");
        pl.closeGraphics()
# %%
    def init_eyelink(self):
        
        event.clearEvents()
        self.Text.text = 'Experiment start'
        self.Text.draw()
            # # # # # # # # # # # # # # # # # # 
        pl.getEYELINK().sendMessage('WaitForExptrStart')
            # # # # # # # # # # # # # # # # # # 
        self.win.flip()
        
        
        while True:
            buttonPress=event.getKeys(keyList = ['7'])
            pl.getEYELINK().sendMessage('WaitForExptrStart press 7')
            if buttonPress==['7']:
                break
        
        event.clearEvents()
        self.Text.text = 'Waiting for the scanner to start...'
        self.Text.draw()
            # # # # # # # # # # # # # # # # # # 
        pl.getEYELINK().sendMessage('WaitForExptrStart')
            # # # # # # # # # # # # # # # # # # 
        self.win.flip()
        
        while True:
            pl.getEYELINK().sendMessage('WaitForScanner')
            buttonPress=event.getKeys(keyList = ['5'])
            
            if buttonPress == ['5']:
                break
        
        self.Text.text = "Ready"
        self.Text.draw()
        self.win.flip()
        current = datetime.datetime.now()
        while (datetime.datetime.now()-current).seconds < 5:
            pl.getEYELINK().sendMessage('ReadyScreen')
            
        self.fixation.draw()
        self.win.flip()
        current = datetime.datetime.now()
        while (datetime.datetime.now()-current).seconds < 2:
            pl.getEYELINK().sendMessage('ReadyITI')
        
        event.clearEvents()

# %% run the experiment        
    def seq_order(self):
   
        #get a start point  
        self.globTime = core.Clock()
        # group A order based on the e-prime
        if self.group == "A":
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
            
        #group B order based on the e-prime
        else:
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

# %%
    def exp_end(self):
        
        # close date file, window and exit experiment
        event.clearEvents()
        pl.getEYELINK().closeDataFile()
        transferFileName = self.edfFileName + '.edf' # fileName
        pl.getEYELINK().receiveDataFile(self.edfFileName, transferFileName)
        pl.getEYELINK().close()
        self.lj.close()
        sub.dataFile.close()
        self.win.close()
        core.quit()
        
        
# %% truak sequence        
    def trial(self, color, US=False):

        '''
        trial procedure
        input   string - color - box color to display
                boolian - US - True for shock
        '''
        event.clearEvents()
        
        fixTime = random.randint(1,2)
        print(fixTime)
        stimTime = 1-0.3*US 
        self.trial_n += 1

        self.rect.fillColor = color
        if color == self.stim["CSplus"]:
            condition = "CSplus"
        else:
            condition = "CSminus"
        
        clock = core.Clock()
        trialClock = clock.getLastResetTime() - self.globTime.getLastResetTime()
        
        # error = pl.getEYELINK().startRecording(1,1,1,1) # flags = (samples in edf, events in edf, samples over link, events over link)
        pl.getEYELINK().sendMessage('TRIALID %d'%(self.trial_n))
        pl.getEYELINK().sendMessage(condition + str(US))
        
        # initate trial display
        fixStart = trialClock + clock.getTime()
        self.fixation.draw()
        self.win.flip()
        
        while clock.getTime() < fixTime:
            #continue
            pl.getEYELINK().sendMessage('fixation')
        

        self.rect.draw()
        stimStart = trialClock + clock.getTime()
        self.lj.setFIOState(0,1)
        self.win.flip()        
                
        while clock.getTime() < stimTime + fixTime:
            #continue
            pl.getEYELINK().sendMessage('stimuli')
        
        # initate shock procedure if US = True
        usStart = trialClock + clock.getTime()
        if US:
            self.lj.setFIOState(3,1)
            
            while clock.getTime() < stimTime + fixTime + 0.3:
                pl.getEYELINK().sendMessage("shock")
                #continue
            self.lj.setFIOState(3,0)
            
            condition = condition+"US"   
        self.lj.setFIOState(0,0)
        
        # write to file trial properties
        sub.dataFile.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n'.format(sub.subjectID,self.group,sub.time_stamp,self.trial_n,condition,color,US,fixStart,stimStart,usStart))
        
        
# %% main budy of experiment   

event.globalKeys.add(key='q',modifiers = ['ctrl'], func = core.quit)
sub = subject(102)
ses = exp(sub)
ses.setup_eyelink()
ses.init_eyelink()
ses.seq_order()
ses.exp_end()
