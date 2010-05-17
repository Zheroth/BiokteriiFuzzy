import gtk

WINDOW_SIZE=700
TRAINING_ZONE_LIMIT=WINDOW_SIZE-100

TOTAL_VIRUS = 2
MAX_CELLS = 3  #Max number of cells on screen
TRAIN_CELLS=0


#imagenes
VIRUS_IMAGE=gtk.gdk.pixbuf_new_from_file("./resources/virus/virus.png")
COLOR_LIST=[("Red",[0.8,0.2,0.1]),("Green",[0,0.8,0.3]),("Blue",[0,0.8,0.8])]

COLOR_RGB_LIST=["Red","Green","Blue"]
INNER_COLOR_LIST=["Red","Green","Blue","Black"]

OUTER_SHAPE_LIST=["Simple","CircleStroke","CircleFill","Square","DoubleSquare"]
ROT_DIRECTION_LIST=[("Left",-1),("Right",1)]
INNER_SHAPE_LIST=["None","CircleStroke","CircleFill","SquareStroke","SquareFill"]

CHARACTERISTICS_DICT = {
"outerShape":OUTER_SHAPE_LIST,
"outerColor":COLOR_RGB_LIST,
"outerRotation":["Left","Right"],
"innerShape":INNER_SHAPE_LIST,
"innerColor":INNER_COLOR_LIST
}

EVALUATE_FUNC_DICT ={
"outerShape":lambda x:x.outerShape,
"outerColor":lambda x:x.outerColor,
"outerRotation":lambda x:x.outerRotation,
"innerShape":lambda x:x.innerShape,
"innerColor":lambda x:x.innerColor
}