import random
import pickle
import neat
import math

class GameState():
    def __init__(self):
        self.tmp = []

class Player():
    def __init__(self, h, w, wall, obj, acc, fps):
        self.height = h
        self.width = w
        self.wall_thickness = wall
        self.object_thickness = obj
        self.acceleration = acc
        self.fps = fps
        self.xspeed = 3
        self.yspeed = 5
        self.position = (self.width/2, self.height/2)
        self.wall_collision = False #indicates the use of animations
        self.collision_direction = None #selects the animations
        self.speed_reduction = 0.8
        self.gameOver = False
        self.score = 0
        self.ycount = 0
        self.xcount = 0
        self.near_miss = False

    def updatePos(self):
        current_x = self.position[0]
        current_y = self.position[1]
        new_x = current_x + self.xspeed
        new_y = current_y + self.yspeed
        self.gravity_effect()
        self.position = (new_x, new_y)
        return self.check_collision()


    def check_collision(self):
        self.wall_collision = False
        if self.yspeed != 0:
            if self.position[1] + self.yspeed + self.object_thickness > (self.height - self.wall_thickness): #going down
                self.wall_collision = True
                self.yspeed = -1 * abs(self.yspeed) * self.speed_reduction
                self.ycount += 1
            elif self.position[1] + self.yspeed < self.wall_thickness * 3: #going up
                self.wall_collision = True
                self.yspeed = abs(self.yspeed) * self.speed_reduction
                self.ycount += 1
            else:
                self.ycount = 0
        if self.xspeed != 0:
            if self.position[0] + self.xspeed + self.object_thickness > (self.width - self.wall_thickness): #going right
                self.wall_collision = True
                self.xspeed = -1 * abs(self.xspeed) * self.speed_reduction
                self.xcount += 1
            elif self.position[0] + self.xspeed < self.wall_thickness: #going left
                self.wall_collision = True
                self.xspeed = abs(self.xspeed) * self.speed_reduction
                self.xcount += 1
            else:
                self.xcount = 0
        return self.ycount, self.xcount
        # if self.position[1] < 0 or self.position[1] > self.height: #off the screen so put in centre
        #     self.position = (self.width/2, self.height/2)
        # if self.position[0] < 0 or self.position[0] > self.width:
        #     self.position = (self.width/2, self.height/2)

    def gravity_effect(self):
        self.yspeed = self.yspeed + self.acceleration/self.fps


    def update_speed(self, x = 0, y = 0):
        self.xspeed += x * self.acceleration/self.fps
        self.yspeed += y * self.acceleration/self.fps

    def collide_with_target(self, target_position, target_size):
        player_x = self.position[0]
        player_y = self.position[1]
        player_size = self.object_thickness
        if (player_x < target_position[0] < player_x + player_size) or \
                (player_x < target_position[0] + target_size < player_x + player_size): #x is overlapping
            if (player_y < target_position[1] < player_y + player_size) or \
                (player_y < target_position[1] + target_size < player_y + player_size): # y is overlapping
                self.xspeed += (self.position[0] - target_position[0]) /target_size
                self.yspeed += (self.position[1] - target_position[1]) / target_size
                self.score += 1
                self.near_miss = False
                return True
            else:
                if abs(player_x - target_position[0]) <= self.object_thickness and abs(player_y - target_position[1]) <= self.object_thickness:
                    self.near_miss = True
                else:
                    self.near_miss = False
                return False
        else:
            return False



class Target():
    def __init__(self, h, w, wall, obj, acc, fps):
        self.height = h
        self.width = w
        self.wall_thickness = wall
        self.object_thickness = obj / 2
        self.acceleration = acc
        self.fps = fps
        self.xspeed = random.randint(0,1)
        self.yspeed = random.randint(0,1)
        self.position = (
        random.randint(0 + self.wall_thickness, self.width - self.wall_thickness - self.object_thickness),
        random.randint(0 + self.wall_thickness * 3, self.height - self.wall_thickness - self.object_thickness))
        self.speed_reduction = 0.8
        self.avoid = random.randint(0, 100) > 60
        # self.avoid = False

    def updatePos(self):
        current_x = self.position[0]
        current_y = self.position[1]
        new_x = current_x + self.xspeed
        new_y = current_y + self.yspeed
        self.position = (new_x, new_y)
        self.check_collision()
        self.xspeed = self.xspeed * 0.999
        self.yspeed = self.yspeed * 0.999

    def check_collision(self):
        if self.yspeed != 0:
            if self.position[1] + self.yspeed + self.object_thickness > (self.height - self.wall_thickness): #going down
                self.wall_collision = True
                self.yspeed = -1 * abs(self.yspeed) * self.speed_reduction
            elif self.position[1] + self.yspeed < self.wall_thickness * 3: #going up
                self.wall_collision = True
                self.yspeed = abs(self.yspeed) * self.speed_reduction
        if self.xspeed != 0:
            if self.position[0] + self.xspeed + self.object_thickness > (self.width - self.wall_thickness): #going right
                self.wall_collision = True
                self.xspeed = -1 * abs(self.xspeed) * self.speed_reduction
            elif self.position[0] + self.xspeed < self.wall_thickness: #going left
                self.wall_collision = True
                self.xspeed = abs(self.xspeed) * self.speed_reduction


    def update_speed(self, x = 0, y = 0):
        if self.avoid:
            self.xspeed += x * self.acceleration/self.fps/2
            self.yspeed += y * self.acceleration/self.fps/2



class Enemy():
    def __init__(self, h, w, wall, obj, acc, fps, player_x, player_y, player_score = 0):
        self.height = h
        self.width = w
        self.wall_thickness = wall
        self.object_thickness = obj/2
        self.acceleration = acc
        self.fps = fps
        self.xspeed = random.randint(2, 5)
        self.yspeed = random.randint(2,5)
        self.position = self.get_position(player_x, player_y)
        self.speed_reduction = 0.8
        self.follow = random.randint(0,100) >= (50 - player_score)
        self.copy_moves = random.randint(0,100) > 30 and not self.follow
        self.anit_gravity = random.randint(0,105)
        self.explode = False
        self.animation_counter = 0
        self.gameOver = False

    def get_position(self, player_x, player_y):
        if player_x < self.width/2:
            width = int(player_x + self.object_thickness * 10)
            if player_y < self.height/2:
                height = int(player_y + self.object_thickness * 10)
                position = (
                random.randint(width , self.width - self.wall_thickness - self.object_thickness),
                random.randint(height, self.height - self.wall_thickness - self.object_thickness))
            else:
                height = int(player_y - self.object_thickness * 10)
                position = (
                random.randint(width, self.width - self.wall_thickness - self.object_thickness),
                random.randint(0 + self.wall_thickness * 3, height))
        else:
            width = int(player_x - self.object_thickness * 10)
            if player_y < self.height/2:
                height = int(player_y + self.object_thickness * 10)
                position = (
                random.randint(0 + self.wall_thickness , width),
                random.randint(height, self.height - self.wall_thickness - self.object_thickness))
            else:
                height = int(player_y - self.object_thickness * 10)
                position = (
                random.randint(0 + self.wall_thickness, width),
                random.randint(0 + self.wall_thickness * 3, height))
        return position

    def updatePos(self, player_position = None):
        current_x = self.position[0]
        current_y = self.position[1]
        new_x = current_x + self.xspeed
        new_y = current_y + self.yspeed
        self.position = (new_x, new_y)
        self.gravity_effect()
        self.check_collision()


    def check_collision(self):
        if self.yspeed != 0: #going down
            if self.position[1] + self.yspeed + self.object_thickness > (self.height - self.wall_thickness):
                self.yspeed = -1 * abs(self.yspeed) * self.speed_reduction
            elif self.position[1] + self.yspeed < self.wall_thickness * 3:
                self.yspeed = abs(self.yspeed) * self.speed_reduction
        if self.xspeed != 0:
            if self.position[0] + self.xspeed + self.object_thickness > (self.width - self.wall_thickness):
                self.xspeed = -1 * abs(self.xspeed) * self.speed_reduction
            elif self.position[0] + self.xspeed < self.wall_thickness:
                self.xspeed = abs(self.xspeed) * self.speed_reduction

    def gravity_effect(self):
        if self.anit_gravity <= 50: # normal gravity
            self.yspeed = self.yspeed + self.acceleration / self.fps / 2
        if 50 < self.anit_gravity <= 70: # reverse gravity
            self.yspeed = self.yspeed - self.acceleration / self.fps / 2
        if 70 < self.anit_gravity <= 85: # left pulling gravity
            self.xspeed = self.xspeed + self.acceleration / self.fps / 2
        if 85 < self.anit_gravity <= 100: # right pulling gravity
            self.xspeed = self.xspeed - self.acceleration / self.fps / 2


    def update_speed(self, x = 0, y = 0):
        if self.copy_moves:
            self.xspeed -= x * self.acceleration/self.fps/2
            self.yspeed -= y * self.acceleration/self.fps/2

    def collide_with_player(self, player_x, player_y, player_size):
        x_distance_to_player = abs((player_x + player_size/2) - (self.position[0] + self.object_thickness/2))
        y_distance_to_player = abs((player_y + player_size/2) - (self.position[1] + self.object_thickness/2))
        distance_to_player = math.sqrt(x_distance_to_player ** 2 + y_distance_to_player ** 2)
        if distance_to_player < (player_size/2 + self.object_thickness/2):
            self.gameOver = True

        return self.gameOver

    def explode_player(self, player_x, player_y, player_size, enemy_size):
        offset_size =  2 * enemy_size - enemy_size / 2
        enemy_x = self.position[0] - offset_size
        enemy_y = self.position[1] - offset_size
        if (player_x < enemy_x < player_x + player_size) or \
                (player_x < enemy_x + enemy_size * 4 < player_x + player_size): #x is overlapping
            if (player_y < enemy_y < player_y + player_size) or \
                (player_y < enemy_y + enemy_size * 4 < player_y + player_size): # y is overlapping
                self.gameOver = True
        return self.gameOver

    def follow_player(self, player_position, player_x_speed, player_y_speed):
        if self.follow:
            x_difference = player_position[0] - self.position[0]
            y_difference = player_position[1] - self.position[1]
            if self.xspeed > 5:
                self.xspeed = 5
            if self.xspeed < -5:
                self.xspeed = -5
            if self.yspeed > 5:
                self.yspeed = 5
            if self.yspeed < -5:
                self.yspeed = -5
            self.xspeed += x_difference/self.width/3 + abs(x_difference/self.width) * player_x_speed/10
            self.yspeed += y_difference/self.height/3 + abs(y_difference/self.height) * player_y_speed/10



def replay_genome(config_path="config.txt", genome_path="winner.pkl"):
    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)


    winner_net = neat.nn.FeedForwardNetwork.create(genome, config)

    return(winner_net, config)