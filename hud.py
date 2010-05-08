from sprite import Sprite
from cell import Cell

ID_PADDING=[0,-5]

class Hud():
    def __init__(self):
        self.allVisible=True
        self.idVisible=True
        self.boundingBoxVisible=True
        self.window=None

    def display_viruses(self,window,objectList):

        if self.allVisible:
            if self.idVisible:
                for object in objectList:
                    if isinstance(object,Sprite):
                        text=str(object)
                        posXText=object.posX+object.width/2-(len(text)/2)*5
                        posYText=object.posY+ID_PADDING[1]
                        window.move_to(posXText,posYText)
                        window.set_source_rgba(1,1,1,0.7)
                        window.show_text(text)

    def display_cells(self,window,cellList):

        if self.allVisible:
            if self.idVisible:
                for cell in cellList:
                    if isinstance(cell,Cell) and cell.status!="Dead":
                        text=str(cell)
                        posXText=cell.posX+cell.width/2-(len(text)/2)*5
                        posYText=cell.posY+ID_PADDING[1]
                        window.move_to(posXText,posYText)
                        window.set_source_rgba(1,1,1)
                        window.show_text(text)

            