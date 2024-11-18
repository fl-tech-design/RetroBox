#version 300 es

precision mediump float;  // Bei ES muss die Präzision für Fließkommawerte festgelegt werden

in vec3 a_position;  // Eingabekoordinaten für die Position
in vec4 a_color;     // Eingabefarbe

out vec4 v_color;    // Ausgabefarbe für den Fragment-Shader

void main()
{
    gl_Position = vec4(a_position, 1.0);  // Berechnung der Position
    v_color = a_color;  // Übergeben der Farbe an den Fragment-Shader
}
