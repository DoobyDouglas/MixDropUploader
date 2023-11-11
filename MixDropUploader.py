import requests
import os
import tkinter
from tkinter import ttk
import json
from threading import Thread
import configparser
from tkinterdnd2 import TkinterDnD, DND_FILES

# pyinstaller --noconfirm --onefile --noconsole --add-data "venv/lib/site-packages/tkinterdnd2;tkinterdnd2/" MixDropUploader.py


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    if 'USER' not in config:
        config['USER'] = {}
    return config


def set_geometry(master: tkinter.Tk):
    width = 690
    height = 400
    s_width = master.winfo_screenwidth()
    s_height = master.winfo_screenheight()
    upper = s_height // 5
    to_left = s_width // 4
    x = (s_width - width) // 2
    y = (s_height - height) // 2
    return f'{width}x{height}+{x - to_left}+{y - upper}'


def clean_json():
    cleaned_data = {}
    with open('data.json', 'w') as file:
        json.dump(cleaned_data, file)


def update_json(name, status):
    if not os.path.exists('data.json'):
        with open('data.json', 'w') as json_file:
            json.dump({}, json_file)
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
    data[name] = status
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file)


def pathfinder(directory):
    nums = []
    for i in range(10):
        nums.append(str(i))
    step = -1
    find = False
    while not find:
        count = 0
        title = directory.split('/')[step]
        for i in title:
            if i in nums:
                count += 1
        if len(title) != count:
            find = True
            return title
        else:
            step -= 1


def post(API_MAIL, API_KEY, event):
    file = event.data.replace('{', '')
    file = file.replace('}', '')
    filename = os.path.splitext(os.path.basename(file))[0]
    directory = os.path.dirname(file)
    directory = pathfinder(directory)
    name = f'{directory} {filename}'
    update_json(name, 'loading...')
    read_json()
    files = {
        'file': open(file, 'rb'),
    }
    data = {
        'email': API_MAIL,
        'key': API_KEY,
    }
    response = requests.post(
        'https://ul.mixdrop.ag/api',
        data=data,
        files=files,
    )
    embedurl = response.json()['result']['embedurl']
    update_json(name, embedurl)
    read_json()


def post_thread(event):
    try:
        config = get_config()
        API_MAIL = config['USER']['API_MAIL']
        API_KEY = config['USER']['API_KEY']
        thread = Thread(target=post, args=(API_MAIL, API_KEY, event))
        thread.start()
    except KeyError:
        print('Нет данных')


def read_json():
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
    left_text.config(state='normal')
    right_text.config(state='normal')
    left_text.delete('1.0', tkinter.END)
    right_text.delete('1.0', tkinter.END)
    left_text.insert(tkinter.END, '\n'.join(data.keys()))
    right_text.insert(tkinter.END, '\n'.join(data.values()))
    left_text.config(state='disabled')
    right_text.config(state='disabled')


master = TkinterDnD.Tk()
master.geometry(set_geometry(master))
master.resizable(False, False)
master.title('MixDropUploader v0.04')
master.drop_target_register(DND_FILES)
master.dnd_bind('<<Drop>>', post_thread)
style = ttk.Style()
style.configure('TButton', width=13)
post_bttn = ttk.Button(master, text='CLEAN', command=clean_json)
post_bttn.place(relx=0.85, rely=0.92, anchor="center")
read_bttn = ttk.Button(master, text='REFRESH', command=read_json)
read_bttn.place(relx=0.15, rely=0.92, anchor="center")


left_text = tkinter.Text(master, width=40, height=20, state='disabled')
left_text.place(relx=0.49, rely=0.44, anchor="e")

right_text = tkinter.Text(master, width=40, height=20, state='disabled')
right_text.place(relx=0.51, rely=0.44, anchor="w")


master.mainloop()
