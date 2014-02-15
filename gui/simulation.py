import wx
import worldmap
import threading
import main

class SimulationThread(threading.Thread):
    def __init__(self, notify_window):
        threading.Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = False
    
    def run(self):
        pass
        wx.PostEvent(self._notify_window, ResultEvent(0))
        
    def abort(self):
        self._want_abort = True

# Button definitions
ID_START = wx.NewId()
ID_STOP = wx.NewId()

# Define simulation finished event
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)
    
class ResultEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
    
class Window(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        
        # Controls
        controls = wx.Panel(self)
        self.controls_sizer = wx.BoxSizer(wx.VERTICAL)
        self.controls_sizer.Add(controls, 1, wx.EXPAND)
        
        ##  Start button
        self.startButton = wx.Button(controls, id=ID_START, label="&Start")
        self.Bind(wx.EVT_BUTTON, self.OnStart, self.startButton)
        
        ##  Stop button
        self.stopButton = wx.Button(controls, id=ID_STOP, pos=(0,30), label="S&top")
        self.Bind(wx.EVT_BUTTON, self.OnStop, self.stopButton)
        
        # World graphic
        graphics = worldmap.WorldMap(self)        
        self.graphics_sizer = wx.BoxSizer(wx.VERTICAL)
        self.graphics_sizer.Add(graphics, 1, wx.EXPAND)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.controls_sizer, 0, wx.EXPAND)
        self.sizer.Add(self.graphics_sizer, 1, wx.EXPAND)
                
        # Layout sizers
        self.SetSizerAndFit(self.sizer)
        
        # Set up event handler for any worker thread results
        EVT_RESULT(self,self.OnResult)
        
        self.simulation_thread = None
        
        self.Show()
        
    # Helper methods
    def set_buttons_running(self):
        self.startButton.Disable()
        self.stopButton.Enable()
    
    def reset_buttons(self):
        self.stopButton.Disable()
        self.startButton.Enable()
        
        
    # Event Methods
    def OnStart(self, event):
        self.set_buttons_running()
        self.simulation_thread = SimulationThread(self)
        self.simulation_thread.start()
        
    def OnStop(self, event):
        self.reset_buttons()
        
    def OnResult(self, event):
        self.reset_buttons()
        if event.data is None:
            print("Simulation aborted")
        else:
            print("Simulation finished")
        
def create_and_run():
    app = wx.App(False)
    Window(None, "Fisherman Simulation")
    app.MainLoop()
    
def main():
    create_and_run()
    return 0
    
if __name__ == "__main__":
    exit(main())