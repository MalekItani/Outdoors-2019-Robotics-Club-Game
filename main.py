import tkinter as tk
from threading import Thread
import time
import Canvas.objects as objects
import numpy as np
import Canvas.audio_handler as ah
from pygame import mixer 
import config
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-g', '--gunmode', default=1)
parser.add_argument('-ct', '--cursortype', default='crosshair')
parser.add_argument('-cc', '--cursorcolor', default='#00FF00')
parser.add_argument('-s', '--sound', default=1)
args = vars(parser.parse_args())

gun_mode = args['gunmode']
cursor_type = args['cursortype']
cursor_color = args['cursorcolor']

music = args['sound']
bg_color = '#0012bc'


def is_game_running():
    if music:
        return mixer.music.get_busy()
    return 1


def launch_music():
    global music
    if music:
        mixer.init(48000, -16, 2, 4096)
        mixer.music.load('Canvas/src/sped.wav')
        mixer.music.play()


root = tk.Tk()


root.configure(background=bg_color)
root.attributes('-fullscreen',  True)

width = 1200
height = 800

score_counter = tk.Label(master=root,text="Score:\n 00",fg="#ffff00", anchor='n', font="Times 34 italic bold", bg=bg_color)
score_counter.pack(padx=5, pady=10, fill=tk.Y, side=tk.LEFT)


canvas = tk.Canvas(root, width=width, height=height, background='black')
canvas.pack(padx=5, pady=10, side=tk.LEFT)
terrain = objects.Terrain(canvas, width, height, enable_music=music)
if cursor_type == 'crosshair':
    cursor = objects.CrossHair(color=cursor_color, thickness=5, radius=30)
elif cursor_type == 'lightsaber':
    cursor = objects.LightSaber(thickness=30, color=cursor_color, buffer_size=128)
else:
    raise NotImplementedError('{} is not a valid cursor type.'.format(cursor_type))

terrain.add_cursor(cursor)


sq_size = 100
circle_radius = 80


if gun_mode:
    import server as server
    server.begin_mouse_control(cursor)
    # server.mouse_control()

def run():
    i = 0
    terrain.show_welcome_screen()
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
t.daemon = True
t.start()

root.mainloop()



