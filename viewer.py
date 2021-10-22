#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import glfw
from core import Shader, Viewer
from viewer_adder import (#add_files_specified_in_the_command,
                          add_the_island, add_the_castle, add_an_elf,
                          add_the_walking_elf, add_an_elf_statue,
                          add_a_catapult, add_a_fountain, add_skybox)


def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    viewer.trackball.distance = 200
    shader = Shader("shader.vert", "shader.frag")

    shader_skybox = Shader("skybox.vert", "skybox.frag")

    # add whatever you want thanks to "adder_to_viewer.py"
    # add_files_specified_in_the_command(viewer, shader)

    # Foundation
    add_skybox(viewer, shader_skybox, 2000)
    add_the_island(viewer, shader)
    add_the_castle(viewer, shader)

    # Elfs inside the castle
    add_an_elf(viewer, shader, (-20, 2.15, 1), actions=["sitting_down", "getting_up"], num_texture=1, key_to_reset=glfw.KEY_G)
    add_an_elf(viewer, shader, (-18.5, 17, 0), ((0, 1, 0), -90), num_texture=3, actions=["talking"], loop_duration=3)
    add_an_elf(viewer, shader, (-20, 17, 0), ((0, 1, 0), 90), actions=["listening"], num_texture=4, loop_duration=3)
    add_an_elf(viewer, shader, (-15, 17, 4.5), ((0, 1, 0), 10), actions=["waiting"], num_texture=6, loop_duration=5)
    add_an_elf(viewer, shader, (-40, 0.5, 1), ((0, 1, 0), -20), actions=["waiting"], num_texture=10, loop_duration=6)
    add_an_elf(viewer, shader, (1.73, 0.5, 11), ((0, 1, 0), -120), num_texture=11, actions=["jumping"], loop_duration=3)
    add_an_elf(viewer, shader, (0, 0.5, 10), ((0, 1, 0), 60), actions=["jumping"], num_texture=12, loop_duration=4)

    # Elfs outside the castle
    add_an_elf(viewer, shader, (-46.1, 0, 36), actions=["walking_in_circle"], num_texture=2, loop_duration=12.5)
    add_an_elf(viewer, shader, (-8, 0, 37), actions=["doing_push_ups"], num_texture=7, loop_duration=0.8)
    add_an_elf(viewer, shader, (-6, 0, 37), actions=["doing_push_ups_slowly"], num_texture=9, loop_duration=1)
    add_an_elf(viewer, shader, (-4, 0, 32), ((0, 1, 0), -20), actions=["stretching"], num_texture=8, loop_duration=6)
    add_an_elf(viewer, shader, (124, 30.15, 12), ((0, 1, 0), -100), actions=["jumping_higher"], num_texture=5, key_to_reset=glfw.KEY_J)
    add_an_elf(viewer, shader, (17.4, 23, 21.7), actions=["saying_hi"], num_texture=5, key_to_reset=glfw.KEY_H)
    add_the_walking_elf(viewer, shader)

    # Other objects
    add_an_elf_statue(viewer, shader, (-47, 0.5, 7))
    add_a_catapult(viewer, shader,  (-45, 0.5, 40), ((0, 1, 0), 15))
    add_a_fountain(viewer, shader, (7, 0, 40))

    print()

    print("################### LISTE DES COMMANDES #######################")
    print("a, Escape : fermer la fenêtre ")
    print("z : \"glPolygonMode\" (utile pour placer/retrouver les individus)")
    print("barre d'espace : recommencer l'ensemble des animations du début")
    print("e (Echelle) : zoomer => utile en cas de problème de souris")
    print("r (Rétrécir): dézoomer => utile en cas de problème de souris")
    print("flèche du haut : monter la catapulte")
    print("flèche du bas : descendre la catapulte")
    print("g (Get up/down) : faire s'asseoir l'elfe s'il est debout et le lever s'il est assis")
    print("  => localisation de l'elfe en question : intérieur du chateau, en bas, sur une plateforme")
    print("h (say Hi) : faire faire coucou à l'elfe")
    print("  => localisation de l'elfe en question : sur la tour avant gauche du château")
    print("j (Jump) : faire sauter l'elfe")
    print("  => localisation de l'elfe en question : sur la tour de garde de la petite île")
    print("##########################################################")

    print()

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
