#version 330 core

out vec4 FragColor;

in vec2 TexCoord;  // Von Vertex-Shader erhalten

uniform sampler2D texture1;  // Textur

void main() {
    FragColor = texture(texture1, TexCoord);  // Texturfarbe an aktueller Koordinate
}
