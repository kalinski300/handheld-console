import pygame
import sys
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

pygame.init()
pygame.joystick.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
font = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
pygame.display.set_caption("Handheld Launcher Prototype")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HIGHLIGHT = (50, 200, 50)

# Supported systems and file extensions
SYSTEMS = {
    "NES": ".nes",
    "SNES": ".sfc",
    "GBA": ".gba"
}

ROM_ROOT = os.path.join(os.path.dirname(__file__), "..", "roms")

def scan_roms(system_name, ext):
    path = os.path.join(ROM_ROOT, system_name.lower())
    if not os.path.exists(path):
        return []
    return [f for f in os.listdir(path) if f.endswith(ext)] or ["No games found"]

system_names = list(SYSTEMS.keys())
system_index = 0
current_system = system_names[system_index]
games = scan_roms(current_system, SYSTEMS[current_system])
selected_index = 0


class ROMHandler(FileSystemEventHandler):
    def on_created(self, event):
        global games, selected_index, current_system
        if event.is_directory:
            return

        _, ext = os.path.splitext(event.src_path)
        ext = ext.lower()

        # Map extensions to systems
        EXT_TO_SYSTEM = {
            ".nes": "NES",
            ".sfc": "SNES",
            ".gba": "GBA"
        }

        if ext in EXT_TO_SYSTEM:
            system = EXT_TO_SYSTEM[ext]
            dest_dir = os.path.join(ROM_ROOT, system.lower())
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, os.path.basename(event.src_path))

            try:
                # Move the file into the proper system directory
                os.replace(event.src_path, dest_path)
                print(f"Moved {event.src_path} → {dest_path}")

                # Refresh games if we’re currently on this system
                if system == current_system:
                    games = scan_roms(current_system, SYSTEMS[current_system])
                    selected_index = 0
            except Exception as e:
                print(f"Failed to move {event.src_path}: {e}")
        else:
            print(f"Ignoring unsupported file: {event.src_path}")

DOWNLOADS = os.path.join(os.path.dirname(__file__), "..", "downloads")

def start_watcher():
    event_handler = ROMHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS, recursive=False)
    observer.start()
    print("Watching downloads/ for new ROMs...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Start watcher in background
threading.Thread(target=start_watcher, daemon=True).start()

# Controller init
if pygame.joystick.get_count() > 0:
    controller = pygame.joystick.Joystick(0)
    controller.init()
    print(f"Controller connected: {controller.get_name()}")
else:
    print("No controller found! Use arrow keys + Enter instead.")

font = pygame.font.SysFont(None, 48)

running_game = None

def launch_game(system, romfile):
    global running_game
    rom_path = os.path.join(ROM_ROOT, system.lower(), romfile)

    # --- Dev mode (Laptop) ---
    # Just simulate launching
    print(f"[DEV] Pretending to launch {system}: {rom_path}")
    running_game = subprocess.Popen(["sleep", "9999"])  # fake long process

    # --- Real mode (Pi) ---
    # Uncomment and adjust paths when on Pi:
    # cores = {
    #     "NES": "/usr/lib/libretro/nestopia_libretro.so",
    #     "SNES": "/usr/lib/libretro/snes9x_libretro.so",
    #     "GBA": "/usr/lib/libretro/mgba_libretro.so"
    # }
    # core = cores.get(system)
    # if core:
    #     subprocess.run(["retroarch", "-L", core, rom_path])

def quit_game():
    global running_game
    if running_game and running_game.poll() is None:  # still running
        print("[DEV] Closing game...")
        running_game.terminate()
        running_game = None

def draw_menu():
    title_text = font.render(f"{current_system} Library", True, (0, 200, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 40))

    y = 120
    for idx, game in enumerate(games):
        color = (255, 255, 0) if idx == selected_index else (255, 255, 255)
        text = font.render(game, True, color)
        screen.blit(text, (100, y))
        y += 50

clock = pygame.time.Clock()
running = True

while running:
    # --- Input handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(games)
            elif event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(games)
            elif event.key == pygame.K_RETURN:
                print(f"Launching {current_system}: {games[selected_index]}")
                launch_game(current_system, games[selected_index])
            elif event.key == pygame.K_RIGHT:
                system_index = (system_index + 1) % len(system_names)
                current_system = system_names[system_index]
                games = scan_roms(current_system, SYSTEMS[current_system])
                selected_index = 0
            elif event.key == pygame.K_LEFT:
                system_index = (system_index - 1) % len(system_names)
                current_system = system_names[system_index]
                games = scan_roms(current_system, SYSTEMS[current_system])
                selected_index = 0
            elif event.key == pygame.K_ESCAPE:
                quit_game()

        # Controller buttons
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A button
                launch_game(current_system, games[selected_index])

        # Controller D-pad
        if event.type == pygame.JOYHATMOTION:
            if event.value[1] == 1:  # Up
                selected_index = (selected_index - 1) % len(games)
            elif event.value[1] == -1:  # Down
                selected_index = (selected_index + 1) % len(games)
            elif event.value[0] == 1:  # Right
                system_index = (system_index + 1) % len(system_names)
                current_system = system_names[system_index]
                games = scan_roms(current_system, SYSTEMS[current_system])
                selected_index = 0
            elif event.value[0] == -1:  # Left
                system_index = (system_index - 1) % len(system_names)
                current_system = system_names[system_index]
                games = scan_roms(current_system, SYSTEMS[current_system])
                selected_index = 0

        # Controller quit combo: Start + Select
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7:  # Start button
                if controller.get_button(6):  # Select held
                    quit_game()
            if event.button == 6:  # Select button
                if controller.get_button(7):  # Start held
                    quit_game()

    # --- Drawing ---
    screen.fill((0, 0, 0))  # Clear screen each frame
    draw_menu()             # Your menu-drawing function
    pygame.display.flip()   # Update display

    clock.tick(60)          # Cap at 60 FPS
pygame.quit()
sys.exit()
