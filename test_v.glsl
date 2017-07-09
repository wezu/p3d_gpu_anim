#version 130

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D pfm;

out vec4 color;
out vec2 texcoord;


void main()
    {

   // vec4 v = p3d_Vertex;
    mat4 matrix = mat4( texelFetch(pfm, ivec2(0,7), 0),
                        texelFetch(pfm, ivec2(0,6), 0),
                        texelFetch(pfm, ivec2(0,5), 0),
                        texelFetch(pfm, ivec2(0,4), 0)
                        );

    gl_Position = p3d_ModelViewProjectionMatrix * matrix * p3d_Vertex;
    //gl_Position = p3d_ModelViewProjectionMatrix *  v;
    color = p3d_Color;
    texcoord = p3d_MultiTexCoord0;
    }

