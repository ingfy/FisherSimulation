"""Main GUI module. Constructs the main window."""

import wx
import threading

from FisherSimulation import simulation
from FisherSimulation import util
import graphs
import worldmap
from controls import Controls
from messages import Messages
from info import Info

class PhaseResultEvent(wx.PyEvent):
    def __init__(self, source, result):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.source = source
        self.result = result

class StopEvent(wx.PyEvent):
    def __init__(self, result):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_STOP_ID)
        self.result = result

class WorkerThread(threading.Thread):
    def __init__(self, simulation, notify):
        threading.Thread.__init__(self)

        self._simulation = simulation
        self._notify = notify

        self.start()

    def run(self):
        result = self._simulation.step()
        wx.PostEvent(self._notify, PhaseResultEvent(self, result))

# Define simulation finished event
EVT_RESULT_ID = wx.NewId()
EVT_STOP_ID = wx.NewId()

def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)

def EVT_STOP(win, func):
    win.Connect(-1, -1, EVT_STOP_ID, func)

class Window(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)

        # Splitters and Panels
        self.controls_map_splitter = wx.SplitterWindow(self)
        self.controls_map_splitter.SetMinimumPaneSize(300)

        controls_panel = wx.Panel(self.controls_map_splitter)
        map_panel = wx.Panel(self.controls_map_splitter)

        self.graphs_messages_splitter = wx.SplitterWindow(controls_panel)
        self.graphs_messages_splitter.SetMinimumPaneSize(50)

        graphs_panel = wx.Panel(self.graphs_messages_splitter)
        messages_panel = wx.Panel(self.graphs_messages_splitter)

        # World graphic
        self._graphics = worldmap.WorldMap(map_panel)
        self.graphics_sizer = wx.BoxSizer(wx.VERTICAL)
        self.graphics_sizer.Add(self._graphics, 1, wx.EXPAND)
        map_panel.SetSizerAndFit(self.graphics_sizer)

        # Controls panel
        self.controls = Controls(controls_panel, (300, 250), self)

        # Info panel
        self.info = Info(controls_panel, (300, 250))

        # Graph canvas
        self.graphs = graphs.Graphs(graphs_panel, (300, 300))

        # Messages panel
        self.messages = Messages(messages_panel, (600, 200))

        self.interface_sizer = wx.BoxSizer(wx.VERTICAL)

        self.controls_info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.controls_info_sizer.Add(self.info, 0, wx.EXPAND)
        self.controls_info_sizer.Add((20, -1), proportion=0)    # Padding
        self.controls_info_sizer.Add(self.controls, 1, wx.EXPAND)

        self.messages_sizer = wx.BoxSizer(wx.VERTICAL)
        self.messages_sizer.Add(self.messages, 1, wx.EXPAND)
        messages_panel.SetSizerAndFit(self.messages_sizer)

        self.graphs_sizer = wx.BoxSizer(wx.VERTICAL)
        self.graphs_sizer.Add(self.graphs, 1, wx.EXPAND)
        graphs_panel.SetSizerAndFit(self.graphs_sizer)

        self.interface_sizer.Add(self.controls_info_sizer, 0, wx.EXPAND)
        self.interface_sizer.Add(self.graphs_messages_splitter, 1, wx.EXPAND)

        controls_panel.SetSizerAndFit(self.interface_sizer)

        self.graphs_messages_splitter.SplitHorizontally(
            messages_panel,
            graphs_panel
        )

        self.controls_map_splitter.SplitVertically(controls_panel, map_panel)

        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)
        EVT_STOP(self, self.OnStop)

        # Set up close event so timer is properly stopped
        wx.EVT_CLOSE(self, self.OnClose)

        self.reset_gui()
        self.Show()

    def reset_gui(self):
        self.controls.reset_buttons()
        self.messages.clear()
        self.graphs.reset_data()

    # Event Methods
    def OnStart(self, event):
        self.controls.set_buttons_ready()

        self._simulation = simulation.Simulation()

        self._simulation.setup_config(self.controls.get_config_filename())
        self.simulation_info = self._simulation.initialize()

        if not self.simulation_info.interface_config.print_messages:
            self.messages.deactivate()

        self._graphics.num_max_complaints = \
            self.simulation_info.num_max_complaints

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
        if not event.source is self.worker: # ongoing simulation was aborted
            return
        self.worker = None
        self.simulation_info.map.grid = util.update_map(
            self.simulation_info.map.grid, event.result.map.grid
        )
        self.next_phase = event.result.next_phase

        handle_statistics(self.graphs, event.result.round, event.result.data)
        self._graphics.set_map(self.simulation_info.map)
        if event.result.phase == "HEARING":
            self._graphics.add_votes(event.result.complaints)
        self._graphics.update()

        for m in event.result.messages:
            self.messages.add(str(m))

        newr = self.prev_phase == "LEARNING" and self.next_phase == "COASTPLAN"
        if newr:
            self._graphics.reset_votes()
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
        self._simulation = None
        self.worker = None
        self.simulation_info = None

    def OnClose(self, event):
        # TODO: Fix
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
