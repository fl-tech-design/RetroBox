#include <iostream>
#define GLEW_STATIC
#include <GL/glew.h>
#define SDL_MAIN_HANDLED

#ifdef _WIN32
#include <SDL.h>
#pragma comment(lib, "SDL2.lib")
#pragma comment(lib, "glew32s.lib")
#pragma comment(lib, "opengl32.lib")
#else
#include <SDL2/SDL.h>
#endif

#include "defines.h"
#include "vertex_buffer.h"
#include "shader.h"

#ifdef __linux__
#include <fstream>
#include <string>

bool isRaspberryPi()
{
    std::ifstream file("/proc/cpuinfo");
    std::string line;
    while (std::getline(file, line))
    {
        if (line.find("Raspberry Pi") != std::string::npos)
        {
            return true;
        }
    }
    return false;
}

std::string getShaderPath(const std::string &shaderType)
{
    if (isRaspberryPi())
    {
        return "shaders_rpi/" + shaderType; // Raspberry Pi spezifischer Pfad
    }
    return "shaders/" + shaderType; // Standardpfad
}
#else
std::string getShaderPath(const std::string &shaderType)
{
    return "shaders/" + shaderType; // Standardpfad für Nicht-Linux-Systeme
}
#endif
int main(int argc, char **argv)
{
    SDL_Window *window;
    SDL_Init(SDL_INIT_EVERYTHING);

    SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_ALPHA_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_BUFFER_SIZE, 32);
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);

    uint32 flags = SDL_WINDOW_OPENGL; // | SDL_WINDOW_FULLSCREEN_DESKTOP;

    window = SDL_CreateWindow("C++ reboxOS", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 480, flags);
    SDL_GLContext glContext = SDL_GL_CreateContext(window);

    GLenum err = glewInit();
    if (err != GLEW_OK)
    {
        std::cout << "Error: " << glewGetErrorString(err) << std::endl;
        std::cin.get();
        return -1;
    }
    std::cout << "OpenGL Version: " << glGetString(GL_VERSION) << std::endl;

    Vertex vertices[] = {
        Vertex{-0.5f, -0.5f, 0.0f,
               1.0f, 0.0f, 0.0f, 1.0f},
        Vertex{-0.5f, 0.5f, 0.0f,
               0.0f, 1.0f, 0.0f, 1.0f},
        Vertex{0.5f, -0.5f, 0.0f,
               0.0f, 0.0f, 1.0f, 1.0f},
        Vertex{0.5f, 0.5f, 0.0f,
               1.0f, 0.0f, 0.0f, 1.0f},
    };
    uint32 numVertices = 4;

    VertexBuffer vertexBuffer(vertices, numVertices);
    vertexBuffer.unbind();

    // Platform-spezifische Shader-Dateipfade holen
    std::string vertexShaderPath = getShaderPath("basic.vs");
    std::string fragmentShaderPath = getShaderPath("basic.fs");

    // Ausgabe der Shader-Pfade
    std::cout << "Vertex Shader Path: " << vertexShaderPath << std::endl;
    std::cout << "Fragment Shader Path: " << fragmentShaderPath << std::endl;

    // Shader laden
    Shader shader(vertexShaderPath.c_str(), fragmentShaderPath.c_str());
    shader.bind();

    uint64 perfCounterFrequency = SDL_GetPerformanceFrequency();
    uint64 lastCounter = SDL_GetPerformanceCounter();
    float32 delta = 0.0f;

    bool close = false;
    while (!close)
    {
        glClearColor(0.05f, 0.05f, 0.05f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        // aktiviert Wireframemode.
        // glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);

        vertexBuffer.bind();
        glDrawArrays(GL_TRIANGLE_STRIP, 0, numVertices);
        vertexBuffer.unbind();

        SDL_GL_SwapWindow(window);

        SDL_Event event;
        while (SDL_PollEvent(&event))
        {
            if (event.type == SDL_QUIT)
            {
                close = true;
            }
        }
        uint64 endCounter = SDL_GetPerformanceCounter();
        uint64 counterElapsed = endCounter - lastCounter;
        delta = ((float32)counterElapsed) / (float32)perfCounterFrequency;
        uint32 FPS = (uint32)((float32)perfCounterFrequency / (float32)counterElapsed);
        // std::cout << "FPS: " << FPS << std::endl;
        lastCounter = endCounter;
    }

    return 0;
}