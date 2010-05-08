# coding: utf-8


import gtk
#import cairo
import gobject
import pygtk

import random
from operator import indexOf

pygtk.require('2.0')

from sprite import Sprite
from virus import Virus
from cell import Cell
from virus import DEFAULT_WIDTH as VIRUS_WIDTH, DEFAULT_HEIGHT as VIRUS_HEIGHT
from cell import DEFAULT_WIDTH as CELL_WIDTH, DEFAULT_HEIGHT as CELL_HEIGHT
from display import display_simulation
from hud import Hud
from constants import WINDOW_SIZE, TOTAL_VIRUS, MAX_CELLS, TRAIN_CELLS
from constants import CHARACTERISTICS_DICT
from constants import TRAINING_ZONE_LIMIT
from constants import MAX_CELLS
virList =[]
cellList =[]

from neuralNetwork import create_trained_network
from neuralNetwork import test_network
from neuralNetwork import transform_cell

#Lienzo es donde se pintara todo
class Lienzo(gtk.DrawingArea):
    def __init__(self, ventana):
        super(Lienzo, self).__init__()
        #Cambiar el color de fondo de la ventana
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
        # Pedir el tamano de la ventana
        self.set_size_request(WINDOW_SIZE,WINDOW_SIZE)
        #Asignar la ventana que recibe de paramentro a la ventana que se
        #utilizara en el lienzo
        self.ventana=ventana
        #expose-event es una propiedad de DrawingArea que le dice como
        #dibujares, aqui le decimos que utilize nuestra funcion paint
        #para ese evento en vez del que trae por defaul.
        self.connect("expose-event", self.paint)
        #reconocer cuando oprimes y sueltas el mouse
        self.connect("button_press_event",self.button_press)
        self.connect("button_release_event",self.button_release)
        self.connect("motion_notify_event",self.actualizar_dragged)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.BUTTON_RELEASE_MASK|gtk.gdk.POINTER_MOTION_MASK)
        self.hud=Hud()
        self.minTimeToNextCell=200
        self.maxTimeToNextCell=200
        self.ticksToNextCell=random.randint(self.minTimeToNextCell,self.maxTimeToNextCell)

        #cells
        self.virus=[Virus(
               random.randint(0,100-VIRUS_WIDTH),
               random.randint(0,WINDOW_SIZE-CELL_HEIGHT),
                ) for i in xrange(TOTAL_VIRUS)]
        self.cells=[]
        
        self.draggingObject = None
        self.objetoSeleccionado=[]

        self.currentState="Running"
        self.classificationList=["Target","Enemy","Food"]

        self.trainingZoneLimit=WINDOW_SIZE-100

        self.fnn = None

        self.init_simulation()
        self.run_simulation()

    def actualizar_dragged(self,widget,event):
        if self.draggingObject:
            self.draggingObject.posX=event.x
            self.draggingObject.posY=event.y

    def on_timer(self):
        self.update()
        return True

    def init_simulation(self):
        """Inicializacion de valores"""
        self.reset()
        gobject.timeout_add(20, self.on_timer)

    def run_simulation(self,extra=0):
        self.currentState="Running"
        for cell in self.cells:
            cell.width=20
            cell.height=20
            cell.velX=random.randint(1,5)/5.0
            cell.velY=random.random()
            break

    def reset(self,extra=0):
        self.currentState="Running"
        self.trainingSet=[]

    def update(self):
        self.queue_draw()
        
        cellsToPop=[]
        for cell in self.cells:
            cell.update(self.currentState)
            if cell.posX+cell.width<0 or cell.isDead==True:
                cellsToPop.append(cell)
        for cell in cellsToPop:
            self.cells.pop(indexOf(self.cells,cell))
            for virus in self.virus:
                if cell==virus.targetCell:
                    virus.targetCell=None
                    break

        if self.currentState=="Running":
            if self.ticksToNextCell<=0:
                if len(self.cells)<MAX_CELLS:
                    self.ticksToNextCell=random.randint(self.minTimeToNextCell,self.maxTimeToNextCell)
                    newCell=Cell(WINDOW_SIZE,
                        random.randint(0,TRAINING_ZONE_LIMIT-CELL_HEIGHT))
                    newCell.velX=-(random.random()+3)
                    newCell.type="NormalCell"
                    self.cells.append(newCell)
            else:
                self.ticksToNextCell-=1

            #update virus
            for virus in self.virus:
                if not virus.isDead:
                    virus.update(self.currentState)
                    if len(self.cells)>0 and virus.targetCell==None and virus.status=="Waiting1":
                        for cell in self.cells:
                            if cell.isAvailable:
                                virus.targetCell=cell
                                cell.isAvailable=False
                                break

    def paint(self, widget, event):
        """Nuestro metodo de pintado propio"""

        #Se crea un widget de cairo que despues se usara para desplegar
        #todo en la ventana
        cr = widget.window.cairo_create()
        #Le decimos a cairo que pinte su widget por primera vez.
        cr.set_source_rgb(0,0,0)
        cr.paint()

        #paint game info
        cr.set_source_rgb(1,1,1)
        cr.save()
        cr.move_to(15,15)
        text="To next cell: %d" % (self.ticksToNextCell)
        cr.show_text(text)
        cr.restore()

        cr.set_source_rgb(1,1,1)
        cr.move_to(100, 15)
        cr.line_to(100,WINDOW_SIZE-15)
        cr.set_line_width(0.6)
        cr.stroke()

        #pintar a los agentes
        if self.currentState=="Training":
            for i in xrange(len(self.classificationList)):
                text=str(self.classificationList[i])
                if i==0:
                    posXText=(self.divisionPoints[i])/2-(len(text)/2)*5
                else:
                    posXText=(self.divisionPoints[i-1]+self.divisionPoints[i])/2-(len(text)/2)*5
                posYText=15
                cr.save()
                cr.move_to(posXText,posYText)
                cr.set_source_rgba(1,1,1,0.7)
                cr.show_text(text)
                cr.restore()
                
            display_simulation(cr,[],self.cells)
            self.hud.display_cells(cr,self.cells)
            self.hud.display_viruses(cr, [])

        if self.currentState=="Running":
            for (cell,type) in self.trainingSet:
                cell.paint(cr)

            display_simulation(cr,self.virus,self.cells)
            self.hud.display_cells(cr,self.cells)
            self.hud.display_viruses(cr, self.virus)

        #pintar efecto de selección sobre un agente
        if self.objetoSeleccionado:
            cr.set_line_width(2)
            cr.set_source_rgba(random.random(), 1, random.random(), 0.3)
            cr.rectangle(self.objetoSeleccionado.posX-20,self.objetoSeleccionado.posY-20,
                            self.objetoSeleccionado.width+40, self.objetoSeleccionado.height+40)

            cr.stroke()
                
        
    #Para drag & drop
    def button_press(self,widget,event):
        if event.button == 1:
            self.objetoSeleccionado=[]
            lstTemp = self.virus+self.cells
            for ob in lstTemp:
                if ob.drag(event.x,event.y):
                    self.draggingObject = ob
                    self.objetoSeleccionado=ob
                    break
                    
    def button_release(self,widget,event):
        if self.draggingObject:
            self.draggingObject.drop(event.x,event.y)
            self.draggingObject = None

    def pausar(self):
        self.corriendo=False

    def correr(self):
        self.corriendo=True
        
#    def mainloop(self):
#        while self.corriendo:
#            # Process all pending events.
#            self.update()
#            while gtk.events_pending():
#                gtk.main_iteration(False)
#                # Generate an expose event (could just draw here as well).
#            self.queue_draw()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Main(gtk.Window):
    def __init__(self):
        super(Main, self).__init__()
        self.set_title('Biokterii')
        self.set_size_request(WINDOW_SIZE,WINDOW_SIZE+20)
        self.set_resizable(True)
        self.set_position(gtk.WIN_POS_CENTER)
        #mainBox contiene el menu superior, contentBox(menu,lienzo) y el menu inferior
        self.mainBox = gtk.VBox(False,0)
        self.mainBox.set_size_request(WINDOW_SIZE,WINDOW_SIZE)
        
        #contentBox contiene el menu lateral y lienzo
        self.contentBox= gtk.HBox(False,0) #Recibe False para no se homogeneo
        
        self.lienzo=Lienzo(self)
        self.lienzo.set_size_request(WINDOW_SIZE+20,WINDOW_SIZE)
        
        self.contentBox.pack_start(self.lienzo, expand=True, fill=True, padding=0)

        #Menu bar
        menuBar = gtk.MenuBar()

        filemenu = gtk.Menu()
        filem = gtk.MenuItem("Actions")
        filem.set_submenu(filemenu)

        annealMenu = gtk.MenuItem("Reset & Train")
        annealMenu.connect("activate", self.lienzo.reset)
        filemenu.append(annealMenu)

        annealMenu = gtk.MenuItem("Start Simulation")
        annealMenu.connect("activate", self.lienzo.run_simulation)
        filemenu.append(annealMenu)

        annealMenu = gtk.MenuItem("Test random cell")
        #annealMenu.connect("activate", None)
        filemenu.append(annealMenu)

        exit = gtk.MenuItem("Exit")
        exit.connect("activate", gtk.main_quit)
        filemenu.append(exit)

        menuBar.append(filem)

        menuBox = gtk.HBox(False, 2)
        menuBox.pack_start(menuBar, False, False, 0)

        #Empaquetado de todos los controles
        self.mainBox.pack_start(menuBox,expand=True,fill=True,padding=0)
        self.mainBox.pack_start(self.contentBox,expand=True, fill=True, padding=0)

        #Agregar la caja que contiene todo a la ventana
        self.add(self.mainBox)
        self.connect("destroy", gtk.main_quit)
        self.show_all()

    def pausar_lienzo(self, widget):
        self.lienzo.pausar()

    def correr_lienzo(self, widget):
        self.lienzo.correr()

#    def cerrar_lienzo(self,widget):
#        self.lienzo.corriendo=False
#        gtk.main_quit

if __name__ == '__main__':
    Main()
    gtk.main()
