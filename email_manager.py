from tkinter import *
from tkinter import ttk
import uuid
import json

global my_data_list
global currentRowIndex

import io
import os

import base64

import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d


my_data_list    = []
file_name="emails.json"
curr_path = os.getcwd()

primary = Tk();
primary.resizable(False,False);
primary.title('Email & Password Manager')

def make_new_record():
    blankTuple = ('','','','')
    open_popup('add',blankTuple,primary)

btnNewRecord=Button(primary,text="Add New",
                    padx=2,pady=3,command=lambda:make_new_record())
btnNewRecord.grid(row=0, column=0, sticky="w")

trv =ttk.Treeview(primary, columns=(1,2,3,4),show="headings",height="20")
trv.grid(row=1,column=0, rowspan=16,columnspan=5)

trv.heading(1,text="ID", anchor="center")
trv.heading(2,text="Email", anchor="center")
trv.heading(3,text="Password", anchor="center")
trv.heading(4,text="Description", anchor="center")

trv.column("#1",anchor="w",width=270, stretch=True)
trv.column("#2",anchor="w", width=140, stretch=True)
trv.column("#3",anchor="w", width=140, stretch=True)
trv.column("#4",anchor="w", width=140, stretch=True)


def load_json_from_file():
    if os.path.isfile(curr_path+"\\"+file_name) and os.access(curr_path+"\\"+file_name, os.R_OK):
        # checks if file exists
        print ("File exists and is readable")
        load_json_from_existing_file()
    else:
        print ("Either file is missing or is not readable, creating file...")
        with io.open(os.path.join(curr_path+"\\", file_name), 'w') as db_file:
            db_file.write(json.dumps({}))
            

def load_json_from_existing_file():
    global my_data_list
    with open(curr_path+"\\"+file_name,"r") as file_handler:
        my_data_list = json.load(file_handler)
        file_handler.close
        print('file has been read and closed')

def remove_all_data_from_trv():
    for item in trv.get_children():
        trv.delete(item)

def load_trv_with_json():
    global my_data_list

    remove_all_data_from_trv()

    rowIndex=1

    for key in my_data_list:
	    guid_value = key["id"]
	    email = key["email"]
	    password = key["password"]
	    description = key["description"]

	    trv.insert('',index='end',iid=rowIndex,text="",
                        values=(guid_value,email,unobscure(password).decode("utf-8"),description))    
	    rowIndex=rowIndex+1

def MouseButtonUpCallBack(event):
    global trv
    currentRowIndex = trv.selection()[0]
    lastTuple = (trv.item(currentRowIndex,'values'))
    open_popup('edit',lastTuple,primary)
  
def open_popup(_mode, _tuple, primary):
    global myname
    child = Toplevel(primary);
    child.resizable(False,False);
    child.title('Edit/Add')
    child.grab_set(); #allow it to receive events 
                        #and prevent users from interacting 
                        #with the main window

    
    child.configure(bg='LightBlue');
    load_form = True;
    input_frame = LabelFrame(child, text='Enter New Record',
                                bg="lightgray",
                                font=('Consolas',14))

    input_frame.grid(row=0,rowspan=6,column=0)

    l1 = Label(input_frame, text="ID",         width=25, height=2, anchor="w", relief="ridge", font=('Consolas',14))
    l2 = Label(input_frame, text="Email", width=25, height=2, anchor="w", relief="ridge", font=('Consolas',14))
    l3 = Label(input_frame, text="Password", width=25, height=2, anchor="w", relief="ridge", font=('Consolas',14))
    l4 = Label(input_frame, text="Description",  width=25, height=2, anchor="w", relief="ridge", font=('Consolas',14))
    l1.grid(column=0,row=0,padx=1, pady=0);
    l2.grid(column=0,row=1,padx=1, pady=0);
    l3.grid(column=0,row=2,padx=1, pady=0);
    l4.grid(column=0,row=3,padx=1, pady=0);

    id_value = StringVar()
    id_value.set(uuid.uuid4())

    crm_id=Label(input_frame,           anchor="w",                 height=1,
                relief="ridge",          textvariable=id_value,      font=('Consolas',14))
    crm_id.grid(row=0, column=1, padx=20)

    crm_fn      =Entry(input_frame,width=30,borderwidth=2,fg="black",font=('Consolas',14))
    crm_fn.grid(row=1, column=1)

    crm_pas      =Entry(input_frame,width=30,borderwidth=2,fg="black",font=('Consolas',14))
    crm_pas.grid(row=2, column=1)

    crm_ln      =Entry(input_frame,width=30,borderwidth=2,fg="black",font=('Consolas',14))
    crm_ln.grid(row=3, column=1)

    btnAdd=Button(input_frame,text="Save",padx=5,pady=10,command=lambda:determineAction())
    btnAdd.grid(row=4, column=0)

    btnDelete=Button(input_frame,text="Delete",padx=5,pady=10,command=lambda:delete_record())
    btnDelete.grid(row=4, column=3)

    btnCancel=Button(input_frame,text="Cancel",padx=5,pady=10,command=lambda:child_cancel())
    btnCancel.grid(row=4, column=4)

    load_form = False;

    def delete_record():
        guid_value = id_value.get()
        email = crm_fn.get()
        password = crm_pas.get()
        description = crm_ln.get()
        process_request('_DELETE_',guid_value,email,password,description)
        reload_main_form()
        child.grab_release();
        child.destroy()
        child.update()


    def child_cancel():
        child.grab_release();
        child.destroy()
        child.update()

    def reload_main_form():
        load_trv_with_json()

    def change_background_color(new_color):
        crm_fn.config(bg=new_color)
        crm_ln.config(bg=new_color)


    def add_entry():
        guid_value = id_value.get()
        email = crm_fn.get()
        description = crm_ln.get()
        password = crm_pas.get()
    

        if len(email)==0:
            change_background_color("#FFB2AE")
            return

        process_request('_INSERT_',guid_value,email,password,description)

    def update_entry():
        guid_value = id_value.get()
        email = crm_fn.get()
        description = crm_ln.get()
        password = crm_pas.get()

        if len(email)==0:
            change_background_color("#FFB2AE")
            return

        process_request('_UPDATE_',guid_value,email,password,description)

    def load_edit_field_with_row_data(_tuple):
        if len(_tuple)==0:
            return;

        id_value.set(_tuple[0]);
        crm_fn.delete(0,END)
        crm_fn.insert(0,_tuple[1])
        crm_pas.delete(0,END)
        crm_pas.insert(0,_tuple[2])
        crm_ln.delete(0,END)
        crm_ln.insert(0,_tuple[3])

    if _mode=='edit':
        load_edit_field_with_row_data(_tuple)

    def process_request(command_type,guid_value,email,password,description):
        global my_data_list
        global dirty

        dirty=True

        print("password "+password+" description "+description)

        if command_type == "_UPDATE_":
            row = find_row_in_my_data_list(guid_value)
            if row >= 0:
                dict = {"id":guid_value, "email":email,"password":obscure(password.encode()).decode("utf-8"), 
                        "description":description}
                my_data_list[row]=dict

        elif command_type == "_INSERT_":
            dict = {"id":guid_value, "email":email,"password":obscure(password.encode()).decode("utf-8"), 
                    "description":description}
            my_data_list.append(dict)

        elif command_type == "_DELETE_":
            row = find_row_in_my_data_list(guid_value)
            if row >= 0:
                del my_data_list[row];

        save_json_to_file();
        clear_all_fields();

    def find_row_in_my_data_list(guid_value):
        global my_data_list
        row     = 0
        found   = False

        for rec in my_data_list:
            if rec["id"] == guid_value:
                found = True
                break
            row = row+1

        if(found==True):
            return(row)

        return(-1)

    def determineAction():
        if load_form == False:
            if _mode == "edit":
                update_entry();
            else:
                add_entry();

        reload_main_form()
        child.grab_release();
        child.destroy()
        child.update()


    def save_json_to_file():
        global my_data_list
        with open(curr_path+"\\"+file_name, "w") as file_handler:
            json.dump(my_data_list, file_handler, indent=4)
        file_handler.close
        print('file has been written to and closed')




    def clear_all_fields():
        crm_fn.delete(0,END)
        crm_ln.delete(0,END)
        crm_pas.delete(0,END)
        crm_id.configure(text="")
        crm_fn.focus_set()
        id_value.set(uuid.uuid4())
        change_background_color("#FFFFFF")

def obscure(data: bytes) -> bytes:
    return b64e(zlib.compress(data, 9))

def unobscure(obscured: bytes) -> bytes:
    return zlib.decompress(b64d(obscured))

trv.bind("<ButtonRelease>",MouseButtonUpCallBack)
load_json_from_file()
load_trv_with_json()
primary.mainloop()
