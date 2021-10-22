import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from math import fmod

from transform import identity
from core import Node, Mesh
from animation import TransformKeyFrames


MAX_VERTEX_BONES = 4
MAX_BONES = 128


class SkinnedMesh(Mesh):
    """class of skinned mesh nodes in scene graph """
    def __init__(self, shader, attribs, bone_nodes, bone_offsets, index=None):
        super().__init__(shader, attribs, index)

        # store skinning data
        self.bone_nodes = bone_nodes
        self.bone_offsets = np.array(bone_offsets, np.float32)

    def draw(self, projection, view, model):
        """ skinning object draw method """
        GL.glUseProgram(self.shader.glid)

        # bone world transform matrices need to be passed for skinning
        world_transforms = [node.world_transform for node in self.bone_nodes]
        bone_matrix = world_transforms @ self.bone_offsets
        loc = GL.glGetUniformLocation(self.shader.glid, 'bone_matrix')
        GL.glUniformMatrix4fv(loc, len(self.bone_nodes), True, bone_matrix)

        super().draw(projection, view, model)


class SkinningControlNode(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, *keys, transform=identity(), loop_duration=0.0):
        super().__init__(transform=transform)
        self.keyframes = TransformKeyFrames(*keys) if keys[0] else None
        self.world_transform = identity()
        self.last_reset_time = 0.0
        self.loop_duration = loop_duration

    def draw(self, projection, view, model):
        """ When redraw requested, interpolate our node transform from keys """
        if self.keyframes:  # no keyframe update should happens if no keyframes
            glfw_time = glfw.get_time()
            if self.loop_duration == 0.0: # on n'a pas demandé à faire boucler l'animation
                time = glfw_time - self.last_reset_time
            else:
                time = fmod(glfw_time, self.loop_duration)
            self.transform = self.keyframes.value(time) # CHANGé pour pouvoir reset les animations individuellement

        # store world transform for skinned meshes using this node as bone
        self.world_transform = model @ self.transform

        # default node behaviour (call children's draw method)
        super().draw(projection, view, model)

    def reset_time(self):
        self.last_reset_time = float(glfw.get_time())
