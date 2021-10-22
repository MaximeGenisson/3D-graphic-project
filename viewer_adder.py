import sys
import glfw

from core import Node, RotationControlNode
from transform import scale, translate, rotate, vec, quaternion, quaternion_from_euler
from mesh_texture_skinning import load_textured_skinned
from mesh_texture_illumination import load_textured_illuminated
from mesh_texture_skinning_illumination import load_textured_skinned_illuminated
from animation import KeyFrameControlNode
from sky import Skybox

NB_TEXTURES_ELF = 12


class Elf(Node):
    def __init__(self, shader, actions, num_texture, key_to_reset=None, loop_duration=0.0):
        # /!\ actions est une liste de strings !
        super().__init__()
        num_texture += int(num_texture > NB_TEXTURES_ELF)
        num_texture %= (NB_TEXTURES_ELF + 1)
        possible_actions = ["walking_in_circle", "walking_on_the_spot",
                            "talking", "listening", "sitting_down",
                            "getting_up", "waiting", "saying_hi",
                            "doing_push_ups", "doing_push_ups_slowly",
                            "stretching", "jumping", "jumping_higher"]
        for action in actions:
            if action not in possible_actions:
                # l'action n'est pas possible ; on va ignorer cette demande et juste
                # le signaler dans la console :
                print("##############################################")
                print("ERREUR DANS LE NOM DE L'ACTION DE L'ELFE !!!")
                print("(" + action + " n'existe pas)")
                print("Voici la liste des actions possibles :")
                for a in possible_actions:
                    print(a + ", ", end='')
                print("\n##############################################")
        else:
            self.key_to_reset = key_to_reset
            self.nb_actions = len(actions) # évite d'avoir à recompter à chaque fois
            if self.nb_actions > 1:
                self.actions = actions
                self.current_action = 0
                self.shader = shader # Pour pouvoir changer d'action
                self.num_texture = num_texture # Pour pouvoir changer d'action
            if self.nb_actions >= 1:
                self.add(*load_textured_skinned("our_creations/elf/elf_"
                         + actions[0] + ".fbx", shader, "our_creations/elf/UV_elf_"
                         + str(num_texture) + ".png", loop_duration))
            # si pas d'action, l'elfe est ignoré (pas affiché)

    def key_handler(self, key): # pour pouvoir reset les animations individuellement
        def recursive_reset_time(cur):
            if hasattr(cur, "children") and len(cur.children) != 0:
                for child in cur.children:
                    if hasattr(child, "reset_time"):
                        child.reset_time()
                    recursive_reset_time(child)
        if key == self.key_to_reset:
            if(self.nb_actions > 1):
                self.current_action = (self.current_action + 1) % self.nb_actions
                self.children = []
                self.add(*load_textured_skinned("our_creations/elf/elf_"
                         + self.actions[self.current_action] + ".fbx", self.shader,
                         "our_creations/elf/UV_elf_" + str(self.num_texture)
                         + ".png")) # éventuellement rajouter la loop_duration si besoin

            recursive_reset_time(self) # cela recommence l'animation à 0

        super().key_handler(key)


class Elf_statue(Node):
    def __init__(self, shader):
        super().__init__()
        self.add(*load_textured_skinned_illuminated("our_creations/elf/elf_statue.obj", shader))


class Fountain(Node):
    def __init__(self, shader):
        super().__init__()
        self.add(*load_textured_skinned("resources/fountain.obj", shader, "resources/fountain.png"))


class Cube(Node):
    def __init__(self, shader, texture="wood"):
        super().__init__()
        self.add(*load_textured_skinned('our_creations/catapult/cube.obj', shader, "resources/" + texture + ".png"))


class Cylinder(Node):
    def __init__(self, shader, texture="wood"):
        super().__init__()
        self.add(*load_textured_skinned('resources/cylinder.obj', shader, "resources/" + texture + ".png"))


class Bucket(Node):
    def __init__(self, shader):
        super().__init__()
        self.add(*load_textured_skinned('our_creations/catapult/bucket.obj', shader, "resources/metal.png"))


# def add_files_specified_in_the_command(viewer, shader):
#     if len(sys.argv) < 2:
#         print("NOTE : IL EST AUSSI POSSIBLE DE METTRE DES FICHIERS EN ARGUMENT"
#               + " POUR LES AFFICHER AU CENTRE DU REPERE")
#     else:
#         viewer.add(*[m for file in sys.argv[1:]
#                      for m in load_textured_skinned_illuminated(file, shader)])


def add_an_elf(viewer, shader, position=(0, 0, 0), orientation=((0, 0, 0), 0), actions=[], num_texture=1, key_to_reset=None, loop_duration=0.0):
    elf = Elf(shader, actions, num_texture, key_to_reset, loop_duration)
    elf_shape = Node(transform=translate(0, -0.4, 0) @ scale(0.006))
    elf_shape.add(elf)
    transform_elf = Node(transform = translate(position) @ rotate(orientation[0], orientation[1]))
    transform_elf.add(elf_shape)
    viewer.add(transform_elf)


def add_the_walking_elf(viewer, shader, position=(0, 0, 0), orientation=((0, 0, 0), 0), num_texture=1):
    elf = Elf(shader, ["walking_on_the_spot"], num_texture, loop_duration=1.3)
    translate_keys = {0: vec(30, 0, 30), 4: vec(30, 0, 13), 5: vec(34, 0, 13),
                      6: vec(35.5, 2, 13), 22: vec(110, 2, 13), 25.6: vec(118, 2, 28),
                      27.6: vec(126.5, 2, 28), 28.6: vec(126.5, 2, 23.5),
                      29.4: vec(126.5, 2, 20.5), 34: vec(126.5, 2, 20.5),
                      34.8: vec(126.5, 2, 23.5), 35.8: vec(126.5, 2, 28),
                      37.8: vec(118, 2, 28), 41.4: vec(110, 2, 13), 57.4: vec(35.5, 2, 13),
                      58.4: vec(34, 0, 13), 59.4: vec(30, 0, 13), 63.4: vec(30, 0, 30)}
    rotate_keys = {0: quaternion_from_euler(0, 180, 0), 3.6: quaternion_from_euler(0, 180, 0),
                   4.4: quaternion_from_euler(0, 90, 0), 21.6: quaternion_from_euler(0, 90, 0),
                   22: quaternion_from_euler(0, 23, 0),
                   25.2: quaternion_from_euler(0, 23, 0), 26: quaternion_from_euler(0, 90, 0),
                   27.2: quaternion_from_euler(0, 90, 0), 28: quaternion_from_euler(0, 180, 0),
                   30: quaternion_from_euler(0, 180, 0), 32: quaternion_from_euler(),
                   35.4: quaternion_from_euler(0, 0, 0), 36.2: quaternion_from_euler(0, -90, 0),
                   37.4: quaternion_from_euler(0, -90, 0), 38.2:quaternion_from_euler(0, -157, 0),
                  41: quaternion_from_euler(0, -157, 0),  41.8: quaternion_from_euler(0, -90, 0),
                  59:quaternion_from_euler(0, -90, 0), 59.8: quaternion()}
    scale_keys = {0: 0.006, 50: 0.006}
    keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys, loop_duration=63.4)
    keynode.add(elf)
    viewer.add(keynode)


def add_an_elf_statue(viewer, shader, position=(0, 0, 0), orientation=((0, 0, 0), 0)):
    elf = Elf_statue(shader)
    elf_shape = Node(transform=translate(0, -0.4, 0) @ scale(4))
    elf_shape.add(elf)
    transform_elf = Node(transform = translate(position) @ rotate(orientation[0], orientation[1]))
    transform_elf.add(elf_shape)
    viewer.add(transform_elf)


def add_a_fountain(viewer, shader, position=(0, 0, 0), orientation=((0, 0, 0), 0)):
    fountain = Fountain(shader)
    fountain_shape = Node(transform= translate(5, -0.5, 0) @ scale(0.02))
    fountain_shape.add(fountain)
    transform_fountain = Node(transform = translate(position) @ rotate(orientation[0], orientation[1]))
    transform_fountain.add(fountain_shape)
    viewer.add(transform_fountain)


def add_a_catapult(viewer, shader, position=(0, 0, 0), orientation=((0, 0, 0), 0)):
    cube = Cube(shader)
    cylinder = Cylinder(shader)
    bucket = Bucket(shader)
    wheels = Cylinder(shader, "darker_wood")
    counterweight = Cube(shader, "metal")

    phi1 = 45.0
    phi2 = 60.0
    phi3 = 90.0
    phi4 = 90.0 + phi2
    phi5 = 180.0

    # les numéros se réfèrent aux légendes de "catapulte_légendée.jpg"

    # ---- on construit les formes ---------------------------
    shape1 = Node(transform=rotate((0, 1, 0), phi5) @ rotate((1, 0, 0), phi3))
    shape1.add(bucket)
    shape2 = Node(transform=rotate((0, 0, 1), phi3) @ scale(0.22, 0.05, 0.22))
    shape2.add(wheels)
    shape3 = Node(transform=rotate((0, 0, 1), phi3) @ scale(0.05, 0.6, 0.05))
    shape3.add(cylinder)
    shape4 = Node(transform=scale(0.15, 0.09, 0.2))
    shape4.add(counterweight)
    shape5 = Node(transform=scale(0.1, 0.06, 1.3))
    shape5.add(cube)
    shape6 = Node(transform= rotate((1, 0, 0), phi2) @ scale(0.4, 0.05, 0.05))
    shape6.add(cube)
    shape7 = Node(transform=rotate((1, 0, 0), phi4) @ scale(0.05, 0.05, 0.75))
    shape7.add(cube)
    shape8 = Node(transform=rotate((1, 0, 0), phi2) @ scale(0.05, 0.05, 0.6))
    shape8.add(cube)
    shape9 = Node(transform=scale(0.05, 0.05, 0.9))
    shape9.add(cube)
    shape10 = Node(transform=scale(0.4, 0.05, 0.05))
    shape10.add(cube)
    shape11 = Node(transform=scale(0.05, 0.13, 0.05))
    shape11.add(cube)

    # ---- on construit la hiérarchie (de bas en haut)-------------------------
    # g = gauche, d = droite, av = avant, ar = arrière, s = supérieur, i = inférieur
    transform1 = Node(transform=translate(0, 0, -1.3))
    transform1.add(shape1)
    transform4 = Node(transform=translate(0, 0, 1))
    transform4.add(shape4, transform1)
    transform5 = RotationControlNode(glfw.KEY_UP, glfw.KEY_DOWN, (1, 0, 0), angle=phi1)
    transform5.add(shape5, transform4)
    transform6i = Node(transform=translate(0, -0.28, 0.16))
    transform6i.add(shape6, transform5)
    transform6s = Node(transform=translate(0.35, 0.48, -0.28))
    transform6s.add(shape6, transform6i)
    transform8d = Node(transform=translate(0, 0.17, 0.77))
    transform8d.add(shape8, transform6s)
    transform7d = Node(transform=translate(-0.7, 0, 0))
    transform7d.add(shape7, transform8d)
    transform7g = Node(transform=translate(0, -0.17, -0.77))
    transform7g.add(shape7, transform7d)
    transform8g = Node(transform=translate(0, 0.55, 0.55))
    transform8g.add(shape8, transform7g)
    transform9sg = Node(transform=translate(0.7, 0, 0))
    transform9sg.add(shape9, transform8g)
    transform9sd = Node(transform=translate(-0.35, 0, 0.85))
    transform9sd.add(shape9, transform9sg)
    transform10ar = Node(transform=translate(0, 0, -1.7))
    transform10ar.add(shape10, transform9sd)
    transform10av = Node(transform=translate(-0.35, 0.08, 0))
    transform10av.add(shape10, transform10ar)
    transform11avg = Node(transform=translate(0.7, 0, 0))
    transform11avg.add(shape11, transform10av)
    transform11avd = Node(transform=translate(0, 0, 1.7))
    transform11avd.add(shape11, transform11avg)
    transform11ard = Node(transform=translate(-0.7, 0, 0))
    transform11ard.add(shape11, transform11avd)
    transform11arg = Node(transform=translate(0, 0.05, -0.85))
    transform11arg.add(shape11, transform11ard)
    transform9ig = Node(transform=translate(-0.15, 0, 0.55))
    transform9ig.add(shape9, transform11arg)
    transform2arg = Node(transform=translate(0.5, 0, 0))
    transform2arg.add(shape2, transform9ig)
    transform3ar = Node(transform=translate(0.5, 0, 0))
    transform3ar.add(shape3, transform2arg)
    transform2ard = Node(transform=translate(-0.15, 0, -0.55))
    transform2ard.add(shape2, transform3ar)
    transform9id = Node(transform=translate(0.15, 0, -0.55))
    transform9id.add(shape9, transform2ard)
    transform2avd = Node(transform=translate(-0.5, 0, 0))
    transform2avd.add(shape2, transform9id)
    transform3av = Node(transform=translate(-0.5, 0, 0))
    transform3av.add(shape3, transform2avd)
    transform2avg = Node(transform=translate(position)
                         @ rotate(orientation[0], orientation[1])
                         @ translate(-1, 0.2, 1) @ scale(4.3))
                         # roue avant gauche, définie comme la base
    transform2avg.add(shape2, transform3av)

    viewer.add(transform2avg)


def add_the_island(viewer, shader):
    island = Node(transform= rotate((0,1,0), 90) @ translate(-50, -9.5, 0) @ scale(3))
    island.add(*load_textured_skinned_illuminated("our_creations/island/island_block.obj", shader, "our_creations/island/island_block.png"))
    transform_boat = Node(transform=translate(-15, 1, 0))
    transform_boat.add(*load_textured_skinned_illuminated("our_creations/island/boat_and_pontoon.obj", shader, "our_creations/island/boat_and_pontoon.png"))
    island.add(transform_boat)
    island.add(*load_textured_skinned_illuminated("our_creations/island/rocks.obj", shader, "our_creations/island/rocks.png"))
    island.add(*load_textured_skinned_illuminated("our_creations/island/sea_and_sand.obj", shader, "our_creations/island/sea_and_sand.png"))
    island.add(*load_textured_skinned_illuminated("our_creations/island/small_island.obj", shader, "our_creations/island/small_island.png"))
    island.add(*load_textured_skinned_illuminated("our_creations/island/bridge.obj", shader, "our_creations/island/bridge.png"))
    island.add(*load_textured_skinned_illuminated("our_creations/island/tower.obj", shader, "our_creations/island/tower.png"))
    viewer.add(island)


def add_the_castle(viewer, shader):
    castle = Node(transform=translate(-33, 11.5, 25) @ scale(0.45))
    castle_walls = Node()

    tower = load_textured_illuminated('resources/castle/tower.FBX', shader, tex_file="resources/castle/Texture/tower_01_D.jpg")
    for i in range(4):
        if(i == 0):
            tower_shape = Node(transform=translate(-30,9,0) @ scale(.15,.25,.15))
        elif(i == 1):
            tower_shape = Node(transform=translate(56,9,0) @ scale(.15,.25,.15))
        elif(i == 2):
            tower_shape = Node(transform=translate(-30,9,-86) @ scale(.15,.25,.15))
        else:
            tower_shape = Node(transform=translate(56,9,-86) @ scale(.15,.25,.15))
        tower_shape.add(*tower)
        castle_walls.add(tower_shape)


    wall = load_textured_illuminated('resources/castle/castle_wall.FBX', shader)
    door = load_textured_illuminated('resources/castle/castle_gate.FBX', shader)
    wall_shape = Node(transform=translate(-20.5, -5, -8)@ scale(.35,.25,.25))
    wall_shape.add(*wall)
    castle_walls.add(wall_shape)

    wall_shape = Node(transform=translate(28.5, -13)@ scale(.25,.25,.25)@ rotate(angle=-90, axis=(1, 0, 0)))
    wall_shape.add(*door)
    castle_walls.add(wall_shape)

    wall_shape = Node(transform=translate(42.5, -5, -8)@ scale(.35,.25,.25))
    wall_shape.add(*wall)
    castle_walls.add(wall_shape)

    for i in range(5):
        wall_shape = Node(transform=translate(52, -5,-12 -16*i)@ scale(.25,.25,.25)@ rotate(angle=90, axis=(0, 1, 0)))
        wall_shape.add(*wall)
        castle_walls.add(wall_shape)

    for i in range(5):
        wall_shape = Node(transform=translate(-15.5 + 16*i, -5, -86)@ scale(.25,.25,.25)@ rotate(angle=180, axis=(0, 1, 0)))
        wall_shape.add(*wall)
        castle_walls.add(wall_shape)

    for i in range(5):
        wall_shape = Node(transform=translate(-26, -5,-16 -16*i)@ scale(.25,.25,.25)@ rotate(angle=-90, axis=(0, 1, 0)))
        wall_shape.add(*wall)
        castle_walls.add(wall_shape)

    castle_walls_shape = Node(transform=scale(2,2,2))
    castle_walls_shape.add(castle_walls)

    castle_inside = load_textured_illuminated("resources/castle/castle.fbx", shader, tex_file="resources/castle/Texture/castle.jpg")
    castle_inside_shape = Node(transform=translate(25, 5, -40)@ scale(.5,.5,.5)@ rotate(angle=-90, axis=(1, 0, 0)))
    castle_inside_shape.add(*castle_inside)

    castle.add(castle_walls_shape)
    castle.add(castle_inside_shape)

    viewer.add(castle)
    floor = Node(transform= translate(-64, -3, 1.5) @ scale(2.15, 1, 2.5))
    floor.add(*load_textured_illuminated("our_creations/castle_floor/castle_floor.obj", shader, "our_creations/castle_floor/castle_floor.png"))
    viewer.add(floor)


def add_skybox(viewer, shader, s):
    sky = Node(transform=scale(s,s,s)*translate(100, 100, 100))
    sky.add(Skybox(shader))
    viewer.add(sky)
