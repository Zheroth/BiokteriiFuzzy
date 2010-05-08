import random
import math
import gtk, gobject, cairo

from sprite import Sprite

MAX_SIZE=15
MIN_SIZE=5

class DyingParticle(Sprite):
    def __init__(self,posX=0, posY=0, velX=0, velY=0, size=0.14, lifetime=0):
        Sprite.__init__(self,posX, posY)
        self.width=random.randint(MIN_SIZE,MAX_SIZE)
        self.height=self.width
        self.velY=velX
        self.velX=velY
        self.size=size
        if lifetime==0:
            self.lifeTime=random.randint(200,300)
        else:
            self.lifeTime=lifetime


    def update(self):
        Sprite.update(self)
        self.color=(random.random(),random.random(),random.random())
        if self.lifeTime>0:
            self.lifeTime-=1
        self.posX+=self.velX
        self.posY+=self.velY

    def paint(self,window):
        window.save()
        ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
        window.transform ( ThingMatrix )
        cairo.Matrix.translate(ThingMatrix, self.width/2,self.height/2)
        window.transform ( ThingMatrix )
        window.arc(self.posX+self.width/2, self.posY+self.height/2, self.width*self.size, 0.0, 2 * math.pi)
        window.set_source_rgba(self.color[0],self.color[1],self.color[2])
        window.stroke()
        window.restore()