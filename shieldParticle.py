import random
import math
import gtk, gobject, cairo

from sprite import Sprite

MAX_SIZE=10
MIN_SIZE=5

class ShieldParticle(Sprite):
    def __init__(self,posX, posY, power,targetCell):
        Sprite.__init__(self,posX, posY)
        self.width=random.randint(MIN_SIZE,MAX_SIZE)
        self.targetCell=targetCell
        self.velX=random.random()+1.5
        self.size=1
        self.posX=posX
        self.posY=posY
        self.power=power

        self.originPower=power
        self.originX=posX
        self.originSize=1

        self.degreePosY=0
        self.deltaDegree=(random.random()+1)/20
        self.alpha=1.0

        self.isDead=False

    def update(self):
        Sprite.update(self)

        if self.size<=0:
            self.isDead=True

        self.color=(1,random.random(),random.random())
        if self.posX<self.targetCell.posX:
            self.posX+=self.velX
        if self.posX>self.targetCell.posX:
            self.posX-=self.velX

        if self.posY<self.targetCell.posY:
            self.posY+=2
        if self.posY>self.targetCell.posY+self.targetCell.height:
            self.posY-=2

        self.posY+=math.sin(self.degreePosY)
        self.degreePosY+=self.deltaDegree

        distance=self.originX-self.posX
        self.power=self.originPower-(distance*0.0034)
        self.size=self.power*self.originSize/self.originPower
        self.alpha=self.size
        print("size: %f" % self.size)

        if Sprite.is_colliding_with(self,self.targetCell):
            self.isDead=True
            self.targetCell.score-=self.power


    def paint(self,window):
        window.save()
        ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
        window.transform ( ThingMatrix )
        cairo.Matrix.translate(ThingMatrix, self.width/2,self.height/2)
        window.transform ( ThingMatrix )
        window.arc(self.posX+self.width/2, self.posY+self.height/2, self.width*self.size, 0.0, 2 * math.pi)
        window.set_source_rgba(self.color[0],self.color[1],self.color[2],self.alpha)
        window.stroke()
        window.restore()