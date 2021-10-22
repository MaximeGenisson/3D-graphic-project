#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import OpenGL.GL as GL              # standard Python OpenGL wrapper
import numpy as np                  # all matrix manipulations & OpenGL args
from PIL import Image               # load images for textures

from core import Mesh


class SkyTexture:
    def __init__(self, faces):
        self.glid = GL.glGenTextures(1)
        try:
            GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.glid)
            # imports image as a numpy array in exactly right format
            for i in range(len(faces)):
                tex = np.asarray(Image.open(faces[i]).convert('RGBA'))
                GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGBA, tex.shape[1],
                                tex.shape[0], 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, tex)

            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)
            # GL.glBindTexture( GL.GL_TEXTURE_CUBE_MAP, 0)

            message = "Loaded texture {}\t{}"
            print(message.format(faces, tex.shape))
        except FileNotFoundError:
            print("ERROR: unable to load texture files {}".format(faces))

    def __del__(self):  # delete GL texture from GPU when object dies
        GL.glDeleteTextures(self.glid)


faces = np.array(["resources/sky/right.jpg",
                  "resources/sky/left.jpg",
                  "resources/sky/top.jpg",
                  "resources/sky/bottom.jpg",
                  "resources/sky/front.jpg",
                  "resources/sky/back.jpg"])

skyboxVertices = np.array([
        (-1.0,  1.0, -1.0),
        (-1.0, -1.0, -1.0),
        (1.0, -1.0, -1.0),
        (1.0, -1.0, -1.0),
        (1.0,  1.0, -1.0),
        (-1.0,  1.0, -1.0),

        (-1.0, -1.0,  1.0),
        (-1.0, -1.0, -1.0),
        (-1.0,  1.0, -1.0),
        (-1.0,  1.0, -1.0),
        (-1.0,  1.0,  1.0),
        (-1.0, -1.0,  1.0),

        (1.0, -1.0, -1.0),
        (1.0, -1.0,  1.0),
        (1.0,  1.0,  1.0),
        (1.0,  1.0,  1.0),
        (1.0,  1.0, -1.0),
        (1.0, -1.0, -1.0),

        (-1.0, -1.0,  1.0),
        (-1.0,  1.0,  1.0),
        (1.0,  1.0,  1.0),
        (1.0,  1.0,  1.0),
        (1.0, -1.0,  1.0),
        (-1.0, -1.0,  1.0),

        (-1.0,  1.0, -1.0),
        (1.0,  1.0, -1.0),
        (1.0,  1.0,  1.0),
        (1.0,  1.0,  1.0),
        (-1.0,  1.0,  1.0),
        (-1.0,  1.0, -1.0),

        (-1.0, -1.0, -1.0),
        (-1.0, -1.0,  1.0),
        (1.0, -1.0, -1.0),
        (1.0, -1.0, -1.0),
        (-1.0, -1.0,  1.0),
        (1.0, -1.0,  1.0)
])


class Skybox(Mesh):
    """ Class for drawing a pyramid object """

    def __init__(self, shader):
        self.shader = shader

        self.cubemapTexture = SkyTexture(faces)

        # TODO: this is still a triangle, new values needed for Pyramid
        position = skyboxVertices

        super().__init__(shader, attributes=[position])

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glUseProgram(self.shader.glid)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.cubemapTexture.glid)
        GL.glUniform1i(GL.glGetUniformLocation(self.shader.glid, "skybox"), 0)

        super().draw(projection, view, model)
        GL.glDepthFunc(GL.GL_LESS)
