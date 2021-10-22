#version 330 core

uniform mat4 model, view, projection;
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texture_coord;
layout(location = 2) in vec4 bone_ids;
layout(location = 3) in vec4 bone_weights;
layout(location = 4) in vec3 normal;

out vec2 frag_tex_coords;


const int MAX_VERTEX_BONES=4, MAX_BONES=128;
uniform mat4 bone_matrix[MAX_BONES];

// position and normal for the fragment shader, in WORLD coordinates
out vec3 w_position, w_normal;

void main() {

    mat4 skin_matrix;
    if (bone_weights == vec4(0))
        skin_matrix = model;  // pas de poids de skinning: calcul de transformation à partir de model
    else {
        skin_matrix= mat4(0);
        // calcul de transformation à partir des matrices bone_matrix :
        for (int j = 0; j < 4; j++) {
            skin_matrix += bone_weights[j] * bone_matrix[int(bone_ids[j])];
        }
    }

    vec4 w_position4 = skin_matrix * vec4(position, 1.0);
    gl_Position = projection * view * w_position4;

    frag_tex_coords = texture_coord;

      // fragment position in world coordinates
    w_position = w_position4.xyz / w_position4.w;  // dehomogenize

    // fragment normal in world coordinates
    mat3 nit_matrix = transpose(inverse(mat3(model)));
    w_normal = normalize(nit_matrix * normal);

}
