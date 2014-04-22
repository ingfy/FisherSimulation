import wx
import math
from BufferedCanvas import BufferedCanvas

def gradient(min_color, max_color, fraction):
    return tuple(a + (b - a) * fraction for a, b in zip(min_color, max_color))

class WorldMap(BufferedCanvas):
    min_vote_color = (0, 128, 0)
    max_vote_color = (128, 0, 0)

    def __init__(self, parent):
        self._size = (600, 600)
        self._data = None
        BufferedCanvas.__init__(self, parent, size = self._size)        
        self.SetBackgroundColour("white")
        
        self._agent_colors = {}
        self._complaints = []
        self.num_max_complaints = 10
        
        self.BufferBmp = None
        self.update()
        
    def set_map(self, map):
        self._data = {"map": map}
        
    def reset_votes(self):
        self._agent_colors = {}
        self._complaints = []      
        
    def add_votes(self, complaints):
        self._complaints = complaints
        votes_by_agent = {}
        for v in self._complaints:
            if not v.agent_id in votes_by_agent:
                votes_by_agent[v.agent_id] = 0
            votes_by_agent[v.agent_id] += 1
        for a in votes_by_agent:
            self._agent_colors[a] = gradient(
                WorldMap.min_vote_color,
                WorldMap.max_vote_color,
                float(votes_by_agent[a]) / self.num_max_complaints
            )
        
    def draw(self, dc):
        dc.Clear()
        dc.SetBackground(wx.Brush(wx.Colour(255, 255, 255), wx.SOLID))
        if self._data is None: return
        try:
            map = self._data["map"]
            num_hor, num_ver = (len(map.grid), len(map.grid[0]))
            w, h = self.GetSize()
            cell_w, cell_h = (float(w) / num_hor, float(h) / num_hor)
            
            grid_color = wx.Colour(0, 0, 0)
            dc.SetPen(wx.Pen(grid_color, 1))
            
            # Draw grid
            ## Horizontal lines
            for x in xrange(num_hor + 1):
                dc.DrawLine(cell_w * x, 0, cell_w * x, h)
            
            ## Vertical lines
            for y in xrange(num_ver + 1):
                dc.DrawLine(0, cell_h * y, w, cell_h * y)             
            
            fish_color = wx.Colour(0, 0, 255)
            fish_pen = wx.Pen(fish_color, 1)
            fish_brush = wx.Brush(fish_color, wx.SOLID)
            
            boat_color = wx.Colour(100, 100, 100)
            
            aquaculture_border_color = wx.Colour(0, 0, 0)
            aquaculture_fill_color = wx.Colour(200, 200, 200)
            aquaculture_pen = wx.Pen(aquaculture_border_color, 1)
            aquaculture_brush = wx.Brush(aquaculture_fill_color, wx.SOLID)
            
            land_color = wx.Colour(0, 255, 0)
            land_len = wx.Pen(land_color, 1)
            land_brush = wx.Brush(land_color, wx.SOLID)
            
            blocked_color = wx.Colour(255, 0, 0)
            
            # Draw entities
            for i in xrange(num_hor):
                for j in xrange(num_ver):
                    x, y = (cell_w * i, cell_h * j)
                    if map.grid[i][j].spawning: 
                        draw_fish_top_left(dc, x, y, cell_w, cell_h, fish_pen, 
                            fish_brush)
                    if map.grid[i][j].blocked:
                        draw_blocked(dc, x, y, cell_w, cell_h, blocked_color)
                    if map.grid[i][j].fisherman:
                        color = next((self._agent_colors[e.id] for e in 
                            map.grid[i][j].fishermen if e.id in 
                            self._agent_colors), WorldMap.min_vote_color)
                        draw_boat_bottom_right(dc, x, y, cell_w, cell_h, 
                            color, map.grid[i][j].num_fishermen)
                    if map.grid[i][j].aquaculture:
                        draw_aquaculture_center(dc, x + cell_w / 2, 
                            y + cell_h / 2, cell_w, cell_h, aquaculture_pen, 
                            aquaculture_brush)
                    if map.grid[i][j].land:
                        draw_land(dc, x, y, cell_w, cell_h, land_pen, 
                            land_brush)
                            
            
            return True
            
        except Exception, e:
            return False
            
def draw_blocked(dc, x, y, cell_w, cell_h, color):
    dc.SetPen(wx.Pen(color, 2))
    dc.DrawLine(x, y, x + cell_w, y + cell_h)
    dc.DrawLine(x + cell_w, y, x, y + cell_h)
            
def draw_land(dc, x, y, cell_w, cell_h, p, b):
    dc.SetPen(p)
    dc.SetBrush(b)
    dc.DrawRectangle(x, y, cell_w, cell_h)
            
def draw_aquaculture_center(dc, x, y, cell_w, cell_h, p, b):
    scale = min(cell_w, cell_h)
    corners = 10
    dc.SetPen(p)
    dc.SetBrush(b)
    points = [wx.Point(
        x + scale / 2 * math.sin(2 * math.pi * p / corners),
        y + scale / 2 * math.cos(2 * math.pi * p / corners)
        ) for p in xrange(corners)]
    dc.DrawPolygon(points)
            
          
def draw_boat_center(dc, x, y, cell_w, cell_h, color, num):
    scale = min(cell_w, cell_h)
    dc.SetPen(wx.Pen(color, 1))
    dc.SetBrush(wx.Brush(color, wx.SOLID))
    # Draw boat bottom
    dc.DrawArc(x - scale / 3, y, x + scale / 3, y, x, y)
    # Draw sail
    dc.DrawPolygon([wx.Point(x - scale / 4, y - scale / 8),
                    wx.Point(x + scale / 4, y - scale / 8),
                    wx.Point(x,              y - scale / 8 - scale / 4)])
    # Draw mast
    dc.DrawLine(x, y, x, y - scale / 8)
    
    if num > 1:
        dc.SetFont(wx.Font(
            pointSize=scale/3,
            family=wx.FONTFAMILY_DEFAULT,
            style=wx.FONTSTYLE_NORMAL,
            weight=wx.FONTWEIGHT_BOLD))
        dc.SetTextForeground(wx.Colour(255, 255, 125))
        text = str(num)
        tw, th = dc.GetTextExtent(text)
        dc.DrawText(text, (x - tw / 2),
                          (y + scale / 6 - th / 2))

def draw_boat_bottom_right(dc, x, y , cell_w, cell_h, color, num):
    scale = min(cell_w, cell_h)
    ox = cell_w - scale / 3
    oy = cell_h - scale / 8 - cell_h / 4
    draw_boat_center(dc, ox + x, oy + y, cell_w, cell_h, color, num)
            
def draw_fish_center(dc, x, y, cell_w, cell_h, p, b):
    scale = min(cell_w, cell_h)
    dc.SetPen(p)
    dc.SetBrush(b)
    # Draw body
    dc.DrawArc(x - scale / 3, y, x + scale / 3, y, x, y - scale / 6)
    dc.DrawArc(x + scale / 3, y, x - scale / 3, y, x, y + scale / 6)
    ## right tip is located at (x + cell_w / 3, y)
    # Draw tail
    dc.DrawPolygon([wx.Point(x + scale / 3 + scale / 5, y - scale / 5),
                    wx.Point(x + scale / 3,              y),
                    wx.Point(x + scale / 3 + scale / 5, y + scale / 5)])
        
def draw_fish_top_left(dc, x, y, cell_w, cell_h, p, b):  # Offset from top left corner
    scale = min(cell_w, cell_h)
    ox = scale / 3
    oy = scale / 5
    draw_fish_center(dc, ox + x, oy + y, cell_w, cell_h, p, b)