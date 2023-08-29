"""
Used during the testing phase of the NAS-22 Formula Car by NUST Formula Student Team.


A auto tuning application for the CBR600F engine used in our Formula Student vehicle.
It takes csv files as data from the engine Engine Control Unit that records a 3d map table of lambda values at periodic RPM and throttle posiotn values,
 and the intended lambda values map from the user.
It converts the file by correcting the lambda values used in the engine based on the difference between the intended values from the intended values map from the user
and the output data from the engine.


"""






from tkinter import *
from tkinter import ttk
import pandas as pd
import numpy as np
import shutil
from tkinter import filedialog
import matplotlib.pyplot as plt

map_accuracy = 0
map_unaffected = 0
max_pwr = 0
max_trq = 0
RPM = [0,250,500,750,800,850,900,1000,1250,1500,1750,2000,2250,2500,2750,3000,3250,3500,3750,4000,4250,4500,4750,5000,5250,5500,5750,6000,6250,6500,6750,7000,7500,8000,8500,9000,9500,10000,10500,11000,]
throttle_position = [0,5,10,15,20,25,30,35,40,45,50,60,70,80,90,100]
lambda_map = pd.read_csv('D:/NFST 2021-22/Engine/Tuning/Lambda table.csv')
lambda_map = lambda_map.to_numpy()
window = Tk()

def throttle_label(throttle_val):
    throttle = np.asarray(throttle_position)
    idx = (np.abs(throttle - throttle_val)).argmin()
    return throttle_position[idx]
      
def RPM_label(rpm):
    RPM1 = np.asarray(RPM)
    idx = (np.abs(RPM1 - rpm)).argmin()
    return RPM[idx]

def browse_run_data():
    run_data = filedialog.askopenfilename(initialdir = "D:/NFST 2021-22/Engine/Tuning",
                                          title = "Select a Run Data",
                                          filetypes = (("CSV files",
                                                        "*.csv*"),
                                                       ("all files",
                                                        "*.*")))
    #label_file_explorer.configure(text="File Opened: "+run_data)
    global new_lambd
    global not_used
    new_lambd = np.zeros(shape=(16,40))
    not_used = 0                       
    Run_Data = pd.read_csv(run_data)
    Data = Run_Data.to_numpy()
    n = np.ones(shape=(16,40))
    for i in range(len(Data)):
        lambd_val = Data.item(i,6)
        if (lambd_val < 1.3 and lambd_val > 0.6):
            rpm_val = Data.item(i,1)
            rpm = RPM_label(rpm_val)
            throttle_val = Data.item(i,2)
            throttle = throttle_label(throttle_val)
            rpm_ind = RPM.index(rpm)
            tp_ind = throttle_position.index(throttle)
        
            if new_lambd.item(tp_ind,rpm_ind) == 0:
                new_lambd[tp_ind,rpm_ind] = lambd_val
                
            else:
                new_lambd[tp_ind,rpm_ind] = new_lambd[tp_ind,rpm_ind] + lambd_val
                n[tp_ind,rpm_ind]+=1
    for j in range(16):
        for k in range(40):
            if new_lambd[j,k] == 0:
                new_lambd[j,k] = lambda_map.item(j,k)
                not_used+=1
            
    new_lambd = new_lambd/n
    
def browse_fuelmap():
    fuelmap = filedialog.askopenfilename(initialdir = "D:/NFST 2021-22/Engine/Tuning",
                                          title = "Select a Fuel Map",
                                          filetypes = (("CSV files",
                                                        "*.csv*"),
                                                       ("all files",
                                                           "*.*")))
    # Change label contents
    #label_file_explorer.configure(text="File Opened: "+fuelmap)
                                                                                                       
    global Fuel_map
    Fuel_map = pd.read_csv(fuelmap)

def browse_acc_file():
    accfile = filedialog.askopenfilename(initialdir = "D:/NFST 2021-22/Engine/Tuning",
                                          title = "Select a Acceleration file",
                                          filetypes = (("CSV files",
                                                        "*.csv*"),
                                                       ("all files",
                                                           "*.*")))
    # Change label contents
    #label_file_explorer.configure(text="File Opened: "+fuelmap)
    m = 292                                                                                                
    global acc_table
    
    acc_table = pd.read_csv(accfile)
    acc_table = acc_table.to_numpy()
    pwr_graph = np.zeros(shape=(2,len(acc_table)))
    velocity = np.zeros(shape = (1,len(acc_table)))
    trq_graph = np.zeros(shape=(2,len(acc_table)))
    
    for i in range(len(acc_table)):
        trq_graph[0,i] = acc_table.item(i,4)  #RPM = acc_table[i,4]
        pwr_graph[0,i] = acc_table.item(i,0)  #time = acc_table[i,0]
        try:
            del_t = abs(acc_table[0,i] - acc_table[0,i+1])
            velocity[0,i+1] = velocity[0,i] + (acc_table[0,i]*acc_table[2,i]) + (acc_table[2,i+1]*(del_t)) #acc = acc_table[2,i]
            energy = 0.5*m*(velocity[0,i]*velocity[0,i])
            power = energy/del_t
            
            trq_graph[1,i] = 1.3558*1.34102*power*5252/trq_graph[0,i]
            pwr_graph[1,i] = power/1000
        except:
            pass
    max_pwr = max(pwr_graph[1])
    max_trq = max(trq_graph[1])
    label_power.configure(text="Power "+str(max_pwr)+'KW')
    label_torque.configure(text="Torque "+str(max_trq)+'Nm')

    plot1 = plt.figure(1)
    plt.xlabel('Time/s')
    plt.ylabel('Power/KW')
    plt.plot(pwr_graph[0], pwr_graph[1])
    


    # create figure and axis objects with subplots()
    fig,ax = plt.subplots()
    # make a plot
    ax.plot(trq_graph[0],pwr_graph[1], color="red", marker="o")
    # set x-axis label
    ax.set_xlabel("RPM",fontsize=14)
    # set y-axis label
    ax.set_ylabel("Power/KW",color="red",fontsize=14)
    # twin object for two different y-axis on the sample plot
    ax2=ax.twinx()
    # make a plot with different y-axis using second axis object
    ax2.plot(trq_graph[0],trq_graph[1],color="blue",marker="o")
    ax2.set_ylabel("Torque/Nm",color="blue",fontsize=14)
    plt.show()
    
def create_file():
    file_name = file_name_entry.get()
    output_file.to_csv(file_name+'.csv')
    save_path = 'D:/NFST 2021-22/Engine/Tuning/'
    original = 'F:/Python Files/Visual Studio Code Files/'+file_name+'.csv'
    shutil.move(original,save_path)
    
def file():
    old_fuelmap = Fuel_map.to_numpy()
    l_t = new_lambd / lambda_map
    new_fuelmap = old_fuelmap * l_t
    new_fuelmap = np.round(new_fuelmap, decimals = 1)
    map_accuracy = 100*(np.sum(abs(new_fuelmap - old_fuelmap))/np.sum(old_fuelmap))
    label_map_accuracy.configure(text="Map Accuracy "+str(map_accuracy)+'%')
    map_unaffected = (not_used/640)*100
    label_map_unaffected.configure(text="Map Unaffected "+str(map_unaffected)+'%')
    global output_file
    output_file = pd.DataFrame(new_fuelmap)
    output_file.index = throttle_position  
    output_file.columns = RPM
    label_file_name = Label(window,
                            text = "Enter File Name:",
                            width = 20, height = 2,
                            fg = "blue",font = 14)
    label_file_name.grid(column=0,row=7)
    global file_name_entry
    file_name_entry = Entry(window, width = 30,bg = 'floral white',font = 15)
    file_name_entry.grid(row=7, column=1)
    
    
    createfile = Button(window, text='Output File',command=create_file)
    createfile.grid(column=1,row=8)


def Process():
    choice = Process_choice.get()
    if choice == 'Fuel Map Tuning':
        global label_map_unaffected
        global label_map_accuracy
        
        label_map_accuracy = Label(window,
                                text = "Map Accuracy "+str(map_accuracy)+'%',
                                width = 30, height = 4,
                                fg = "blue",font = 14)
        label_map_unaffected = Label(window,
                                text = "Map Unaffected "+str(map_unaffected)+'%',
                                width = 30, height = 4,
                                fg = "blue",font = 14)  
        label_file_fuelmap = Label(window,
                            text = "File for Fuelmap",
                            width = 30, height = 2,
                            bg = "yellow")
        label_file_rundata = Label(window,
                                    text = "File for Run Data",
                                    width = 30, height = 2,
                                    bg = "yellow")
        old_fuelmap_button = Button(window,
                                text = "Browse Files",
                                command = browse_fuelmap)
        
        new_lambd_button = Button(window,
                                text = "Browse Files",
                                command = browse_run_data)
        label_file_fuelmap.grid(column=1,row = 3)
        label_file_rundata.grid(column=1,row = 5)
        old_fuelmap_button.grid(column = 1, row = 4)
        
        new_lambd_button.grid(column = 1, row = 6)
        label_map_accuracy.grid(column = 1, row = 9)
        label_map_unaffected.grid(column = 1, row =10)
        outputfile = Button(window,
                        text = "Start Tuning",
                        command = file)
        outputfile.grid(column = 1, row = 8)
    elif choice == 'Power and Torque':
        button = Button(window,
                        text = "Browse Acceleration File",
                        command = browse_acc_file)
        button.grid(column = 1, row = 4)
        global label_power
        global label_torque
        label_power = Label(window,
                                text = "Power "+str(max_pwr)+'KW',
                                width = 30, height = 4,
                                fg = "blue",font = 14)
        label_power.grid(column = 1, row = 9)
        label_torque = Label(window,
                                text = "Torque "+str(max_trq)+'Nm',
                                width = 30, height = 4,
                                fg = "blue",font = 14)
        label_torque.grid(column = 1, row = 10)
        
    

Process_choice = ttk.Combobox(window, 
                            values=[
                                    "Fuel Map Tuning", 
                                    "Power and Torque",
                                    ])
window.title('Engine Auto-Tuner')
window.geometry("780x570")
window.config(background = "white")
                           
label_file_explorer = Label(window,
                            text = "Engine Auto-Tuner",
                            width = 40, height = 4,
                            fg = "blue",font = 20)    
button_exit = Button(window,
                     text = "Exit",
                     command = exit)
process_button = Button(window,
                        text = "Select",
                        command = Process)

label_file_explorer.grid(column = 1, row = 1)
process_button.grid(column = 1, row = 3)
Process_choice.grid(column=1,row=2)
button_exit.grid(column = 1,row = 11)



window.mainloop()