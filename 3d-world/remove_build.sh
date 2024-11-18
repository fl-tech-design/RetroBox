#!/bin/bash

# Navigiere in den OS-Ordner
cd "$(dirname "$0")"

# Lösche den bestehenden Build-Ordner, falls vorhanden
if [ -d "build" ]; then
    echo "Lösche bestehenden Build-Ordner..."
    rm -rf build
fi

# Erstelle den Build-Ordner neu und navigiere hinein
mkdir build && cd build

# Führe cmake und make aus
echo "Führe cmake und make aus..."
cmake .. && make

# Erfolgsmeldung
if [ $? -eq 0 ]; then
    echo "Build erfolgreich abgeschlossen."
else
    echo "Fehler beim Build-Prozess."
fi
