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
from player import *
from planet import *
from particle import *
from menu import *
from network import *
from inputbox import *

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

        self.screen = pygame.display.set_mode((800, 600))
        icon, rect = load_image("icon64x64.png", (0,0,0))
        pygame.display.set_icon(icon)
        pygame.display.set_caption('Mesiacik jediny')
        
        Settings.particle_image10, Settings.particle_image10_rect = load_image("explosion-10.png", (0,0,0))
        Settings.particle_image5, Settings.particle_image5_rect = load_image("explosion-5.png", (0,0,0))
        
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
        
        self.missile = Mesiac2(self.trail_screen)
        self.missilesprite = pygame.sprite.RenderPlain((self.missile))

        self.lock = thread.allocate_lock()

        #self.game_init()
        self.load_settings()
        
        


### original: round_init

        pygame.key.set_repeat(Settings.KEY_DELAY, Settings.KEY_REPEAT)

        planetlist = None

        self.particlesystem = pygame.sprite.RenderPlain()
        self.planetsprites = self.create_planets(planetlist)
        
        self.trail_screen.fill((0, 0, 0))
            
        #self.show_planets = 100


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

    
    def draw_zoom(self):
        normal_screen = pygame.Surface((800, 600))
        normal_screen.set_colorkey((0,0,0))
        normal_screen.convert_alpha()
        #self.playersprites.draw(normal_screen)
        if not Settings.INVISIBLE:
            self.planetsprites.draw(normal_screen)

        zoom_screen = pygame.Surface((600, 450))
        zoom_screen.set_colorkey((0,0,0))
        zoom_screen.convert_alpha()

        background = pygame.transform.scale(self.background, (600,450))
        zoom_screen.blit(self.background, (0,0))
        normal_screen = pygame.transform.scale(normal_screen, (200,150))
        zoom_screen.blit(normal_screen, (200,150))

        missilesprite = self.missile.get_image()
        missilesprite = pygame.transform.scale(missilesprite, (missilesprite.get_size()[0] / 3, missilesprite.get_size()[1] / 3))
        pos = self.missile.get_pos()
        pos = (200 + pos[0] / 4 - missilesprite.get_width() / 2, 150 + pos[1] / 4- missilesprite.get_height() / 2)
        zoom_screen.blit(missilesprite, pos)

        pygame.draw.rect(zoom_screen, (255,255,255), pygame.Rect(0, 0, 600, 450), 1)
        pygame.draw.rect(zoom_screen, (150,150,150), pygame.Rect(200, 150, 200, 150), 1)
        #self.screen.blit(self.dim_screen, (0,0))
        #self.screen.blit(zoom_screen, (100, 75))

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        if Settings.BOUNCE:
            pygame.draw.rect(self.screen, (self.bounce_count, 0, 0), pygame.Rect(0, 0, 800, 600), 1)

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
        #if Settings.PARTICLES:
        #    self.particlesystem.draw(self.screen)
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

        if self.missile.visible():
            self.missilesprite.draw(self.screen)
        if not self.missile.visible():
            self.draw_zoom()

        pygame.display.flip()


    def update(self):
        #self.update_particles()
        #self.firing = self.missile.update(self.planetsprites, self.players)
        self.cotrafil = self.missile.update(self.planetsprites)
        print("cotrafil", self.cotrafil)
        #if self.firing <= 0:
        if self.cotrafil <= 0:
            # Collision between missile and planet (0) or
            # a black hole (-1).
            #
            # Don't create any particles when we hit a black
            # hole, the missile got sucked up.
            if self.cotrafil == 0 and self.missile.visible():
                #self.create_particlesystem(self.missile.get_impact_pos(), Settings.n_PARTICLES_10, 10e20)
                ()
            #self.end_shot()


        #self.started = True
    
    
    def event_check(self):
        self.lock.acquire()
        result=pygame.event.get()
        self.lock.release()
        return result



    def run(self):
        self.fire()
        while True:    
            self.clock.tick(Settings.FPS)
            #print clock.get_fps()

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        print("hovno")
                        self.fire()

            #if pygame.key.get_pressed()[K_SPACE]:
            #    self.fire()
            
            #for event in self.event_check():
            #    if event.key == K_RETURN or event.key == K_SPACE:
            #        self.fire()
            
            '''
            for event in self.event_check():
                if event.type == QUIT:
                    self.q = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.toggle_menu()

                    if (not self.net_play() or self.active_net_player()):
                        if event.mod == KMOD_CTRL or event.mod == KMOD_LCTRL or event.mod == KMOD_RCTRL \
                            or event.mod == 4160 or event.mod == 4224:
                            p = 1
                            a = 0.25
                        elif event.mod == KMOD_SHIFT or event.mod == KMOD_LSHIFT or event.mod == KMOD_RSHIFT \
                            or event.mod == 4097 or event.mod == 4098:
                            p = 25
                            a = 5
                        elif event.mod == KMOD_ALT or event.mod == KMOD_LALT or event.mod == KMOD_RALT \
                            or event.mod == 4352 or event.mod == 20480 or event.mod == 4608:
                            p = 0.2
                            a = 0.05
                        else:
                            p = 10
                            a = 2

                        if not self.round_over:
                            if event.key == K_UP:
                                self.change_power(p)
                            elif event.key == K_DOWN:
                                self.change_power(-p)
                            elif event.key == K_LEFT:
                                self.change_angle(-a)
                            elif event.key == K_RIGHT:
                                self.change_angle(a)

                        if event.key == K_RETURN or event.key == K_SPACE:
                            if self.net_play():
                                if self.net.send((self.players[self.player].get_angle(),
                                    self.players[self.player].get_power(), True)) == False:
                                    self.net.close()
                            self.fire()
                        else:
                            if self.net_play():
                                if self.net.send((self.players[self.player].get_angle(),
                                    self.players[self.player].get_power(), False)) == False:
                                    self.net.close()

                    self.q = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.toggle_menu()

                    if (not self.net_play() or self.active_net_player()):
                        if event.mod == KMOD_CTRL or event.mod == KMOD_LCTRL or event.mod == KMOD_RCTRL \
                            or event.mod == 4160 or event.mod == 4224:
                            p = 1
                            a = 0.25
                        elif event.mod == KMOD_SHIFT or event.mod == KMOD_LSHIFT or event.mod == KMOD_RSHIFT \
                            or event.mod == 4097 or event.mod == 4098:
                            p = 25
                            a = 5
                        elif event.mod == KMOD_ALT or event.mod == KMOD_LALT or event.mod == KMOD_RALT \
                            or event.mod == 4352 or event.mod == 20480 or event.mod == 4608:
                            p = 0.2
                            a = 0.05
                        else:
                            p = 10
                            a = 2

                        if not self.round_over:
                            if event.key == K_UP:
                                self.change_power(p)
                            elif event.key == K_DOWN:
                                self.change_power(-p)
                            elif event.key == K_LEFT:
                                self.change_angle(-a)
                            elif event.key == K_RIGHT:
                                self.change_angle(a)

                        if event.key == K_RETURN or event.key == K_SPACE:
                            if self.net_play():
                                if self.net.send((self.players[self.player].get_angle(),
                                    self.players[self.player].get_power(), True)) == False:
                                    self.net.close()
                            self.fire()
                        else:
                            if self.net_play():
                                if self.net.send((self.players[self.player].get_angle(),
                                    self.players[self.player].get_power(), False)) == False:
                                    self.net.close()
                        '''

            
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
