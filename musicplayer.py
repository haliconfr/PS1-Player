import os
import json
import spotipy
import math
import time
from pypresence import Presence
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
from threading import Thread
from time import strftime
from time import gmtime
from spotipy.oauth2 import SpotifyOAuth
from tkinter import *
from PIL import Image
from PIL import ImageTk
from tkextrafont import Font

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

tk = Tk()
tk.title("PS1 - Spotify Player")
tk.geometry("821x626")
tk.wm_iconbitmap(bitmap = resource_path(r"images\icon.ico"))
mainFont = "Gamestation Condensed"
paused = False
tiles = []
SpotifyObject = 0
bg = ImageTk.PhotoImage(Image.open(resource_path(r"images\\background.png")))
play = ImageTk.PhotoImage(Image.open(resource_path(r"images\\play.png")))
pause = ImageTk.PhotoImage(Image.open(resource_path(r"images\\pause.png")))
skiplayout = ImageTk.PhotoImage(Image.open(resource_path(r"images\\skiplayout.png")))
forward = ImageTk.PhotoImage(Image.open(resource_path(r"images\\forward.png")))
back = ImageTk.PhotoImage(Image.open(resource_path(r"images\\back.png")))
timer2 = ImageTk.PhotoImage(Image.open(resource_path(r"images\\timer2.png")))
Label(tk, image=bg).place(x=0, y=0, relwidth=1, relheight=1)
Label(tk, image=skiplayout, borderwidth=0).place(x=193, y=498)
Label(tk, image=timer2, borderwidth=0).place(x=68, y=53)
secText = Label(tk, bg="#351189", text="s", fg="white", font=(mainFont, 25))
minText = Label(tk, bg="#351189", text="m", fg="white", font=(mainFont, 25))
secText.place(x=221, y=64)
minText.place(x=105, y=64)
tk.resizable(False, False)

client_id = "CLIENTID"
RPC = Presence(client_id)
RPC.connect()

def quitHandler():
    global RPC
    global tk
    RPC.close()
    tk.destroy()
    
def getLocalImage(name, data):
    image = os.path.abspath(os.getcwd() + "\\custom" + "\\" + name + ".txt")
    if(os.path.isfile(image)):
        text = open(image)
        stringText = text.read()
        return stringText
    else:
        RPC.update(details="Listening to Spotify", state=str(data["item"]["artists"][0]["name"]) + " - " + str(data["item"]["name"]), start=data["progress_ms"], end=data["item"]["duration_ms"])

def initTrackNum(data):
    global RPC
    timesDone = 0
    xValue = 321
    yValue = 53
    global tiles
    artist = data["item"]["artists"][0]["name"]
    name = data["item"]["name"]
    tk.title("PS1: " + str(artist) + " - " + str(name))
    if data["item"]["is_local"] == False:
        RPC.update(details="Listening to Spotify", large_image=data["item"]["album"]["images"][0]["url"], state=artist + " - " + name, start=data["progress_ms"], end=data["item"]["duration_ms"])
        tracks = data["item"]["album"]["total_tracks"]
        size = len(tiles)
        for i in range(size):
            tiles[i].destroy()
        for i in range(tracks):
            xValue = xValue + 62
            numTile = ImageTk.PhotoImage(Image.open(resource_path("images\\numbertile.png")))
            numberTile = Label(tk, text=str(i + 1), font=(mainFont, 20), bg = "black", fg = "white", image=numTile, compound = "center", borderwidth=0)
            numberTile.place(x=xValue, y=yValue)
            tiles.append(numberTile)
            timesDone += 1
            if timesDone == 6:
                yValue = yValue + 63
                xValue = 321
                timesDone = 0
    else:
        numTile = ImageTk.PhotoImage(Image.open(resource_path("images\\numbertile.png")))
        numberTile = Label(tk, text=str(1), font=(mainFont, 20), bg = "black", fg = "white", image=numTile, compound = "center", borderwidth=0).place(x=xValue + 62, y=yValue)
        image = getLocalImage(data["item"]["album"]["name"], data)
        RPC.update(details="Listening to Spotify", large_image=image, state=str(data["item"]["artists"][0]["name"]) + " - " + str(data["item"]["name"]), start=data["progress_ms"], end=data["item"]["duration_ms"])

def SpotifySetup():
    global spotifyObject
    username = ""
    clientID = "CLIENTID"
    clientSecret = "CLIENTSECRET"
    scope = "user-read-currently-playing user-modify-playback-state"
    redirectURI = "https://example.com/callback"
    sp = spotipy.Spotify()
    token = spotipy.util.prompt_for_user_token(username,
                           scope,
                           client_id = "CLIENTID",
                           client_secret = "CLIENTSECRET",
                           redirect_uri="https://example.com/callback")
    spotifyObject = spotipy.Spotify(auth=token)
    user = spotifyObject.current_user()
    initTrackNum(spotifyObject.current_user_playing_track())
    
SpotifySetup()

def PlayMusic():
    global paused
    if(paused):
        paused = False
        tk.after(10, TrackTime)
        spotifyObject.start_playback()
    
def PauseMusic():
    global paused
    if(paused == False):
        paused = True
        spotifyObject.pause_playback()

def SkipTrack():
    spotifyObject.next_track()

def BackTrack():
    spotifyObject.previous_track()
        
def TrackTime():
    if(paused == False):
        global spotifyObject
        global secText
        global minText
        global minutes
        TrackInfo = spotifyObject.current_user_playing_track()
        seconds = math.trunc((TrackInfo["progress_ms"]/1000)%60)
        minutes = math.trunc((TrackInfo["progress_ms"]/(1000*60))%60)
        secText.config(text = math.trunc(seconds))
        minText.config(text = math.trunc(minutes))
    else:
        RPC.update(state="Paused on Spotify")
    time.sleep(0.3)
    Thread(target = TrackTime).start()

def updateProgram():
    data = spotifyObject.current_user_playing_track()
    if(data["progress_ms"]/1000 < 2):
        updateable = True
    else:
        updateable = False
    if(updateable):
        initTrackNum(data)
    time.sleep(0.1)
    Thread(target = updateProgram).start()

tk.protocol('WM_DELETE_WINDOW', quitHandler)
Thread(target = TrackTime).start()
Thread(target = updateProgram).start()
Button(tk, image=play, command=PlayMusic, highlightthickness=0, borderwidth=0).place(x=193, y=514)
Button(tk, image=pause, command=PauseMusic, highlightthickness=0, borderwidth=0).place(x=256, y=512)
Button(tk, image=forward, command=SkipTrack, highlightthickness=0, borderwidth=0).place(x=442, y=511)
Button(tk, image=back, command=BackTrack, highlightthickness=0, borderwidth=0).place(x=378, y=513)

tk.mainloop()