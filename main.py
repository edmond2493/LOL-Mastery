import gc
import _tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import colorchooser
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import socket
import threading as th
import pathlib
import re
import psutil
import os
from pathlib import *
from PIL import Image, ImageTk, UnidentifiedImageError
from datetime import datetime

# API AND THE MAIN REGIONS USED TO SEARCH, CAN STILL ADD BR:br1, LAN:la1, LAS:la2, OCE:oc1, RU:ru1, TR:tr1--------------
API = ""  # INSERT THE API KEY HERE
regions = ['EUNE', 'EUW', 'NA', 'JP', 'KR']
d_r = {'EUNE': 'eun1', "EUW": 'euw1', 'NA': 'na1', 'JP': 'jp1', 'KR': 'kr'}
d_r2 = {'eun1': 'EUNE', 'euw1': "EUW", 'na1': 'NA', 'jp1': 'JP', 'kr': 'KR'}
app_icon = "Images/mastery.ico"

# FIRST CHECK FOR INTERNET CONNECTION-----------------------------------------------------------------------------------
internet_connection = socket.gethostbyname(socket.gethostname())
# MAIN WINDOW ROOT AND CONFIG-------------------------------------------------------------------------------------------
root = Tk()
root.title("League Mastery")
root.iconbitmap(app_icon)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
app_width = 1000
height = 0
if screen_height > 1000:
    height = 300
elif screen_height > 900:
    height = 200
elif screen_width > 700:
    height = 150
app_height = (screen_height - height)
bot_height = (app_height-150)
friends_h = (app_height - 48)
root.geometry(f'{app_width}x{app_height+20}+{(screen_width//2)-(app_width//2)}+{(screen_height//2)-(app_height//2)-30}')
root.resizable(False, False)


# START FUNCTION TO CHECK IF THERE IS A DATABASE AND START UP WITH THE DEFAULT NAME OF THE SUMMONER---------------------
def startup_function():
    # CHECKS FOR THE LATEST VERSION OF THE GAME AND UPDATES THE DATABASE------------------------------------------------
    try:
        url_version = "https://ddragon.leagueoflegends.com/api/versions.json"
        version_request = requests.get(url_version)
        version = version_request.json()[0]
        database = Path('Default Name.db')
        try:
            # CHECK FOR THE DATABASE AND PROCEED WITH THE DEFAULT NAME AND UPDATE THE GAME VERSION----------------------
            if database.is_file():
                conn = sqlite3.connect('Default Name.db')
                cur = conn.cursor()
                # cur.execute("UPDATE start SET version = :version", {'version': version})
                cur.execute("""SELECT * FROM data""")
                info2 = cur.fetchall()
                Mastery().request_data(info2[0][0])
                conn.commit()
                conn.close()
            # WHEN THERE IS NO DATABASE, CREATES A DATABASE AND VALIDATE IF THE SUMMONER NAME ENTERED IS VALID----------
            else:
                def confirm(*_):
                    # API REQUEST FOR THE CHAMPIONS NAME, CREATES A DICT WHICH IS INSERTED IN THE DATABASE--------------
                    url_champ_names = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
                    name_requests = requests.get(url_champ_names)
                    name = name_requests.json()

                    # API REQUEST FOR THE SUMMONER BASE INFO------------------------------------------------------------
                    url_summoner_info = f"https://{d_r[sv_region.get()]}.api.riotgames.com/lol/summoner/v4/summoners/" \
                                        f"by-name/{e_start_name.get()}?api_key={API}"
                    summoner_info_request = requests.get(url_summoner_info)
                    data = summoner_info_request.json()

                    # SUMMONER CHAMPIONS MASTERY, IS INSERTED IN THE DATABASE AS A STR WHICH IS CONVERTED BY EVAL LATER-
                    url = f"https://{d_r[sv_region.get()]}.api.riotgames.com/lol/champion-mastery/v4/champion-" \
                          f"masteries/by-puuid/{data['id']}?api_key={API}"
                    lol_request = requests.get(url)
                    data1 = lol_request.json()

                    # VALIDATE IF THE INSERTED NAME EXISTS, CREATE A DB FOR : FRIENDS, CHAMPION, SUMMONER OFFLINE DATA
                    # THEME AND THE BASIC STARTUP INFO -----------------------------------------------------------------
                    if summoner_info_request.status_code == 200:
                        conn1 = sqlite3.connect('Default Name.db')
                        cur1 = conn1.cursor()
                        cur1.execute("""CREATE TABLE IF NOT EXISTS friends (name text, region text, UNIQUE(name))""")
                        cur1.execute("""CREATE TABLE IF NOT EXISTS champion (id integer, name text)""")
                        cur1.execute("""CREATE TABLE IF NOT EXISTS data (data text)""")
                        cur1.execute("""CREATE TABLE IF NOT EXISTS start (
                        id text,
                        lvl text,
                        name text,
                        region text,
                        bg text,
                        bg2 text,
                        bt text,
                        fg text, 
                        version text)""")
                        cur1.execute("""CREATE TABLE IF NOT EXISTS theme (
                        theme_name text,
                        bg text,
                        bg2 text,
                        bt text, 
                        fg text,
                        UNIQUE(theme_name))""")
                        cur1.execute("INSERT INTO start VALUES(:id, :lvl, :name, :region, :bg, :bg2, :bt, :fg, "
                                     ":version)", {
                                                 'id': data['puuid'],
                                                 'lvl': data['summonerLevel'],
                                                 'name': data['name'],
                                                 'region': d_r[sv_region.get()],
                                                 'bg': '#D3F5A8',
                                                 'bg2': '#79BF8B',
                                                 'bt': '#2EDAD5',
                                                 'fg': '#000000',
                                                 'version': version})
                        for k in name['data']:
                            cur1.execute("INSERT INTO champion VALUES(:id, :name)", {
                                'id': name['data'][k]['key'],
                                'name': name['data'][k]['id']
                            })
                        cur1.execute("INSERT INTO data VALUES(:data)", {'data': f'{data1}'})
                        cur1.executemany("INSERT INTO theme VALUES (?, ?, ?, ?, ?);", [
                                        ('Default', '#D3F5A8', '#79BF8B', '#2EDAD5', '#000000'),
                                        ('Light', '#FFFFFF', '#FFA500', '#3498DB', '#000000'),
                                        ('Dark', '#000000', '#8B0000', '#008B8B', '#FFFFFF'),
                                        ('Gray', '#A9A9A9', '#708090', '#008B8B', '#000000'),
                        ])
                        conn1.commit()
                        conn1.close()
                        Mastery().request_data(str(data1))
                        top.destroy()
                    else:
                        l_error = Label(top, text='Not valid!', fg='red')
                        l_error.place(y=80, x=145)

                # CREATES A TOPLEVEL WINDOW TO ENTER THE DEFAULT NAME AND THE CONFIRM BUTTON----------------------------
                top_width = 350
                top_height = 100
                top = Toplevel(root)
                top.protocol("WM_DELETE_WINDOW", root.quit)
                top.geometry(f'{top_width}x{top_height}+{(screen_width // 2) - (top_width // 2)}+'
                             f'{(screen_height // 2) - (top_height // 2)}')
                top.attributes('-topmost', 'true')
                top.title('Default summoner')
                for j in range(10):
                    top.columnconfigure(j, weight=1)
                e_start_name = Entry(top, font=('Comic Sans MS', 12), width=15)
                e_start_name.grid(row=0, column=3, columnspan=4, sticky='w')
                e_start_name.bind('<Return>', confirm)
                sv_region = StringVar()
                om_region = ttk.OptionMenu(top, sv_region, 'EUNE', *regions)
                om_region.grid(row=0, column=2, sticky='e')
                bt_confirm = Button(top, text='Confirm', command=confirm)
                bt_confirm.place(x=120, y=50)
                bt_cancel = Button(top, text='Cancel', command=root.quit)
                bt_cancel.place(x=190, y=50)

        except FileNotFoundError:
            pass

    except requests.exceptions.ConnectionError:
        startup_function()


# START FUNCTION IN OFFLINE MODE IF THERE IS ALREADY A DATABASE---------------------------------------------------------
def offline_function():
    database = Path('Default Name.db')
    if internet_connection == "127.0.0.1" and not database.is_file():
        messagebox.showerror('File not found!', 'No database found \nNo internet connection!', parent=root)

    elif database.is_file():
        conn = sqlite3.connect('Default Name.db')
        cur = conn.cursor()
        cur.execute("""SELECT * FROM data""")
        info2 = cur.fetchall()
        Mastery().request_data(info2[0][0])
        conn.commit()
        conn.close()


# MAIN AND ONLY CLASS---------------------------------------------------------------------------------------------------
class Mastery:

    def __init__(self):
        # DATABASE CONNECTION TO GET THE START INFO---------------------------------------------------------------------
        conn = sqlite3.connect('Default Name.db')
        cur = conn.cursor()
        cur.execute('''SELECT * FROM theme''')
        self.theme_db = cur.fetchall()
        cur.execute('''SELECT * FROM start''')
        self.info_db = cur.fetchall()[0]
        cur.execute('''SELECT * FROM champion''')
        self.champ_db = cur.fetchall()
        conn.commit()
        conn.close()

        # THEME MENU CREATE TO CHANGE AND ADD NEW ONE-------------------------------------------------------------------
        self.my_menu = Menu(root)
        root.config(menu=self.my_menu)
        self.theme_menu = Menu(self.my_menu, tearoff=False, background='#ffd000')
        self.my_menu.add_cascade(label='Theme', menu=self.theme_menu)
        self.my_menu.add_cascade(label='Edit theme', command=self.edit_theme)
        self.my_menu.add_cascade(label='Search', command=lambda: (self.filter.grid_forget() if
                                 self.filter.winfo_ismapped() else self.filter.grid(row=0, column=3, pady=10, ipady=2)))
        self.my_menu.add_cascade(label='Champions', command=self.swap_frames)
        for j in self.theme_db:
            self.theme_menu.add_command(label=j[0],
                                        command=lambda n=j[1], i=j[2], c=j[3], e=j[4]: self.change_theme(n, i, c, e))

        # START SUMMONER ID, LEVEL, NAME, REGION, GAME VERSION AND THE SAVED THEME COLOR--------------------------------
        self.summoner_id = self.info_db[0]
        self.lvl = self.info_db[1]
        self.start_name = self.info_db[2]
        self.region = self.info_db[3]
        self.bg = self.info_db[4]
        self.bg2 = self.info_db[5]
        self.bt = self.info_db[6]
        self.fg = self.info_db[7]
        self.version = self.info_db[8]
        self.my_menu.add_cascade(label=f'Patch {self.version}', state='disabled')
        self.f = 'Comic Sans MS'

        # CHAMPIONS ID AND NAME USED TO MAKE THE CONVERT----------------------------------------------------------------
        self.dicts = {}
        for k in self.champ_db:
            self.dicts[k[0]] = k[1]

        # TOP FRAME, SEARCH BUTTON AND ENTRY, AND THE SUMMONER INFO-----------------------------------------------------
        root.config(bg=self.bg)
        self.f_top = Frame(root, width=app_width, height=150, bg=self.bg)
        self.f_top.grid(row=0, column=0, columnspan=4)
        self.f_top.grid_propagate(False)
        for d in range(8):
            self.f_top.columnconfigure(d, weight=1)

        # FIRST FRAME WITH THE SUMMONER NAME AND THE BUTTON IF THE PLAYER IS IN GAME------------------------------------
        self.fs = {3: 22, 4: 21, 5: 20, 6: 19, 7: 18, 8: 17, 9: 16, 10: 16, 11: 15, 12: 15, 13: 13, 14: 13, 15: 12,
                   16: 12}
        self.l_name = Label(self.f_top, text=self.start_name, bg=self.bg, fg=self.fg)
        self.l_name.config(font=(self.f, self.fs[len(self.start_name)], "italic"))
        self.l_name.grid(row=0, column=0)
        self.bt_status = Button(self.f_top, text='⭕', bd=0, fg='red', bg=self.bg, command=self.status, cursor='hand2')

        # SUMMONER LEVEL AND FILTER FOR THE CHAMPIONS-------------------------------------------------------------------
        self.l_level = Label(self.f_top, text=f"Level: {self.lvl}", font=(self.f, 14, "italic"), bg=self.bg, fg=self.fg)
        self.l_level.grid(row=0, column=2)
        self.filter = Entry(self.f_top, font=(self.f, 11), justify=RIGHT, bg=self.bg2, fg=self.fg, width=12)

        # OPTION MENU TO SELECT THE REGION, THE ENTRY AND BUTTON TO SEARCH A PLAYER, ENTER IS BIND ON THE ENTRY---------
        self.sv_region = StringVar()
        self.om_region = ttk.OptionMenu(self.f_top, self.sv_region, d_r2[self.region], *regions)
        self.om_region.grid(row=0, column=4)
        self.e_search = Entry(self.f_top, font=(self.f, 11), justify=RIGHT, bg=self.bg2, fg=self.fg)
        self.e_search.grid(row=0, column=5, pady=10, ipady=2, sticky="E", columnspan=1)
        self.e_search.bind('<Return>', lambda n: self.search(self.e_search.get(), d_r[self.sv_region.get()]))
        self.bt_search = Button(self.f_top, text='Search', font=(self.f, 10), width=13, bg=self.bt,
                                command=lambda: self.search(self.e_search.get(), d_r[self.sv_region.get()]))
        self.bt_search.grid(row=0, column=6)

        # BUTTON TO CHANGE THE DEFAULT SUMMONER AND THE FRIEND BUTTON TO SEE, ADD AND DELETE FRIENDS--------------------
        photo = PhotoImage(file=f"Images/user.png")
        self.bt_friend = Button(self.f_top, image=photo, height=26, width=30, command=self.friends, bg=self.bt)
        self.bt_friend.grid(row=0, column=7, padx=10, sticky="w")
        self.bt_friend.image = photo
        self.bt_change = Button(self.f_top, text='♻', font=('Arial', 10), command=self.default, width=3, bg=self.bt)
        self.bt_change.grid(row=0, column=7, ipady=2, padx=10, sticky="e")
        self.check_status = True
        self.settings_value = False
        self.frames_status = False

        # FRAMES FOR CHAMPIONS INFO, ALL CHAMPIONS AND FRIENDS----------------------------------------------------------
        self.f_champ = Frame(root, width=app_width, height=bot_height, bg=self.bg)
        self.f_champ.grid(row=1, column=0, columnspan=4)
        self.f_champ.grid_propagate(False)

        self.f_bot = Frame(root, width=app_width, height=bot_height, bg=self.bg)
        self.f_bot.grid(row=1, column=0, columnspan=4)
        self.f_bot.grid_propagate(False)

        self.friend_list = Frame(root, height=app_height, width=230, bg=self.bg)

        # VARIABLES THAT ARE USED TO STORE INFO, WERE CREATED FOR A SMOOTH CHANGE OF THE THEME--------------------------
        self.name, self.points, self.chest, self.token, self.level_check = [], [], [], [], []
        self.frames = [self.bt_status, self.f_champ, self.f_top, self.f_bot, self.friend_list]
        self.frames2 = []
        self.top_level = []
        self.labels = [self.l_name, self.l_level]
        self.buttons = [self.bt_search, self.bt_friend, self.bt_change]
        self.entries = [self.filter, self.e_search]
        self.f_c = []
        self.f_f = []
        self.champ_top = None
        self.logo()

        # CHECKS FOR THE INTERNET CONNECTION ON THE START, IF OK THEN PROCEEDS TO UPDATE THE PLAYER DATA AND THE ICONS--
        if internet_connection == "127.0.0.1":
            pass
        else:
            try:
                def download_media():
                    self.my_menu.entryconfigure('Champions', state='disabled')
                    self.check_media()
                    self.champions()
                    self.my_menu.entryconfigure('Champions', state='normal')
                    self.internet_check()
                    self.update_data()
                th.Thread(target=download_media).start()
            except requests.exceptions.ConnectionError:
                pass

    @staticmethod
    def scroll(widget, event):
        widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

    @staticmethod
    def final_scroll(widget, func, *_):
        widget.bind_all("<MouseWheel>", func)

    @staticmethod
    def stop_scroll(widget, *_):
        widget.unbind_all("<MouseWheel>")

    # SWAP BETWEEN THE MAIN FRAME AND THE CHAMPIONS FRAME---------------------------------------------------------------
    def swap_frames(self):
        if self.frames_status:
            self.frames_status = False
            self.f_bot.lift()
        else:
            self.frames_status = True
            self.f_champ.lift()

    # FUNCTION TO KEEP CONSTANT CHECK ON THE INTERNET CONNECTION EVERY 2 SEC, IF IS OFF IT DISABLES THE MAIN BUTTONS----
    def internet_check(self):
        try:
            connection_test = socket.gethostbyname(socket.gethostname())
            if connection_test == "127.0.0.1":
                self.check_status = False
                self.friends()
                for top in self.top_level:
                    top.withdraw()
                for name in self.name:
                    name.config(cursor="arrow")
                    name.unbind("<Button-1>")
                self.my_menu.entryconfigure('Champions', state='disabled')
                self.e_search.config(state='disabled')
                self.bt_search.config(state='disabled')
                self.bt_status.config(state='disabled')
                self.bt_friend.config(state='disabled')
                self.bt_change.config(state='disabled')
            else:
                for name in self.name:
                    if name.bind('<Button-1>'):
                        pass
                    else:
                        name.config(cursor="hand2")
                        name.bind('<Button-1>', lambda event, n=name.cget("text").split(":")[1].strip(): self.skins(n))

                if self.my_menu.entrycget('Champions', 'state') != 'normal':
                    self.my_menu.entryconfigure('Champions', state='normal')
                if self.e_search.cget('state') != 'normal':
                    self.e_search.config(state='normal')
                if self.bt_search.cget('state') != 'normal':
                    self.bt_search.config(state='normal')
                if self.bt_status.cget('state') != 'normal':
                    self.bt_status.config(state='normal')
                if self.bt_friend.cget('state') != 'normal':
                    self.bt_friend.config(state='normal')
                if self.bt_change.cget('state') != 'normal':
                    self.bt_change.config(state='normal')
                self.game_status()
                gc.collect()
        except RuntimeError:
            root.quit()
        root.after(2500, self.internet_check)

    # IS CALLED ON THE REQUEST DATA TO CHECK IF A PLAYER IS IN GAME, RED CIRCLE APPEARS NEAR THE NAME-------------------
    def game_status(self):
        url_status = "https://" + self.region + ".api.riotgames.com/lol/spectator/v4/active-games/by-puuid/" + \
                     self.summoner_id + "?api_key=" + API
        game_status = requests.get(url_status)

        if game_status.status_code != 200 and self.bt_status.winfo_ismapped():
            self.bt_status.grid_remove()
        elif game_status.status_code == 200 and not self.bt_status.winfo_ismapped():
            self.bt_status.grid(row=0, column=1, sticky='w', padx=10)

    # IS CALLED ON A THREAT NOT TO SLOW THE APP, IT SERVES TO UPDATE THE CUSTOMER DATA----------------------------------
    def update_data(self):
        conn = sqlite3.connect('Default Name.db')
        cur = conn.cursor()
        cur.execute("""SELECT * FROM start""")
        fetch = cur.fetchall()

        url_data = f"https://{self.region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/" \
                   f"{fetch[0][0]}?api_key={API}"
        lol_request = requests.get(url_data)
        data = lol_request.json()
        cur.execute("UPDATE data SET data = :data", {'data': str(data)})

        url_info = f"https://{fetch[0][3]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{fetch[0][2]}?api_key=" \
                   f"{API}"
        summoner_info_request = requests.get(url_info)
        info = summoner_info_request.json()
        cur.execute("UPDATE start SET lvl = :lvl, name = :name", {'lvl': info['summonerLevel'], 'name': info['name']})
        conn.commit()
        conn.close()

    # CHECK FOR THE CHAMPIONS ICONS AND FOLDER, IF NOT EXIST IT DOWNLOADS THEM ALL THE ONCE USING A THREAD--------------
    def check_media(self, max_retries=5, retry_delay=1):
        for _ in range(max_retries):
            try:
                icon_folder = Path('Icons')
                if not icon_folder.is_dir():
                    pathlib.Path("Icons").mkdir(exist_ok=True)

                url_version = "https://ddragon.leagueoflegends.com/api/versions.json"
                version_request = requests.get(url_version)
                version = version_request.json()[0]

                url_champ_name = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
                name_request = requests.get(url_champ_name)
                names = name_request.json()

                conn_media = sqlite3.connect('Default Name.db')
                cur_media = conn_media.cursor()
                for i in names['data']:
                    def download_icon():
                        icons = Path(f"Icons/{names['data'][i]['id']}.png")
                        champ_name = names['data'][i]['id']
                        if not icons.is_file():
                            url_photo = f'http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/' \
                                        f'{champ_name}.png'
                            icon = requests.get(url_photo).content
                            with open(f'Icons/{champ_name}.png', 'wb') as photo:
                                photo.write(icon)

                        if self.version != version:
                            url_photo = f'http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/' \
                                        f'{champ_name}.png'
                            icon = requests.get(url_photo).content
                            with open(f'Icons/{champ_name}.png', 'wb') as photo:
                                photo.write(icon)

                    th.Thread(target=download_icon).start()

                cur_media.execute("UPDATE start SET version = :version", {'version': version})
                conn_media.commit()
                conn_media.close()
                self.my_menu.entryconfig(f"Patch {self.version}", label=f"Patch {version}")
                self.version = version
            except (FileNotFoundError, requests.exceptions.ConnectionError):
                time.sleep(retry_delay)
        else:
            pass

    # DOWNLOADS THE SKINS, ICONS AND INFO OF A SELECTED CHAMPION--------------------------------------------------------
    def skins(self, name, widget=None):
        max_tries = 5
        for _ in range(max_tries):
            try:
                url_champ_i = f"http://ddragon.leagueoflegends.com/cdn/{self.version}/data/en_US/champion/{name}.json"
                champ_info = requests.get(url_champ_i)
                info = champ_info.json()['data'][name]
                spell_list = []
                description_list = []
                skin_list = []
                # lore = info['lore']
                p_name = info['passive']['image']['full']
                p_description = info['passive']['description']
                spell_list.append(p_name)
                description_list.append(p_description)

                skin_folder = Path('Champs')
                if not skin_folder.is_dir():
                    pathlib.Path("Champs").mkdir(exist_ok=True)

                p_path = Path(f"Champs/{p_name}")
                if not p_path.is_file():
                    url_p = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/passive/{p_name}"
                    p_icon = requests.get(url_p).content
                    with open(f"Champs/{p_name}", 'wb') as foto:
                        foto.write(p_icon)

                def download_spell(s_n, max_retries=5, retry_delay=1):
                    for _ in range(max_retries):
                        try:
                            s_p = Path(f"Champs/{s_n}.png")
                            if not s_p.is_file():
                                url_s = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/spell/{s_n}.png"
                                s_icon = requests.get(url_s).content
                                with open(s_p, 'wb') as f:
                                    f.write(s_icon)
                                break
                        except requests.exceptions.ConnectionError:
                            time.sleep(retry_delay)
                    else:
                        pass

                spell_threads = []
                for spell in info['spells']:
                    s_name = spell['id']
                    s_description = spell['description']
                    spell_list.append(f"{s_name}.png")
                    description_list.append(s_description)
                    download_thread = th.Thread(target=lambda n=s_name: download_spell(n))
                    spell_threads.append(download_thread)
                    download_thread.start()

                def download_skin(ss_name, n, max_retries=5, retry_delay=1):
                    for _ in range(max_retries):
                        try:
                            path = Path(f"Champs/{ss_name}.jpg")
                            if not path.is_file():
                                url_ph = f'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{name}_{n}.jpg'
                                skin = requests.get(url_ph).content
                                with open(path, 'wb') as image:
                                    image.write(skin)
                            break
                        except requests.exceptions.ConnectionError:
                            time.sleep(retry_delay)
                    else:
                        pass

                skin_threads = []
                for i in info['skins']:
                    skin_name = i['name'].replace('/', '_')
                    if skin_name == 'default':
                        skin_name = f"Default {name}"
                    skin_list.append(skin_name)
                    d_thread = th.Thread(target=lambda n=skin_name, m=i["num"]: download_skin(n, m))
                    skin_threads.append(d_thread)
                    d_thread.start()

                for thread in spell_threads + skin_threads:
                    thread.join()
                if widget is not None:
                    widget.withdraw()
                if self.champ_top is not None:
                    try:
                        self.champ_top.destroy()
                        if self.champ_top in self.top_level:
                            self.top_level.remove(self.champ_top)
                        gc.collect()
                    except _tkinter.TclError:
                        pass
                self.champ_top = Toplevel(root, bg=self.bg)
                self.champ_top.iconbitmap(app_icon)
                self.top_level.append(self.champ_top)
                self.champion_info(spell_list, description_list, skin_list, widget)
                break

            except requests.exceptions.ConnectionError:
                self.skins(name, widget)

        else:
            self.skins(name, widget)
            max_tries -= 1

    # CHECKS ALL THE CHAMPIONS AND CAN SEE THE SKINS AND ABILITIES------------------------------------------------------
    def champions(self):
        if all(Path(f"Icons/{i[1]}.png").is_file() for i in self.champ_db):
            c_champ = Canvas(self.f_champ, width=app_width - 17, height=bot_height, bg=self.bg, bd=0,
                             highlightthickness=0)
            c_champ.pack(side=LEFT, fill=BOTH, expand=1)
            s_champ = Scrollbar(self.f_champ, orient=VERTICAL, command=c_champ.yview, bg=self.bg)
            s_champ.pack(side=RIGHT, fill=Y)
            c_champ.configure(yscrollcommand=s_champ.set)
            f_champ2 = Frame(c_champ, bg=self.bg)
            self.frames.append(f_champ2)
            c_champ.create_window((0, 0), window=f_champ2, anchor='nw', width=app_width - 17)
            c_champ.bind('<Configure>', lambda event: c_champ.configure(scrollregion=c_champ.bbox('all')))
            c_champ.bind("<Enter>", lambda e: self.final_scroll(c_champ, lambda event: self.scroll(c_champ, event), e))
            c_champ.bind("<Leave>", lambda e: self.stop_scroll(c_champ, e))
            row = 0
            col = 0
            for champ in self.champ_db:
                img = Image.open(f"Icons/{champ[1]}.png")
                img = img.resize((64, 64))
                photo = ImageTk.PhotoImage(img)
                icon = Button(f_champ2, image=photo, relief="flat", borderwidth=0, cursor='hand2')
                icon.config(command=lambda n=champ[1]: self.skins(n))
                icon.image = photo
                icon.grid(row=row, column=col, padx=2, pady=2)
                col += 1
                if col == 14:
                    col = 0
                    row += 1
            c_champ.configure(scrollregion=c_champ.bbox('all'))
        else:
            pass

    # SHOWS THE SKINS AND ABILITIES OF THE CHAMPIONS--------------------------------------------------------------------
    def champion_info(self, skills, description, skins, widget=None):

        def swap(index):
            curr1 = index
            prev1 = (curr1 - 1) % len(skins)
            next1 = (curr1 + 1) % len(skins)

            ind = [prev1, curr1, next1]
            paths = [f"Champs/{skins[prev1]}.jpg", f"Champs/{skins[curr1]}.jpg", f"Champs/{skins[next1]}.jpg"]
            sizes = [(w2, h2), (w, h), (w2, h2)]
            for s in range(3):
                try:
                    img = Image.open(paths[s])
                except (UnidentifiedImageError, FileNotFoundError):
                    img = Image.open(default_path)
                img = img.resize(sizes[s])
                foto = ImageTk.PhotoImage(img)
                buttons[s].config(command=lambda m=ind[s]: swap(m), image=foto, text=skins[ind[s]], compound="top")
                buttons[s].photo = foto

        def show_champ_top():
            self.champ_top.destroy()
            self.top_level.remove(self.champ_top)
            gc.collect()
            if widget is not None:
                widget.deiconify()

        w, h, w2, h2, app_w, app_h = 700, 415, 300, 178, 1315, 510
        screen_w = self.champ_top.winfo_screenwidth()
        screen_h = self.champ_top.winfo_screenheight()
        self.champ_top.geometry(f'{app_w}x{app_h}+{(screen_w // 2) - (app_w // 2)}+'f'{(screen_h // 2) - (app_h // 2)}')

        inde = [(0 - 1) % len(skins), 0, (0 + 1) % len(skins)]
        size = [(w2, h2), (w, h), (w2, h2)]
        buttons = []
        col = [0, 3, 8]
        col_span = [3, 5, 3]
        default_path = 'Images/mastery.ico'
        for i in range(3):
            image_path = f"Champs/{skins[inde[i]]}.jpg"
            try:
                image = Image.open(image_path)
            except (UnidentifiedImageError, FileNotFoundError):
                image = Image.open(default_path)

            image = image.resize((size[i]))
            photo = ImageTk.PhotoImage(image)
            image_b = Button(self.champ_top, image=photo, text=skins[inde[i]], compound="top",
                             relief="flat", borderwidth=0, font=('Arial', 11, 'italic'))
            image_b.photo = photo
            try:
                image_b.config(command=lambda g=inde[i]: swap(g))
                image_b.grid(row=0, column=col[i], columnspan=col_span[i])
                buttons.append(image_b)
            except FileNotFoundError:
                pass

        s_col = 3
        for j in skills:
            spell_path = f"Champs/{j}"
            try:
                s_image = Image.open(spell_path)
            except (UnidentifiedImageError, FileNotFoundError):
                s_image = Image.open(default_path)
            s_image = s_image.resize((50, 50))
            s_photo = ImageTk.PhotoImage(s_image)
            spell_b = Label(self.champ_top, image=s_photo, width=50, height=50)
            spell_b.photo = s_photo
            spell_b.grid(row=1, column=s_col)
            soup = BeautifulSoup(description[s_col-3], "html.parser")
            clean_desc = soup.get_text()
            CreateToolTip(spell_b, text=clean_desc)
            s_col += 1
        self.champ_top.protocol("WM_DELETE_WINDOW", show_champ_top)

    # FUNCTION TO DELETE AND ADD NEW THEMES, CANT DELETE OR EDIT THE 4 INITIAL THEMES-----------------------------------
    def edit_theme(self):

        def pick(widget, original_text):
            choose = colorchooser.askcolor()
            if choose[1]:
                widget.delete(0, "end")
                widget.insert(0, choose[1])
                widget.config(bg=choose[1])
            else:
                # If no color was chosen, keep the original text
                widget.delete(0, "end")
                widget.insert(0, original_text)

        def add_new():

            def confirm():
                try:
                    hex_list = [colors[0].get(), colors[1].get(), colors[2].get(), colors[3].get()]
                    if e_name.get().isnumeric() or e_name.get() == '' or len(e_name.get()) > 15:
                        l_error.config(text='Enter a full name and not only numbers \n Min 1 - Max 15 characters')
                    elif not all(re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hx) for hx in hex_list):
                        l_error.config(text='HEX code is not valid')
                    else:
                        conn1 = sqlite3.connect('Default Name.db')
                        cur1 = conn1.cursor()
                        cur1.execute("INSERT INTO theme VALUES(:theme_name, :bg, :bg2, :bt, :fg)", {
                            'theme_name': e_name.get(), 'bg': colors[0].get(), 'bg2': colors[1].get(),
                            'bt': colors[2].get(), 'fg': colors[3].get()})
                        cur1.execute("SELECT * FROM theme")
                        theme_db_update = cur1.fetchall()
                        j2 = theme_db_update[-1]
                        self.theme_menu.add_command(label=j2[0], command=lambda n=j2[1], o=j2[2], c=j2[3], e=j2[4]:
                                                    self.change_theme(n, o, c, e))

                        conn1.commit()
                        conn1.close()
                        on_closing()
                        top_main.withdraw()
                        self.edit_theme()
                        self.change_theme(j2[1], j2[2], j2[3], j2[4])
                        # self.edit_theme()
                except sqlite3.IntegrityError:
                    l_error.config(text='Name already exists')

            def on_closing():
                top.withdraw()
                bt_add.config(state='normal')

            bt_add.config(state='disabled')
            top_width2 = 250
            top_height2 = 200
            top = Toplevel(root, bg=self.bg)
            self.top_level.append(top)
            top.geometry(f'{top_width2}x{top_height2}+{((screen_width // 2) - (top_width2 // 2)) + 150}+'
                         f'{(screen_height // 2) - (top_height2 // 2)}')
            top.attributes('-topmost', 'true')
            top.title('Add Theme')
            top.iconbitmap(app_icon)
            for config2 in range(10):
                top.columnconfigure(config, weight=1)
                top.rowconfigure(config, weight=1)

            con = sqlite3.connect('Default Name.db')
            cur = con.cursor()
            cur.execute("SELECT bg, bg2, bt, fg FROM start")
            fetch = cur.fetchone()
            colors = ['Background 1', 'Background 2', 'Button', 'Text']
            row2 = 0
            for i2 in colors:
                colors[row2] = Entry(top, bg=self.bg2, fg=self.fg, width=15, bd=0)
                colors[row2].insert(0, fetch[row2])
                colors[row2].grid(row=row2, column=0, padx=10, ipady=2)
                self.entries.append(colors[row2])
                i2 = Button(top, text=i2, bg=self.bt, fg=self.fg, width=13)
                i2.config(command=lambda n=colors[row2], m=fetch[row2]: pick(n, m))
                i2.grid(row=row2, column=1, pady=2)
                self.buttons.append(i2)
                row2 += 1
            e_name = Entry(top, width=15, bg=self.bg2, fg=self.fg, justify=RIGHT)
            e_name.grid(row=4, column=0, ipady=3)
            bt_confirm = Button(top, text='Confirm', command=confirm, width=13, bg=self.bt, fg=self.fg)
            bt_confirm.grid(row=4, column=1, pady=10)
            l_error = Label(top, fg=self.fg, bg=self.bg)
            l_error.grid(row=5, column=0, columnspan=10)
            self.entries.append(e_name)
            self.buttons.append(bt_confirm)
            self.labels.append(l_error)
            top.protocol("WM_DELETE_WINDOW", on_closing)

        def edit(widget, bt, theme):
            colorchooser_top = Toplevel(top_main)
            colorchooser_top.withdraw()
            choose = colorchooser.askcolor(parent=colorchooser_top)
            if choose[1]:
                widget.config(bg=choose[1])
                conn1 = sqlite3.connect('Default Name.db')
                cur1 = conn1.cursor()
                cur1.execute(f"UPDATE theme SET {bt} = '{choose[1]}' WHERE theme_name = '{theme}'")
                cur1.execute(f"SELECT * FROM theme WHERE theme_name = '{theme}'")
                u = cur1.fetchone()
                cur1.execute("UPDATE start SET bg = ?, bg2 = ?, bt = ?, fg = ? WHERE name = ?",
                             (u[1], u[2], u[3], u[4], self.start_name))
                conn1.commit()
                colorchooser_top.protocol("WM_DELETE_WINDOW", self.change_theme(u[1], u[2], u[3], u[4]))

        def delete(name, widget, *_):
            ask = messagebox.askyesno("Delete", f"Delete theme {name}", parent=top_main)
            if ask:
                self.labels.remove(widget[0])
                for w in widget:
                    w.destroy()
                self.theme_menu.delete(str(name))
                conn3 = sqlite3.connect('Default Name.db')
                cur3 = conn3.cursor()
                cur3.execute(f'''DELETE FROM theme WHERE theme_name LIKE "{name}"''')
                conn3.commit()
                conn3.close()
            else:
                pass

        top_width = 300
        top_height = 400
        top_main = Toplevel(root, bg=self.bg)
        top_main.resizable(False, False)
        top_main.geometry(f'{top_width}x{top_height}+{((screen_width // 2) - (top_width // 2)) + 150}+'
                          f'{(screen_height // 2) - (top_height // 2)}')
        top_main.attributes('-topmost', 'true')
        top_main.title('Add Theme')
        top_main.iconbitmap(app_icon)
        self.top_level.append(top_main)
        top_main.protocol("WM_DELETE_WINDOW", top_main.withdraw)
        for config in range(20):
            top_main.columnconfigure(config, weight=1)
            top_main.rowconfigure(config, weight=1)

        bt_add = Button(top_main, text='Add New', width=13, bg=self.bt, fg=self.fg, command=add_new)
        bt_add.grid(row=0, column=0, columnspan=20, pady=5)
        self.buttons.append(bt_add)
        l_warning = Label(top_main, bg=self.bg, fg=self.fg, font=(self.f, 10),
                          text='Delete the theme by clicking on the name\n Max number of themes is 10!')
        l_warning.grid(row=1, column=0, columnspan=20, sticky='n')
        self.labels.append(l_warning)

        conn2 = sqlite3.connect('Default Name.db')
        cur2 = conn2.cursor()
        cur2.execute('''SELECT * FROM theme''')
        info = cur2.fetchall()
        cur2.execute('''SELECT COUNT(theme_name) FROM theme''')
        check = cur2.fetchone()
        if check[0] >= 14:
            bt_add.config(state='disabled')
        else:
            bt_add.config(state='normal')

        column = 4
        name_list = ['bg', 'bg2', 'bt', 'fg']

        for j in name_list:
            lbl_name = Label(top_main, text=j, width=3, height=1, bg=self.bg, fg=self.fg)
            lbl_name.grid(row=2, column=column, columnspan=4, pady=1, sticky='n')
            self.labels.append(lbl_name)
            column += 4
        row = 3
        for i in info[4:]:
            theme_name = Label(top_main, text=i[0], bg=self.bg, fg=self.fg, bd=0)
            theme_name.grid(row=row, column=0, columnspan=4, pady=1, sticky='e')
            self.labels.append(theme_name)
            color_bg = Button(top_main, bg=i[1], width=3, height=1, borderwidth=3, relief="groove")
            color_bg.config(command=lambda btn=color_bg, name=i[0]: edit(btn, 'bg', name))
            color_bg.grid(row=row, column=4, columnspan=4, pady=1)
            color_bg2 = Button(top_main, bg=i[2], width=3, height=1, borderwidth=3, relief="groove")
            color_bg2.config(command=lambda btn=color_bg2, name=i[0]: edit(btn, 'bg2', name))
            color_bg2.grid(row=row, column=8, columnspan=4, pady=1)
            color_bt = Button(top_main, bg=i[3], width=3, height=1, borderwidth=3, relief="groove")
            color_bt.config(command=lambda btn=color_bt, name=i[0]: edit(btn, 'bt', name))
            color_bt.grid(row=row, column=12, columnspan=4, pady=1)
            color_fg = Button(top_main, bg=i[4], width=3, height=1, borderwidth=3, relief="groove")
            color_fg.config(command=lambda btn=color_fg, name=i[0]: edit(btn, 'fg', name))
            color_fg.grid(row=row, column=16, columnspan=4, pady=1)
            theme_name.bind("<Button-1>", lambda e, n=i[0], w1=theme_name, w2=color_bg, w3=color_bg2, w4=color_bt,
                            w5=color_fg: delete(n, [w1, w2, w3, w4, w5]))
            row += 1
        conn2.commit()
        conn2.close()

    # USED TO PLACE THE FOUR PHOTOS OF THE CHAMPION MASTERY-------------------------------------------------------------
    def logo(self):
        f_column = 0
        p_name = 7
        # TOP FRAMES AND PHOTOS-----------------------------------------------------------------------------------------
        for i in range(4):
            img = Image.open(f"Images/lvl{p_name}.png")
            img = img.resize((248, 100))
            photo7 = ImageTk.PhotoImage(img)
            icons = Label(self.f_top, image=photo7, bg=self.bg2)
            icons.image = photo7
            icons.grid(row=1, column=f_column, columnspan=2)
            self.frames2.append(icons)
            f_column += 2
            p_name -= 1

    # CHANGES THE THEME FOR THE MAIN WINDOW AND THE FRIENDS LIST, SAVES THE LAST THEME SET ON THE DATABASE--------------
    def change_theme(self, bg, bg2, bt, fg):
        conn1 = sqlite3.connect('Default Name.db')
        cur1 = conn1.cursor()
        cur1.execute("UPDATE start SET bg = :bg, bg2 = :bg2, bt = :bt, fg = :fg",
                     {'bg': bg, 'bg2': bg2, 'bt': bt, 'fg': fg})
        conn1.commit()
        self.bg, self.bg2, self.bt, self.fg = bg, bg2, bt, fg

        def configure_widgets(widgets, bg_color, fg_color=None):
            for widget in widgets:
                widget.configure(bg=bg_color)
                if fg_color is not None:
                    try:
                        widget.configure(fg=fg_color)
                    except _tkinter.TclError:
                        pass

        th.Thread(target=lambda: configure_widgets(self.f_f + self.f_c + self.frames, bg)).start()
        th.Thread(target=lambda: configure_widgets(self.name, bg, fg)).start()
        th.Thread(target=lambda: configure_widgets(self.points, bg, fg)).start()
        th.Thread(target=lambda: configure_widgets(self.labels, bg, fg)).start()
        th.Thread(target=lambda: configure_widgets(self.buttons, bt, fg)).start()
        th.Thread(target=lambda: configure_widgets(self.entries, bg2, fg)).start()
        th.Thread(target=lambda: configure_widgets(self.chest + self.top_level, bg)).start()
        th.Thread(target=lambda: configure_widgets(self.token, bg)).start()
        th.Thread(target=lambda: configure_widgets(self.frames2, bg2, fg)).start()
        th.Thread(target=lambda: configure_widgets(self.level_check, bg, bt)).start()
        gc.collect()

    # FUNCTION TO CHECK THE PLAYERS IN-GAME AND THE CHAMPS PICKED, APPEARS THE CIRCLE NEAR THE NAME---------------------
    def status(self):
        # URL TO CHECK IF THERE IS AN ACTIVE GAME FOR A SEARCHED PLAYER-------------------------------------------------
        url_game = f"https://{self.region}.api.riotgames.com/lol/spectator/v4/active-games/by-puuid/" \
                   f"{self.summoner_id}?api_key={API}"
        game_data = requests.get(url_game)
        info = game_data.json()
        if game_data.status_code == 200:
            # FUNCTION TO ADD AS FRIEND A PLAYER IN-GAME----------------------------------------------------------------
            def confirm(summoner_name, region):
                try:
                    conn = sqlite3.connect('Default Name.db')
                    cur = conn.cursor()
                    cur.execute("INSERT INTO friends VALUES(:name, :region)", {
                        'name': summoner_name,
                        'region': region
                    })
                    conn.commit()
                    conn.close()
                    self.check_status = True
                    self.friends()
                except sqlite3.IntegrityError:
                    messagebox.showerror('Database error', f'{summoner_name} is already a friend', parent=f_live)

            def watch_live():
                lol_dir = "C:\Riot Games\League of Legends\Game"
                lol_exe = "League of Legends.exe"
                server = f"spectator spectator-consumer.{info['platformId'].lower()}.lol.pvp.net:80"
                key = info['observers']['encryptionKey']
                game_id = str(info['gameId'])
                platform = info['platformId']
                command = f'cd /d "{lol_dir}" & "{lol_exe}" "{server} {key} {game_id} {platform}" "-UseRads"'
                try:
                    l_live.config(state="disabled", text="Game running")
                    os.popen(command)
                except Exception as e:
                    print(f"Error: {e}")

            # TOPLEVEL WINDOWS FOR THE DISPLAY OF THE GAME TIME AND THE PLAYERS NAME AND CHAMP--------------------------
            def check_running():
                try:
                    url_game2 = f"https://{self.region}.api.riotgames.com/lol/spectator/v4/active-games/by-puuid/" \
                               f"{self.summoner_id}?api_key={API}"
                    game_data2 = requests.get(url_game2)
                    if game_data2.status_code == 200 and f_live.winfo_viewable() and os.path.exists(lol_path):
                        root.after(2000, check_running)
                    else:
                        f_live.withdraw()
                    processes = psutil.process_iter()
                    for process in processes:
                        if process.name() == "League of Legends.exe":
                            if l_live.cget('text') == "Game running":
                                pass
                            else:
                                l_live.config(state="disabled", text="Game running")
                            break
                        else:
                            if l_live.cget('text') == "LIVE":
                                pass
                            else:
                                l_live.config(state="normal", text="LIVE")
                except requests.exceptions.ConnectionError:
                    pass

            self.bt_status.config(state='disabled')
            top_w = 700
            top_h = 400
            f_live = Toplevel(root, width=top_w, height=top_h)
            f_live.geometry(f'{top_w}x{top_h}+{(screen_width // 2)-(top_w // 2)}+{(screen_height // 2)-(top_h // 2)}')
            f_live.attributes('-topmost', 'true')
            f_live.grid_propagate(False)
            f_live.resizable(False, False)
            f_live.protocol("WM_DELETE_WINDOW", lambda: (f_live.withdraw(), self.bt_status.config(state='normal')))
            f_live.iconbitmap(app_icon)
            self.top_level.append(f_live)
            f_top = Frame(f_live, width=top_w, height=100, bg=self.bg)
            f_top.grid(row=0, column=0)
            f_top.grid_propagate(False)
            for cl in range(2):
                f_top.columnconfigure(cl, weight=1)
            self.frames.append(f_top)
            game = info['gameMode'].capitalize()
            l_mode = Label(f_top, text=f"Game mode: {game}", font=(self.f, 15), bg=self.bg, fg=self.fg)
            l_mode.grid(row=0, column=0, sticky='w')
            self.labels.append(l_mode)
            l_live = Button(f_top, text="LIVE", bg=self.bg, font=(self.f, 15, "bold"), fg='red', cursor='hand2', bd=0)
            # l_live.bind("<Button-1>", lambda e: watch_live())
            l_live.config(command=watch_live)
            l_live.grid(row=0, column=1, padx=10, sticky='e')
            lol_path = r"C:\Riot Games\League of Legends\Game\League of Legends.exe"
            if not os.path.exists(lol_path):
                l_live.config(state="disabled", text="Game not found")
            else:
                check_running()
            self.token.append(l_live)

            def update():
                now = datetime.fromtimestamp(time.time()).replace(microsecond=0)
                start_time = datetime.fromtimestamp(info['gameStartTime'] / 1000).replace(microsecond=0)
                l_time.config(text=f'Time in game: {now - start_time}')
                l_time.after(1000, update)

            l_time = Label(f_top, text='', font=(self.f, 15), bg=self.bg, fg=self.fg)
            self.labels.append(l_time)
            l_time.grid(row=1, column=0, columnspan=2, sticky='w')
            l_time.after(500, update)

            separator = ttk.Separator(f_live, orient='horizontal')
            separator.grid(row=1, column=0, sticky='ew', ipady=1)

            f_bot = Frame(f_live, width=top_w, height=300, bg=self.bg2)
            f_bot.grid(row=2, column=0)
            self.frames2.append(f_bot)
            f_bot.grid_propagate(False)
            for c in range(6):
                f_bot.columnconfigure(c, weight=1)

            self.dicts = {}
            for k in self.champ_db:
                self.dicts[k[0]] = k[1]

            row = 0
            z = 0
            for i in info['participants']:
                img = Image.open(f"Icons/{self.dicts[i['championId']]}.png")
                img = img.resize((50, 50))
                photo = ImageTk.PhotoImage(img)
                icon = Button(f_bot, image=photo, bg=self.bt)
                icon.config(command=lambda name=self.dicts[i['championId']]: self.skins(name, f_live))
                icon.image = photo
                self.buttons.append(icon)

                img2 = Image.open(f"Images/add.png")
                img2 = img2.resize((25, 25))
                photo2 = ImageTk.PhotoImage(img2)
                add = Label(f_bot, image=photo2, bg=self.bg2, cursor='hand2')
                add.bind("<Button-1>", lambda e, n=i['summonerName'], m=d_r[self.sv_region.get()]: confirm(n, m))
                add.image = photo2

                names = Label(f_bot, text=i['summonerName'], font=(self.f, 12), bg=self.bg2, fg=self.fg, cursor='hand2')
                names.bind("<Button-1>", lambda e, n=i['summonerName'], m=d_r[self.sv_region.get()]: self.search(n, m))
                self.frames2.extend([add, names])
                if z < 5:
                    icon.grid(row=row, column=0, pady=1, padx=(5, 0), sticky='w')
                    add.grid(row=row, column=0, padx=(0, 5), ipadx=5, sticky='e')
                    names.grid(row=row, column=1, sticky='w')
                    row += 1
                    if row == 5:
                        row = 0
                    z += 1
                elif z > 4:
                    icon.grid(row=row, column=5, pady=1, padx=(0, 5), sticky='e')
                    add.grid(row=row, column=5, padx=(5, 0), ipadx=5, sticky='w')
                    names.grid(row=row, column=4, sticky='e')
                    row += 1
                    z += 2
        else:
            pass

    # FUNCTION FOR THE FRIENDS LIST, CAN ADD, DELETE AND SEARCH SUMMONERS-----------------------------------------------
    def friends(self):
        top_width = 230
        if self.check_status:
            self.check_status = False
            self.settings_value = True
            root.geometry(f'{app_width+230}x{app_height}')
            dl_list, fr_list, up_list, down_list = [], [], [], []

            def friends_list():

                def delete(name, region, w):
                    rsp = messagebox.askyesno("Delete", f"Delete {name} from friends?", parent=root)
                    if rsp == 1:
                        conn2 = sqlite3.connect('Default Name.db')
                        cur2 = conn2.cursor()
                        cur2.execute(f"DELETE FROM friends WHERE name = '{name}' AND region = '{region}'")
                        conn2.commit()
                        conn2.close()
                        self.labels.remove(dl_list[w])
                        self.labels.remove(up_list[w])
                        self.labels.remove(down_list[w])
                        self.buttons.remove(fr_list[w])
                        dl_list[w].destroy()
                        dl_list.pop(w)
                        up_list[w].destroy()
                        up_list.pop(w)
                        down_list[w].destroy()
                        down_list.pop(w)
                        fr_list[w].destroy()
                        fr_list.pop(w)
                    else:
                        pass

                def swap(iid, move, *_):
                    up = (iid + 1) % len(info)
                    if move == 'up':
                        up = (iid - 1) % len(info)
                    id1, id2 = info[iid], info[up]
                    conn2 = sqlite3.connect('Default Name.db')
                    cur2 = conn2.cursor()
                    temp_name = f'temp_{id1[0]}'
                    cur2.execute("UPDATE friends SET name = ? WHERE name = ?", (temp_name, id1[0]))
                    cur2.execute("UPDATE friends SET name = ?, region = ? WHERE name = ?", (id1[0], id1[1], id2[0]))
                    cur2.execute("UPDATE friends SET name = ?, region = ? WHERE name = ?", (id2[0], id2[1], temp_name))
                    conn2.commit()
                    conn2.close()
                    name1 = f"{id2[0]} -{d_r2[id2[1]]}"
                    name2 = f"{id1[0]} -{d_r2[id1[1]]}"

                    dl_list[iid].bind("<Button-1>", lambda e, o=id2[0], p=id2[1], t=iid: delete(o, p, t))
                    fr_list[iid].config(command=lambda n=id2[0], m=id2[1]: self.search(n, m), text=name1)
                    up_list[iid].bind("<Button-1>", lambda e, c=iid, p='up': swap(c, p))
                    down_list[iid].bind("<Button-1>", lambda e, c=iid, p='down': swap(c, p))

                    dl_list[up].bind("<Button-1>", lambda e, o=id1[0], p=id1[1], t=up: delete(o, p, t))
                    fr_list[up].config(command=lambda n=id1[0], m=id1[1]: self.search(n, m), text=name2)
                    up_list[up].bind("<Button-1>", lambda e, c=up, p='up': swap(c, p))
                    down_list[up].bind("<Button-1>", lambda e, c=up, p='down': swap(c, p))

                    info[iid], info[up] = info[up], info[iid]

                def settings():

                    if self.settings_value:
                        self.settings_value = False
                        for items in up_list + down_list + dl_list:
                            items.grid_remove()
                    else:
                        self.settings_value = True
                        for items in up_list + down_list + dl_list:
                            items.grid()

                f_friends = Frame(self.friend_list, width=208, height=friends_h, bg=self.bg)
                f_friends.grid(row=2, column=0, sticky='nsew')
                f_friends.grid_propagate(False)

                c_friend = Canvas(f_friends, width=208, height=friends_h, bg=self.bg, highlightthickness=0)
                c_friend.pack(side=LEFT, fill=BOTH, expand=1)
                s_friend = Scrollbar(f_friends, orient=VERTICAL, command=c_friend.yview, bg=self.bg)
                s_friend.pack(side=RIGHT, fill=Y)
                c_friend.configure(yscrollcommand=s_friend.set)
                c_friend.bind('<Configure>', lambda event: c_friend.configure(scrollregion=c_friend.bbox('all')))
                f_fr = Frame(c_friend, bg=self.bg)
                self.frames.extend([f_friends, c_friend, f_fr])
                c_friend.create_window((0, 2), window=f_fr, anchor='nw')
                c_friend.bind("<Enter>", lambda e: self.final_scroll(c_friend,
                                                                     lambda event: self.scroll(c_friend, event), e))
                c_friend.bind("<Leave>", lambda e: self.stop_scroll(c_friend, e))

                conn1 = sqlite3.connect('Default Name.db')
                cur1 = conn1.cursor()
                cur1.execute('SELECT *, oid FROM friends')
                info = cur1.fetchall()
                conn1.close()
                row = 0
                bt_stg.config(command=settings)

                for i in range(len(info)):
                    bt_friends = Button(f_fr, text=f'{info[i][0]} -{d_r2[info[i][1]]}', bg=self.bt, fg=self.fg,
                                        cursor='hand2', command=lambda n=info[i][0], m=info[i][1]: self.search(n, m))
                    bt_friends.grid(row=row, column=3, sticky='w', padx=5, pady=3)
                    fr_list.append(bt_friends)
                    self.buttons.append(bt_friends)
                    if self.settings_value:
                        bt_del = Label(f_fr, text='X', font=(self.f, 8), bg=self.bg, fg=self.fg, bd=0, cursor='hand2')
                        bt_del.grid(row=row, column=0, sticky='w', padx=3, pady=3)
                        bt_up = Label(f_fr, text='↑', font=(self.f, 8), bg=self.bg, fg=self.fg, bd=0, cursor='hand2')
                        bt_up.grid(row=row, column=1, sticky='w', padx=3, pady=3)
                        bt_down = Label(f_fr, text='↓', font=(self.f, 8), bg=self.bg, fg=self.fg, bd=0, cursor='hand2')
                        bt_down.grid(row=row, column=2, sticky='w', padx=3, pady=3)
                        bt_del.bind("<Button-1>", lambda e, o=info[i][0], p=info[i][1], t=i: (delete(o, p, t)))
                        bt_up.bind("<Button-1>", lambda e, c=i, p='up': swap(c, p))
                        bt_down.bind("<Button-1>", lambda e, c=i, n='down': swap(c, n))
                        dl_list.append(bt_del)
                        up_list.append(bt_up)
                        down_list.append(bt_down)
                        self.labels.extend([bt_del, bt_down, bt_up])
                    row += 1
                settings()

            def add():
                # friend_list.config(bg=self.bg)

                def confirm(*_):
                    url_info = f"https://{d_r[sv_region.get()]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/" \
                               f"{e_start_name.get()}?api_key={API}"
                    summoner_info_request = requests.get(url_info)
                    data = summoner_info_request.json()
                    if summoner_info_request.status_code == 200:
                        try:
                            conn = sqlite3.connect('Default Name.db')
                            cur = conn.cursor()
                            cur.execute("INSERT INTO friends VALUES(:name, :region)", {
                                'name': data['name'],
                                'region': d_r[sv_region.get()]
                            })
                            conn.commit()
                            conn.close()
                            top_add.withdraw()
                            friends_list()

                        except sqlite3.IntegrityError:
                            l_error.configure(text='Already exist')
                    else:
                        l_error.configure(text='Not found')

                top_w = 350
                top_h = 100
                top_add = Toplevel(self.friend_list)
                top_add.protocol("WM_DELETE_WINDOW", top_add.withdraw)
                top_add.geometry(
                    f'{top_w}x{top_h}+{(screen_width // 2) - (top_w // 2)}+{(screen_height // 2) - (top_h // 2)}')
                top_add.attributes('-topmost', 'true')
                top_add.title('Add friend')
                top_add.iconbitmap(app_icon)
                self.top_level.append(top_add)
                top_add.grid_rowconfigure(0, weight=1)
                top_add.grid_columnconfigure(0, weight=1)

                top_frame = Frame(top_add, bg=self.bg)
                top_frame.grid(row=0, column=0, sticky='nsew')
                sv_region = StringVar()
                om_region = ttk.OptionMenu(top_frame, sv_region, d_r2[self.region], *regions)
                om_region.grid(row=0, column=0, pady=7, padx=(40, 5))
                e_start_name = Entry(top_frame, font=(self.f, 12), width=15, bg=self.bg2, fg=self.fg)
                e_start_name.grid(row=0, column=1, pady=7)
                e_start_name.bind('<Return>', confirm)
                e_start_name.focus()
                bt_confirm = Button(top_frame, text='Confirm', command=confirm, bg=self.bt)
                bt_confirm.grid(row=1, column=1, pady=4)
                l_error = Label(top_frame, text='', fg='red', bg=self.bg)
                l_error.grid(row=2, column=1, pady=4)
                self.frames.append(top_frame)
                self.entries.append(e_start_name)
                self.buttons.append(bt_confirm)
                self.labels.append(l_error)

            self.friend_list.grid(row=0, column=4, columnspan=1, rowspan=2, sticky='n')
            self.friend_list.grid_propagate(False)
            # friend_list.bind("<Destroy>", frame_destroyed)
            f_button = Frame(self.friend_list, width=top_width, height=48, bg=self.bg2)
            f_button.grid(row=0, column=0)
            f_button.grid_propagate(False)
            bt_add = Button(f_button, text='Add', font=(self.f, 10), width=8, command=add, bg=self.bt, fg=self.fg)
            bt_add.grid(row=0, column=0, pady=10, padx=(50, 20))
            bt_stg = Button(f_button, text='⚙', font=(self.f, 10), bg=self.bt, fg=self.fg)
            bt_stg.grid(row=0, column=1)
            self.frames2.append(f_button)
            self.buttons.extend([bt_stg, bt_add])
            friends_list()

        else:
            try:
                self.check_status = True
                root.geometry(f'1000x{app_height}')
                top_f = self.friend_list.winfo_children()[0]
                bot_f1 = self.friend_list.winfo_children()[1]
                bot_f2 = self.friend_list.winfo_children()[1].winfo_children()[0]
                bot_s2 = self.friend_list.winfo_children()[1].winfo_children()[1]
                bot_f3 = self.friend_list.winfo_children()[1].winfo_children()[0].winfo_children()[0]
                for bt1 in top_f.winfo_children():
                    if isinstance(bt1, Button):
                        bt1.destroy()
                        self.buttons.remove(bt1)
                top_f.destroy()
                self.frames2.remove(top_f)
                for bt2 in bot_f3.winfo_children():
                    if isinstance(bt2, Button):
                        bt2.destroy()
                        self.buttons.remove(bt2)
                    elif isinstance(bt2, Label):
                        bt2.destroy()
                        self.labels.remove(bt2)
                bot_f3.destroy()
                self.frames.remove(bot_f3)
                bot_f2.destroy()
                self.frames.remove(bot_f2)
                bot_s2.destroy()
                bot_f1.destroy()
                self.frames.remove(bot_f1)
                gc.collect()
            except IndexError:
                pass

    # FUNCTION TO CHANGE THE DEFAULT SUMMONER NAME----------------------------------------------------------------------
    def default(self):
        # CHECKS IF THE SUMMONER NAME ENTERED IS VALID------------------------------------------------------------------
        def confirm(*_):
            url_summoner_info = f"https://{d_r[sv_region.get()]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/" \
                                f"{e_start_name.get()}?api_key={API}"
            summoner_info_request = requests.get(url_summoner_info)
            info = summoner_info_request.json()

            # IF THE SEARCHED SUMMONER EXISTS IT INSERTS THE INFO ON THE DATABASE---------------------------------------
            if summoner_info_request.status_code == 200:
                url_mastery = f"https://{d_r[sv_region.get()]}.api.riotgames.com/lol/champion-mastery/v4/champion-" \
                              f"masteries/by-puuid/{info['id']}?api_key={API}"
                lol_request = requests.get(url_mastery)
                data = lol_request.json()
                conn1 = sqlite3.connect('Default Name.db')
                cur1 = conn1.cursor()
                cur1.execute("UPDATE start SET id = :id, lvl = :lvl, name = :name, region = :region",
                             {
                                 'id': info['id'],
                                 'lvl': info['summonerLevel'],
                                 'name': info['name'],
                                 'region': d_r[sv_region.get()],
                             })
                cur1.execute("UPDATE data SET data = :data", {'data': str(data)})
                conn1.commit()
                conn1.close()
                self.l_name.config(text=info['name'])
                self.l_level.config(text=info['summonerLevel'])
                self.region = d_r[sv_region.get()]
                self.sv_region.set(sv_region.get())
                self.request_data(str(data))
                top_add.withdraw()
            else:
                l_error.config(text='Not valid!', fg='red')

        # CREATES A TOPLEVEL WINDOW TO ENTER THE DEFAULT NAME AND THE CONFIRM BUTTON------------------------------------
        top_w = 350
        top_h = 100
        top_add = Toplevel(root)
        top_add.protocol("WM_DELETE_WINDOW", top_add.withdraw)
        top_add.geometry(
            f'{top_w}x{top_h}+{(screen_width // 2) - (top_w // 2)}+{(screen_height // 2) - (top_h // 2)}')
        top_add.attributes('-topmost', 'true')
        top_add.title('Default summoner')
        top_add.iconbitmap(app_icon)
        self.top_level.append(top_add)
        top_add.grid_rowconfigure(0, weight=1)
        top_add.grid_columnconfigure(0, weight=1)

        top_frame = Frame(top_add, bg=self.bg)
        top_frame.grid(row=0, column=0, sticky='nsew')
        sv_region = StringVar()
        om_region = ttk.OptionMenu(top_frame, sv_region, d_r2[self.region], *regions)
        om_region.grid(row=0, column=0, pady=7, padx=(40, 5))
        e_start_name = Entry(top_frame, font=(self.f, 12), width=15, bg=self.bg2, fg=self.fg)
        e_start_name.grid(row=0, column=1, pady=7)
        e_start_name.bind('<Return>', confirm)
        e_start_name.focus()
        bt_confirm = Button(top_frame, text='Confirm', command=confirm, bg=self.bt)
        bt_confirm.grid(row=1, column=1, pady=4)
        l_error = Label(top_frame, text='', fg='red', bg=self.bg)
        l_error.grid(row=2, column=1, pady=4)
        self.frames.append(top_frame)
        self.entries.append(e_start_name)
        self.buttons.append(bt_confirm)
        self.labels.append(l_error)

    # SEARCH FUNCTION TO SHOW A GIVEN SUMMONER DATA---------------------------------------------------------------------
    def search(self, name, region, *_):
        self.frames_status = True
        self.swap_frames()
        try:
            # IF THE SEARCH ENTRY IS EMPTY IT RETURNS THE DEFAULT PLAYER DATA-------------------------------------------
            if name == '':
                self.update_data()
                conn = sqlite3.connect('Default Name.db')
                cur = conn.cursor()
                cur.execute("""SELECT * FROM data""")
                info = cur.fetchall()
                cur.execute("""SELECT * FROM start""")
                info2 = cur.fetchall()
                self.l_name.config(text=info2[0][2])
                self.l_level.config(text=f"Level: {info2[0][1]}")
                self.summoner_id = info2[0][0]
                self.region = info2[0][3]
                self.sv_region.set(d_r2[info2[0][3]])
                self.request_data(info[0][0])
                conn.commit()
                conn.close()
                # th.Thread(target=self.update_data).start()
            else:
                self.l_name.grid_forget()
                self.l_name.grid(row=0, column=0)
                self.l_name.config(font=(self.f, self.fs[len(name)], 'italic'))
                self.l_name.config(text=name)
                url_summoner_name = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}" \
                                    f"?api_key={API}"
                summoner_name_request = requests.get(url_summoner_name)
                summoner_info = summoner_name_request.json()
                self.e_search.delete(0, END)
                self.summoner_id = summoner_info["puuid"]
                self.l_level.config(text=f"Level: {summoner_info['summonerLevel']}")
                self.region = region
                self.sv_region.set(d_r2[region])
                url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/" \
                      f"{self.summoner_id}?api_key={API}"
                lol_request = requests.get(url)
                data = lol_request.json()
                self.request_data(str(data))

        except KeyError:
            pass

    # MAIN FUNCTION FOR THE REQUEST AND DISPLAY OF THE SUMMONER DATA----------------------------------------------------
    def request_data(self, dat):

        for w1 in self.f_bot.winfo_children():
            for w2 in w1.winfo_children():
                for w3 in w2.winfo_children():
                    for w4 in w3.winfo_children():
                        w4.destroy()
                    w3.destroy()
                w2.destroy()
            w1.destroy()
        gc.collect()

        # GIVEN PLAYER DATA AS A STRING CONVERTED TO THE ORIGINAL DICT--------------------------------------------------
        data = eval(dat)
        if internet_connection == "127.0.0.1":
            self.e_search.config(state='disabled')
            self.bt_search.config(state='disabled')
            self.bt_friend.config(state='disabled')
            self.bt_status.config(state='disabled')
            self.bt_change.config(state='disabled')
        else:
            th.Thread(target=self.game_status).start()

        # CREATE FRAMES WITH A FOR LOOP---------------------------------------------------------------------------------
        self.f_f.clear()
        self.f_c.clear()
        for f in range(4):
            frame1 = Frame(self.f_bot, width=254, height=bot_height, bg=self.bg)
            frame1.grid(row=1, column=f)
            frame1.grid_propagate(False)
            canvas1 = Canvas(frame1, width=233, height=bot_height, bg=self.bg, bd=0, highlightthickness=0)
            canvas1.pack(side=LEFT, fill=BOTH, expand=1)
            self.f_c.append(canvas1)
            scrollbar = Scrollbar(frame1, orient=VERTICAL, command=canvas1.yview, bg=self.bg)
            scrollbar.pack(side=RIGHT, fill=Y)
            canvas1.configure(yscrollcommand=scrollbar.set)
            canvas1.bind('<Configure>', lambda event: event.widget.configure(scrollregion=event.widget.bbox('all')))
            frame2 = Frame(canvas1, bg=self.bg)
            self.f_f.append(frame2)
            canvas1.create_window((0, 2), window=frame2, anchor='nw')
            canvas1.bind("<Enter>", lambda e: self.final_scroll(e.widget,
                                                                lambda event: self.scroll(e.widget, event), e))
            canvas1.bind("<Leave>", lambda e: self.stop_scroll(e.widget, e))

        # API TO CONVERT THE CHAMPION ID TO NAME------------------------------------------------------------------------
        # Issue with link, had to change it with the other url
        # url_champ_name = "https://www.masterypoints.com/api/v1.1/static/champions"

        # CHAMPION NUMBER COUNT, INCREASING WITH EACH CREATED LABEL-----------------------------------------------------
        def filter_champ(*_):
            for i in range(4):
                for j in self.f_f[i].winfo_children():
                    j.destroy()
            row = 0
            frames = {7: self.f_f[0], 6: self.f_f[1], 5: self.f_f[2], 4: self.f_f[3], 3: self.f_f[3], 2: self.f_f[3],
                      1: self.f_f[3]}
            count = {7: 1, 6: 1, 5: 1, 4: 1, 3: 1, 2: 1, 1: 1}
            # FOR LOOP TO CREATE THE LABELS WITH THE CHAMPIONS INFO-----------------------------------------------------
            self.name.clear(), self.points.clear(), self.chest.clear(), self.token.clear(), self.level_check.clear()
            check = [True, True, True]
            chp = "championPoints"
            for i in data:
                fn = (self.f, 10)
                name = self.dicts.get(i["championId"], "Unknown")
                frame = frames[i["championLevel"]]
                lvl = i["championLevel"]

                if lvl <= 3 and check[(lvl-1)]:
                    level_ch = Label(frame, text=f'Level {lvl}', bg=self.bg, fg=self.bt, font=(self.f, 16, 'bold'))
                    level_ch.grid(row=row, column=0, sticky="W")
                    self.level_check.append(level_ch)
                    check[(lvl-1)] = False
                    row += 1

                if self.filter.get().lower() in name.lower():
                    names = Label(frame, text=f'{count[lvl]}: {name}', bg=self.bg, fg=self.fg, font=fn, cursor='hand2')
                    names.bind('<Button-1>', lambda event, n=name: self.skins(n))
                    names.grid(row=row, column=0, sticky="W")
                    self.name.append(names)
                    count[lvl] += 1
                    points = Label(frame, text=f'--{i[chp]}', bg=self.bg, fg=self.fg, font=(self.f, 9))
                    points.grid(row=row, column=1, sticky="W")
                    self.points.append(points)
                    column = 3

                    for t1 in range(i["tokensEarned"]):
                        token = PhotoImage
                        if lvl == 5:
                            token = PhotoImage(file="Images/token6.png")
                        elif lvl == 6:
                            token = PhotoImage(file="Images/token7.png")
                        tokens = Label(frame, image=token, bg=self.bg, fg=self.fg)
                        tokens.image = token
                        tokens.grid(row=row, column=column)
                        self.token.append(tokens)
                        column += 1
                    if i["chestGranted"]:
                        photo = PhotoImage(file=f"Images/chest2.png")
                        chests = Label(frame, image=photo, bg=self.bg, fg=self.fg)
                        chests.image = photo
                        chests.grid(row=row, column=2)
                        self.chest.append(chests)
                    row += 1

        self.filter.bind('<KeyRelease>', filter_champ)
        filter_champ()


class CreateToolTip(object):

    def __init__(self, widget, text='widget info'):
        self.wait_time = 1
        self.wrap_length = 400
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, *_):
        self.schedule()

    def leave(self, *_):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.wait_time, self.showtip)

    def unschedule(self):
        oid = self.id
        self.id = None
        if oid:
            self.widget.after_cancel(oid)

    def showtip(self, *_):
        # x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left', background="#ffffff", relief='solid', borderwidth=1,
                      wraplength=self.wrap_length)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


if __name__ == "__main__":
    if internet_connection == "127.0.0.1":
        offline_function()
    else:
        startup_function()

root.mainloop()
