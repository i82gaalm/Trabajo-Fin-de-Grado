from tkinter import filedialog
from tkinter import *
from tkinter.ttk import*
from functools import partial
import runpy
import sys

def OpenFileSegment(img):
    archivo_abierto = StringVar()
    archivo_abierto.set(filedialog.askopenfilename(initialdir = "./images/trees/raw_trees", title = "Seleccione archivo", filetypes = (("jpg files", " .jpg"),("jpeg files", " .jpeg"),("all files","*.*"))))
    img.set(archivo_abierto.get())
    if archivo_abierto.get()=="":
            root = Tk()
            root.title("WARNING")
            root.config(width="700", height="200",background = "#eced87")
            frame1 = Frame(root)
            frame1.pack()
            texto =Label(frame1, text = "DEBE SELECCIONAR UNA IMAGEN PARA EXTRAER EL FONDO", background = "#eced87")
            texto.pack()
            root.mainloop()
            exit()
    sys.argv = [' ',img.get()]
    runpy.run_path('segment.py',run_name = '__main__')
    
def OpenFileMain(img):
    archivo_abierto = StringVar()
    archivo_abierto.set(filedialog.askopenfilename(initialdir = "./images/trees/segmented_trees", title = "Seleccione archivo", filetypes = (("jpeg files", " .jpg"),("all files","*.*"))))
    if archivo_abierto.get()=="":
            root = Tk()
            root.title("WARNING")
            root.config(width="700", height="200",background = "#eced87")
            frame1 = Frame(root)
            frame1.pack()
            texto =Label(frame1, text = "DEBE SELECCIONAR UNA IMAGEN PARA ANALIZAR", background = "#eced87")
            texto.pack()
            root.mainloop()
            exit()
    img.set(archivo_abierto.get())
    sys.argv = [' ',img.get()]
    runpy.run_path('host.py',run_name = '__main__')
    root.mainloop()

#--------------------------------------Setting up interface------------------------------------#

root = Tk()
root.title("Menú principal")
root.config(width="700", height="600",background = "#eced87")
root.iconbitmap('./images/interface/icon.ico')
root.resizable(0,0)

frame1 = Frame(root)
frame1.place(x = 150, y = 100)

foto = PhotoImage(file='./images/interface/icon.png')
Label(frame1,image=foto).grid(row = 0, column = 0)  

img1 = StringVar()
img2 = StringVar()

ParticleButton = Button(frame1, text = 'Iniciar identificacion de sintomas de cerambyx', width = 62,command = partial(OpenFileSegment, img1))
ParticleButton.grid(row=1,column=0)

root.mainloop()
