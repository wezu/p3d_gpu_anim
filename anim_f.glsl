#version 130
in vec4 color;
in vec2 texcoord;

uniform sampler2D p3d_Texture0;

void main() {
  gl_FragColor = color * texture(p3d_Texture0, texcoord);
}
