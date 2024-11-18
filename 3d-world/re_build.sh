#!/bin/bash

# Navigiere in den OS-Ordner
cd "$(dirname "$0")"

# Führe cmake und make aus
echo "Programm wird kompiliert..."
g++ -g -std=c++11 main.cpp shader.cpp -o reboxOS -D _DEBUG -lGL -lSDL2 -lGLEW

# Erfolgsmeldung
if [ $? -eq 0 ]; then
    echo "Programm fertig kompiliert."

    # Programm starten
    echo "Programm wird gestartet..."
    ./reboxOS
else
    echo "Fehler beim Kompilieren."
fi
