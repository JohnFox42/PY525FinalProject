#import statments
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import LightSource
import random
import rasterio
from scipy.ndimage import zoom
from collections import deque

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

def AveElevCheck(array,i,j):
    #Still need to be able to differentiate from rock and snow
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

def main() -> None:
    #Starting with a very basic verision of the abelian sandpile model
    '''
    Field = np.zeros([100,100])

    #Color map setup
    colors = ["green","blue"]
    cmap = LinearSegmentedColormap.from_list("CustomCmap",colors)

    #Randomly snowing on the field 
    for k in range(80001):
        i = random.randint(0,99)
        j = random.randint(0,99)
        Field[i,j] += 0.1
        Field = AveElevCheck(Field,i,j)
        if k % 10000 == 0:
            plt.pcolor(np.linspace(0,99,100),np.linspace(0,99,100),Field,cmap=cmap)    
            plt.colorbar()
            plt.show()


    '''
    #Color map setup
    colors = ["green","blue"]
    cmap = LinearSegmentedColormap.from_list("CustomCmap",colors)
    dataset = rasterio.open("PalisadesFingers.tif")
    data = dataset.read(1)
    high_res = zoom(data,5,order=1)
    plt.figure(0)
    plt.imshow(data,cmap=cmap,origin="lower")
    plt.colorbar()

    #Lighting the slope to make it look more realistic 
    '''
    ls = LightSource(azdeg=315,altdeg=45)
    rgb = ls.hillshade(high_res,vert_exag=5)

    plt.imshow(rgb,cmap="grey",interpolation="nearest",resample=False)
    plt.axis("off")
    plt.show()
    '''

    #Randomly snowing on the elevation map
    for k in range(10000):
        i = random.randint(0,112)
        j = random.randint(0,122)
        data[i,j] += 0.01
        data = AveElevCheck(data,i,j)    
    plt.figure(1)
    plt.imshow(data,cmap=cmap,origin="lower")
    plt.colorbar()
    plt.show()
    
