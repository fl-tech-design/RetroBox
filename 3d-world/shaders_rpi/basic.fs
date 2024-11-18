#version 300 es

precision mediump float;  // Präzision für Fließkommawerte festlegen

in vec4 v_color;    // Eingabefarbe vom Vertex-Shader

out vec4 f_color;   // Ausgabefarbe des Fragment-Shaders, bleibt bei f_color

void main()
{
    f_color = v_color;  // Die Farbe vom Vertex-Shader direkt an den Output weitergeben
}
