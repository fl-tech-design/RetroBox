#version 300 es
precision highp float;  // Setze Präzision für OpenGL ES

in vec4 fragColor;  // Eingabe aus dem Vertex-Shader (falls benötigt)
out vec4 color;  // Ausgabe der Farbe

void main()
{
    color = vec4(1.0, 1.0, 0.0, 1.0);  // Gelb
}
