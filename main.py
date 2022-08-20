from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import colorchooser
import requests
import time
import sqlite3
import socket
import threading as th
import pathlib
from pathlib import *
from PIL import Image, ImageTk
from datetime import datetime

# API AND THE MAIN REGIONS USED TO SEARCH, CAN STILL ADD BR:br1, LAN:la1, LAS:la2, OCE:oc1, RU:ru1, TR:tr1--------------
API = ""  # INSERT THE RIOT API KEY HERE--------------------------------------------------------------------------------
regions = ['EUNE', 'EUW', 'NA', 'JP', 'KR']
d_r = {'EUNE': 'eun1', "EUW": 'euw1', 'NA': 'na1', 'JP': 'jp1', 'KR': 'kr'}
d_r2 = {'eun1': 'EUNE', 'euw1': "EUW", 'na1': 'NA', 'jp1': 'JP', 'kr': 'KR'}

# FIRST CHECK FOR INTERNET CONNECTION-----------------------------------------------------------------------------------
internet_connection = socket.gethostbyname(socket.gethostname())
# MAIN WINDOW ROOT AND CONFIG-------------------------------------------------------------------------------------------
root = Tk()
root.title("League Mastery")
root.iconbitmap("chest.ico")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
app_width = 1000
app_height = 750
root.geometry(f'{app_width}x{app_height}+{(screen_width//2)-(app_width//2)}+{(screen_height//2)-(app_height//2)}')
root.resizable(False, False)


# START FUNCTION TO CHECK IF THERE IS A DATABASE AND START UP WITH THE DEFAULT NAME OF THE SUMMONER---------------------
def startup_function():
    # CHECKS FOR THE LATEST VERSION OF THE GAME AND UPDATES THE DATABASE------------------------------------------------
    url_version = "https://ddragon.leagueoflegends.com/api/versions.json"
    version_request = requests.get(url_version)
    version = version_request.json()[0]

    database = Path('Default Name.db')
    try:
        # CHECK FOR THE DATABASE AND PROCEED WITH THE DEFAULT NAME AND UPDATE THE GAME VERSION--------------------------
        if database.is_file():
            conn = sqlite3.connect('Default Name.db')
            cur = conn.cursor()
            cur.execute("UPDATE start SET version = :version", {'version': version})
            cur.execute("""SELECT * FROM data""")
            info2 = cur.fetchall()
            Mastery().request_data(info2[0][0])
            conn.commit()
            conn.close()
        # WHEN THERE IS NO DATABASE, CREATES A DATABASE AND VALIDATE IF THE SUMMONER NAME ENTERED IS VALID--------------
        else:
            def confirm(*_):
                # API REQUEST FOR THE CHAMPIONS NAME, CREATES A DICT WHICH IS INSERTED IN THE DATABASE------------------
                url_champ_names = "http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/champion.json"
                name_requests = requests.get(url_champ_names)
                name = name_requests.json()

                # API REQUEST FOR THE SUMMONER BASE INFO----------------------------------------------------------------
                url_summoner_info = "https://"+sv_region.get()+".api.riotgames.com/lol/summoner/v4/summoners/by-name/" \
                                    + e_start_name.get() + "?api_key=" + API
                summoner_info_request = requests.get(url_summoner_info)
                data = summoner_info_request.json()

                # SUMMONER CHAMPIONS MASTERY, IS INSERTED IN THE DATABASE AS A STR WHICH IS CONVERTED BY EVAL LATER-----
                url = f"https://{sv_region.get()}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-" \
                      f"summoner/{data['id']}?api_key={API}"
                lol_request = requests.get(url)
                data1 = lol_request.json()

                # VALIDATE IF THE INSERTED NAME EXISTS, CREATE A DB FOR : FRIENDS, CHAMPION, SUMMONER OFFLINE DATA,-----
                # THEME AND THE BASIC STARTUP INFO ---------------------------------------------------------------------
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
                    cur1.execute("INSERT INTO start VALUES(:id, :lvl, :name, :region, :bg, :bg2, :bt, :fg, :version)", {
                        'id': data['id'],
                        'lvl': data['summonerLevel'],
                        'name': data['name'],
                        'region': sv_region.get(),
                        'bg': '#DCF7BA',
                        'bg2': '#79BF8B',
                        'bt': '#CCFFFF',
                        'fg': '#000000',
                        'version': version
                    })
                    for k in name['data']:
                        cur1.execute("INSERT INTO champion VALUES(:id, :name)", {
                            'id': name['data'][k]['key'],
                            'name': name['data'][k]['id']
                        })
                    cur1.execute("INSERT INTO data VALUES(:data)", {'data': f'{data1}'})
                    cur1.executemany("INSERT INTO theme VALUES (?, ?, ?, ?, ?);", [
                                    ('Default', '#DCF7BA', '#79BF8B', '#CCFFFF', '#000000'),
                                    ('Light', '#EEEEEE', '#BDBDBD', '#66B2FF', '#000000'),
                                    ('Dark', '#222831', '#393E46', '#00ADB5', '#EEEEEE'),
                                    ('Gray', '#AAB7B8', '#85929E', '#ABEBC6', '#000000'),
                    ])
                    conn1.commit()
                    conn1.close()
                    Mastery().request_data(str(data1))
                    top.destroy()
                else:
                    l_error = Label(top, text='Not valid!', fg='red')
                    l_error.place(y=80, x=145)

            # CREATES A TOPLEVEL WINDOW TO ENTER THE DEFAULT NAME AND THE CONFIRM BUTTON--------------------------------
            top_width = 350
            top_height = 100
            top = Toplevel(root)
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
            om_region = ttk.OptionMenu(top, sv_region, 'eun1', 'eun1', 'euw1', 'na1', 'jp1', 'kr')
            om_region.grid(row=0, column=2, sticky='e')
            bt_confirm = Button(top, text='Confirm', command=confirm)
            bt_confirm.place(x=120, y=50)
            bt_cancel = Button(top, text='Cancel', command=root.quit)
            bt_cancel.place(x=190, y=50)

    except FileNotFoundError:
        pass


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
        self.info_db = cur.fetchall()
        cur.execute('''SELECT * FROM champion''')
        self.champ_db = cur.fetchall()
        conn.commit()
        conn.close()

        # THEME MENU CREATE TO CHANGE AND ADD NEW ONE-------------------------------------------------------------------
        self.my_menu = Menu(root)
        root.config(menu=self.my_menu)
        self.theme_menu = Menu(self.my_menu, tearoff=False, background='orange')
        self.my_menu.add_cascade(label='Theme', menu=self.theme_menu)
        self.my_menu.add_cascade(label='Edit theme', command=self.edit_theme)
        for j in self.theme_db:
            self.theme_menu.add_command(label=j[0],
                                        command=lambda n=j[1], i=j[2], c=j[3], e=j[4]: self.change_theme(n, i, c, e))

        # START SUMMONER ID, LEVEL, NAME, REGION, GAME VERSION AND THE SAVED THEME COLOR--------------------------------
        self.summoner_id = self.info_db[0][0]
        self.lvl = self.info_db[0][1]
        self.start_name = self.info_db[0][2]
        self.region = self.info_db[0][3]
        self.bg = self.info_db[0][4]
        self.bg2 = self.info_db[0][5]
        self.bt = self.info_db[0][6]
        self.fg = self.info_db[0][7]
        self.version = self.info_db[0][8]
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
        self.l_name = Label(self.f_top, text=self.start_name, font=(self.f, 16, "italic"), bg=self.bg, fg=self.fg)
        self.l_name.grid(row=0, column=0)
        self.bt_status = Button(self.f_top, text='⭕', bd=0, fg='red', bg=self.bg, command=self.status)

        # SUMMONER LEVEL------------------------------------------------------------------------------------------------
        self.l_level = Label(self.f_top, text=f"Level: {self.lvl}", font=(self.f, 16, "italic"), bg=self.bg, fg=self.fg)
        self.l_level.grid(row=0, column=2)

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
        photo = PhotoImage(file=f"user.png")
        self.bt_friend = Button(self.f_top, image=photo, height=26, width=30, command=self.friends, bg=self.bt)
        self.bt_friend.grid(row=0, column=7, padx=10, sticky="w")
        self.bt_friend.image = photo
        self.bt_change = Button(self.f_top, text='♻', font=('Arial', 10), command=self.change, width=3, bg=self.bt)
        self.bt_change.grid(row=0, column=7, ipady=2, padx=10, sticky="e")
        self.check_status = True

        # BOT FRAME WHICH IS USED TO HOLD 4 FRAMES FOR THE CHAMPIONS INFO-----------------------------------------------
        self.f_bot = Frame(root, width=app_width, height=600, bg=self.bg)
        self.f_bot.grid(row=1, column=0, columnspan=4)
        self.f_bot.grid_propagate(False)

        # VARIABLES THAT ARE USED TO STORE INFO, WERE CREATED FOR A SMOOTH CHANGE OF THE THEME--------------------------
        self.name = []
        self.points = []
        self.chest = []
        self.token = []
        self.labels = None
        self.f_c = None
        self.f_f = None
        self.logo()
        self.internet_check()

        # CHECKS FOR THE INTERNET CONNECTION ON THE START, IF OK THEN PROCEEDS TO UPDATE THE PLAYER DATA AND THE ICONS--
        if internet_connection == "127.0.0.1":
            pass
        else:
            th.Thread(target=self.update_data).start()
            th.Thread(target=self.check_media).start()

    # FUNCTION TO KEEP CONSTANT CHECK ON THE INTERNET CONNECTION EVERY 2 SEC, IF IS OFF IT DISABLES THE MAIN BUTTONS----
    def internet_check(self):
        try:
            connection_test = socket.gethostbyname(socket.gethostname())
            if connection_test == "127.0.0.1":
                self.bt_search.config(state='disabled')
                self.bt_friend.config(state='disabled')
                self.bt_status.config(state='disabled')
                self.bt_change.config(state='disabled')
            else:
                self.bt_search.config(state='normal')
                self.bt_friend.config(state='normal')
                self.bt_status.config(state='normal')
                self.bt_change.config(state='normal')
        except RuntimeError:
            root.quit()
        root.after(2000, self.internet_check)

    # IS CALLED ON THE REQUEST DATA TO CHECK IF A PLAYER IS IN GAME, RED CIRCLE APPEARS NEAR THE NAME-------------------
    def game_status(self):
        url_status = "https://" + self.region + ".api.riotgames.com/lol/spectator/v4/active-games/by-summoner/" + \
                     self.summoner_id + "?api_key=" + API
        game_status = requests.get(url_status)

        if game_status.status_code != 200:
            self.bt_status.grid_remove()
        else:
            self.bt_status.grid(row=0, column=1, sticky='w', padx=10)

    # IS CALLED ON A THREAT NOT TO SLOW THE APP, IT SERVES TO UPDATE THE CUSTOMER DATA----------------------------------
    def update_data(self):
        conn = sqlite3.connect('Default Name.db')
        cur = conn.cursor()
        cur.execute("""SELECT * FROM start""")
        fetch = cur.fetchall()

        url_data = f"https://{self.region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" \
                   f"{fetch[0][0]}?api_key={API}"
        lol_request = requests.get(url_data)
        data = lol_request.json()
        cur.execute("UPDATE data SET data = :data", {'data': str(data)})

        url_info = f"https://{fetch[0][3]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/" \
                   f"{fetch[0][2]}?api_key={API}"
        summoner_info_request = requests.get(url_info)
        info = summoner_info_request.json()
        cur.execute("UPDATE start SET lvl = :lvl, name = :name", {'lvl': info['summonerLevel'], 'name': info['name']})
        conn.commit()
        conn.close()

    # CHECK FOR THE CHAMPIONS ICONS AND FOLDER, IF NOT EXIST IT DOWNLOADS THEM ALL THE ONCE USING A THREAD--------------
    def check_media(self):
        try:
            icon_folder = Path('Icons')
            if icon_folder.is_dir():
                url_champ_name = f"http://ddragon.leagueoflegends.com/cdn/{self.version}/data/en_US/champion.json"
                name_request = requests.get(url_champ_name)
                names = name_request.json()

                for i in names['data']:
                    def download_icon():
                        icons = Path(f"Icons/{names['data'][i]['id']}.png")
                        champ_name = names['data'][i]['id']
                        if not icons.is_file():
                            url_photo = f'http://ddragon.leagueoflegends.com/cdn/{self.version}/img/champion/' \
                                        f'{champ_name}.png'
                            # icon = requests.get(url_photo).content
                            icon = requests.get(url_photo).content
                            with open(f'Icons/{champ_name}.png', 'wb') as photo:
                                photo.write(icon)
                    th.Thread(target=download_icon).start()
            else:
                pathlib.Path("Icons").mkdir(exist_ok=True)
                self.check_media()

        except FileNotFoundError:
            pass

    # FUNCTION TO DELETE AND ADD NEW THEMES, CANT DELETE OR EDIT THE 4 INITIAL THEMES-----------------------------------
    def edit_theme(self):

        def add_new():

            def pick(label):
                choose = colorchooser.askcolor()
                label.config(text=choose[1], bg=choose[1])

            def change():
                try:
                    if e_name.get().isnumeric() or e_name.get() == '' or len(e_name.get()) > 15:
                        l_error.config(text='Enter a full name and not only numbers \n Min 1 - Max 15 characters')

                    else:
                        conn1 = sqlite3.connect('Default Name.db')
                        cur1 = conn1.cursor()
                        cur1.execute("INSERT INTO theme VALUES(:theme_name, :bg, :bg2, :bt, :fg)", {
                            'theme_name': e_name.get(),
                            'bg': colors[0].cget('text'),
                            'bg2': colors[1].cget('text'),
                            'bt': colors[2].cget('text'),
                            'fg': colors[3].cget('text')
                        })
                        cur1.execute("SELECT * FROM theme")
                        theme_db_update = cur1.fetchall()
                        j2 = theme_db_update[-1]
                        self.theme_menu.add_command(label=j2[0], command=lambda n=j2[1], o=j2[2], c=j2[3], e=j2[4]:
                                                    self.change_theme(n, o, c, e))

                        conn1.commit()
                        conn1.close()
                        top.destroy()
                        top_main.destroy()
                        self.edit_theme()
                except sqlite3.IntegrityError:
                    l_error.config(text='Name already exists')

            top_width2 = 250
            top_height2 = 200
            top = Toplevel(root, bg=self.bg)
            top.geometry(f'{top_width2}x{top_height2}+{((screen_width // 2) - (top_width2 // 2)) + 150}+'
                         f'{(screen_height // 2) - (top_height2 // 2)}')
            top.attributes('-topmost', 'true')
            top.title('Add Theme')
            for config2 in range(10):
                top.columnconfigure(config, weight=1)
                top.rowconfigure(config, weight=1)
            colors = ['Background 1', 'Background 2', 'Button', 'Text']
            row2 = 0
            for i2 in colors:
                colors[row2] = Label(top, bg='#AAB7B8', text='#AAB7B8', width=15, bd=0)
                colors[row2].grid(row=row2, column=0, padx=10, ipady=2)
                button = Button(top, text=i2, bg=self.bt, fg=self.fg, command=lambda n=colors[row2]: pick(n), width=13)
                button.grid(row=row2, column=1, pady=2)
                row2 += 1
            e_name = Entry(top, width=15, bg=self.bg2, fg=self.fg, justify=RIGHT)
            e_name.grid(row=4, column=0, ipady=3)
            bt_confirm = Button(top, text='click', command=change, width=13, bg=self.bt, fg=self.fg)
            bt_confirm.grid(row=4, column=1, pady=10)
            l_error = Label(top, fg=self.fg, bg=self.bg)
            l_error.grid(row=5, column=0, columnspan=10)

        def delete(name):
            ask = messagebox.askyesno("Delete", f"Delete theme {name}", parent=top_main)
            if ask:
                self.theme_menu.delete(str(name))
                conn3 = sqlite3.connect('Default Name.db')
                cur3 = conn3.cursor()
                cur3.execute(f'''DELETE FROM theme WHERE theme_name LIKE "{name}"''')
                conn3.commit()
                conn3.close()
                top_main.destroy()
                self.edit_theme()
            else:
                pass

        top_width = 300
        top_height = 400
        top_main = Toplevel(root, bg=self.bg)
        top_main.geometry(f'{top_width}x{top_height}+{((screen_width // 2) - (top_width // 2)) + 150}+'
                          f'{(screen_height // 2) - (top_height // 2)}')
        top_main.attributes('-topmost', 'true')
        top_main.title('Add Theme')
        top_main.resizable(False, False)
        for config in range(20):
            top_main.columnconfigure(config, weight=1)
            top_main.rowconfigure(config, weight=1)

        bt_add = Button(top_main, text='Add New', width=13, command=add_new)
        bt_add.grid(row=0, column=0, columnspan=20, pady=5)
        l_warning = Label(top_main, bg=self.bg, fg=self.fg, font=(self.f, 10),
                          text='Delete the theme by clicking on the name\n Max number of themes is 10!')
        l_warning.grid(row=1, column=0, columnspan=20, sticky='n')

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
            column += 4
        row = 3
        for i in info[4:]:
            theme_name = Button(top_main, text=i[0], bg=self.bg, fg=self.fg, bd=0, command=lambda n=i[0]: delete(n))
            theme_name.grid(row=row, column=0, columnspan=4, pady=1, sticky='e')
            color_bg = Label(top_main, bg=i[1], width=3, height=1)
            color_bg.grid(row=row, column=4, columnspan=4, pady=1)
            color_bg2 = Label(top_main, bg=i[2], width=3, height=1)
            color_bg2.grid(row=row, column=8, columnspan=4, pady=1)
            color_bt = Label(top_main, bg=i[3], width=3, height=1)
            color_bt.grid(row=row, column=12, columnspan=4, pady=1)
            color_fg = Label(top_main, bg=i[4], width=3, height=1)
            color_fg.grid(row=row, column=16, columnspan=4, pady=1)
            row += 1
        conn2.commit()
        conn2.close()

    # USED TO PLACE THE FOUR PHOTOS OF THE CHAMPION MASTERY-------------------------------------------------------------
    def logo(self):
        f_column = 0
        p_name = 7
        # TOP FRAMES AND PHOTOS-----------------------------------------------------------------------------------------
        for i in range(4):
            img = Image.open(f"lvl{p_name}.png")
            img = img.resize((248, 100))
            photo7 = ImageTk.PhotoImage(img)
            self.labels = Label(self.f_top, image=photo7, bg=self.bg2)
            self.labels.image = photo7
            self.labels.grid(row=1, column=f_column, columnspan=2)
            f_column += 2
            p_name -= 1

    # CHANGES THE THEME FOR THE MAIN WINDOW AND THE FRIENDS LIST, SAVES THE LAST THEME SET ON THE DATABASE--------------
    def change_theme(self, bg, bg2, bt, fg):
        conn1 = sqlite3.connect('Default Name.db')
        cur1 = conn1.cursor()
        cur1.execute("UPDATE start SET bg = :bg, bg2 = :bg2, bt = :bt, fg = :fg", {
            'bg': bg,
            'bg2': bg2,
            'bt': bt,
            'fg': fg
        })
        conn1.commit()
        conn1.close()
        self.bg = bg
        self.bg2 = bg2
        self.bt = bt
        self.fg = fg
        for (n, m) in zip(self.name, self.points):
            n.configure(bg=bg, fg=fg)
            m.configure(bg=bg, fg=fg)
        for (i, j) in zip(self.f_f, self.f_c):
            i.config(bg=bg)
            j.config(bg=bg)
        for o in self.chest:
            o.config(bg=bg)
        for t in self.token:
            t.config(bg=bg, fg=fg)
        self.f_top.config(bg=bg)
        self.l_name.config(bg=bg, fg=fg)
        self.bt_status.config(bg=bg)
        self.l_level.config(bg=bg, fg=fg)
        self.e_search.config(bg=bg2, fg=fg)
        self.bt_search.config(bg=bt, fg=fg)
        self.bt_friend.config(bg=bt, fg=fg)
        self.bt_change.config(bg=bt, fg=fg)
        self.logo()

        if not self.check_status:
            self.check_status = True
            self.friends()

    # FUNCTION TO CHECK THE PLAYERS IN-GAME AND THE CHAMPS PICKED, APPEARS THE CIRCLE NEAR THE NAME---------------------
    def status(self):
        # URL TO CHECK IF THERE IS AN ACTIVE GAME FOR A SEARCHED PLAYER-------------------------------------------------
        url_game = f"https://{self.region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/" \
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

            # TOPLEVEL WINDOWS FOR THE DISPLAY OF THE GAME TIME AND THE PLAYERS NAME AND CHAMP--------------------------
            top_w = 700
            top_h = 400
            f_live = Toplevel(root, width=top_w, height=top_h)
            f_live.geometry(f'{top_w}x{top_h}+{(screen_width // 2)-(top_w // 2)}+{(screen_height // 2)-(top_h // 2)}')
            f_live.attributes('-topmost', 'true')
            f_live.grid_propagate(False)
            f_live.resizable(False, False)
            f_top = Frame(f_live, width=top_w, height=100, bg=self.bg)
            f_top.grid(row=0, column=0)
            f_top.grid_propagate(False)
            game = info['gameMode'].capitalize()
            l_mode = Label(f_top, text=f"Game mode: {game}", font=(self.f, 20), bg=self.bg, fg=self.fg)
            l_mode.grid(row=0, column=0)

            def update():
                now = datetime.fromtimestamp(time.time()).replace(microsecond=0)
                start_time = datetime.fromtimestamp(info['gameStartTime'] / 1000).replace(microsecond=0)
                l_time.config(text=f'Time in game: {now - start_time}')
                l_time.after(1000, update)

            l_time = Label(f_top, text='', font=(self.f, 15), bg=self.bg, fg=self.fg)
            l_time.grid(row=1, column=0, sticky='w')
            l_time.after(1000, update)

            separator = ttk.Separator(f_live, orient='horizontal')
            separator.grid(row=1, column=0, sticky='ew', ipady=1)

            f_bot = Frame(f_live, width=top_w, height=300, bg=self.bg)
            f_bot.grid(row=2, column=0)
            f_bot.grid_propagate(False)
            for c in range(6):
                f_bot.columnconfigure(c, weight=1)

            self.dicts = {}
            for k in self.champ_db:
                self.dicts[k[0]] = k[1]

            row = 0
            z = 0
            for i in info['participants']:
                img = Image.open(f"""Icons/{self.dicts[i["championId"]]}.png""")
                img = img.resize((50, 50))
                photo = ImageTk.PhotoImage(img)
                icon = Button(f_bot, image=photo, bg=self.bg2)
                icon.image = photo

                img2 = Image.open(f"add.png")
                img2 = img2.resize((25, 25))
                photo2 = ImageTk.PhotoImage(img2)
                add = Button(f_bot, image=photo2, bg=self.bg, bd=0,
                             command=lambda n=i['summonerName'], m=d_r[self.sv_region.get()]: confirm(n, m))
                add.image = photo2

                name = Button(f_bot, text=i['summonerName'], font=(self.f, 12), bg=self.bg, fg=self.fg, bd=0,
                              command=lambda n=i['summonerName'], m=d_r[self.sv_region.get()]: self.search(n, m))

                if z < 5:
                    icon.grid(row=row, column=0, pady=1, padx=(5, 0), sticky='w')
                    add.grid(row=row, column=0, padx=(0, 5), ipadx=5, sticky='e')
                    name.grid(row=row, column=1, sticky='w')
                    row += 1
                    if row == 5:
                        row = 0
                    z += 1
                elif z > 4:
                    icon.grid(row=row, column=5, pady=1, padx=(0, 5), sticky='e')
                    add.grid(row=row, column=5, padx=(5, 0), ipadx=5, sticky='w')
                    name.grid(row=row, column=4, sticky='e')
                    row += 1
                    z += 2
        else:
            pass

    # FUNCTION FOR THE FRIENDS LIST, CAN ADD, DELETE AND SEARCH SUMMONERS-----------------------------------------------
    def friends(self):

        if self.check_status:
            self.check_status = False
            root.geometry('1200x730')

            def friends_list():
                f_friends = Frame(friend_list, width=top_width, height=650, bg=self.bg)
                f_friends.grid(row=2, column=0, sticky='nsew')
                f_friends.grid_propagate(False)

                conn1 = sqlite3.connect('Default Name.db')
                cur1 = conn1.cursor()
                cur1.execute('SELECT * FROM friends')
                info = cur1.fetchall()

                for i in info:
                    bt_friends = Button(f_friends, text=f'{i[0]} -{d_r2[i[1]]}', bg=self.bt, fg=self.fg,
                                        command=lambda n=i[0], m=i[1]: self.search(n, m))
                    bt_friends.pack(pady=5, padx=5, anchor="w")

            def add():
                friends_list()
                friend_list.config(bg=self.bg)

                def confirm(*_):
                    url_info = "https://"+d_r[sv_region.get()]+".api.riotgames.com/lol/summoner/v4/summoners/by-name/"\
                               + e_start_name.get() + "?api_key=" + API
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
                            top_add.destroy()
                            friends_list()

                        except sqlite3.IntegrityError:
                            l_error.configure(text='Already exist')
                    else:
                        l_error.configure(text='Not found')

                top_w = 350
                top_h = 100
                top_add = Toplevel(friend_list, bg=self.bg)
                top_add.geometry(f'{top_w}x{top_h}+{(screen_width // 2) - (top_w // 2)}+'
                                 f'{(screen_height // 2) - (top_h // 2)}')
                top_add.attributes('-topmost', 'true')
                top_add.title('Add friend')

                e_start_name = Entry(top_add, font=(self.f, 12), width=15, bg=self.bg2, fg=self.fg)
                e_start_name.place(y=7, x=100)
                e_start_name.bind('<Return>', confirm)
                e_start_name.focus()
                sv_region = StringVar()
                om_region = ttk.OptionMenu(top_add, sv_region, d_r2[self.region], *regions)
                om_region.place(y=10, x=35)
                bt_confirm = Button(top_add, text='Confirm', command=confirm, bg=self.bt)
                bt_confirm.place(x=150, y=50)
                l_error = Label(top_add, text='', fg='red', bg=self.bg)
                l_error.place(y=80, x=145)

            def delete():

                def confirm(userid):
                    rsp = messagebox.askyesno("Delete", "Delete from friends?", parent=f_delete)
                    if rsp == 1:
                        conn2 = sqlite3.connect('Default Name.db')
                        cur2 = conn2.cursor()
                        cur2.execute("DELETE FROM friends WHERE oid = " + str(userid))
                        conn2.commit()
                        conn2.close()
                        f_delete.destroy()
                        delete()
                    else:
                        pass

                def cancel():
                    f_delete.destroy()
                    friend_list.config(bg=self.bg)
                    friends_list()

                f_delete = Frame(friend_list, width=top_width, height=650, bg='#FF0000')
                f_delete.grid(row=2, column=0, sticky='nsew')
                f_delete.grid_propagate(False)
                friend_list.config(bg='#FF0000')
                bt_cancel = Button(f_delete, text='Cancel', bg=self.bg, fg=self.fg, command=cancel)
                bt_cancel.pack(pady=5)

                conn = sqlite3.connect('Default Name.db')
                cur = conn.cursor()
                cur.execute('SELECT *, oid FROM friends')
                data = cur.fetchall()
                for j in data:
                    bt_del = Button(f_delete, text=f'{j[0]}:{d_r2[j[1]]}', bg=self.bt, fg=self.fg,
                                    command=lambda n=j[2]: confirm(n))
                    bt_del.pack(pady=5, padx=5, anchor="w")

            top_width = 200
            top_height = 750
            friend_list = Frame(root, height=top_height, width=top_width, bg=self.bg)
            friend_list.grid(row=0, column=4, columnspan=1, rowspan=2, sticky='n')
            friend_list.grid_propagate(False)
            f_button = Frame(friend_list, width=top_width, height=52, bg=self.bg2)
            f_button.grid(row=0, column=0)
            f_button.grid_propagate(False)
            bt_add = Button(f_button, text='Add', font=(self.f, 10), width=8, command=add, bg=self.bt, fg=self.fg)
            bt_add.grid(row=0, column=0, pady=10, padx=12)
            bt_delete = Button(f_button, text='Delete', font=(self.f, 10), width=8, bg=self.bt, fg=self.fg,
                               command=delete)
            bt_delete.grid(row=0, column=1, pady=10, padx=12)
            friends_list()
        else:
            self.check_status = True
            root.geometry('1000x730')

    # FUNCTION TO CHANGE THE DEFAULT SUMMONER NAME----------------------------------------------------------------------
    def change(self):
        # CHECKS IF THE SUMMONER NAME ENTERED IS VALID------------------------------------------------------------------
        def confirm(*_):
            url_summoner_info = f"https://{d_r[sv_region.get()]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/" \
                                f"{e_start_name.get()}?api_key={API}"
            summoner_info_request = requests.get(url_summoner_info)
            info = summoner_info_request.json()

            url_mastery = f"https://{d_r[sv_region.get()]}.api.riotgames.com/lol/champion-mastery/v4/champion-" \
                          f"masteries/by-summoner/{info['id']}?api_key={API}"
            lol_request = requests.get(url_mastery)
            data = lol_request.json()

            # IF THE SEARCHED SUMMONER EXISTS IT INSERTS THE INFO ON THE DATABASE---------------------------------------
            if summoner_info_request.status_code == 200:
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
                top.destroy()
            else:
                l_error = Label(top, text='Not valid!', fg='red', bg=self.bg)
                l_error.place(y=80, x=150)

        # CREATES A TOPLEVEL WINDOW TO ENTER THE DEFAULT NAME AND THE CONFIRM BUTTON------------------------------------
        top_width = 350
        top_height = 100
        top = Toplevel(root, bg=self.bg)
        top.geometry(f'{top_width}x{top_height}+{(screen_width // 2) - (top_width // 2)}+'
                     f'{(screen_height // 2) - (top_height // 2)}')
        top.attributes('-topmost', 'true')
        top.title('Default summoner')
        e_start_name = Entry(top, font=(self.f, 12), width=15, bg=self.bg2, fg=self.fg)
        e_start_name.place(y=7, x=100)
        e_start_name.bind('<Return>', confirm)
        e_start_name.focus()
        sv_region = StringVar()
        om_region = ttk.OptionMenu(top, sv_region, d_r2[self.region], *regions)
        om_region.place(y=10, x=35)
        bt_confirm = Button(top, text='Confirm', command=confirm, bg=self.bt)
        bt_confirm.place(x=150, y=50)

    # SEARCH FUNCTION TO SHOW A GIVEN SUMMONER DATA---------------------------------------------------------------------
    def search(self, name, region, *_):
        self.f_bot.grid_remove()
        try:
            # IF THE SEARCH ENTRY IS EMPTY IT RETURNS THE DEFAULT PLAYER DATA-------------------------------------------
            if name == '':
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

            else:
                url_summoner_name = "https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" \
                                    + name + "?api_key=" + API
                summoner_name_request = requests.get(url_summoner_name)
                summoner_info = summoner_name_request.json()
                self.e_search.delete(0, END)
                self.summoner_id = summoner_info["id"]
                self.l_name.config(text=summoner_info['name'])
                self.l_level.config(text=f"Level: {summoner_info['summonerLevel']}")
                self.region = region
                self.sv_region.set(d_r2[region])
                url = "https://"+region+".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" \
                      + self.summoner_id + "?api_key=" + API
                lol_request = requests.get(url)
                data = lol_request.json()
                self.request_data(str(data))

        except KeyError:
            pass

    # MAIN FUNCTION FOR THE REQUEST AND DISPLAY OF THE SUMMONER DATA----------------------------------------------------
    def request_data(self, dat):
        self.f_bot.grid()
        # GIVEN PLAYER DATA AS A STRING CONVERTED TO THE ORIGINAL DICT--------------------------------------------------
        data = eval(dat)

        if internet_connection == "127.0.0.1":
            self.bt_search.config(state='disabled')
            self.bt_friend.config(state='disabled')
            self.bt_status.config(state='disabled')
            self.bt_change.config(state='disabled')
        else:
            th.Thread(target=self.game_status).start()

        # CREATE FRAMES WITH A FOR LOOP---------------------------------------------------------------------------------
        f_s = ['s_one', 's_two', 's_three', 's_four']
        f_o = ['f_one', 'f_two', 'f_three', 'f_four']
        self.f_c = ['c_one', 'c_two', 'c_three', 'c_four']
        self.f_f = ['fs_one', 'fs_two', 'fs_three', 'fs_four']
        for f in range(4):
            f_o[f] = Frame(self.f_bot, width=250, height=600, bg=self.bg)
            f_o[f].grid(row=1, column=f)
            f_o[f].grid_propagate(False)
            self.f_c[f] = Canvas(f_o[f], width=229, height=600, bg=self.bg)
            self.f_c[f].pack(side=LEFT, fill=BOTH, expand=1)
            f_s[f] = Scrollbar(f_o[f], orient=VERTICAL, command=self.f_c[f].yview, bg=self.bg)
            f_s[f].pack(side=RIGHT, fill=Y)
            self.f_c[f].configure(yscrollcommand=f_s[f].set)
            self.f_c[f].bind('<Configure>', lambda event: event.widget.configure(scrollregion=event.widget.bbox('all')))
            self.f_f[f] = Frame(self.f_c[f], bg=self.bg)
            self.f_c[f].create_window((0, 0), window=self.f_f[f], anchor='nw')

        # API TO CONVERT THE CHAMPION ID TO NAME------------------------------------------------------------------------
        # Issue with link, had to change it with the other url
        # url_champ_name = "https://www.masterypoints.com/api/v1.1/static/champions"

        # CHAMPION NUMBER COUNT, INCREASING WITH EACH CREATED LABEL-----------------------------------------------------
        row = 0
        frames = {7: self.f_f[0],
                  6: self.f_f[1],
                  5: self.f_f[2],
                  4: self.f_f[3], 3: self.f_f[3], 2: self.f_f[3], 1: self.f_f[3]}
        count = {7: 1, 6: 1, 5: 1, 4: 1, 3: 1, 2: 1, 1: 1}
        c = t = v = 0

        # FOR LOOP TO CREATE THE LABELS WITH THE CHAMPIONS INFO---------------------------------------------------------
        self.name.clear()
        self.points.clear()
        self.chest.clear()
        self.token.clear()
        for i in data:
            name = self.dicts[i["championId"]]
            frame = frames[i["championLevel"]]
            lvl = i["championLevel"]
            self.name.append(self.dicts[(i["championId"])])
            self.points.append(i["championPoints"])
            self.name[c] = Label(frame, text=f'{count[lvl]}: {name}', bg=self.bg, fg=self.fg, font=(self.f, 10))
            self.name[c].grid(row=row, column=0, sticky="W")
            count[lvl] += 1
            self.points[c] = Label(frame, text=f'--{i["championPoints"]}', bg=self.bg, fg=self.fg, font=(self.f, 10))
            self.points[c].grid(row=row, column=1, sticky="W")
            column = 3
            c += 1

            for t1 in range(i["tokensEarned"]):
                self.token.append(1)
                self.token[t] = Label(frame, text='🗸', font=(self.f, 10), bg=self.bg, fg=self.fg)
                self.token[t].grid(row=row, column=column)
                column += 1
                t += 1
            if i["chestGranted"]:
                self.chest.append(1)
                photo = PhotoImage(file=f"chest2.png")
                self.chest[v] = Label(frame, image=photo, bg=self.bg, fg=self.fg)
                self.chest[v].image = photo
                self.chest[v].grid(row=row, column=2)
                v += 1
            row += 1


if __name__ == "__main__":
    if internet_connection == "127.0.0.1":
        offline_function()
    else:
        startup_function()

root.mainloop()
