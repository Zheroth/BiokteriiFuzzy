

DISPLAY_IDS=True

def display_simulation(window,virusList,cellList):
    """Fucntion that diplays the whole simulation"""
    display_virus(window,virusList)
    display_cells(window,cellList)

def display_virus(window,virusList):
    """Fucntion that diplays the virus"""
    for virus in virusList:
        virus.paint(window)

def display_cells(window,cellList):
    """Fucntion that diplays the virus"""
    for cell in cellList:
        cell.paint(window)
