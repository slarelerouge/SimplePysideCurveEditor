"""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>. 3
"""

# IMPORT
import pathlib
from OpenGL import GL
from PySide2.QtWidgets import QOpenGLWidget
from PySide2.QtCore import *
import ctypes


# FUNCTION


# CLASS
# Widget class that contains the opengl renderer
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
        GL.glClearColor(0.3, 0.3, 0.3, 1.0)
        # Set refresh rate
        self.timer.start(33)

        GL.glLineWidth(3)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        for entity in self.entities:
            self.entities[entity].draw()


# ShaderProgram is a class that creates a shader program that manage how to interpret data in the buffers
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


# Entity is a class to manage objects to render
class Entity:
    def __init__(self, draw_method=GL.GL_TRIANGLES):
        self.shader_program = ShaderProgram()

        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        self.draw_method = draw_method
        self.length = int(0)

    def update_vertices_data(self, v_data):
        # Format pos.xyz, color.xyz
        self.length = int(len(v_data) / 6)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    # Buffer format means elements per vao; for instance, data like pos.xyz, color.xyz needs buffer_format = [3, 3],
    # while pos.xyz, normal.xyz, color.xyz, uv.xy would need [3, 3, 3, 2]
    def set_vertices_data(self, v_data, buffer_format=[3, 3]):
        self.length = int(len(v_data)/sum(buffer_format))
        self.byte_size = 4  # 4B = 32b

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, v_data.nbytes, v_data, GL.GL_STATIC_DRAW)

        #
        GL.glBindVertexArray(self.vao)

        stride = sum(buffer_format)*self.byte_size

        i=0
        offset = 0
        for elem_number in buffer_format:
            GL.glVertexAttribPointer(i, elem_number, GL.GL_FLOAT, GL.GL_FALSE, stride, ctypes.cast(offset, ctypes.c_void_p))
            GL.glEnableVertexAttribArray(i)
            offset = self.byte_size*elem_number
            i+=1

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def draw(self):
        self.shader_program.use()
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(self.draw_method, 0, self.length)