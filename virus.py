import random
import math
import gtk, gobject, cairo

from sprite import Sprite
from attackParticle import AttackParticle
from hpParticle import HpParticle
from shieldParticle import ShieldParticle

from operator import indexOf

from constants import VIRUS_IMAGE
from constants import WINDOW_SIZE
from constants import TRAINING_ZONE_LIMIT

DEFAULT_WIDTH=50
DEFAULT_HEIGHT=50

MAX_PUSH_PARTICLES=50

ATTACK_DICT={"Puny":(10,4),"Weak": (34,6), "Normal": (25,8), "Strong": (40,8), "VeryStrong": (50,9)}
DISTANCE_DICT={"Close": (1,0.01),"Near":(3,0.025), "Middle": (6,0.06), "Far": (8,0.065), "VeryFar": (10,0.09)}

class Virus(Sprite):
    def __init__(self, posX=0, posY=0,
                 ):
        Sprite.__init__(self,posX,posY)
        self.width=DEFAULT_WIDTH
        self.height=DEFAULT_HEIGHT
        self.color=(1,1,1)
        self.maxHp=1000
        self.hp=self.maxHp
        self.isDead=False
        self.baseVelX=2
        self.baseVelY=2
        self.velX=0
        self.velY=0

        self.deltaTransX=0.1
        self.deltaTransY=0.1
        self.transVelX=0
        self.transVelY=0

        self.imagen=VIRUS_IMAGE
        self.targetCell=None
        self.status="Waiting1"
        self.policy="Fuzzy"

        #movement
        self.degreeRotY=random.random()
        self.degreeRotX=random.random()

        self.limitMax=10
        self.limitMin=-10

        #score
        self.score=0

        #effects
        self.pushParticles=[]

        #attack
        self.attackParticleNumber=0
        self.attackPower=0
        self.attackParticles=[]
        self.hpParticles=[]
        self.shieldParticles=[]

        #suck
        self.suckingDeltaForce=0
        self.suckingForce=0

        #rotation
        self.transDeltaRot=0
        self.deltaRot=0.1
        self.deltaDeltaRot=0.001

        self.rotDirection=1
        self.rot=0

        #Wait ticks
        self.totalWaitTicks=100
        self.waitTicks=0

    def __str__(self):
        return "Virus: %s - Score: %f" % (self.policy,self.score)

    def get_type(self):
        return "Virus"

    def attack(self):
        self.status="Attacking"

    def analyze(self):
        self.status="Analyzing"

    def eat(self):
        self.status="Eating"

    def update(self,state):
        Sprite.update(self)
        
        if state=="Running":
            for particle in self.shieldParticles:
                particle.update()
            for particle in self.attackParticles:
                particle.update()
            for particle in self.hpParticles:
                particle.update()

            if self.score<0:
                self.score=0

            if abs(self.transVelY-self.velY)<=self.deltaTransY*2:
                self.trasnVelY=self.velY
            elif self.transVelY < self.velY:
                self.transVelY+=self.deltaTransY
            elif self.transVelY > self.velY:
                self.transVelY-=self.deltaTransY

            if abs(self.transVelX-self.velX)<=self.deltaTransX*2:
                self.transVelX=self.velX
            elif self.transVelX < self.velX:
                self.transVelX+=self.deltaTransX
            elif self.transVelX > self.velX:
                self.transVelX-=self.deltaTransX

            if abs(self.transDeltaRot-self.deltaRot)<=self.deltaDeltaRot*2:
                self.transDeltaRot=self.deltaRot
            elif self.transDeltaRot < self.deltaRot:
                self.transDeltaRot+=self.deltaDeltaRot
            elif self.transDeltaRot > self.deltaRot:
                self.transDeltaRot-=self.deltaDeltaRot

            self.rot+=self.transDeltaRot*self.rotDirection

            self.degreeRotY+=self.deltaRot
            if self.degreeRotY>360:
                self.degreeRotY=0

            if self.hp<=0:
                self.isDead=True
            else:
                self.isDead=False;

            self.posY+=self.transVelY

            if self.targetCell:
                #Get close to target
                (myX,myY)=self.get_center()
                (targetX,targetY)=self.targetCell.get_center()
                absX=abs(myX-targetX)
                absY=abs(myY-targetY)

                if absY >self.limitMax:
                    if myY<targetY:
                        self.velY=self.baseVelY
                    else:
                        self.velY=-self.baseVelY
                elif absY<self.limitMin:
                    if myY<targetY:
                        self.velY=-self.baseVelY
                    else:
                        self.velY=+self.baseVelY
                else:
                    self.velY=0

                if self.status=="Waiting1" and self.targetCell.velX==0 and abs(self.posY-self.targetCell.posY)<10:
                    self.status="Attacking"

                particlesToPop=[]
                for particle in self.attackParticles:
                    if particle.isDead==True:
                        particlesToPop.append(particle)
                for particle in particlesToPop:
                    self.attackParticles.pop(indexOf(self.attackParticles,particle))

                particlesToPop=[]
                for particle in self.hpParticles:
                    if particle.isDead==True:
                        particlesToPop.append(particle)
                for particle in particlesToPop:
                    self.hpParticles.pop(indexOf(self.hpParticles,particle))

                particlesToPop=[]
                for particle in self.shieldParticles:
                    if particle.isDead==True:
                        particlesToPop.append(particle)
                for particle in particlesToPop:
                    self.shieldParticles.pop(indexOf(self.shieldParticles,particle))

                ##Actions
                if self.status=="Attacking":
                    self.deltaRot=0.1
                    self.waitTicks+=1
                    if self.waitTicks>=self.totalWaitTicks:
                        self.waitTicks=0
                        self.status="Attacking2"
                        self.launchedParticles=0
                        #@TODO decide attack Power with fuzzy logic depending on shileds/distance
                        #Power is represented by number of particles to launch
                        #Puny: N=10|P=4, debil: N=34|P=6, medio: N=25|P=8, fuerte: N=40|P=8, muy fuerte N=50|P=9
                        if self.policy=="Fuzzy":
                            self.attackParticleNumber=25
                            self.attackPower=8
                        if self.policy=="Random":
                            self.attackParticleNumber,self.attackPower=ATTACK_DICT[random.choice(ATTACK_DICT.keys())]

                if self.status=="Attacking2":
                    self.deltaRot=0.1
                    if self.launchedParticles<self.attackParticleNumber:
                        self.launchedParticles+=1
                        self.attackParticles.append(AttackParticle(self.posX+self.width/2,self.posY,self.attackPower,self.targetCell))

                    if not self.attackParticles:
                        self.waitTicks+=1
                        if self.waitTicks>=self.totalWaitTicks:
                            self.waitTicks=0
                            self.status="Sucking"
                            #@TODO decide suckingForce with fuzzy logic depending on distance F=force D=delta
                            #Muy cerca: F=1|D=0.01, cerca: F=3|D=0.025, medio: F=6|D=0.06, lejos: F=8|D=0.065, muy lejos: F=10|D=0.09
                            if self.policy=="Fuzzy":
                                self.suckingForce=6
                                self.suckingDeltaForce=0.06
                            if self.policy=="Random":
                                self.suckingForce,self.suckingDeltaForce=DISTANCE_DICT[random.choice(DISTANCE_DICT.keys())]

                if self.status=="Sucking":
                    self.targetCell.posX-=self.suckingForce
                    self.suckingForce-=self.suckingDeltaForce
                    if self.suckingForce<=0:
                        self.status="Eating"
                    

                if self.status=="Eating":
                    self.deltaRot=-0.1
                    if self.posX+self.width<100:
                        self.posX+=1
                    if self.targetCell.shield>0:
                        self.shieldParticles.append(ShieldParticle(self.targetCell.posX+self.targetCell.width/2,self.targetCell.posY,4,self))
                        self.targetCell.shield-=2
                    elif len(self.shieldParticles)==0:
                        if self.targetCell.hp>0:
                            self.hpParticles.append(HpParticle(self.targetCell.posX+self.targetCell.width/2,self.targetCell.posY,2,self))
                            self.targetCell.hp-=2
                    if len(self.hpParticles)==0:
                        self.state="Waiting1"

            else:
                self.velX=0
                self.velY=0
                self.deltaRot=0
                self.status="Waiting1"

            if self.posY<=0:
                self.posY=0
            if self.posY+self.height>=WINDOW_SIZE:
                self.posY=WINDOW_SIZE-self.width
            if self.posX<=0:
                self.posX=0
            if self.posX+self.width>=100:
                self.posX=100-self.width

    def paint(self,window):
        for particle in self.shieldParticles:
            particle.paint(window)
        for particle in self.attackParticles:
            particle.paint(window)
        for particle in self.hpParticles:
            particle.paint(window)

        pixbuf = self.imagen
        pixbuf1=pixbuf.scale_simple(self.width,self.height,gtk.gdk.INTERP_BILINEAR)

        #visibility representation
        window.save()
        ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
        window.transform ( ThingMatrix )
        cairo.Matrix.translate(ThingMatrix, self.posX+self.width/2,self.posY+self.height/2)
        cairo.Matrix.rotate( ThingMatrix, self.rot) # Do the rotation
        cairo.Matrix.translate(ThingMatrix, -(self.posX+self.width/2),-(self.posY+self.height/2))
        window.transform ( ThingMatrix ) # and commit it to the context
        window.set_source_rgb(1,0,0)
        window.set_source_pixbuf(pixbuf1,self.posX,self.posY)
        window.paint()
        window.restore()

        if self.targetCell!=None:
            window.save()
            window.move_to(self.posX+self.width/2,self.posY+self.height/2)
            window.line_to(self.targetCell.posX+self.targetCell.width/2,
                self.targetCell.posY+self.targetCell.height/2)
            if self.status=="Analyzing":
                window.set_source_rgb(1,1,0)
            if self.status=="Attacking":
                window.set_source_rgb(1,0,0)
            if self.status=="Defending":
                window.set_source_rgb(0,1,1)
            if self.status=="Eating":
                window.set_source_rgb(0,1,0)

            window.stroke()
            window.restore()


