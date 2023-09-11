import cv2 as cv
import numpy as np
import sys
import random as rand
import runpy
import time

def get_pixel(click, x, y, flag_param, parameters):
    global x_pt, y_pt, drawing, top_left_point, bottom_right_point, original_image, resized_image
    
    if click == cv.EVENT_LBUTTONDOWN:
        serrin_selected = True
        clicked_pixel = resized_image[y, x]#format bgr
        cv.namedWindow('Color de pixel seleccionado, pulse "Esc" cuando este conforme')
        cv.moveWindow('Color de pixel seleccionado, pulse "Esc" cuando este conforme', 600,200)
        blank_image = np.zeros((100,500,3), np.uint8)
        blank_image[:]=(clicked_pixel[0],clicked_pixel[1],clicked_pixel[2])
        cv.imshow('Color de pixel seleccionado, pulse "Esc" cuando este conforme', blank_image)
        sys.argv = [' ', route, clicked_pixel[0],clicked_pixel[1],clicked_pixel[2]]

def draw_bounding_box(click, x, y, flag_param, parameters):
    global x_pt, y_pt, drawing, top_left_point, bottom_right_point, original_image, resized_image
    
    if click == cv.EVENT_LBUTTONDOWN:
        drawing = True
        x_pt, y_pt = x, y   

    elif click == cv.EVENT_MOUSEMOVE:
        if drawing:
            top_left_point, bottom_right_point = (x_pt,y_pt), (x,y)
            image[y_pt:y, x_pt:x] = 255 - resized_image[y_pt:y, x_pt:x]
            cv.rectangle(image, top_left_point, bottom_right_point, (0,255,0), 2)

    elif click == cv.EVENT_LBUTTONUP:
        drawing = False
        top_left_point, bottom_right_point = (x_pt,y_pt), (x,y)
        image[y_pt:y, x_pt:x] = 255 - image[y_pt:y, x_pt:x]
        cv.rectangle(image, top_left_point, bottom_right_point, (0,255,0), 2)
        bounding_box = (x_pt, y_pt, x-x_pt, y-y_pt)

        global start
        start = time.time()
        grabcut_algorithm(original_image, bounding_box)
        
        
def grabcut_algorithm(original_image, bounding_box):
    
    global result_image
    segment = np.zeros(original_image.shape[:2],np.uint8)
    
    #revert scaling factor for processing full size image
    x,y,width,height = bounding_box
    x = int((100/scale_percent)*x)
    y = int((100/scale_percent)*y)
    width = int((100/scale_percent)*width)
    height = int((100/scale_percent)*height)
    bounding_box = x,y,width,height
    
    segment[y:y+height, x:x+width] = 1

    background_mdl = np.zeros((1,65), np.float64)
    foreground_mdl = np.zeros((1,65), np.float64)
    
    cv.grabCut(original_image, segment, bounding_box, background_mdl, foreground_mdl, 5,
    cv.GC_INIT_WITH_RECT)
    
    new_mask = np.where((segment==2)|(segment==0),0,1).astype('uint8')
    
    original_image = original_image*new_mask[:,:,np.newaxis]
    
    
    result_image = cv.resize(original_image, dim, interpolation = cv.INTER_AREA)
    cv.imshow('Resultado del procesamiento', result_image)
    
    cv.imwrite(route, original_image)
    
    
if __name__=='__main__':
    
    img_code = str(rand.randrange(10000))
    route = './images/trees/segmented_trees/trees_cut'+img_code+'.jpg'
    drawing = False
    serrin_selected = False
    top_left_point, bottom_right_point = (-1,-1), (-1,-1)
    clicked_pixel = None

    #read image and set standard size 
    original_image = cv.imread(sys.argv[1])
    if(sys.argv[1] == ""):
        print("Error, debe seleccionar una ruta o la ruta seleccionada no existe.")
        exit()
        
    original_width = int(original_image.shape[1])
    original_height = int(original_image.shape[0])
    original_dim = (original_width, original_height)

    scale_percent = 18 # percent of original size
    width = int(original_image.shape[1] * (scale_percent / 100))
    height = int(original_image.shape[0] * (scale_percent / 100))
    dim = (width, height)
    

    resized_image = cv.resize(original_image, dim, interpolation = cv.INTER_AREA)
    
    image = resized_image.copy()
    cv.namedWindow('Seleccione la zona a extraer del fondo')
    cv.moveWindow('Seleccione la zona a extraer del fondo', 200,30)
    cv.setMouseCallback('Seleccione la zona a extraer del fondo', draw_bounding_box)
    
    while True:
        cv.imshow('Seleccione la zona a extraer del fondo', image)
        c = cv.waitKey(1)
        if c == 27:
            break
            
    cv.destroyAllWindows()
    
    cv.namedWindow('Seleccione un pixel que sea serrin')
    cv.moveWindow('Seleccione un pixel que sea serrin', 40,30)
    cv.setMouseCallback('Seleccione un pixel que sea serrin', get_pixel)

    while True:
        cv.imshow('Seleccione un pixel que sea serrin', result_image)
        c = cv.waitKey(1)
        if c == 27:
            break
            
    cv.destroyAllWindows()

    if not serrin_selected: sys.argv = [' ', route]#Prevent argument not passing due to not selecting a pixel    

    end = time.time()   
    print('El tiempo de ejecución de segment es: ', end-start, 'segundos')
    
    runpy.run_path('host.py',run_name = '__main__')