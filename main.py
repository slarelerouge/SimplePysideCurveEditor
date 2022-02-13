# IMPORT
import pathlib
import numpy as np
from OpenGL import GL
from PySide2.QtWidgets import QOpenGLWidget, QApplication
from PySide2.QtOpenGL import QGLWidget
from PySide2.QtCore import *
import ctypes
import math


# FUNCTION


# CLASS
class OpenGLWidget(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        QOpenGLWidget.__init__(self, *args, **kwargs)

        # Set update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.line_data = Line(color=(1.0, 0.3, 0.3))
        self.line_data.add_point((0.0, 0.0))
        self.line_data.add_point((0.5, 0.5))

        self.selected_point = None


    def initializeGL(self):
        # Prepare openGL
        background = Entity(draw_method=GL.GL_TRIANGLES)

        # Format pos.xyz, color.xyz
        v_data_background = np.array(
            [1.0, 1.0, 0.5,  0.5, 0.5, 0.5,
             -1.0, 1.0, 0.5,  0.5, 0.5, 0.5,
             -1.0, -1.0, 0.5,  0.5, 0.5, 0.5,
             1.0, 1.0, 0.5,  0.5, 0.5, 0.5,
             -1.0, -1.0, 0.5,  0.5, 0.5, 0.5,
             1.0, -1.0, 0.5,  0.5, 0.5, 0.5],
            dtype=np.float32)
        background.set_vertices_data(v_data_background)

        v_data_line = self.line_data.get_vertex_array()

        line = Entity(draw_method=GL.GL_LINES)
        line.set_vertices_data(v_data_line)

        self.entities = [line]

        # Clear color
        GL.glClearColor(0.2, 0.3, 0.3, 1.0)

        # Set refresh rate
        self.timer.start(33)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        v_data_line = self.line_data.get_vertex_array()
        self.entities[0].update_vertices_data(v_data_line)

        for entity in self.entities:
            entity.draw()

    def mousePressEvent(self, event):
        mouse_pos = event.pos().toTuple()
        size = self.size().toTuple()
        pos = (2*mouse_pos[0]/size[0] - 1, -(2*mouse_pos[1]/size[1] - 1))
        self.selected_point = self.line_data.get_close_point(pos)

    def mouseMoveEvent(self, event):
        mouse_pos = event.pos().toTuple()
        size = self.size().toTuple()
        pos = (2 * mouse_pos[0] / size[0] - 1, -(2 * mouse_pos[1] / size[1] - 1))

        if self.selected_point != None:
            self.line_data.points[self.selected_point].move(pos)

    def mouseReleaseEvent(self, event):
        self.selected_point = None


class Line:
    def __init__(self, color=(1.0, 1.0, 1.0)):
        self.points = []
        self.color = color

    def add_point(self, pos=(0, 0)):
        self.points.append(Point(pos=pos, color=self.color))

    def get_vertex_array(self):
        out = []
        for point in self.points:
            out += list(point.pos) + [0.5] + list(point.color)
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

def distance_sq(pos_a, pos_b):
    x_dif = abs(pos_a[0] - pos_b[0])
    y_dif = abs(pos_a[1] - pos_b[1])
    return math.pow(x_dif, 2) + math.pow(y_dif, 2)

class Point:
    def __init__(self, pos=(0, 0), color=(1, 0.3, 0.3)):
        self.pos = pos
        self.color = color

    def move(self, pos):
        self.pos = pos


class ShaderProgram:
    def __init__(self, vs="vert.glsl", fs="frag.glsl"):
        vertex_shader_source_path = pathlib.Path("glsl/" + vs)
        fragment_shader_source_path = pathlib.Path("glsl/" + fs)

        with open(vertex_shader_source_path, 'r') as vertex_shader_source:
            vertex_shader_code = vertex_shader_source.read()
        with open(fragment_shader_source_path, 'r') as fragment_shader_source:
            fragment_shader_code = fragment_shader_source.read()

        vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(vertex_shader, vertex_shader_code)
        GL.glCompileShader(vertex_shader)

        fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(fragment_shader, fragment_shader_code)
        GL.glCompileShader(fragment_shader)

        self.shader_program = GL.glCreateProgram()

        GL.glAttachShader(self.shader_program, vertex_shader)
        GL.glAttachShader(self.shader_program, fragment_shader)
        GL.glLinkProgram(self.shader_program)

    def use(self):
        GL.glUseProgram(self.shader_program)


class Entity:
    def __init__(self, draw_method=GL.GL_TRIANGLES):
        self.shader_program = ShaderProgram()

        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        self.draw_method = draw_method
        self.length = int(0)

    def update_vertices_data(self, v_data):
        # Format pos.xyz, color.xyz
        self.vertices = v_data
        self.length = int(len(v_data) / 6)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def set_vertices_data(self, v_data):
        # Format pos.xyz, color.xyz
        self.vertices = v_data
        self.length = int(len(v_data)/6)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL.GL_STATIC_DRAW)

        #
        GL.glBindVertexArray(self.vao)
        # Position
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 4*3*2, ctypes.cast(0, ctypes.c_void_p))
        GL.glEnableVertexAttribArray(0)
        # Color
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 4*3*2, ctypes.cast(4*3, ctypes.c_void_p))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def draw(self):
        self.shader_program.use()
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(self.draw_method, 0, self.length)


app = QApplication([])

widget = OpenGLWidget()
widget.show()

app.exec_()