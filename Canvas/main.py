import tkinter as tk
from threading import Thread
import time
import objects
import numpy as np
import audio_handler as ah
from pygame import mixer 

music = 0
bg_color = '#0012bc'

def is_game_running():
    if music:
        return mixer.music.get_busy()
    return 1


def launch_music():
    global music
    if music:
        mixer.init(48000, -16, 2, 4096)
        mixer.music.load('src/sped.wav')
        mixer.music.play()

root = tk.Tk()
root.geometry("1200x800")
root.configure(background=bg_color)
root.attributes('-fullscreen',  True)

width = 1200
height = 800

score_counter = tk.Label(master=root,text="Score:\n 00",fg="red", anchor='n', font="Times 34 italic bold", bg=bg_color)
score_counter.pack(padx=5, pady=10, fill=tk.Y, side=tk.LEFT)

# logo = ImageTk.PhotoImage(Image.open("src/robotics_club.png"))
# background_label = tk.Label(root, image = logo)
# background_label.place(x=0, y=0, relwidth=1.0, relheight=1.0, anchor="center")
# background_label.pack(padx=5, pady=10, fill=tk.Y, side=tk.BOTTOM)


canvas = tk.Canvas(root, width=width, height=height, background='black')
canvas.pack(padx=5, pady=10, side=tk.LEFT)
terrain = objects.Terrain(canvas, width, height, enable_music=music)
cursor = objects.CrossHair(color='red', thickness=2, radius=30)
# cursor = objects.LightSaber(thickness=30, color='pride')
terrain.add_cursor(cursor)


sq_size = 100
circle_radius = 80

def run():
    i = 0
    try:
        launch_music()
        while is_game_running():
            t1 = time.time()
            score = terrain.update()
            if np.random.randint(0, 100) >= 99:
                if np.random.randint(0, 100) >= 95:
                    terrain.spawn_Yves(sq_size, sq_size)
                else:
                    x = np.random.choice([0, 1])
                    if x:
                        terrain.spawn_square(sq_size, sq_size)
                    else:
                        terrain.spawn_circle(circle_radius)
            t2 = time.time()
            time.sleep(max(0,0.002 - (t2-t1)))
            t3 = time.time()
            score_counter['text'] = "Score:\n{}".format(score)
        while terrain.contains_elements():
            t1 = time.time()
            score = terrain.update()
            t2 = time.time()
            time.sleep(max(0,0.002 - (t2-t1)))
            t3 = time.time()
            # print(t3-t1)
            score_counter['text'] = "Score:\n{}".format(score)
        
        code = terrain.show_end_screen()
        if code == objects.PLAY_AGAIN:
            terrain.reset()
            run()
    except KeyboardInterrupt:
        pass
    root.quit()


t = Thread(target=run)
t.start()
root.mainloop()



