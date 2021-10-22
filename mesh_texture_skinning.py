import os
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import numpy as np                  # all matrix manipulations & OpenGL args
import assimpcy                     # 3D resource loader

from core import Mesh
from mesh_texture import Texture
from mesh_skinning import SkinningControlNode, MAX_BONES, MAX_VERTEX_BONES


class SkinnedAndTexturedMesh(Mesh):
    """class of skinned mesh nodes in scene graph """
    def __init__(self, bone_nodes, bone_offsets, texture, shader, attributes, index=None):
        super().__init__(shader, attributes, index)
        # PARTIE TEXTURE :
        self.texture = texture
        self.loc['diffuse_map'] = GL.glGetUniformLocation(shader.glid, 'diffuse_map')
        # PARTIE SKIN :
        self.bone_nodes = bone_nodes
        self.bone_offsets = np.array(bone_offsets, np.float32)
        self.loc['bone_matrix'] = GL.glGetUniformLocation(self.shader.glid, 'bone_matrix')

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        """ skinning object draw method """
        GL.glUseProgram(self.shader.glid)

        # PARTIE TEXTURE :
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(self.loc['diffuse_map'], 0)

        # PARTIE SKIN :
        world_transforms = [node.world_transform for node in self.bone_nodes]
        bone_matrix = world_transforms @ self.bone_offsets
        GL.glUniformMatrix4fv(self.loc['bone_matrix'], len(self.bone_nodes), True, bone_matrix)

        # super().draw(projection, view, model) # Pas de primitives pr Skin
        super().draw(projection, view, model, primitives)


def load_textured_skinned(file, shader, tex_file=None, loop_duration=0.0):
    """load resources from file using assimp, return node hierarchy """

    ################## PARTIE COMMUNE (aux flags près, combinés) ##############
    # On teste si le file peut bien être chargé
    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_Triangulate | pp.aiProcess_GenSmoothNormals | pp.aiProcess_FlipUVs # changé
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('ERROR loading', file + ': ', exception.args[0].decode())
        return []
    ##########################################################################

    ###################### PARTIE SKIN ######################################

    def conv(assimp_keys, ticks_per_second):
        """ Conversion from assimp key struct to our dict representation """
        return {key.mTime / ticks_per_second: key.mValue for key in assimp_keys}

    # load first animation in scene file (could be a loop over all animations)
    transform_keyframes = {}
    if scene.mAnimations:
        anim = scene.mAnimations[0]
        for channel in anim.mChannels:
            # for each animation bone, store TRS dict with {times: transforms}
            transform_keyframes[channel.mNodeName] = (
                conv(channel.mPositionKeys, anim.mTicksPerSecond),
                conv(channel.mRotationKeys, anim.mTicksPerSecond),
                conv(channel.mScalingKeys, anim.mTicksPerSecond)
            )
    # ---- prepare scene graph nodes
    # create SkinningControlNode for each assimp node.
    # node creation needs to happen first as SkinnedMeshes store an array of
    # these nodes that represent their bone transforms
    nodes = {}                                       # nodes name -> node lookup
    nodes_per_mesh_id = [[] for _ in scene.mMeshes]  # nodes holding a mesh_id

    def make_nodes(assimp_node):
        """ Recursively builds nodes for our graph, matching assimp nodes """
        trs_keyframes = transform_keyframes.get(assimp_node.mName, (None,))
        skin_node = SkinningControlNode(*trs_keyframes,
                                        transform=assimp_node.mTransformation,
                                        loop_duration=loop_duration)
        nodes[assimp_node.mName] = skin_node
        for mesh_index in assimp_node.mMeshes:
            nodes_per_mesh_id[mesh_index].append(skin_node)
        skin_node.add(*(make_nodes(child) for child in assimp_node.mChildren))
        return skin_node

    root_node = make_nodes(scene.mRootNode)
    ##########################################################################

    ####################### PARTIE TEXTURE ##################################
    # on crée l'objet Texture si les textures peuvent bien être chargées
    path = os.path.dirname(file) if os.path.dirname(file) != '' else './'
    for mat in scene.mMaterials:
        if not tex_file and 'TEXTURE_BASE' in mat.properties:  # texture token
            name = os.path.basename(mat.properties['TEXTURE_BASE'])
            # search texture in file's whole subdir since path often screwed up
            paths = os.walk(path, followlinks=True)
            found = [os.path.join(d, f) for d, _, n in paths for f in n
                     if name.startswith(f) or f.startswith(name)]
            assert found, 'Cannot find texture %s in %s subtree' % (name, path)
            tex_file = found[0]
        if tex_file:
            mat.properties['diffuse_map'] = Texture(tex_file=tex_file)
    ###########################################################################

    ####################### PARTIE COMBINEE ##################################
    # ---- create SkinnedMesh objects
    for mesh_id, mesh in enumerate(scene.mMeshes):
        # PARTIE SKIN :
        # -- skinned mesh: weights given per bone => convert per vertex for GPU
        # first, populate an array with MAX_BONES entries per vertex
        v_bone = np.array([[(0, 0)]*MAX_BONES] * mesh.mNumVertices,
                          dtype=[('weight', 'f4'), ('id', 'u4')])
        for bone_id, bone in enumerate(mesh.mBones[:MAX_BONES]):
            for entry in bone.mWeights:  # weight,id pairs necessary for sorting
                v_bone[entry.mVertexId][bone_id] = (entry.mWeight, bone_id)

        v_bone.sort(order='weight')             # sort rows, high weights last
        v_bone = v_bone[:, -MAX_VERTEX_BONES:]  # limit bone size, keep highest

        # prepare bone lookup array & offset matrix, indexed by bone index (id)
        bone_nodes = [nodes[bone.mName] for bone in mesh.mBones]
        bone_offsets = [bone.mOffsetMatrix for bone in mesh.mBones]

        # PARTIE TEXTURE :
        mat = scene.mMaterials[mesh.mMaterialIndex].properties
        assert mat['diffuse_map'], "Trying to map using a textureless material"

        # PARTIE COMBINEE à proprement parler :
        # initialize skinned mesh and store in assimp mesh for node addition
        attrib = [mesh.mVertices, mesh.mTextureCoords[0], v_bone['id'], v_bone['weight']] # VA DETERMINER LES LAYOUTS DU VERTEX SHADER
        mesh = SkinnedAndTexturedMesh(bone_nodes, bone_offsets, mat['diffuse_map'], shader, attrib, mesh.mFaces)

        for node in nodes_per_mesh_id[mesh_id]:
            node.add(mesh)

    # AFFICHAGE DANS LA CONSOLE
    nb_triangles = sum((mesh.mNumFaces for mesh in scene.mMeshes))
    print('Loaded', file, '\t(%d meshes, %d faces, %d nodes, %d animations)' %
          (scene.mNumMeshes, nb_triangles, len(nodes), scene.mNumAnimations))

    # RETURN
    return [root_node]
    ###########################################################################
