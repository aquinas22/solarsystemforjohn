# Solar System for John — desktop version

The original Python + PyOpenGL desktop app (`main.py`, `solar_orbit.py`), packaged with PyInstaller via `main.spec`.

    pip install pyopengl glfw pillow numpy pyinstaller
    python main.py
    pyinstaller main.spec   # builds dist/JT_Solar_System.exe

The web version (three.js + Vite) lives at the repository root and is what solarsystemforjohn.com serves.

Imported from the archived `solarpython` repo (commit 6c99533); its prebuilt zips and .exe stay there.
