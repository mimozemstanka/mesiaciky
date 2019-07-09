# k mesiacikom


import pygame
from random import randint

import math
from settings import *
from general import *

class Player(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.init()
        
    def init(self, coord=(0, 0), angle=(90), power=100):
        self.coord = coord
        self.angle = angle
        self.power = power
        if Settings.FIXED_POWER:
            self.power = Settings.POWER
        self.rel_rot = 0.01
    
    def change_angle(self, a):
        self.angle += a
        self.rel_rot += a
        if self.angle >= 360:
            self.angle -= 360
        if self.angle < 0:
            self.angle += 360
        if self.rel_rot >= 360:
            self.rel_rot -= 360
        if self.rel_rot < 0:
            self.rel_rot += 360
    
    def change_power(self, p):
        if not Settings.FIXED_POWER:
            self.power += p
            if self.power < 0:
                self.power = 0
            if self.power > Settings.MAXPOWER:
                self.power = Settings.MAXPOWER

    def get_angle(self):
        return self.angle

    def get_power(self):
        return self.power

    def get_launchpoint(self):
        return self.coord
    
    def draw_line(self, screen):
        ''' Draws the aiming line out of the ship's gun. '''
        (sx,sy) = self.get_launchpoint()
        self.color = (209,170,133)
        pygame.draw.aaline(screen, self.color, (sx,sy), (sx + self.power * math.sin(math.radians(self.angle)), sy - self.power * math.cos(math.radians(self.angle))))

