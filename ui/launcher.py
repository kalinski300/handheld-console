import pygame
import sys
import os
import subprocess

pygame.init()
pygame.joystick.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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

# Controller init
if pygame.joystick.get_count() > 0:
    controller = pygame.joystick.Joystick(0)
    controller.init()
    print(f"Controller connected: {controller.get_name()}")
else:
    print("No controller found! Use arrow keys + Enter instead.")

font = pygame.font.SysFont(None, 48)


def launch_game(system, romfile):
    rom_path = os.path.join(ROM_ROOT, system.lower(), romfile)

    # --- Dev mode (Laptop) ---
    # Just simulate launching
    print(f"[DEV] Pretending to launch {system}: {rom_path}")
    subprocess.run(["echo", f"Launching {system}: {romfile}"])

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

def draw_menu():
    screen.fill(BLACK)

    # Draw current system at top
    sys_text = font.render(f"System: {current_system}", True, WHITE)
    screen.blit(sys_text, (WIDTH//2 - sys_text.get_width()//2, 20))

    # Draw game list
    for i, game in enumerate(games):
        color = HIGHLIGHT if i == selected_index else WHITE
        text = font.render(game, True, color)
        screen.blit(text, (100, 100 + i*60))

    pygame.display.flip()

running = True
while running:
    draw_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(games)
            elif event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(games)
            elif event.key == pygame.K_RETURN:
                print(f"Launching {current_system}: {games[selected_index]}")
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

pygame.quit()
sys.exit()
