import wx
from wx.lib import intctrl
import worldmap
import Queue
import graphs
from FisherSimulation import do
from FisherSimulation import simulation
from FisherSimulation import util
from BufferedCanvas import BufferedCanvas
import time
import threading

class PhaseResultEvent(wx.PyEvent):
    def __init__(self, result):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.result = result

class WorkerThread(threading.Thread):
    def __init__(self, simulation, notify):
        threading.Thread.__init__(self)
        
        self._simulation = simulation
        self._notify = notify
        
        self.start()
        
    def run(self):
        result = self._simulation.step()
        wx.PostEvent(self._notify, PhaseResultEvent(result))

# Button definitions
ID_START = wx.NewId()
ID_STEP = wx.NewId()
ID_RUN = wx.NewId()
ID_STOP = wx.NewId()

# Define simulation finished event
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)
        
class Controls(wx.Panel):
    def __init__(self, parent, size):
        wx.Panel.__init__(self, parent, size=size)

        ##  Start button
        self.startButton = wx.Button(self, id=ID_START, label="&Initialize")
        self.Bind(wx.EVT_BUTTON, self.GetParent().OnStart, self.startButton)
        
        ## Run rounds, steps inputs
        self.rounds_input = intctrl.IntCtrl(self, pos=(10, 60), size=(20, -1),
            value=0, min=0)
        self.steps_input = intctrl.IntCtrl(self, pos=(40, 60), size=(20, -1),
            value=1, min=0)
        
        ## Run button
        self.runButton = wx.Button(self, id=ID_RUN, pos=(100, 60), 
            label = "&Run")
        self.Bind(wx.EVT_BUTTON, self.OnRun, self.runButton)
        
        ##  Stop button
        self.stopButton = wx.Button(self, id=ID_STOP, pos=(0, 120), 
            label="S&top")
        self.Bind(wx.EVT_BUTTON, self.GetParent().OnStop, self.stopButton)
        
        self.reset_buttons()
        
    def set_status(self, rounds, steps):
        self.rounds_input.SetValue(rounds)
        self.steps_input.SetValue(steps)
        
    def OnRun(self, event):
        rounds = self.rounds_input.GetValue()
        steps = self.steps_input.GetValue()
        self.GetParent().run(rounds, steps)
        
    # Helper methods
    def set_buttons_processing(self):
        self.startButton.Disable()
        self.runButton.Disable()
        self.stopButton.Enable()
        self.rounds_input.Disable()
        self.steps_input.Disable()

    def set_buttons_ready(self):
        self.rounds_input.Enable()
        self.steps_input.Enable()
        self.startButton.Disable()
        self.runButton.Enable()
        self.stopButton.Enable()
        self.set_status(0, 1)
    
    def reset_buttons(self):
        self.stopButton.Disable()
        self.runButton.Disable()
        self.startButton.Enable()
        self.rounds_input.Disable()
        self.steps_input.Disable()

class Info(wx.Panel):
    phase_names = {
        "COASTPLAN":    "Coastal Planning",
        "HEARING":      "Hearing",
        "GOVDECISION":  "Government Decision",
        "FISHING1":     "Fishing and Working (1)",
        "BUILDING":     "Building of Aquaculture",
        "FISHING2":     "Fishing and Working (2)",
        "LEARNING":     "Learning Phase"
    }
    
    round = [
        "COASTPLAN", "HEARING", "GOVDECISION", "FISHING1", "BUILDING",
        "FISHING2", "LEARNING"
    ]

    def __init__(self, parent, size):
        wx.Panel.__init__(self, parent, size=size)
        
        padding = 10
        
        phases_x = padding
        phases_y = padding
        
        w, h = size
        phases_w = w - padding * 2
        phases_h = h - padding * 2
        
        between = 2
        
        line_height = phases_h / len(Info.round) - between
        font_size = min(18, line_height / 2)
        
        self.phase_name_font = wx.Font(font_size, wx.DECORATIVE, wx.NORMAL, 
            wx.BOLD)
        
        self.phases = {
            Info.round[i]: wx.StaticText(self, 
                                label=Info.phase_names[Info.round[i]],
                                pos=(phases_x, phases_y + line_height * i))
                for i in xrange(len(Info.round))
        }
        
        for label in Info.phase_names:
            self.phases[label].SetFont(self.phase_name_font)       

        self.set_current_phase(Info.round[0])
        
    def set_current_phase(self, name):
        for label in self.phases:
            color = "red" if name == label else "black"
            self.phases[label].SetForegroundColour(color)
            self.phases[label].Refresh()
            

class Messages(wx.Panel):
    def __init__(self, parent, size):
        wx.Panel.__init__(self, parent, size=size)
        
        self.textbox = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=size)
        self.textbox.SetEditable(False)
        self.textbox.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.header = wx.StaticText(self, label="Messages")
        self.header_font = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.header.SetFont(self.header_font)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer.Add(self.header, 0)
        self.sizer.Add(self.textbox, 1, wx.EXPAND)
        
        self.SetSizerAndFit(self.sizer)
        
    def add(self, message):
        self.textbox.AppendText("\n" + message)
        self.textbox.ShowPosition(self.textbox.GetLastPosition())
        
    def clear(self):
        self.textbox.Clear()

class Window(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        
        # World graphic
        self._graphics = worldmap.WorldMap(self)
        self.graphics_sizer = wx.BoxSizer(wx.VERTICAL)
        self.graphics_sizer.Add(self._graphics, 1, wx.EXPAND)
        
        # Controls panel
        self.controls = Controls(self, (300, 250))
        
        # Info panel
        self.info = Info(self, (300, 250))
        
        # Graph canvas
        self.graphs = graphs.Graphs(self, (300, 300))
                
        # Messages panel
        self.messages = Messages(self, (600, 200))
        
        self.interface_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.controls_info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.controls_info_sizer.Add(self.info, 0, wx.EXPAND)
        self.controls_info_sizer.Add(self.controls, 1, wx.EXPAND)
        
        self.messages_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.messages_sizer.Add(self.messages, 1, wx.EXPAND)
        
        self.graphs_sizer = wx.BoxSizer(wx.VERTICAL)
        self.graphs_sizer.Add(self.graphs, 1, wx.EXPAND)
        
        self.interface_sizer.Add(self.controls_info_sizer, 0, wx.EXPAND)
        self.interface_sizer.Add(self.messages_sizer, 1, wx.EXPAND)
        self.interface_sizer.Add(self.graphs_sizer, 1, wx.EXPAND)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.interface_sizer, 0, wx.EXPAND)
        self.sizer.Add(self.graphics_sizer, 1, wx.EXPAND)       
        
                
        # Layout sizers
        self.SetSizerAndFit(self.sizer)
        
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)
        
        # Set up close event so timer is properly stopped
        wx.EVT_CLOSE(self, self.OnClose)        
        
        self.reset_gui()
        self.Show()
    
    def reset_gui(self):
        self.controls.reset_buttons()
        self.messages.clear()    
        
    # Event Methods
    def OnStart(self, event):
        self.controls.set_buttons_ready()
        
        self._simulation = simulation.Simulation()
        
        self._simulation.setup_config()
        self.simulation_info = self._simulation.initialize() 
        
        self.rounds = 0
        self.steps = 0
        
        self.next_phase = "COASTPLAN"
        self.prev_phase = None
        
        self.worker = None
        
    def run(self, rounds, steps):
        assert rounds >= 0, "Rounds has to be a positive integer."
        assert steps >= 0, "Steps has to be a positive integer."
        assert steps > 0 or rounds > 0, "Rounds or steps needs to be positive."
        self.controls.set_status(rounds, steps)
        self.controls.set_buttons_processing()
        self.rounds = rounds
        self.steps = steps
        if self.worker is None:
            self.prev_phase = self.next_phase
            self.info.set_current_phase(self.next_phase)
            self.worker = WorkerThread(self._simulation, self)
        
    def OnResult(self, event):
        self.worker = None
        self.simulation_info.map.grid = util.update_map(
            self.simulation_info.map.grid, event.result.map.grid
        )
        self.next_phase = event.result.next_phase

        handle_statistics(self.graphs, event.result.round, event.result.data)
        self._graphics.set_map(self.simulation_info.map)
        self._graphics.update()
        
        for m in event.result.messages:
            self.messages.add(str(m))
        
        newr = self.prev_phase == "LEARNING" and self.next_phase == "COASTPLAN"
        if newr and self.rounds > 0:
            self.rounds -= 1
        elif self.rounds == 0:
            self.steps -= 1

        if self.rounds > 0 or self.steps > 0:            
            self.run(self.rounds, self.steps)
        else:
            self.controls.set_buttons_ready()
        
    def OnStop(self, event):
        self.reset_gui()
            
    def OnClose(self, event):
        self.Destroy()
        
def handle_statistics(graphs, round, data):
    if "statistics" in data:
        for label in data["statistics"]:
            mode = data["statistics"][label].get("mode", "add")
            value = data["statistics"][label].get("value")
            graphs.add_data_point(label, round, value, mode)
    graphs.update()

def create_and_run():    
    app = wx.App(redirect=False)
    Window(None, "Fisherman Simulation")
    app.MainLoop()
    
def main():
    create_and_run()
    return 0
    
if __name__ == "__main__":    
    exit(main())