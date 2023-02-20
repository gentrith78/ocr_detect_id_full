from tkinter import *
from tkinter import ttk
import os, shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
from scripts import initiator
from scripts.logger import Logger
import subprocess
#################################################
#                  VARIABLES
PATH = os.path.abspath(os.path.dirname(__file__))

##################################################
#                  FUNCTIONS
#TODO make algorithm to check for new file each 30 secs
def start(input_path,output_path):
    ##############################
    #        HANDLE EMPTY
    if output_path == '' or output_path.isspace() or output_path.isdigit():
        messagebox.showerror("Wrong Output", "Please make sure that the output folder is selected correctly")
        return
    if input_path == '' or input_path.isspace() or input_path.isdigit():
        messagebox.showerror("Wrong Input", "Please make sure that the input folder is selected correctly")
        return
    ##############################
    #        START INITIATOR
    # initiator.logger_obj = Logger(os.path.join(PATH,'scripts','logs'))
    initiator.input_folder_path = input_path
    initiator.output_folder_path = output_path
    initiator.main()
    print('started')
def select_input(entry):
    path = filedialog.askdirectory()
    entry.config(text=str(path))
    entry.insert(0, path)
def select_output(entry):
    path = filedialog.askdirectory()
    entry.config(text=str(path))
    entry.insert(0, path)

##################################################
#               MAIN FRAME
win = Tk(screenName='Id Extractor')
win.geometry("1050x400")
main_frame = Frame(win,width=600,height=260,background='#D9D9D9')
main_frame.pack(fill=BOTH, expand=1)
select_folders_FRAME = tk.Frame(main_frame,highlightthickness=2)
select_folders_FRAME.config(highlightbackground = "gray", highlightcolor= "gray")
select_folders_FRAME.pack(side=TOP,pady=50,padx=40)
##################################################
#           SELECT INPUT FOLDER
input_folder_FRAME = tk.Frame(select_folders_FRAME)
input_folder_LABEL = tk.Label(input_folder_FRAME,text='Input Folder')
input_folder_ENTRY = tk.Entry(input_folder_FRAME,width=70)
input_folder_BUTTON = tk.Button(input_folder_FRAME,text='Select Input Folder',background='#AAA5A5',command=lambda :select_input(input_folder_ENTRY))
input_folder_LABEL.pack(side=TOP,expand=0,padx=10,pady=10)
input_folder_ENTRY.pack(side=TOP,expand=0,padx=10,pady=10)
input_folder_BUTTON.pack(side=TOP,expand=0,padx=10,pady=10)
input_folder_FRAME.grid(row=0,column=0,padx=10,pady=20)
##################################################
#           SELECT OUTPUT FOLDER
output_folder_FRAME = tk.Frame(select_folders_FRAME)
output_folder_LABEL = tk.Label(output_folder_FRAME,text='Output Folder')
output_folder_ENTRY = tk.Entry(output_folder_FRAME,width=70)
output_folder_BUTTON = tk.Button(output_folder_FRAME,text='Select Output Folder',background='#AAA5A5',command=lambda :select_output(output_folder_ENTRY))
output_folder_LABEL.pack(side=TOP,expand=0,padx=10,pady=10)
output_folder_ENTRY.pack(side=TOP,expand=0,padx=10,pady=10)
output_folder_BUTTON.pack(side=TOP,expand=0,padx=10,pady=10)
output_folder_FRAME.grid(row=0,column=1,padx=10,pady=20)
##################################################
#                  START
start_button = tk.Button(main_frame,text='            Start            ',background='#AAA5A5',command= lambda :start(input_folder_ENTRY.get(),output_folder_ENTRY.get()))
start_button.pack(side=TOP,pady=50,padx=40)



win.mainloop()
#
# import random
# import time
#
# import pyautogui, sys
# try:
#     while True:
#         pyautogui.click()
#         a = [-100,-100,-200,-200,-300,-300]
#         pyautogui.scroll(random.choice(a))
#         for  i in range(random.randint(2,5)):
#             pyautogui.press('left')
#             time.sleep(1)
#             pyautogui.press('right')
#         print('###')
#         time.sleep(random.randint(10,20))
# except KeyboardInterrupt:
#     print('\n')
