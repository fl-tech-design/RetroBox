#version 300 es

precision mediump float;  // Präzision für Fließkommawerte festlegen

// Eingabefarbe vom Vertex-Shader
in vec4 v_color;

// Ausgabefarbe des Fragment-Shaders
out vec4 f_color;

// Uniform-Variable für eine globale Farbe
uniform vec4 u_color;

void main()
{
    // Verwende die Uniform-Farbe u_color als Ausgabe
    f_color = u_color;
}
