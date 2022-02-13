# IMPORT
import numpy as np
from PySide2.QtWidgets import QApplication
import math
from small_renderer import *


# FUNCTION
def distance_sq(pos_a, pos_b):
    x_dif = abs(pos_a[0] - pos_b[0])
    y_dif = abs(pos_a[1] - pos_b[1])
    return math.pow(x_dif, 2) + math.pow(y_dif, 2)


# CLASS
class CurveEditor(OpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.line_data = Line(color=(1.0, 0.3, 0.3))
        self.line_data.add_point((0.0, 0.0))
        self.line_data.add_point((0.5, 0.5))
        self.line_data.add_point((1.0, 1.0))

        self.selected_point = None

    def initializeGL(self):
        super().initializeGL()
        v_data_line = self.line_data.get_vertex_array()

        line = Entity(draw_method=GL.GL_LINES)
        line.set_vertices_data(v_data_line)

        self.add_entity(line)

    def paintGL(self):

        v_data_line = self.line_data.get_vertex_array()
        self.entities[0].update_vertices_data(v_data_line)
        super().paintGL()

    def mousePressEvent(self, event):
        mouse_pos = event.pos().toTuple()
        size = self.size().toTuple()
        pos = (2*mouse_pos[0]/size[0] - 1, -(2*mouse_pos[1]/size[1] - 1))
        self.selected_point = self.line_data.get_close_point(pos)

    def mouseMoveEvent(self, event):
        mouse_pos = event.pos().toTuple()
        size = self.size().toTuple()
        pos = (max(min(2 * mouse_pos[0] / size[0] - 1, 1), -1), max(min(-(2 * mouse_pos[1] / size[1] - 1), 1), -1))

        if self.selected_point != None:
            self.line_data.points[self.selected_point].move(pos)
            self.selected_point = self.line_data.reorder(self.selected_point)

    def mouseReleaseEvent(self, event):
        self.selected_point = None

    def mouseDoubleClickEvent(self, event):
        mouse_pos = event.pos().toTuple()
        size = self.size().toTuple()
        pos = (2 * mouse_pos[0] / size[0] - 1, -(2 * mouse_pos[1] / size[1] - 1))
        self.line_data.add_point(pos)
        self.line_data.reorder()

class Line:
    def __init__(self, color=(1.0, 1.0, 1.0)):
        self.points = []
        self.color = color

    def add_point(self, pos=(0, 0)):
        self.points.append(Point(pos=pos, color=self.color))

    def reorder(self, current_point=0):
        for i in range(len(self.points)):
            if i != len(self.points)-1:
                if self.points[i+1].pos[0] < self.points[i].pos[0]:
                    item = self.points.pop(i + 1)
                    self.points.insert(i, item)
                    if current_point == i:
                        current_point += 1
                    elif current_point == i+1:
                        current_point -= 1
        return current_point

    def get_vertex_array(self):
        out = []
        i=0
        for point in self.points:
            if len(out) > 10:
                out += list(self.points[i-1].pos) + [0.5] + list(self.points[i-1].color)
                pass
            out += list(point.pos) + [0.5] + list(point.color)
            i += 1
        out += list(self.points[-1].pos) + [0.5] + list(self.points[-1].color)
        out += list((1, self.points[-1].pos[1])) + [0.5] + list(self.points[-1].color)
        out = list(self.points[0].pos) + [0.5] + list(self.points[0].color) + out
        out = list((-1, self.points[0].pos[1])) + [0.5] + list(self.points[0].color) + out
        return np.array(out, dtype=np.float32)

    def get_close_point(self, pos, margin=0.02):
        closest_id = None
        closest_dist = 99999
        i=0
        for point in self.points:
            dist = distance_sq(pos, point.pos)
            if closest_id == None:
                if dist < margin:
                    closest_id = i
                    closest_dist = dist
            else:
                if dist < closest_dist:
                    closest_id = i
                    closest_dist = dist
            i += 1
        return closest_id


class Point:
    def __init__(self, pos=(0, 0), color=(1, 0.3, 0.3)):
        self.pos = pos
        self.color = color

    def move(self, pos):
        self.pos = pos


app = QApplication([])

widget = CurveEditor()
widget.show()

app.exec_()