# Compiler flags
CXXARGS = -g -std=c++11 -D _DEBUG

# Directories
SRC_DIR = .
TOOLS_DIR = tools
LIBS_DIR = libs
SHADERS_DIR = shaders

# Output binaries
BIN_DIR = .

# Targets
all: opengl_tutorial tools/modelexporter

# opengl_tutorial target
opengl_tutorial: $(SRC_DIR)/main.cpp $(SRC_DIR)/shader.cpp
	g++ $(CXXARGS) $(SRC_DIR)/main.cpp $(SRC_DIR)/shader.cpp -o $(BIN_DIR)/opengl_tutorial -lGL -lSDL2 -lGLEW

# modelexporter target
tools/modelexporter: $(TOOLS_DIR)/modelexporter.cpp
	g++ $(CXXARGS) $(TOOLS_DIR)/modelexporter.cpp -o $(BIN_DIR)/tools/modelexporter -lassimp

# Clean up
clean:
	rm -f $(BIN_DIR)/opengl_tutorial $(BIN_DIR)/tools/modelexporter
