import random

import pygame as p
import ball_engine
import neat
import os
import visualize
import pickle

'''
Play as an object moving around similar to snake collecting target objects.
Avoid colliding with other objects.
'''


WIDTH = 1200
HEIGHT = 800
OBJECT_SIZE = 50
WALL_THICKNESS = 25
MAX_FPS = 60


#game physics
ACCELERATION = 10

N_OF_ENEMIES = 1

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


N_OF_ENEMIES = 1

p.init()


def main(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        # screen = p.display.set_mode((WIDTH, HEIGHT))
        # clock = p.time.Clock()
        # screen.fill(p.Color(LIGHT_GRAY))
        player = ball_engine.Player(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS)
        target = ball_engine.Target(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS)
        left_key_down = False
        right_key_down = False
        up_key_down = False
        down_key_down = False
        game_over = False
        enemy = ball_engine.Enemy(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS, player.position[0], player.position[1])
        counter = 0
        while not game_over:
            counter += 1
            if counter > 3600:
                break
            if not enemy.follow and not enemy.copy_moves:
                enemy_type = 0
            elif enemy.follow:
                enemy_type = 1
            else:
                enemy_type = 2
            inputs = [(enemy.position[0] - player.position[0]),
                      (enemy.position[1] - player.position[1]),
                      (enemy.xspeed - player.xspeed),
                      (enemy.yspeed - player.yspeed),
                      (target.position[0] - player.position[0]),
                      (target.position[1] - player.position[1])]

            # inputs = [
            #           (target.position[0] - player.position[0]),
            #           (target.position[1] - player.position[1])]


            output = net.activate(inputs)
            # print(output, genome.fitness, player.position)
            if player.position[0] < 0 or player.position[0] > WIDTH or player.position[1] < 0 or player.position[1] > HEIGHT:
                genome.fitness -= 10
                game_over = True
            else:
                genome.fitness += 0.00000001
            if output[0] < 0.5:
                player.update_speed(x=-1)
                target.update_speed(x=-1)
                enemy.update_speed(x=-1)
            if output[0] >= 0.5:
                player.update_speed(x=1)
                target.update_speed(x=1)
                enemy.update_speed(x=1)
            if output[1] < 0.5:
                player.update_speed(y=-2)
                target.update_speed(y=-1)
                enemy.update_speed(y=-1)
            if output[1] >= 0.5:
                player.update_speed(y=1)
                target.update_speed(y=1)
                enemy.update_speed(y=1)
            enemy.updatePos(player.position)
            enemy.follow_player(player.position, player.xspeed, player.yspeed)
            if not game_over:
                game_over = enemy.collide_with_player(player.position[0], player.position[1], player.object_thickness)
            if game_over:
                genome.fitness -= 50
            x_count, y_count = player.updatePos()
            if x_count > 20 or y_count > 20:
                game_over = True
                genome.fitness -= 50
            target.updatePos()
            target_hit = player.collide_with_target(target.position, target.object_thickness)
            if target_hit:
                target = ball_engine.Target(HEIGHT, WIDTH, WALL_THICKNESS, OBJECT_SIZE, ACCELERATION, MAX_FPS)
                genome.fitness += 5
            # drawWalls(screen, HEIGHT, WIDTH, WALL_THICKNESS, DARK_GREEN)
            # drawHeaderRegion(screen, player)
            # drawTarget(screen, target)
            # drawEnemies(screen, enemy)
            # drawBall(screen, player)

            # clock.tick(MAX_FPS * 4)
            # p.display.flip()




def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(100))

    # Run for up to 1000 generations.
    winner = p.run(main, 1000)

    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()

    node_names = {-1:'A', -2: 'B', -3: 'C', -4: 'D', -5: 'E',
    -6: 'F', -7: 'G', -8: 'H', -9: 'I', -10: 'J', -11: 'K', 0:'left', -12: 'right'}
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-9999')
    p.run(main, 10)



def drawWalls(screen, h, w, wall, colour_value):
    screen.fill(p.Color(LIGHT_GRAY))
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

def drawEnemies(screen, enemy):
    mine_img = 'mine-blue' if enemy.follow else 'mine'
    screen.blit(p.transform.scale(IMAGES[mine_img], (enemy.object_thickness, enemy.object_thickness)),
                        p.Rect(enemy.position[0], enemy.position[1], enemy.object_thickness, enemy.object_thickness))



def drawHeaderRegion(screen, player):
    font = p.font.SysFont("Helvitica", 32, True, False)
    score = player.score
    textSquares = font.render('Score: ' + str(score), 0, p.Color('black'))
    textSquaresLocation = p.Rect(0,0, WIDTH, HEIGHT).move(OBJECT_SIZE, textSquares.get_height()/2)
    screen.blit(textSquares, textSquaresLocation)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)