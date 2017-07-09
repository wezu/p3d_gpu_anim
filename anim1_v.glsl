#version 130

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

in vec4 joint;
in vec4 weight;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D animation;
uniform vec4 frame;

uniform float osg_FrameTime;

out vec4 color;
out vec2 texcoord;

mat4 get_mat_from_tex( float current_frame, float joint_index)
    {
    vec4 v0 = texelFetch(animation, ivec2(int(joint_index), 1023-int(current_frame)*4 ),0);
    vec4 v1 = texelFetch(animation, ivec2(int(joint_index), 1023-int(current_frame)*4-1),0);
    vec4 v2 = texelFetch(animation, ivec2(int(joint_index), 1023-int(current_frame)*4-2),0);
    vec4 v3 = texelFetch(animation, ivec2(int(joint_index), 1023-int(current_frame)*4-3),0);

    return mat4(v0, v1, v2, v3);
    }

void main()
    {
    float fps=frame.x;
    float start_frame=frame.y;
    float num_frame=frame.z;
    float offset_frame=frame.w;

    float current_frame=start_frame+mod(floor(osg_FrameTime*fps),num_frame);


    mat4 matrix = get_mat_from_tex(current_frame, joint.x)*weight.x
                 +get_mat_from_tex(current_frame, joint.y)*weight.y
                 +get_mat_from_tex(current_frame, joint.z)*weight.z
                 +get_mat_from_tex(current_frame, joint.w)*weight.w;

    //no per instanc matrix yet, just offset to the right
    vec4 v = matrix *p3d_Vertex;
    v += vec4(gl_InstanceID*25.0,0.0, 0.0, 0.0);

    gl_Position = p3d_ModelViewProjectionMatrix * v;
    //gl_Position = p3d_ModelViewProjectionMatrix *  p3d_Vertex;
    color = p3d_Color;
    //color = vec4(current_frame/35.0, 0.0, 0.0, 1.0);
    texcoord = p3d_MultiTexCoord0;
    }

