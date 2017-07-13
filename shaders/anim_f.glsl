#version 140
in vec4 color;
in vec2 texcoord;

uniform sampler2D p3d_Texture0;

void main() {

  gl_FragData[0] = color * texture(p3d_Texture0, texcoord);
}
