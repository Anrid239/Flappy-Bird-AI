from distutils.command.config import config
import importlib
from operator import ne
from pickle import GLOBAL
import pygame
pygame.font.init()
import neat
import time
import os
import random
import matplotlib.pyplot as plt
import visualize

#Increase font size in graphs
plt.rcParams['font.size'] = '20'

#Window parameters of game
win_width = 576
win_height = 800

#Required images
bird_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("/home/anirudh/ANN/Flappy Bird/imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("/home/anirudh/ANN/Flappy Bird/imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("/home/anirudh/ANN/Flappy Bird/imgs", "bird3.png")))]
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("/home/anirudh/ANN/Flappy Bird/imgs", "pipe.png")))
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("/home/anirudh/ANN/Flappy Bird/imgs", "base.png")))
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join("/home/anirudh/ANN/Flappy Bird/imgs", "bg.png")))

#Fonts
stat_font = pygame.font.SysFont("comicsans", 50)

#other miscellaneous global variables
gen = -1
gen_all = []
max_score = 0
gen_score = []

#------------------------------------------------------------------------------------------------------------Code for creating and moving bird
class Bird:
    IMGS = bird_imgs
    MAX_ROTATION = 25
    ROTATION_VEL = 20
    ANIM_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + 1.5*self.tick_count**2
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > - 90:
                self.tilt -= self.ROTATION_VEL
            
    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIM_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIM_TIME*2 :
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIM_TIME*3 :
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIM_TIME*4 :
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIM_TIME*4 +1 :
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIM_TIME*2
        
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        win.blit(rotated_img, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

#-----------------------------------------------------------------------------------------------Code related to creating pipes
class Pipe:
    GAP = 200
    PIPE_VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
        
    def move(self):
        self.x -= self.PIPE_VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask, top_offset)
        
        if top_point or bottom_point:
            return True

        return False
#--------------------------------------------------------------------------------------------------Code related to Base
class Base:
    BASE_VEL = 5
    BASE_WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.BASE_WIDTH

    def move(self):
        self.x1 -= self.BASE_VEL
        self.x2 -= self.BASE_VEL

        if self.x1 + self.BASE_WIDTH < 0:
            self.x1 = self.x2 + self.BASE_WIDTH
        if self.x2 + self.BASE_WIDTH < 0:
            self.x2 = self.x1 + self.BASE_WIDTH
    
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

#-----------------------------------------------------------------------------------------------Code to draw all images in and other data in pygame window
def draw_window(win, birds, pipes, base, score, gen, max_score, alive):
    win.blit(bg_img, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)
    
    text = stat_font.render("Score: " +str(score), 1, (255, 255, 255))
    win.blit(text, (win_width - 10 -text.get_width(), 10))
    
    text = stat_font.render("Gen: " +str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    text = stat_font.render("Alive: " +str(alive), 1, (255, 255, 255))
    win.blit(text, (10, 50))

    text = stat_font.render("Max Score: " +str(max_score), 1, (255, 255, 255))
    win.blit(text, (win_width - 10 -text.get_width(), 50))
    
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

#----------------------------------------------------------Main function for playing the game, calculating fitness value & providing I/P and recieving O/P from Neural network
def main(genomes, config):
    global gen
    global max_score
    global gen_score
    global gen_all
    gen += 1
    score = 0
    gen_score.append(0)
    gen_all.append(gen)

    n_net = []
    genome = []
    birds = []
    
    #Initializing genomes with feed forward network
    for _,g in genomes:
        n_net.append(neat.nn.FeedForwardNetwork.create(g, config))
        birds.append(Bird(230,350))
        #Setting initial fitness value of each bird to 0
        g.fitness = 0
        genome.append(g)

    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((win_width, win_height))
    clock = pygame.time.Clock()
    run = True
    while (run):
        clock.tick(100) #Decides the speed of the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_index = 0
        if len(birds)>0:
            if len(pipes)>1 and birds[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:
            run = False
            break

        for x,bird in enumerate(birds):
            bird.move()
            #Reward bird for being alive
            genome[x].fitness += 0.1
            
            #output = n_net[x].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))
            
            #Providing I/P parameters to neural network
            output = n_net[x].activate((bird.y, (bird.y - pipes[pipe_index].height), 
                                        (bird.y - pipes[pipe_index].bottom), abs(bird.x - pipes[pipe_index].x)))
        
            #If O/P satisfies a certain threshold then JUMP
            if output[0] > 0.7:
                bird.jump()

        add_pipe = False
        rem_pipes = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    #Punish bird if it collides
                    genome[x].fitness -= 5
                    birds.pop(x)
                    n_net.pop(x)
                    genome.pop(x)
                    
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                #Adding pipes that have been passed for removal
                rem_pipes.append(pipe)
            pipe.move()

        if add_pipe:
            score += 1
            for g in genome:
                #Reward bird if it scores a point
                g.fitness += 5
            #Create a new pipe Ahead
            pipes.append(Pipe(700))
        
        for r in rem_pipes:
            #Removing/deleting passed pipes
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height()>=730 or bird.y < 0:
                #Deleting data of birds that have failed
                birds.pop(x)
                n_net.pop(x)
                genome.pop(x)
        
        base.move()
        
        if max_score < score:
            #Reward bird if it beats the previous set Max Score
            genome[x].fitness += 10
            max_score = score
        
        gen_score[gen] = score
        

        draw_window(win, birds, pipes, base, score, gen, max_score, len(birds))
                
#---------------------------------------------------------------------------Recives the config file and starts the NEAT algorithm for specifed number of generations and drawns graphs at the end
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    #We run the main function for a set number of generations
    winner = population.run(main, 20)
    plt.plot(gen_all, gen_score)
    plt.show()

    #To draw the necessary graphs
    node_names = {-1: 'Dist from top', -2: 'Dist from corner of top pipe', -3: 'Dist from corner of bottom pipe', -4:'Horizontal dis from pipes', 0: 'OUT'}
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

#----------------------------------------------------------------------------------------------------------------------To provide the config file and run the programme
if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    config_path = os.path.join(dir, "config-feedforward.txt")
    run(config_path)