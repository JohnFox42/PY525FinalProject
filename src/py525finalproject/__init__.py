#import statments
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import LightSource
import random
import rasterio
from scipy.ndimage import zoom

def AveCheck(array,i,j):
    #Still need to add in bounds checks
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

def main() -> None:
    #Starting with a very basic verision of the abelian sandpile model
    Field = np.zeros([100,100])

    #Color map setup
    colors = ["green","blue"]
    cmap = LinearSegmentedColormap.from_list("CustomCmap",colors)

    #Randomly snowing on the field 
    for k in range(80001):
        i = random.randint(0,99)
        j = random.randint(0,99)
        Field[i,j] += 1
        AveCheck(Field,i,j)
        if k % 10000 == 0:
            plt.pcolor(np.linspace(0,99,100),np.linspace(0,99,100),Field,cmap=cmap,vmin=0,vmax=9)    
            plt.colorbar()
            plt.show()
    
    dataset = rasterio.open("PalisadesFingers.tif")
    data = dataset.read(1)
    high_res = zoom(data,5,order=1)

    #Lighting the slope to make it look more realistic 
    ls = LightSource(azdeg=315,altdeg=45)
    rgb = ls.hillshade(high_res,vert_exag=5)

    plt.imshow(rgb,cmap="grey",interpolation="nearest",resample=False)
    plt.axis("off")
    plt.show()
    
