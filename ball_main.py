import random

import pygame as p
import ball_engine
from pygame import mixer
import math

'''
Play as an object moving around similar to snake collecting target objects.
Avoid colliding with other objects.
'''


WIDTH = 1920
HEIGHT = 1080
OBJECT_SIZE = 50
WALL_THICKNESS = 25
MAX_FPS = 60
VOLUME = 0.01

#game physics
ACCELERATION = 10

#colours
DARK_GRAY = (50,50,50)
LIGHT_GRAY = (220,220,220)
DARK_GREEN = (0,50,0)

IMAGES = {}

IMAGES['ball-1'] = p.transform.scale(p.image.load('images/ball-1.png'), (OBJECT_SIZE, OBJECT_SIZE))
IMAGES['target'] = p.transform.scale(p.image.load('images/mushroom.png'), (OBJECT_SIZE/2, OBJECT_SIZE/2))
IMAGES['mine'] = p.image.load('images/mine.png')
IMAGES['mine-blue'] = p.image.load('images/mine-blue.png')
IMAGES['explosion-1'] = p.image.load('images/explosion-1.png')
IMAGES['explosion-2'] = p.image.load('images/explosion-2.png')
IMAGES['explosion-3'] = p.image.load('images/explosion-3.png')
IMAGES['bg'] = p.image.load('images/field.png')

SOUNDS = {}



N_OF_ENEMIES = 1

p.init()

mixer.music.load('sounds/drone.mp3')
mixer.music.play(-1)
mixer.music.set_volume(VOLUME)

target_hit_sound = mixer.Sound('sounds/mixkit-bonus-earned-in-video-game-2058.wav')
enemy_reset = mixer.Sound('sounds/mixkit-thin-metal-card-deck-shuffle-3175.wav')
enemy_follow= mixer.Sound('sounds/mixkit-hard-horror-hit-drum-565.wav')
near_miss_sound = mixer.Sound('sounds/swoosh.mp3')
bounce_sound = mixer.Sound('sounds/sfx-boing9.mp3')
game_over_sound = mixer.Sound('sounds/mixkit-low-explosion-indoors-2187.wav')

def main():
    closest_enemy = WIDTH
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color(LIGHT_GRAY))
    running = True
    drawWalls(screen, HEIGHT, WIDTH, WALL_THICKNESS, DARK_GREEN)
    player = ball_engine.Player(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS)
    target = ball_engine.Target(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS)
    target_hit = False
    left_key_down = False
    right_key_down = False
    up_key_down = False
    down_key_down = False
    game_over = False
    enemies = []
    for i in range(0, N_OF_ENEMIES):
        enemies.append(ball_engine.Enemy(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS, player.position[0], player.position[1]))
    while running:
        for e in p.event.get():
            #exit handler
            if e.type == p.QUIT:
                running = False
            #keys handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    left_key_down = True

                elif e.key == p.K_RIGHT:
                    right_key_down = True
                if e.key == p.K_UP:
                    up_key_down = True
                elif e.key == p.K_DOWN:
                    down_key_down = True
                if e.key == p.K_r and p.key.get_mods() & p.KMOD_CTRL:
                    player = ball_engine.Player(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS)
                    target = ball_engine.Target(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS)
                    game_over = False
                    enemies = []
                    for i in range(0, N_OF_ENEMIES):
                        enemies.append(
                            ball_engine.Enemy(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS,
                                              player.position[0], player.position[1], player_score = player.score))
                    left_key_down = False
                    right_key_down = False
                    up_key_down = False
                    down_key_down = False
                    mixer.music.play(-1)
                    mixer.music.set_volume(VOLUME)
            elif e.type == p.KEYUP:
                if e.key == p.K_LEFT:
                    left_key_down = False
                if e.key == p.K_RIGHT:
                    right_key_down = False
                if e.key == p.K_UP:
                    up_key_down = False
                if e.key == p.K_DOWN:
                    down_key_down = False
        if not game_over:
            if left_key_down:
                player.update_speed(x=-1)
                target.update_speed(x=-1)
                for enemy in enemies:
                    enemy.update_speed(x=-1)
            if right_key_down:
                player.update_speed(x=1)
                target.update_speed(x=1)
                for enemy in enemies:
                    enemy.update_speed(x=1)
            if up_key_down:
                player.update_speed(y=-2)
                target.update_speed(y=-1)
                for enemy in enemies:
                    enemy.update_speed(y=-1)
            if down_key_down:
                player.update_speed(y=1)
                target.update_speed(y=1)
                for enemy in enemies:
                    enemy.update_speed(y=1)

            player.updatePos()
            if player.wall_collision:
                bounce_sound.play()
            target.updatePos()
            if len(enemies) > 10:
                enemy_reset.play()
                for i in range(8, -1 , -1):
                    enemies.remove(enemies[i])
            closest_enemy = WIDTH
            for enemy in enemies:
                if not game_over:
                    enemy.updatePos(player.position)
                    enemy.follow_player(player.position, player.xspeed, player.yspeed)
                    game_over = enemy.collide_with_player(player.position[0], player.position[1], player.object_thickness)
                    enemy_distance = math.sqrt((player.position[0] + player.object_thickness/2 - enemy.position[0] - enemy.object_thickness/2) ** 2 + \
                    (player.position[1] + player.object_thickness/2 - enemy.position[1] - enemy.object_thickness/2) ** 2)
                    if closest_enemy > enemy_distance:
                        closest_enemy = enemy_distance
                    
                    enemy_volume = (WIDTH - closest_enemy)/WIDTH
                    enemy_volume = ((enemy_volume * 10) ** 4)/10000
                    mixer.music.set_volume(enemy_volume)
            target_hit = player.collide_with_target(target.position, target.object_thickness)
            if target_hit:
                target_hit_sound.play()
                target = ball_engine.Target(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS)
                if random.randint(0,100) >= 20:
                    enemies.append(ball_engine.Enemy(HEIGHT, WIDTH, WALL_THICKNESS,
                                                     OBJECT_SIZE, ACCELERATION, MAX_FPS,
                                                     player.position[0], player.position[1], player_score = player.score))
                    if enemies[-1].follow:
                        enemy_follow.play()
            drawWalls(screen, HEIGHT, WIDTH, WALL_THICKNESS, DARK_GREEN)
            drawHeaderRegion(screen, player)
            drawTarget(screen, target)
            drawEnemies(screen, enemies)
            drawBall(screen, player)
            if game_over:
                game_over_sound.play()
                mixer.music.fadeout(2000)

        
            
           

        clock.tick(MAX_FPS)
        p.display.flip()

def drawWalls(screen, h, w, wall, colour_value):
    screen.fill(p.Color(LIGHT_GRAY))
    # screen.blit(p.transform.scale(IMAGES['bg'], (w, h - wall * 2)),
    #                     p.Rect(0, wall * 2, w, h - wall * 2))
    #draw bottom
    s = p.Surface((w, wall))
    s.fill(p.Color(colour_value))
    screen.blit(s, (0, (h - wall)))
    #draw top
    s = p.Surface((w, wall*2))
    s.fill(p.Color(LIGHT_GRAY))
    screen.blit(s, (0, 0))
    s = p.Surface((w, wall))
    s.fill(p.Color(colour_value))
    screen.blit(s, (0, wall*2))
    #draw left
    s = p.Surface((wall, h))
    s.fill(p.Color(colour_value))
    screen.blit(s, (0, 0))
    #draw right
    screen.blit(s, ((w - wall), 0))


def drawBall(screen, player):
    screen.blit(IMAGES['ball-1'],
                p.Rect(player.position[0], player.position[1], OBJECT_SIZE, OBJECT_SIZE))

def drawTarget(screen, target):
    screen.blit(IMAGES['target'],
                p.Rect(target.position[0], target.position[1], OBJECT_SIZE/2, OBJECT_SIZE/2))

def drawEnemies(screen, enemies):
    for enemy in enemies:
        mine_img = 'mine-blue' if enemy.follow else 'mine'
        if enemy.explode:
            drawExplosion(screen, enemy)
        else:
            screen.blit(p.transform.scale(IMAGES[mine_img], (enemy.object_thickness, enemy.object_thickness)),
                        p.Rect(enemy.position[0], enemy.position[1], enemy.object_thickness, enemy.object_thickness))


def drawExplosion(screen, enemy):
    offset_size = enemy.object_thickness/2 - OBJECT_SIZE/4
    if 5 <= enemy.animation_counter <= 7:
        screen.blit(p.transform.scale(IMAGES['explosion-1'], (enemy.object_thickness * enemy.animation_counter / 10, enemy.object_thickness * enemy.animation_counter / 10)),
                        p.Rect(enemy.position[0] - offset_size * 2, enemy.position[1] - offset_size * 2, 2 * enemy.object_thickness, 2 * enemy.object_thickness))
    if 7 <= enemy.animation_counter <= 9:
        screen.blit(p.transform.scale(IMAGES['explosion-2'], (
                enemy.object_thickness * enemy.animation_counter / 10,
                enemy.object_thickness * enemy.animation_counter / 10)),
                            p.Rect(enemy.position[0] - offset_size * 2, enemy.position[1] - offset_size * 2, 2 * enemy.object_thickness,
                                   2 * enemy.object_thickness))
    if enemy.animation_counter >= 9:
        screen.blit(p.transform.scale(IMAGES['explosion-3'], (
                enemy.object_thickness * enemy.animation_counter / 10,
                enemy.object_thickness * enemy.animation_counter / 10)),
                        p.Rect(enemy.position[0] - offset_size, enemy.position[1] - offset_size,
                               enemy.object_thickness,
                               enemy.object_thickness))
    if enemy.animation_counter <= 5:
        mine_img = 'mine-blue' if enemy.follow else 'mine'
        screen.blit(p.transform.scale(IMAGES[mine_img], (enemy.object_thickness, enemy.object_thickness)),
                    p.Rect(enemy.position[0] - offset_size, enemy.position[1] - offset_size, enemy.object_thickness, enemy.object_thickness))

def drawHeaderRegion(screen, player):
    font = p.font.SysFont("Helvitica", 32, True, False)
    score = player.score
    textSquares = font.render('Score: ' + str(score), 0, p.Color('black'))
    textSquaresLocation = p.Rect(0,0, WIDTH, HEIGHT).move(OBJECT_SIZE, textSquares.get_height()/2)
    screen.blit(textSquares, textSquaresLocation)



if __name__ == '__main__':
    main()