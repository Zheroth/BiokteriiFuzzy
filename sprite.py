import random

DEFAULT_WIDTH=10
DEFAULT_HEIGHT=10

class Sprite():
    def __init__(self, posX=0, posY=0):
        """Default initial sprite values"""
        self.id=random.randint(0,10000);
        self.posX=posX
        self.posY=posY
        self.width=DEFAULT_WIDTH
        self.height=DEFAULT_HEIGHT
        self.colPosX=self.posX
        self.colPosY=self.posY
        self.colWidth=DEFAULT_WIDTH
        self.colHeight=DEFAULT_HEIGHT
        self.isVisible=True
        self.color=(random.random(),random.random(),random.random())
        self.alpha=1.0
    def __str__(self):
        return "Sprite - Id: %d pos:[%d,%d]" % (self.id,self.posX,self.posY)

    def get_type(self):
        return "Sprite"

    def get_center(self):
        """Returns the center of the sprite in a two value tuple """
        centerX=self.posX+(self.width/2)
        centerY=self.posY+(self.height/2)
        return [centerX,centerY]

    def drag(self,xMouse, yMouse):
        if self.is_colliding_with_mouse(xMouse, yMouse):
                self.dragging=True
                return True
        return False

    def drop(self,xMouse,yMouse):
        if self.is_colliding_with_mouse(xMouse, yMouse):
            self.dragging=False
        if self.dragging:
            self.dragging=False
            self.posX=xMouse
            self.posY=yMouse

    def is_colliding_with_mouse(self, xMouse,yMouse):
        if self.posX<=xMouse and self.posX+self.width>=xMouse and self.posY<=yMouse and self.posY+self.height>=yMouse:
            return True
        return False

    def is_colliding_with(self, sprite):
        if sprite:
            if self.posX+self.width>sprite.posX and self.posX < sprite.posX+sprite.width:
                if self.posY+self.height>sprite.posY and self.posY < sprite.posY+sprite.height:
                    return True
        return False

    def update(self):
        pass

    def paint(self,window):
        """How a sprite is painted by default"""
        if self.isVisible:
            window.rectangle(self.posX,self.posY,self.width,self.height)
            window.set_source_rgba(self.color[0],self.color[1],self.color[2],self.alpha)
            window.fill()
