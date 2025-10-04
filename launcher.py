import pygame
import sys

# Init pygame
pygame.init()
pygame.joystick.init()

# Window setup
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Handheld Launcher Prototype")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HIGHLIGHT = (50, 200, 50)

# Fake game list
games = ["Super Mario", "Legend of Zelda", "Metroid", "Mega Man"]
selected_index = 0

# Try to init controller
if pygame.joystick.get_count() > 0:
    controller = pygame.joystick.Joystick(0)
    controller.init()
    print(f"Controller connected: {controller.get_name()}")
else:
    print("No controller found! Use arrow keys + Enter instead.")

# Font
font = pygame.font.SysFont(None, 48)

def draw_menu():
    screen.fill(BLACK)
    for i, game in enumerate(games):
        color = HIGHLIGHT if i == selected_index else WHITE
        text = font.render(game, True, color)
        screen.blit(text, (100, 100 + i*60))
    pygame.display.flip()

# Main loop
running = True
while running:
    draw_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard fallback
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(games)
            elif event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(games)
            elif event.key == pygame.K_RETURN:
                print(f"Launching {games[selected_index]}...")

        # Controller
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A button on Xbox
                print(f"Launching {games[selected_index]}...")

        if event.type == pygame.JOYHATMOTION:
            # D-pad navigation
            if event.value[1] == 1:  # Up
                selected_index = (selected_index - 1) % len(games)
            elif event.value[1] == -1:  # Down
                selected_index = (selected_index + 1) % len(games)

pygame.quit()
sys.exit()
