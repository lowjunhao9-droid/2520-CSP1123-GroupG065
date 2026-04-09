import pygame, sys
pygame.init()

canvas = pygame.display.set_mode((630,480))
pygame.display.set_caption("Hello World")
canvas.fill((0,0,0))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()