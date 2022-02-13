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
    return vertices


# CLASS
class OpenGLWidget(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        self.t = 0
        QOpenGLWidget.__init__(self, *args, **kwargs)

        # Set update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

    def initializeGL(self):
        self.OGL = OGL()
        # Set refresh rate
        self.timer.start(33)

    def paintGL(self):
        self.OGL.draw()


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
    def __init__(self):
        self.vertices = []
        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

    def set_vertices_data(self, v_data):
        self.vertices = v_data
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL.GL_STATIC_DRAW)


        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        GL.glEnableVertexAttribArray(0)




        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)


class OGL:
    def __init__(self):
        self.shader_program = ShaderProgram()
        self.shader_program.use()

        entity = Entity()
        v_data = create_vertices_data()
        print(v_data)
        entity.set_vertices_data(v_data)
        self.entities = [entity]


        """self._init_shader_program()
        self._init_array_buffer()

        self._va_index = {"vertex": 0, "color": 1}
        #self._init_background()"""

    def _init_shader_program(self):
        vertex_shader_source_path = pathlib.Path("glsl/vert.glsl")
        fragment_shader_source_path = pathlib.Path("glsl/frag.glsl")

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

        GL.glUseProgram(self.shader_program)

    def _init_array_buffer(self):
        # Create generic buffer
        self.vertex_buffer = GL.glGenBuffers(1)
        self.color_buffer = GL.glGenBuffers(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        vertices = create_vertices_data()
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

        GL.glEnableVertexAttribArray(0)
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

    def _create_color_data(self):
        background_color = np.array(
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], dtype=np.float32)
        return background_color

    def draw(self):
        #GL.glEnableVertexAttribArray(self._va_index["vertex"])
        #GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
        GL.glBindVertexArray(self.entities[0].vao)
        GL.glDrawArrays(GL.GL_LINES, 6, 10)


app = QApplication([])

widget = OpenGLWidget()
widget.show()

app.exec_()
