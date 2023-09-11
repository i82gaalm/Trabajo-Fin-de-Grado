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
        # Apply approxPolyDP to simplify the contour as much as possible
        epsilon = 0.01 * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        simplified_contours.append(approx)

    return contours2



def SetContoursVector(mat):
    ret,thresh = cv.threshold(mat,127,255,0)
    contours,hierarchy = cv.findContours(thresh,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
    return contours

#----------------------------------main program------------------------------------------#

#read image and set standard size

start = time.time()

if(sys.argv[1] == ""):
        print("Error, debe seleccionar una ruta o la ruta seleccionada no existe.")
        exit() 
else:
    image = cv.imread(sys.argv[1])

if(image is None):
    print("Error, debe seleccionar una ruta o la ruta seleccionada no existe.")
    exit()

    
#Standard size
scale = 1
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
        serrin = np.array([sys.argv[4],sys.argv[3],sys.argv[2]])#swapped index due to bgr format instead of rgb
            


#Set color limits

#LIGHT BROWN (SERRIN)
#Red channel: Lower limit around 150-180, Upper limit around 200-230
#Green channel: Lower limit around 100-130, Upper limit around 150-180
#Blue channel: Lower limit around 50-80, Upper limit around 100-130
rng = 30
min_agujero= np.array([1,1,1])
max_agujero= np.array([13,13,13])
if(('serrin' not in globals()) or (serrin.size == 0)):
    print("Aviso, no se ha establecido un valor medio del serrín, estableciendo valores medios.")
    min_serrin= np.array([155,110,70])
    max_serrin= np.array([240,185,135])
else:
    min_serrin= np.array([serrin[0]-rng,serrin[1]-rng,serrin[2]-rng])
    max_serrin= np.array([serrin[0]+rng,serrin[1]+rng,serrin[2]+rng])


#-----------------------------------OpenCL-----------------------------------------------#


#choose platform and device

platform = cl.get_platforms()[0]
gpu = cl.get_platforms()[0].get_devices()


#creating context

context = cl.Context(
                        dev_type = cl.device_type.ALL,
                        properties= [(cl.context_properties.PLATFORM, platform)])


#creating command queue

queue = cl.CommandQueue(context)


#Creating buffers
mf = cl.mem_flags

imageBuffer = image.astype(np.uint8)

#image buffer and other arguments
a_g = cl.Buffer(context,mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=imageBuffer)
max_agujero_buffer = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=max_agujero)
min_agujero_buffer = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=min_agujero)
min_serrin_buffer = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=min_serrin)
max_serrin_buffer = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=max_serrin)


rows = np.intc(imageBuffer.shape[0])
cols = np.intc(imageBuffer.shape[1])


#Provisional result matrix dimensioning and counter result
resBuffer = cv.cvtColor(image,cv.COLOR_BGR2GRAY).astype(np.uint8)
num_pixel_serrin = np.empty_like(0, dtype=np.int32)
num_pixel_total= np.empty_like(0, dtype=np.int32)

#result vector buffers
b_g_agujero = cl.Buffer(context,mf.WRITE_ONLY ,  resBuffer.nbytes)    
b_g_serrin = cl.Buffer(context,mf.WRITE_ONLY ,  resBuffer.nbytes)
b_g_count = cl.Buffer(context, mf.WRITE_ONLY, num_pixel_serrin.nbytes)
b_g_total = cl.Buffer(context, mf.WRITE_ONLY, num_pixel_total.nbytes)

#creating program
src = ''.join(open('kernel.cl').readlines())

program = cl.Program(context,src).build()

#setting arguments and launching program

program.ctm(queue, imageBuffer.shape, None, a_g, b_g_agujero, b_g_serrin, b_g_count, b_g_total, rows, cols, max_agujero_buffer, min_agujero_buffer, min_serrin_buffer, max_serrin_buffer)


#getting results

result_agujero = np.empty_like(resBuffer)
result_serrin = np.empty_like(resBuffer)
result_count = np.empty_like(num_pixel_serrin)
result_pixels = np.empty_like(num_pixel_total)
cl.enqueue_copy(queue,result_agujero,b_g_agujero)
cl.enqueue_copy(queue,result_serrin,b_g_serrin)
cl.enqueue_copy(queue,result_count,b_g_count)
cl.enqueue_copy(queue,result_pixels,b_g_total)


contours = SetContoursVector(result_agujero)
contours = np.array(contours,dtype = object)
contours = DeleteSmallObjects(contours)
cv.drawContours(image,contours,-1,(0,255,73),3)



# Calculate the area of result_agujero contours
agujero_area = 0
for contour in contours:
    agujero_area += cv.contourArea(contour)

# Calculate the percentage of result_agujero
agujero_percentage = (agujero_area / result_pixels) * 100
serrin_percentage = (result_count / result_pixels) * 100

# Print the percentage
print("Porcentaje de agujeros en el tronco: ", agujero_percentage)
print("Porcentaje de serrín en el tronco: ", serrin_percentage)


#--------------------------------------------------OpenCV----------------------------------------------------#



code = rand.randrange(10000)
#saving images
cv.imwrite('./result/res_agujero'+str(code)+'.jpg',result_agujero)
cv.imwrite('./result/res_serrin'+str(code)+'.jpg',result_serrin)
cv.imwrite('./result/contours'+str(code)+'.jpg',image)

#resize images
result_agujero = cv.resize(result_agujero,(450,800))
result_serrin = cv.resize(result_serrin,(450,800))
image = cv.resize(image,(450,800))

file = open("result/results.txt", "a")
file.write("Codigo_imagenes: ")
file.write(str(code))
file.write(", Porcentaje_serrin: ")
file.write(str(serrin_percentage))
file.write("%, Porcentaje_agujeros: ")
file.write(str(agujero_percentage))
file.write("%\n")
file.close()

cv.imshow('Serrin',result_serrin)
cv.moveWindow('Serrin',500,0)
cv.imshow('Agujeros identificados',image)
cv.moveWindow('Agujeros identificados',1000,0)

end = time.time()   
print('El tiempo de ejecución de host y kernel es: ', end-start, 'segundos')


cv.waitKey(0)