#version 330 core

layout(location = 0) in vec3 aPos;       // Vertex-Position
layout(location = 1) in vec2 aTexCoord;  // Texturkoordinaten

out vec2 TexCoord;  // Weiterleitung an den Fragment-Shader

uniform mat4 model;       // Modellmatrix
uniform mat4 view;        // Kameramatrix
uniform mat4 projection;  // Projektionsmatrix

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);  // Transformierte Position
    TexCoord = aTexCoord;  // Texturkoordinaten weitergeben
}
