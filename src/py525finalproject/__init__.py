#import statments
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import LightSource
import random
import rasterio
from scipy.ndimage import zoom
from collections import deque
from functools import singledispatch

def AveCheck(array,i,j):
    if array[i,j] >= 10:
        array[i,j] -= 4
        if i+1 < 10:
            array[i+1,j] += 2
            array = AveCheck(array,i+1,j)
        if j+1 < 10:
            array[i,j+1] += 1
            array = AveCheck(array,i,j+1)
        if j-1 > -1:
            array[i,j-1] += 1
            array = AveCheck(array,i,j-1)
    return array

#Function Overloading b/c I miss C++ sometimes 
@singledispatch
def AveElevCheck(background, array, i ,j):
    raise TypeError("Unsupported Background Type")

@AveElevCheck.register(type(None))
def _(background,array,i,j):
    #Iterative approach gotten from chatgpt 
    rows, cols = array.shape
    queue = deque([(i,j)])
    while queue:
        i, j = queue.popleft()
        #Bounds checking
        neighbors = []
        if i+1 < rows:
            neighbors.append((i+1,j))
        if i-1 >= 0:
            neighbors.append((i-1,j))
        if j+1 < cols:
            neighbors.append((i,j+1))
        if j-1 >= 0:
            neighbors.append((i,j-1))

        #Calculate elevation differences 
        drops = []
        for ni,nj in neighbors:
            difference = array[i,j] - array[ni,nj]
            if np.arctan(difference) >= np.pi/4:
                drops.append((ni,nj,difference))

        #If no eligible neighbors
        if len(drops) == 0:
            continue

        #Find minimum elevation drop
        height = min(drop[2] for drop in drops)
        direc = len(drops)
        AveMag = height/(direc+1)

        #Avelanche Materials 
        array[i,j] -= height*(direc/(direc+1))
        for ni,nj, difference in drops:
            array[ni,nj] += AveMag
            queue.append((ni,nj))

    return array   

@AveElevCheck.register(np.ndarray)
def _(background,array,i,j):
    rows, cols = array.shape
    queue = deque([(i,j)])
    while queue:
        i, j = queue.popleft()
        if background[i,j] == array[i,j]:
            continue
        #Bounds checking
        neighbors = []
        if i+1 < rows:
            neighbors.append((i+1,j))
        if i-1 >= 0:
            neighbors.append((i-1,j))
        if j+1 < cols:
            neighbors.append((i,j+1))
        if j-1 >= 0:
            neighbors.append((i,j-1))

        #Calculate elevation differences 
        drops = []
        for ni,nj in neighbors:
            difference = array[i,j] - array[ni,nj]
            if np.arctan(difference) >= 2*np.pi/9:
                AveMaterial = array[i,j] - background[i,j]
                drops.append((ni,nj,AveMaterial))

        #If no eligible neighbors
        if len(drops) == 0:
            continue

        #Find minimum elevation drop
        height = min(drop[2] for drop in drops)
        direc = len(drops)
        AveMag = height/(direc+1)

        #Avelanche Materials 
        array[i,j] -= height*(direc/(direc+1))
        for ni,nj, difference in drops:
            array[ni,nj] += AveMag
            queue.append((ni,nj))

    return array

def main() -> None:
    #Color map setup
    colors = ["green","blue"]
    cmap = LinearSegmentedColormap.from_list("CustomCmap",colors)

    #Elevation based abelian sandpile
    #Initial Field
    Field = np.zeros([100,100])
    plt.pcolor(np.linspace(0,99,100),np.linspace(0,99,100),Field,cmap=cmap)    
    plt.colorbar()
    plt.show()

    #Randomly snowing on the field 
    for k in range(80000):
        i = random.randint(0,99)
        j = random.randint(0,99)
        Field[i,j] += 0.1
        Field = AveElevCheck(None,Field,i,j)
        if (k+1) % 10000 == 0:
            plt.pcolor(np.linspace(0,99,100),np.linspace(0,99,100),Field,cmap=cmap)    
            plt.colorbar()
            plt.show()
    
    #Color map setup
    colors = ["green","blue"]
    cmap = LinearSegmentedColormap.from_list("CustomCmap",colors)

    #Sandpile applied to the fingers 
    #Getting elevation data 
    dataset = rasterio.open("PalisadesFingers.tif")
    data = dataset.read(1)
    BedRock = np.copy(data)
    HighResInitial = zoom(data,5,order=1)

    #Lighting the slope to make it look more realistic 
    ls = LightSource(azdeg=315,altdeg=45)
    rgbInitial = ls.hillshade(HighResInitial,vert_exag=5)

    #Showing the initial contour map
    plt.figure(0)
    plt.imshow(rgbInitial,cmap="grey",interpolation="nearest",resample=False)
    plt.axis("off")

    #Randomly snowing on the elevation map
    for k in range(10000000):
        i = random.randint(0,112)
        j = random.randint(0,122)
        data[i,j] += 0.01
        data = AveElevCheck(data,BedRock,i,j)
    HighResFinal =  zoom(data,5,order=1)
    rgbFinal = ls.hillshade(HighResFinal,vert_exag=5)

    #Showing the final contour map 
    plt.figure(1)
    plt.imshow(rgbFinal,cmap="grey",interpolation="nearest",resample=False)
    plt.axis("off")
    plt.show()
    
