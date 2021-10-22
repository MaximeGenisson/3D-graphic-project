from bisect import bisect_left      # search sorted keyframe lists

# External, non built-in modules
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args

from transform import (lerp, quaternion_slerp, quaternion_matrix)
from core import Node
from numbers import Number
from math import fmod


# -------------- KeyFrames part ---------------------------------
class KeyFrames:
    """ Stores keyframe pairs for any value type with interpolation_function"""
    def __init__(self, time_value_pairs, interpolation_function=lerp):
        if isinstance(time_value_pairs, dict):  # convert to list of pairs
            time_value_pairs = time_value_pairs.items()
        keyframes = sorted(((key[0], key[1]) for key in time_value_pairs))
        self.times, self.values = zip(*keyframes)  # pairs list -> 2 lists
        self.interpolate = interpolation_function

    def value(self, time):
        """ Computes interpolated value from keyframes, for a given time """
        t = self.times
        v = self.values
        # 1. ensure time is within bounds else return boundary keyframe
        if(time <= t[0]):
            return v[0] # donc on sait que si on passe au 2. on aura ind != 0
        if(time >= t[-1]):
            return v[-1]
        # 2. search for closest index entry in self.times, using bisect_left function
        ind = bisect_left(t, time) # indice là où on l'insèrerait
        # 3. using the retrieved index, interpolate between the two neighboring values
        # in self.values, using the initially stored self.interpolate function
        f = (time - t[ind-1]) / (t[ind] - t[ind-1])
        return self.interpolate(v[ind-1], v[ind], f)


class TransformKeyFrames:
    """ KeyFrames-like object dedicated to 3D transforms """
    def __init__(self, translate_keys, rotate_keys, scale_keys):
        """ stores 3 keyframe sets for translation, rotation, scale """
        self.trans = KeyFrames(translate_keys)
        self.rot = KeyFrames(rotate_keys, quaternion_slerp)
        self.scale = KeyFrames(scale_keys) # donne directement les quaternions

    def value(self, time):
        """ Compute each component's interpolation and compose TRS matrix """
        T = self.trans.value(time) # numpy vector pour la translation
        s = self.scale.value(time)
        final_quaternion = self.rot.value(time)
        R = quaternion_matrix(final_quaternion)
        if (isinstance(s, Number)): # si c'est un scalaire (Number a été importé)
            S = [s, s, s]
        else:
            S = s
        M = np.array([[R[0, 0] * S[0], R[0, 1] * S[1], R[0, 2] * S[2], T[0]],
                      [R[1, 0] * S[0], R[1, 1] * S[1], R[1, 2] * S[2], T[1]],
                      [R[2, 0] * S[0], R[2, 1] * S[1], R[2, 2] * S[2], T[2]],
                      [0, 0, 0, 1]])
        return M


class KeyFrameControlNode(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, trans_keys, rotat_keys, scale_keys, loop_duration=0.0):
        super().__init__()
        self.keyframes = TransformKeyFrames(trans_keys, rotat_keys, scale_keys)
        self.loop_duration = loop_duration

    def draw(self, projection, view, model):
        """ When redraw requested, interpolate our node transform from keys """
        glfw_time = glfw.get_time()
        if self.loop_duration == 0.0: # on n'a pas demandé à faire boucler l'animation
            time = glfw_time
            # rq : on a pas implémenté les reset_time pour KeyFrameControlNode
            # parce qu'on en a pas eu besoin,
            # mais on pourrait le faire exactement de la mm façon que pour
            # SkinningControlNode (cf mesh_skinning.py)
        else:
            time = fmod(glfw_time, self.loop_duration)
        self.transform = self.keyframes.value(time)
        super().draw(projection, view, model)
