import random
import sys
import pygame
from pygame.locals import *

FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_images = {}
GAME_SOUNDS = {}
BACKGROUND = 'assets/images/background.png'
PIPE = 'assets/images/pipe.png'


def welcomeScreen():
    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_images['player'].get_height()) / 2)
    messagex = int((SCREENWIDTH - GAME_images['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                chooseBirdScreen()  
                return
            else:
                SCREEN.blit(GAME_images['background'], (0, 0))
                SCREEN.blit(GAME_images['player'], (playerx, playery))
                SCREEN.blit(GAME_images['message'], (messagex, messagey))
                SCREEN.blit(GAME_images['base'], (basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def chooseBirdScreen():
    selected_bird = None  # Track which bird is selected
    font = pygame.font.SysFont('Arial', 30)

    # Positions for the birds
    red_bird_rect = pygame.Rect(SCREENWIDTH // 4, SCREENHEIGHT // 3, GAME_images['red'].get_width(), GAME_images['red'].get_height())
    blue_bird_rect = pygame.Rect(SCREENWIDTH // 4 + 60, SCREENHEIGHT // 3, GAME_images['blue'].get_width(), GAME_images['blue'].get_height())
    yellow_bird_rect = pygame.Rect(SCREENWIDTH // 4 + 120, SCREENHEIGHT // 3, GAME_images['yellow'].get_width(), GAME_images['yellow'].get_height())

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # Mouse click detection for bird select
            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if red_bird_rect.collidepoint(mouse_x, mouse_y):
                    selected_bird = 'red'
                elif blue_bird_rect.collidepoint(mouse_x, mouse_y):
                    selected_bird = 'blue'
                elif yellow_bird_rect.collidepoint(mouse_x, mouse_y):
                    selected_bird = 'yellow'

            # Start the game when Enter is pressed after selecting a bird
            if event.type == KEYDOWN and event.key == K_RETURN and selected_bird:
                GAME_images['player'] = GAME_images[selected_bird]  
                countdown()
                return  

        SCREEN.blit(GAME_images['background'], (0, 0))
        title = font.render("Choose your Bird", True, (255, 255, 255))
        SCREEN.blit(title, (SCREENWIDTH // 5.2, SCREENHEIGHT // 6))

        SCREEN.blit(GAME_images['red'], (SCREENWIDTH // 4, SCREENHEIGHT // 3))
        SCREEN.blit(GAME_images['blue'], (SCREENWIDTH // 4 + 60, SCREENHEIGHT // 3))  
        SCREEN.blit(GAME_images['yellow'], (SCREENWIDTH // 4 + 120, SCREENHEIGHT // 3)) 

        # Highlight selected bird
        if selected_bird == 'red':
            pygame.draw.rect(SCREEN, (235, 38, 38), red_bird_rect, 5)  
        elif selected_bird == 'blue':
            pygame.draw.rect(SCREEN, (53, 195, 246), blue_bird_rect, 5)  
        elif selected_bird == 'yellow':
            pygame.draw.rect(SCREEN, (255, 206, 68), yellow_bird_rect, 5) 

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def countdown():
    font = pygame.font.SysFont('Arial', 50)
    for i in range(3, 0, -1):
        SCREEN.fill((114, 199, 255))  
        countdown_text = font.render(str(i), True, (255, 255, 255))
        SCREEN.blit(countdown_text, (SCREENWIDTH // 2 - 10, SCREENHEIGHT // 2 - 50)) 
        pygame.display.update()
        pygame.time.wait(1000) 


def mainGame():
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)
    basex = 0

    # Create 2 pipes
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    # List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8  # speed while flapping
    playerFlapped = False  # Only true when the bird is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        # This function return true if the player crashes
        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            GAME_images['gameover'] = pygame.image.load('assets/images/gameover.png').convert_alpha()  
            SCREEN.blit(GAME_images['gameover'], (SCREENWIDTH // 5.2, SCREENHEIGHT // 2.5)) 
            pygame.display.update()
            pygame.time.wait(2000)  
            return

        # Check for score
        playerMidPos = playerx + GAME_images['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_images['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"Your score is {score}")
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_images['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # Moving Pipes
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Adding Pipes
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # Removing Pipes
        if upperPipes[0]['x'] < -GAME_images['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Blitting the images
        SCREEN.blit(GAME_images['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_images['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_images['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_images['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_images['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_images['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_images['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_images['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipeHeight = GAME_images['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_images['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_images['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_images['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False


def getRandomPipe():
    pipeHeight = GAME_images['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_images['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},  # Upper Pipe
        {'x': pipeX, 'y': y2}  # Lower Pipe
    ]
    return pipe


if __name__ == "__main__":
    # This will be the main point from where game will start
    pygame.init()  # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird')
    GAME_images['numbers'] = (
        pygame.image.load('assets/images/0.png').convert_alpha(),
        pygame.image.load('assets/images/1.png').convert_alpha(),
        pygame.image.load('assets/images/2.png').convert_alpha(),
        pygame.image.load('assets/images/3.png').convert_alpha(),
        pygame.image.load('assets/images/4.png').convert_alpha(),
        pygame.image.load('assets/images/5.png').convert_alpha(),
        pygame.image.load('assets/images/6.png').convert_alpha(),
        pygame.image.load('assets/images/7.png').convert_alpha(),
        pygame.image.load('assets/images/8.png').convert_alpha(),
        pygame.image.load('assets/images/9.png').convert_alpha(),
    )

    GAME_images['message'] = pygame.image.load('assets/images/message.png').convert_alpha()
    GAME_images['base'] = pygame.image.load('assets/images/base.png').convert_alpha()
    GAME_images['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha()
    )

    # Load the bird images
    GAME_images['red'] = pygame.image.load('assets/images/bird_red.png').convert_alpha()
    GAME_images['blue'] = pygame.image.load('assets/images/bird_blue.png').convert_alpha()
    GAME_images['yellow'] = pygame.image.load('assets/images/bird_yellow.png').convert_alpha()

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('assets/sound/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('assets/sound/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('assets/sound/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('assets/sound/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('assets/sound/wing.wav')

    GAME_images['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_images['player'] = GAME_images['red']  # Default bird: red

    while True:
        welcomeScreen()
        mainGame()
