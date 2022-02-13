import pathlib
import numpy as np
from OpenGL import GL
from PySide2.QtWidgets import QOpenGLWidget, QApplication
from PySide2.QtOpenGL import QGLWidget
from PySide2.QtCore import *


# FUNCTION
def create_vertices_data():
    background_vertices = np.array([1.0, 1.0, 0.5, -1.0, 1.0, 0.5, -1.0, -1.0, 0.5, 1.0, 1.0, 0.5, -1.0, -1.0, 0.5, 1.0, -1.0, 0.5], dtype=np.float32)
    line_vertices = np.array([0.0, 0.0, 0.5, 1.0, 1.0, 0.5], dtype=np.float32)
    vertices = np.concatenate((background_vertices, line_vertices))
    return background_vertices


# CLASS
class OpenGLWidget(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        self.t = 0
        QOpenGLWidget.__init__(self, *args, **kwargs)

        # Set update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

    def initializeGL(self):
        # Prepare openGL
        background = Entity(draw_method=GL.GL_TRIANGLES)
        v_data_background = np.array(
            [1.0, 1.0, 0.5, -1.0, 1.0, 0.5, -1.0, -1.0, 0.5, 1.0, 1.0, 0.5, -1.0, -1.0, 0.5, 1.0, -1.0, 0.5],
            dtype=np.float32)
        background.set_vertices_data(v_data_background)

        line = Entity(draw_method=GL.GL_LINES)
        v_data_line = np.array([0.0, 0.0, 0.5, 1.0, 1.0, 0.5], dtype=np.float32)
        line.set_vertices_data(v_data_line)

        self.entities = [background, line]

        # Set refresh rate
        self.timer.start(33)

    def paintGL(self):
        for entity in self.entities:
            entity.draw()


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
        self.vertices = []

        self.shader_program = ShaderProgram()

        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        self.draw_method = draw_method
        self.length = int(0)

    def set_vertices_data(self, v_data):
        self.vertices = v_data
        self.length = int(len(v_data)/3)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL.GL_STATIC_DRAW)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def draw(self):
        self.shader_program.use()
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(self.draw_method, 0, self.length)


app = QApplication([])

widget = OpenGLWidget()
widget.show()

app.exec_()
