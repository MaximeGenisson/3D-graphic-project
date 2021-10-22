#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
This module demonstrates the functionality of PyAssimp.
"""

import assimpcy
import logging
logging.basicConfig(level=logging.INFO)


def print_node(node, indent='  '):
    print(indent + 'NODE', node.mName[2:-1])
    print(indent + '  transform: ' + str(node.mTransformation.tolist()))
    if node.mMeshes:
        print(indent + '  meshes: ' + str([m+1 for m in node.mMeshes]))
    for child in node.mChildren:
        print_node(child, indent=indent + '  ')


def keys(key):
    return dict(((k.mTime, list(k.mValue)) for k in key[:2]))


def main(args):
    pp = assimpcy.aiPostProcessSteps
    flags = pp.aiProcess_JoinIdenticalVertices | pp.aiProcess_FlipUVs
    flags |= pp.aiProcess_Triangulate | pp.aiProcess_GenSmoothNormals
    for f in args.files:
        scene = assimpcy.aiImportFile(f, flags)

        # the model we load
        print("MODEL:", f)
        print()

        # write some statistics
        print("SCENE:")
        print("  meshes:", scene.mNumMeshes)
        print("  materials:", scene.mNumMaterials)
        print("  textures:", scene.mNumTextures)
        print("  animations:", scene.mNumAnimations)
        print("  lights:", scene.mNumLights)
        print("  cameras:", scene.mNumCameras)

        print()
        print("MESHES:")
        for index, mesh in enumerate(scene.mMeshes):
            print("  MESH", index+1)
            print("    material:", mesh.mMaterialIndex+1)
            print("    vertices:", len(mesh.mVertices))
            print("    first:", [list(v) for v in mesh.mVertices[:3]], '...')
            print("    normals:", len(mesh.mNormals))
            print("    first:", [list(n) for n in mesh.mNormals[:3]], '...')
            print("    colors:", len(mesh.mColors))
            for i, tex in enumerate(mesh.mTextureCoords):
                if tex is not None:
                    print("    texture-coords "+str(i)+", first:",
                          [list(t) for t in tex[:3]], '...')

            print("    uv-component-count:", mesh.mNumUVComponents)
            print("    faces:", len(mesh.mFaces), "first:",
                  [list(f) for f in mesh.mFaces[:3]], '...')
            print("    bones:", len(mesh.mBones), "first:",
                  [b.mName[2:-1] for b in mesh.mBones[:3]])
        print()

        print("MATERIALS:")
        for index, material in enumerate(scene.mMaterials):
            print("  MATERIAL " + str(index+1))
            for key, value in material.properties.items():
                print("    %s: %s" % (key, value))
        print()

        print("ANIMATIONS:")
        for index, anim in enumerate(scene.mAnimations):
            print("  ANIMATION", index+1, ": ", anim.mName[2:-1])
            print("    duration:", anim.mDuration)
            print("    tickspersecond:", anim.mTicksPerSecond)
            print("    nummeshchannels:", len(anim.mChannels))
            for idx, chan in enumerate(anim.mChannels):
                print("    CHANNEL", idx, chan.mNodeName[2:-1])
                lenpos = len(chan.mPositionKeys)
                lenrot = len(chan.mRotationKeys)
                lenscl = len(chan.mScalingKeys)
                print("      pos keys", lenpos, keys(chan.mPositionKeys), '...')
                print("      rot keys", lenrot, keys(chan.mRotationKeys), '...')
                print("      scl keys", lenscl, keys(chan.mScalingKeys), '...')

        print()

        if scene.mNumTextures:
            print("TEXTURES:")
            for index, texture in enumerate(scene.mTextures):
                 print("  TEXTURE", index+1)
                 print("    width:", texture.mWidth)
                 print("    height:", texture.mHeight)
                 print("    hint:", texture.AchFormatHint)
                 print("    data (size):", texture.mWidth*texture.mHeight)
            print()

        print("NODES:")
        print_node(scene.mRootNode)


if __name__ == "__main__":
    import argparse  # backport < 2.7
    parser = argparse.ArgumentParser(
        description='Assimp dump for a set of 3d objects.')
    parser.add_argument('files', metavar='3d_file', type=str, nargs='+',
                        help='a set of 3d files to analyze')
    args = parser.parse_args()
    main(args)
