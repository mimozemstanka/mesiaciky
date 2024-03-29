#!/usr/bin/python

import pygame
from pygame.locals import *
import math
import os
import sys
import time
import thread

from random import randint

from settings import *
from general import *
from player_my import *
from planet import *
from particle import *
from menu import *
from network import *
from inputbox import *

from kreslenie import *

class Game:

    particle_image = None
    particle_image_rect = None
#
    pygame.font.init()
    Settings.font = pygame.font.Font(get_data_path("FreeSansBold.ttf"), 14)
    Settings.menu_font = pygame.font.Font(get_data_path("FreeSansBold.ttf"), Settings.MENU_FONT_SIZE)
    Settings.round_font = pygame.font.Font(get_data_path("FreeSansBold.ttf"), 100)
    Settings.fineprint = pygame.font.Font(get_data_path("FreeSansBold.ttf"), 8)

    def __init__(self):
        pygame.display.init()

        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((1000, 700))
        icon, rect = load_image("icon64x64.png", (0,0,0))
        pygame.display.set_icon(icon)
        pygame.display.set_caption('Mesiacik jediny')

        pygame.mixer.init()
        pygame.mixer.music.load('data/vysehrad.mp3')
        pygame.mixer.music.play(-1)
        
        #Settings.particle_image10, Settings.particle_image10_rect = load_image("explosion-10.png", (0,0,0))
        #Settings.particle_image5, Settings.particle_image5_rect = load_image("explosion-5.png", (0,0,0))
        
        self.trail_screen = pygame.Surface(self.screen.get_size())
        self.trail_screen = self.trail_screen.convert()
        self.trail_screen.set_colorkey((0,0,0))
        self.trail_screen.set_alpha(0)

        self.planet_screen = pygame.Surface(self.screen.get_size())
        self.planet_screen = self.trail_screen.convert()
        self.planet_screen.set_colorkey((0,0,0))

        self.dim_screen = pygame.Surface(self.screen.get_size())
        self.dim_screen.set_alpha(175)
        self.dim_screen = self.dim_screen.convert_alpha()
        #self.dim_screen.fill((0,0,0))

        self.background, r = load_image("backdrop.png")
        
        self.nina = Player()
        self.nina.init(coord=(200, 200))

        #self.missile = Mesiac2(self.trail_screen)
        #self.missile = Mesiac3()
        #self.missilesprite = pygame.sprite.RenderPlain((self.missile))

        self.lock = thread.allocate_lock()

        #self.game_init()
        self.load_settings()
        
        


### original: round_init

        pygame.key.set_repeat(Settings.KEY_DELAY, Settings.KEY_REPEAT)

        planetlist = None

        self.particlesystem = pygame.sprite.RenderPlain()
        self.mesiacovysystem = pygame.sprite.RenderPlain()
        self.planetsprites = self.create_planets(planetlist)
        self.vykresleniesprites = pygame.sprite.RenderPlain()
        
        self.trail_screen.fill((0, 0, 0))
            
        #self.show_planets = 100

    def create_mesiacovysystem(self, pos, size):
        self.mesiacovysystem.add(Particle(pos, size))


    def create_particlesystem(self, pos, n, size):
        if Settings.PARTICLES:
            if Settings.BOUNCE:
                nn = n / 2
            else:
                nn = n
            for i in xrange(nn):
                self.particlesystem.add(Particle(pos, size))

    def create_planets(self, planetlist=None):
        result = pygame.sprite.RenderPlain()

        if planetlist == None:
            if Settings.MAX_BLACKHOLES > 0:
                n = randint(1, Settings.MAX_BLACKHOLES)
                for i in xrange(n):
                    result.add(Blackhole(result, self.background))
            else:
                # Only have planets if we don't have any
                # blackholes.
                n = randint(2, Settings.MAX_PLANETS)
                for i in xrange(n):
                    result.add(Planet(result, self.background))
        else:
            for p in planetlist:
                if p[0] > Settings.MAX_PLANETS:
                    # Numbers above Settings.MAX_PLANETS are
                    # allocated to blackholes.
                    result.add(Blackhole(None, self.background, p[0], p[1], p[2], p[3]))
                else:
                    result.add(Planet(None, self.background, p[0], p[1], p[2], p[3]))
        return result


    def fire(self):
        self.missile.launch()
        pygame.key.set_repeat()
        #self.end_shot()
    
    def fire2(self):
        self.missile.launch()
        pygame.key.set_repeat()
        #self.end_shot()

    

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        if Settings.BOUNCE:
            pygame.draw.rect(self.screen, (self.bounce_count, 0, 0), pygame.Rect(0, 0, 1000, 700), 1)

        show_planets = False
        if not Settings.INVISIBLE:
            show_planets = True
        else:
            show_planets = True
        if show_planets:
            self.planetsprites.draw(self.screen)
        self.screen.blit(self.trail_screen, (0,0))
        #self.playersprites.draw(self.screen)
#        self.players[1].draw(self.screen)
#        self.players[2].draw(self.screen)
#        print self.particlesystem
        if Settings.PARTICLES:
            self.particlesystem.draw(self.screen)
        #if self.firing:
        #    if self.missile.visible():
        #        self.missilesprite.draw(self.screen)
#        print self.planetsprites
        #if self.firing:
        #    if not self.missile.visible():
        #        self.draw_zoom()
        #self.players[1].draw_status(self.screen)
        #self.players[2].draw_status(self.screen)

        #if self.firing:
        #    self.missile.draw_status(self.screen)

        self.particlesystem.draw(self.screen)
        self.mesiacovysystem.draw(self.screen)

        #if self.missile.visible():
        #    self.missilesprite.draw(self.screen)
        #if not self.missile.visible():
        #    self.draw_zoom()

        obr_nina()
        self.vykresleniesprites.add(obr_nina())
        self.vykresleniesprites.draw(self.screen)

        aa = pygame.image.load('data/nina.png')
        #self.screen.blit(aa, (300, 300))

        self.nina.draw_line(self.screen)

        pygame.display.flip()


    def update_particles(self):
        if Settings.PARTICLES:
            for p in self.particlesystem:
    #            print p.get_pos()
                if p.update(self.planetsprites) == 0 or p.flight < 0:
                    if p.flight >= 0 and p.in_range():
                        if p.get_size() == 10:
                            self.create_particlesystem(p.get_impact_pos(), Settings.n_PARTICLES_5, 5)
    #                print "removing: ", p.get_pos()
                    self.particlesystem.remove(p)
                if p.flight > Settings.MAX_FLIGHT:
                    self.particlesystem.remove(p)

    def update_mesiace(self):
        if Settings.PARTICLES:
            for p in self.mesiacovysystem:
    #            print p.get_pos()
                if p.update(self.planetsprites) == 0:
                    if p.flight >= 0 and p.in_range():
                        if p.get_size() == 10:
                            self.create_particlesystem(p.get_impact_pos(), Settings.n_PARTICLES_5, 5)
    #                print "removing: ", p.get_pos()
                    self.mesiacovysystem.remove(p)


    def update(self):
        self.update_particles()
        self.update_mesiace()
        #self.firing = self.missile.update(self.planetsprites, self.players)
        #self.cotrafil = self.missile.update(self.planetsprites)
        #print("cotrafil", self.cotrafil)
        #if self.firing <= 0:
        #if self.cotrafil <= 0:
            # Collision between missile and planet (0) or
            # a black hole (-1).
            #
            # Don't create any particles when we hit a black
            # hole, the missile got sucked up.
        #    if self.cotrafil == 0 and self.missile.visible():
        #        self.create_particlesystem(self.missile.get_impact_pos(), Settings.n_PARTICLES_10, 10e20)
        #        ()
            #self.end_shot()


        #self.started = True
    
    
    def event_check(self):
        self.lock.acquire()
        result=pygame.event.get()
        self.lock.release()
        return result



    def run(self):
        #self.fire()
        #self.missilei = Mesiac2(self.trail_screen)
        #self.mesiacovysystem.add(Mesiac2(self.trail_screen).launch())
        #self.mesiacovysystem.add(Particle((100,100), 20))
        #self.particlesystem.add(Particle((100,100), 20))
        #create_particlesystem(self, pos, n, size):
        while True:    
            self.clock.tick(Settings.FPS)
            #print clock.get_fps()

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        print("hovno")
                        #self.fire()
                        aa=Mesiac3()
                        self.mesiacovysystem.add(aa)
                        aa.launch(self.nina)
                        #self.mesiacovysystem.add(Mesiac3())
                        #self.particlesystem.add(Particle((100,100), 20))
                        #self.mesiacovysystem.add(Mesiac2(self.trail_screen).launch())
                    a=2
                    p=5
                    if event.key == K_UP:
                        self.nina.change_power(p)
                    elif event.key == K_DOWN:
                        self.nina.change_power(-p)
                    elif event.key == K_LEFT:
                        self.nina.change_angle(-a)
                    elif event.key == K_RIGHT:
                        self.nina.change_angle(a)

                    if event.key == K_n:
                        planetlist = None
                        self.planetsprites = self.create_planets(planetlist)


            #if pygame.key.get_pressed()[K_SPACE]:
            #    self.fire()
            
            #for event in self.event_check():
            #    if event.key == K_RETURN or event.key == K_SPACE:
            #        self.fire()
            

            
            #self.lock.acquire()
            self.update()
            self.draw()
        #self.lock.release()
    
    
    
    def load_settings(self):

        self.bounce = Settings.BOUNCE
        self.fixed_power = Settings.FIXED_POWER
        self.invisible = Settings.INVISIBLE
        self.random = Settings.RANDOM
        self.max_planets = Settings.MAX_PLANETS
        self.max_blackholes = Settings.MAX_BLACKHOLES
        self.timeout = Settings.MAX_FLIGHT
        self.max_rounds = Settings.MAX_ROUNDS
        self.fullscreen = Settings.FULLSCREEN

        path = os.path.expanduser("~") + "/.slingshot/settings"

        if os.path.exists(path):
            f=open(path, 'r')
            lines = f.readlines()
            for l in lines:
                tokens = l.split()
                if tokens[0] == "Bounce:":
                    if tokens[1] == "1":
                        self.bounce = True
                if tokens[0] == "Fixed_Power:":
                    if tokens[1] == "1":
                        self.fixed_power = True
                elif tokens[0] == "Particles:":
                    if tokens[1] == "1":
                        Settings.PARTICLES = True
                    elif tokens[0] == "Fullscreen:":
                        if tokens[1] == "1":
                            self.fullscreen = True
                elif tokens[0] == "Random:":
                    if tokens[1] == "1":
                        self.random = True
                elif tokens[0] == "Invisible:":
                    if tokens[1] == "1":
                        self.invisible = True
                elif tokens[0] == "Max_Blackholes:":
                    self.max_blackholes = int(tokens[1])
                elif tokens[0] == "Max_Planets:":
                    self.max_planets = int(tokens[1])
                elif tokens[0] == "Timeout:":
                    self.timeout = int(tokens[1])
                elif tokens[0] == "Rounds:":
                    self.max_rounds = int(tokens[1])
            f.close()
    
def main():

    #sys.stdout = Blackhole()
    #sys.stderr = Blackhole()

    path = os.path.expanduser("~") + "/.slingshot"
    if not os.path.exists(path):
        os.mkdir(path)
    path += "/logfile.txt"
    sys.stderr = open(path,"w")
    sys.stdout = sys.stderr
    game = Game()
    game.run()

if __name__ == '__main__': main()
