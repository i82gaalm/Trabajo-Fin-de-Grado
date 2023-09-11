import pyopencl as cl
import cv2 as cv
import numpy  as np
import sys
import time
import random as rand


def DeleteSmallObjects(contours):
    delete = []
    for i in range(len(contours)):
        if(len(contours[i]) < 50): 
                delete.append(i)
    contours2 = np.delete(contours,delete,0)
    simplified_contours = []
    for contour in contours2:
        epsilon = 0.01 * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        simplified_contours.append(approx)

    return contours2



def SetContoursVector(mat):
    ret,thresh = cv.threshold(mat,127,255,0)
    contours,hierarchy = cv.findContours(thresh,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
    return contours


start = time.time()


image = cv.imread('images/trees/raw_trees/20230125_113841.jpg')

if(image is None):
    print("Error, debe seleccionar una ruta o la ruta seleccionada no existe.")
    exit()

scale = 8
y = 1008*scale
x = 567*scale
tam =x*y 
size = (x,y)

pixels = image.shape[0] * image.shape[1]

if(pixels != tam):
    print("Tamaño de imagen distinto al adecuado, redimensionando...")
    image = cv.resize(image,size)


if(len(sys.argv)>3):
    if(sys.argv[2] == "" or sys.argv[3] == "" or sys.argv[4] == ""):
            print("Aviso, no se ha establecido un valor medio del serrín.")
    else:
        val_serrin = np.array([sys.argv[4],sys.argv[3],sys.argv[2]])
            


rng = 30
min_agujero= np.array([0,0,0])
max_agujero= np.array([13,13,13])
if(('val_serrin' not in globals()) or (val_serrin.size == 0)):
    print("Aviso, no se ha establecido un valor medio del serrín, estableciendo valores medios.")
    min_serrin= np.array([165,110,70])
    max_serrin= np.array([230,185,135])
else:
    min_serrin= np.array([val_serrin[0]-rng,val_serrin[1]-rng,val_serrin[2]-rng])
    max_serrin= np.array([val_serrin[0]+rng,val_serrin[1]+rng,val_serrin[2]+rng])

array = cv.cvtColor(image,cv.COLOR_BGR2GRAY).astype(np.uint8)
agujero = np.empty_like(array)
serrin = np.empty_like(array)
result_pixels = 0
result_count = 0


for x in range(image.shape[1]):
    for y in range(image.shape[0]):
        colors = image[y,x]
        red = colors[0]
        green = colors[1]
        blue = colors[2]
        result_pixels+=1
        if(red >= min_agujero[0] and green >= min_agujero[1] and blue >= min_agujero[2]):
            if(red <= max_agujero[0] and green <= max_agujero[1] and blue <= max_agujero[2]):
                agujero[y,x] = 255
                
        if(red >= min_serrin[0] and green >= min_serrin[1] and blue >= min_serrin[2]):
            if(red <= max_serrin[0] and green <= max_serrin[1] and blue <= max_serrin[2]):
                serrin[y,x] = 255
                result_count+=1

contours = SetContoursVector(agujero)
contours = np.array(contours,dtype = object)
contours = DeleteSmallObjects(contours)
cv.drawContours(image,contours,-1,(0,255,73),3)


agujero_area = 0
for contour in contours:
    agujero_area += cv.contourArea(contour)

agujero_percentage = (agujero_area / result_pixels) * 100
serrin_percentage = (result_count / result_pixels) * 100

print("Porcentaje de agujeros en el tronco: ", agujero_percentage)
print("Porcentaje de serrín en el tronco: ", serrin_percentage)


result_agujero = cv.resize(agujero,(450,800))
result_serrin = cv.resize(serrin,(450,800))

cv.imshow('Serrin',result_serrin)
cv.moveWindow('Serrin',500,0)
cv.imshow('Agujeros identificados',result_agujero)
cv.moveWindow('Agujeros identificados',1000,0)

end = time.time()   
print('El tiempo de ejecución es: ', end-start, 'segundos')


cv.waitKey(0)