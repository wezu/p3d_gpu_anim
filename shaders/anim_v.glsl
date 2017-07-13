#version 140

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

in vec4 joint;
in vec4 weight;

uniform mat4 p3d_ViewProjectionMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D anim_texture;

uniform mat4 matrix_data[NUM_ACTORS];
uniform vec4 anim_data[NUM_ACTORS];

uniform float osg_FrameTime;

out vec4 color;
out vec2 texcoord;

mat4 get_mat_from_tex( float current_frame, float joint_index)
    {
    vec4 v0 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame)*4 ),0);
    vec4 v1 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame)*4-1),0);
    vec4 v2 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame)*4-2),0);
    vec4 v3 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame)*4-3),0);

    return mat4(v0, v1, v2, v3);
    }

mat4 get_blend_mat(float current_frame, float joint_index, float blend)
    {
    vec4 v0 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame)*4 ),0);
    vec4 v1 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame)*4-1),0);
    vec4 v2 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame)*4-2),0);
    vec4 v3 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame)*4-3),0);

    vec4 v0_1 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame+1)*4 ),0);
    vec4 v1_1 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame+1)*4-1),0);
    vec4 v2_1 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame+1)*4-2),0);
    vec4 v3_1 = texelFetch(anim_texture, ivec2(int(joint_index), 1023-int(current_frame+1)*4-3),0);

    v0=mix(v0, v0_1, blend);
    v1=mix(v1, v1_1, blend);
    v2=mix(v2, v2_1, blend);
    v3=mix(v3, v3_1, blend);

    return mat4(v0, v1, v2, v3);
    }


void main()
    {
    float start_frame=anim_data[gl_InstanceID].x;
    float num_frame=anim_data[gl_InstanceID].y;
    float fps=anim_data[gl_InstanceID].z;
    float offset_time=anim_data[gl_InstanceID].w;

    float current_frame=start_frame+mod(floor((osg_FrameTime+offset_time)*fps),num_frame);

    #ifdef FRAME_BLEND
    float blend = fract(mod((osg_FrameTime+offset_time)*fps,num_frame));
    mat4 anim_matrix = get_blend_mat(current_frame, joint.x, blend)*weight.x
                 +get_blend_mat(current_frame, joint.y, blend)*weight.y
                 +get_blend_mat(current_frame, joint.z, blend)*weight.z
                 +get_blend_mat(current_frame, joint.w, blend)*weight.w;
    #endif
    #ifndef FRAME_BLEND
    mat4 anim_matrix = get_mat_from_tex(current_frame, joint.x)*weight.x
                     +get_mat_from_tex(current_frame, joint.y)*weight.y
                     +get_mat_from_tex(current_frame, joint.z)*weight.z
                     +get_mat_from_tex(current_frame, joint.w)*weight.w;
    #endif
    vec4 v=anim_matrix *p3d_Vertex;
    v=matrix_data[gl_InstanceID] *v;

    gl_Position = p3d_ViewProjectionMatrix * v;

    color = p3d_Color;

    texcoord = p3d_MultiTexCoord0;
    }

