import wx
import numpy
from BufferedCanvas import BufferedCanvas

class Graphs(BufferedCanvas):
    axis = (10, 10)
    num_rounds = 10
    graph_colors = [
        wx.Colour(255, 0, 0),
        wx.Colour(0, 255, 0),
        wx.Colour(0, 0, 255),
        wx.Colour(255, 0, 255),
        wx.Colour(0, 255, 255),
        wx.Colour(0, 128, 0),
        wx.Colour(128, 0, 0),
        wx.Colour(0, 0, 128)
    ]

    def __init__(self, parent, size):
        self.reset_data()
        
        BufferedCanvas.__init__(self, parent, size=size)        
        self.SetBackgroundColour("white")
        
        self.BufferBmp = None
        
        
        self.update()
        
    def reset_data(self):
        self._data = {}
        self._assigned_colors = {}
        self._colors_iter = iter(Graphs.graph_colors)
        
    def add_data_point(self, label, round, value, mode="add"):
        if not label in self._data:
            self._data[label] = {}
            self._assigned_colors[label] = next(self._colors_iter, "black")
        if not round in self._data[label]:
            self._data[label][round] = 0
        if mode == "add":
            self._data[label][round] += value
        else:
            self._data[label][round] = value
        
    def draw(self, dc):
        # draw axis
        dc.Clear()
        dc.SetBackground(wx.Brush(wx.Colour(255, 255, 255), wx.SOLID))

        try:
            w, h = self.GetSize()
            
            # vertical axis
            axis_padding_left = w / 20
            axis_padding_top = h / 15
            axis_padding_bottom = h / 15
            axis_label_padding = 4
            axis_padding_right = w / 20
            label_marker_size = 4
            dc.DrawLine(axis_padding_left, axis_padding_top, 
                axis_padding_left, h - axis_padding_bottom)
            dc.DrawLine(axis_padding_left, h - axis_padding_bottom,
                w - axis_padding_right, h - axis_padding_bottom)
                
            num_v, num_h = Graphs.axis
            
            # can't plot variables with 0 or 1 values
            data = {variable: self._data[variable] for variable in self._data if 
                len(self._data[variable]) > 1}
            
            values = [data[label][e] for label in data for e in data[label]]
            
            if len(values) == 0:
                return True
            
            min_val = min(values)
            max_val = max(values)
            
            
            
            # axis label font
            dc.SetFont(wx.Font(pointSize=8, family=wx.FONTFAMILY_DEFAULT,
                style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL))
                
            # vertical axis labels
            axis_height = h - axis_padding_top - axis_padding_bottom
            v_labels = sorted(list(set([int(e) for e in numpy.arange(0, 
                max_val, float(max_val) / num_v)])))
            
            for y in xrange(len(v_labels)):
                text = str(v_labels[y])
                
                tw, th = dc.GetTextExtent(text)
                
                tx = axis_padding_left - tw - axis_label_padding
                _y = h - axis_padding_bottom - axis_height / len(v_labels) * y
                ty = _y - th / 2
                
                dc.DrawText(text, tx, ty)
                dc.DrawLine(axis_padding_left - label_marker_size / 2, _y, 
                    axis_padding_left + label_marker_size / 2, _y)
                    
            # calculate rounds to draw
            rounds = sorted(list(set(e for subl in [data[label].keys() for 
                label in data] for e in subl)))
            
            selected_rounds = range(rounds[:Graphs.num_rounds][0], 
                rounds[-1] + 1, 1)
            
            # horizontal axis labels
            axis_width = w - axis_padding_left - axis_padding_right
            h_labels = selected_rounds
            
            if len(selected_rounds) > 0:
                min_round = selected_rounds[0]
                max_round = selected_rounds[-1]
            else:
                min_round = 0
                max_round = 0
            
            for x in xrange(len(h_labels)):
                text = str(h_labels[x])
                
                tw, th = dc.GetTextExtent(text)
                
                _x = axis_padding_left + axis_width / len(h_labels) * x
                tx = _x - tw / 2
                ty = h - axis_padding_bottom + axis_label_padding
                
                dc.DrawText(text, tx, ty)
                dc.DrawLine(_x, h - axis_padding_bottom - label_marker_size / 2,
                    _x, h - axis_padding_bottom + label_marker_size / 2)
        
            graph_h = h - axis_padding_bottom - axis_padding_top
            graph_w = w - axis_padding_left - axis_padding_right
            graph_x = axis_padding_left
            graph_y = axis_padding_top
            scale_y = graph_h / float(max_val)
            scale_x = graph_w / float(max_round - min_round)
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 2))
            
            #plot the data
            for label in data:
                values = {r: data[label][r] for r in selected_rounds if r 
                    in data[label]}
                points = [(
                    int((float(i) / len(selected_rounds)) * graph_w),
                    -int(values[i] * scale_y)
                ) for i in xrange(len(selected_rounds)) if i in values]
                dc.SetPen(wx.Pen(self._assigned_colors[label], 2))
                dc.DrawLines(points, xoffset=graph_x, yoffset=graph_y+graph_h)
                
            # Draw explanations
            num_expl = len(data)
            min_size, max_size = size_constraints = (6, 20)
            expl_h = h / 4
            expl_size = max(min_size, min(max_size, float(expl_h)/num_expl/1.5))    
            dc.SetFont(wx.Font(pointSize=expl_size, 
                family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL, 
                weight=wx.FONTWEIGHT_NORMAL))
            expl_box_w = expl_size
            expl_box_h = expl_size
            expl_padding = 2
            expl_text_padding = 2
            expl_w = max(
                w for w, h in [dc.GetTextExtent(label) for label in data]
            ) + expl_box_w + expl_padding * 2 + expl_text_padding
            expl_x = w - expl_w
            expl_y = 0
            ## draw box
            dc.SetPen(wx.Pen(wx.Colour(255, 255, 255, alpha=100), 1))
            dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255, alpha=100)))
            dc.DrawRectangle(expl_x, expl_y, expl_w, expl_h)
            expl_padding = 2
            expl_text_padding = 2
            __, line_h = dc.GetTextExtent("A")
            line_h += expl_text_padding * 2
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
            for i, label in zip(xrange(len(data)), data):
                line_y = line_h / 2 + expl_y + i * float(expl_h) / num_expl
                dc.SetBrush(wx.Brush(self._assigned_colors[label]))
                dc.DrawRectangle(
                    expl_x + expl_padding, 
                    line_y - expl_box_h / 2,
                    expl_box_w, 
                    expl_box_h
                )
                __, th = dc.GetTextExtent(label)
                dc.DrawText(label, 
                    expl_x + expl_padding + expl_box_w + expl_padding,
                    line_y - th/2)
            
                
            return True
            
        except Exception, e:
            return False