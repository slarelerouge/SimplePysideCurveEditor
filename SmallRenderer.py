# IMPORT
import pathlib
from OpenGL import GL
from PySide2.QtWidgets import QOpenGLWidget
from PySide2.QtCore import *
import ctypes


# FUNCTION


# CLASS
class OpenGLWidget(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        QOpenGLWidget.__init__(self, *args, **kwargs)

        # Set update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.entities = {}

    def add_entity(self, entity, name):
        self.entities[name] = entity

    def initializeGL(self):
        # Clear color
        GL.glClearColor(0.2, 0.3, 0.3, 1.0)
        # Set refresh rate
        self.timer.start(33)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        for entity in self.entities:
            self.entities[entity].draw()


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

    def set_vertices_data(self, v_data, buffer_format=[3, 3]):
        # Format pos.xyz, color.xyz
        self.vertices = v_data
        self.length = int(len(v_data)/6)
        self.byte_size = 4

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL.GL_STATIC_DRAW)

        #
        GL.glBindVertexArray(self.vao)

        stride = 0
        for elem_number in buffer_format:
            stride += self.byte_size*elem_number

        i=0
        offset = 0
        for elem_number in buffer_format:
            GL.glVertexAttribPointer(i, elem_number, GL.GL_FLOAT, GL.GL_FALSE, stride, ctypes.cast(offset, ctypes.c_void_p))
            GL.glEnableVertexAttribArray(i)
            offset = self.byte_size*elem_number
            i+=1

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def draw(self):
        self.shader_program.use()
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(self.draw_method, 0, self.length)