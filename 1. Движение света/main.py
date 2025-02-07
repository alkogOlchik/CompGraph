import pygame
from pygame.locals import *
import Light

pygame.init()

pygame.display.set_caption("Light Render")
display = pygame.display.set_mode((500, 500), pygame.DOUBLEBUF)
clock, fps = pygame.time.Clock(), 240


light = Light.Light(500, Light.pixel_shader(500, (255, 255, 255), 1, False)) # White light

squares = [
    pygame.Rect(50, 50, 120, 120),
    pygame.Rect(300, 200, 150, 150),
    pygame.Rect(180, 350, 100, 100)
]


x, y = 250, 250
speed_x, speed_y = 1, 1

time = 0
while True:
    clock.tick(fps)
    display.fill((255, 255, 255))

    hue = (time % 360)  # Ensure hue stays in range [0, 360]
    color = pygame.Color(0)
    color.hsva = (hue, 100, 100)
    light = Light.Light(500, Light.pixel_shader(500, color[:3], 1, False))

    lights_display = pygame.Surface((display.get_size()))

    lights_display.blit(Light.global_light(display.get_size(), 25), (0, 0))

    light.main(squares, lights_display, x, y)  # Moving white light

    display.blit(lights_display, (0, 0), special_flags=BLEND_RGBA_MULT)

    for square in squares:
        pygame.draw.rect(display, (255, 255, 255), square)

    x += speed_x
    y += speed_y

    if x >= 450 or x <= 50:
        speed_x *= -1
    if y >= 450 or y <= 50:
        speed_y *= -1

    light_rect = pygame.Rect(x - 5, y - 5, 10, 10)  
    for square in squares:
        if light_rect.colliderect(square):
            if abs((light_rect.right - square.left)) < 10 or abs((light_rect.left - square.right)) < 10:
                speed_x *= -1
            if abs((light_rect.bottom - square.top)) < 10 or abs((light_rect.top - square.bottom)) < 10:
                speed_y *= -1
    time+=1

    for event in pygame.event.get():
        if event.type == QUIT: pygame.quit()

    pygame.display.set_caption(str(clock.get_fps()))
    pygame.display.update()
