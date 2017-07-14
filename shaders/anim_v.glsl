#version 140

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;
in vec3 p3d_Normal;
in vec3 p3d_Tangent;
in vec3 p3d_Binormal;

in vec4 joint;
in vec4 weight;

uniform mat4 p3d_ViewProjectionMatrix;
uniform mat4 p3d_ViewMatrix;
uniform sampler2D anim_texture;

uniform mat4 matrix_data[NUM_ACTORS];
uniform vec4 anim_data[NUM_ACTORS];

uniform float osg_FrameTime;

out vec2 texcoord;
out vec3 T;
out vec3 B;
out vec3 N;
out vec3 vpos;

mat4 get_mat_from_tex( int current_frame, int joint_index)
    {
    return mat4(
                texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame)*4 ),0),
                texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame)*4-1),0),
                texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame)*4-2),0),
                texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame)*4-3),0)
                );
    }

mat4 get_blend_mat(int current_frame, int joint_index, float blend)
    {
    return mat4(
                mix(
                    texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame)*4 ),0),
                    texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame+1)*4 ),0),
                    blend
                    ),
                mix(
                    texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame)*4 -1),0),
                    texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame+1)*4 -1),0),
                    blend
                    ),
                mix(
                    texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame)*4 -2 ),0),
                    texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame+1)*4 -2),0),
                    blend
                    ),
                mix(
                    texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame)*4 -3),0),
                    texelFetch(anim_texture, ivec2(joint_index, 1023-(current_frame+1)*4 -3),0),
                    blend
                    )
                );
    }


void main()
    {
    //float start_frame=anim_data[gl_InstanceID].x;
    //float num_frame=anim_data[gl_InstanceID].y;
    //float fps=anim_data[gl_InstanceID].z;
    //float offset_time=anim_data[gl_InstanceID].w;
    //float current_frame=start_frame+mod(floor((osg_FrameTime+offset_time)*fps),num_frame);
    int current_frame=int(anim_data[gl_InstanceID].x+mod(floor((osg_FrameTime+anim_data[gl_InstanceID].w)*anim_data[gl_InstanceID].z),anim_data[gl_InstanceID].y));
    ivec4 joint_id=ivec4(joint);

    #ifdef FRAME_BLEND
    //float blend = fract(mod((osg_FrameTime+offset_time)*fps,num_frame));
    float blend = fract(mod((osg_FrameTime+anim_data[gl_InstanceID].w)*anim_data[gl_InstanceID].z,anim_data[gl_InstanceID].y));
    mat4 anim_matrix = get_blend_mat(current_frame, joint_id.x, blend)*weight.x
                      +get_blend_mat(current_frame, joint_id.y, blend)*weight.y
                      +get_blend_mat(current_frame, joint_id.z, blend)*weight.z
                      +get_blend_mat(current_frame, joint_id.w, blend)*weight.w;
    #endif
    #ifndef FRAME_BLEND
    mat4 anim_matrix = get_mat_from_tex(current_frame, joint_id.x)*weight.x
                      +get_mat_from_tex(current_frame, joint_id.y)*weight.y
                      +get_mat_from_tex(current_frame, joint_id.z)*weight.z
                      +get_mat_from_tex(current_frame, joint_id.w)*weight.w;
    #endif
    vec4 v=anim_matrix *p3d_Vertex;
    v=matrix_data[gl_InstanceID] *v;
    gl_Position = p3d_ViewProjectionMatrix * v;

    texcoord = p3d_MultiTexCoord0;

    mat3 normal_matrix=mat3(matrix_data[gl_InstanceID])*mat3(anim_matrix)*mat3(p3d_ViewMatrix);
    T=normal_matrix * p3d_Tangent;
    B=normal_matrix * p3d_Binormal;
    N=normal_matrix * p3d_Normal;

    vpos=vec3(p3d_ViewMatrix * v);
    }

