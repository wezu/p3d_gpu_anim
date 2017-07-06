#version 130

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

in vec4 joint;
in vec4 weight;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D animation;
uniform float frame;

out vec4 color;
out vec2 texcoord;

mat4 get_mat_from_tex( float frame, float joint_index)
    {
    vec4 v0 = texelFetch(animation, ivec2(int(joint_index), int(frame)*4 ),0);
    vec4 v1 = texelFetch(animation, ivec2(int(joint_index), int(frame)*4+1),0);
    vec4 v2 = texelFetch(animation, ivec2(int(joint_index), int(frame)*4+2),0);
    vec4 v3 = texelFetch(animation, ivec2(int(joint_index), int(frame)*4+3),0);

    return mat4(v0, v1, v2, v3);
    }

void main()
    {

    mat4 matrix = get_mat_from_tex(frame, joint.x)*weight.x
                 +get_mat_from_tex(frame, joint.y)*weight.y
                 +get_mat_from_tex(frame, joint.z)*weight.z
                 +get_mat_from_tex(frame, joint.w)*weight.w;


    gl_Position = p3d_ModelViewProjectionMatrix * matrix * p3d_Vertex;
    //gl_Position = p3d_ModelViewProjectionMatrix *  p3d_Vertex;
    color = p3d_Color;
    texcoord = p3d_MultiTexCoord0;
    }

