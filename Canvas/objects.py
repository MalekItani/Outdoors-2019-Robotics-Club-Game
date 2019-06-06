import numpy as np
import collections
import queue
from Canvas.audio_handler import AudioHandler
from PIL import ImageTk, Image

QUIT = 0
PLAY_AGAIN = 1

colors = ['#ff0000', '#00ff00', '#0000ff', '#ff00ff', '#ff6e00','#00ffff', '#ffffff']
Buttons = []
button_choice = -1

def select_choice(event, cursor):
    global Buttons
    global button_choice
    for button in Buttons:
        if button.selected(cursor.center[0], cursor.center[1]):
            button_choice = button.id
            return
    button_choice = -1

def random_color():
    tmp = np.random.randint(0, 100) >= 98
    if tmp:
        return 'pride'
    return np.random.choice(colors)

def next_color(c, shift=1):
    if c[0] >= 255:
        if c[2] > 0:
            c[2] = max(0, c[2] - shift)
        elif c[1] < 255:
            c[1] = min(255, c[1] + shift)
        else:
            c[0] = max(0, c[0] - shift)
    elif c[1] == 255:
        if c[0] > 0:
            c[0] = max(0, c[0] - shift)
        elif c[2] >= 255:
            c[1] = max(0, c[1] - shift)
        elif c[2] < 255:
            c[2] = min(255, c[2] + shift)
    elif c[2] == 255:
        if c[1] > 0:
            c[1] = max(0, c[1] - shift)
        elif c[0] >= 255:
            c[2] = max(0, c[2] - shift)
        elif c[0] < 255:
            c[0] = min(255, c[0] + shift)
    return c

def parse(h):
    s = ""
    if h < 16:
        s+= "0"
    s += hex(h)[2:]
    return s

def parse_color(c):
    l = ''.join([parse(i) for i in c])
    return '#' + l


def angle(p1, p2):
    vec = p2-p1
    if vec[0] == 0:
        theta = ((-1) ** (vec[1] < 0)) * np.pi/2
    else:
        theta = np.arctan(vec[1]/vec[0])
    if theta < 0 and vec[1] > 0:
        theta += np.pi
    elif theta > 0 and vec[1] < 0:
        theta += np.pi
    return theta

class Button(object):
    def __init__(self, top_left, bottom_right, id):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.id = id
    
    def selected(self, x, y):
        return (x > self.top_left[0] and x < self.bottom_right[0]) and (y > self.top_left[1] and y < self.bottom_right[1])

class GameObj_Base(object):
    def __init__(self, points, center, metric, color):
        self.points = points
        self.center = center
        self.speed = np.zeros(2)
        self.forces = np.zeros(2)
        self.id = -1
        self.metric = metric
        self.age = 0
        self.time_since_last_hit = 10000
        self.hp = 1
        self.color = color
        self.worth = 1
        if self.color is None:
            self.color = 'white'
        if self.color == "pride":
            self.color_array = [255, 0, 0]
            self.worth = 2

    def next(self):
        self.speed = self.speed + self.forces
        self.points = self.points + self.speed
        self.center = self.center + self.speed
        self.age += 1
        self.time_since_last_hit +=1 

    def immune(self):
        return self.time_since_last_hit < 60

    def reset_immunity(self):
        self.time_since_last_hit = 0

    def harm(self, dmg = 1):
        self.hp -= dmg

    def dead(self):
        return self.hp < 1

    def add_force(self, force):
        self.forces = self.forces + force

    def push(self, push):
        self.speed = self.speed + push

    def remove(self, canvas):
        canvas.delete(self.id)

    def crosses(self, point, error=0):
        return 0

    def get_color(self):
        if self.color == 'pride':
            self.color_array = next_color(self.color_array, 8)
            return parse_color(self.color_array)
        return self.color

    def play_sound(self, ah):
        ah.play_random_effect()


class Terrain():
    def __init__(self, canvas, width, height, field = None, enable_music=1):
        self.canvas = canvas
        self.ah = AudioHandler(path='src/effects')
        self.ah.enabled = enable_music
        self.ah.build()
        self.width = width
        self.height = height
        self.objects = []
        self.field = field
        self.score = 0
        if self.field is None:
            self.field = np.array([0, 0.003])
    
    def add_object(self, obj):
        obj.add_force(self.field)
        self.objects.append(obj)
        return obj
    
    def add_cursor(self,cursor):
        for event in cursor.events:
            self.canvas.bind(event, cursor.events[event])
            cursor.enable_audio(self.ah.enabled)
        self.cursor = cursor

    def update(self):
        self.cursor.enable()
        self.cursor.update()
        tmp = []
        shards = []
        for i in range(len(self.objects)):
            self.objects[i].next()
            if self.out_of_bounds(self.objects[i].center):
                self.objects[i].remove(self.canvas)
            elif type(self.objects[i]) == Shard and self.objects[i].expired():
                self.objects[i].remove(self.canvas)
            elif self.cursor.hits(self.objects[i]):
                self.objects[i].play_sound(self.ah)
                self.objects[i].harm()
                if self.objects[i].dead():
                    self.objects[i].remove(self.canvas)
                    self.score += self.objects[i].worth
                    obj = self.objects[i]
                    s1 = Shard(center = obj.center, size = obj.metric//3, color = obj.color)
                    s2 = Shard(center = obj.center, size = obj.metric//3, color = obj.color)
                    s3 = Shard(center = obj.center, size = obj.metric//3, color = obj.color)
                    # vec = self.cursor.front() - obj.center
                    # theta = np.arctan(vec[1]/vec[0])
                    theta = angle(self.cursor.front(), obj.center)
                    s1.push(np.array([np.cos(theta), np.sin(theta)]))
                    s2.push(np.array([np.sin(theta), np.cos(theta) + np.pi/6]))
                    s3.push(np.array([np.cos(theta), np.sin(theta) - np.pi/6 ]))
                    shards.append(s1)
                    shards.append(s2)
                    shards.append(s3)
                else:
                    self.objects[i].reset_immunity()
                    tmp.append(self.objects[i])    
            else:
                tmp.append(self.objects[i])
        self.objects = tmp
        for shard in shards:
            self.add_object(shard)
        # print(len(self.objects))
        self.draw()
        return self.score

    def out_of_bounds(self, center):
        return (center[0] < 0 or center[0] > self.width) or (center[1] < 0 or center[1] > self.height)

    def draw(self):
        # self.canvas.delete('object')
        for i in range(len(self.objects)):
            self.objects[i].draw(self.canvas)
        self.cursor.draw(self)

    def spawn_square(self, width = 10, height = 10):
        sq = Square(center=np.array([self.width//2+np.random.randint(-self.width, self.width)//3, self.height]), width=width, height = height, color=random_color())
        sq.push(np.array([np.random.randint(-1, 2), -np.random.randint(2, 3)]))
        self.add_object(sq)
        return sq

    def spawn_circle(self, radius=10):
        cr = Circle(center=np.array([self.width//2+np.random.randint(-self.width, self.width)//3, self.height]), radius=radius, color=random_color())
        cr.push(np.array([np.random.randint(-1, 2), -np.random.randint(2, 3)]))
        self.add_object(cr)
        return cr

    def spawn_Yves(self, width=10, height=10):
        yv = Yves(path='Canvas/src/img/yves.jpeg',center=np.array([self.width//2+np.random.randint(-self.width, self.width)//3, self.height]), width=width, height = height)
        yv.push(np.array([np.random.randint(-1, 2), -np.random.randint(2, 3)]))
        self.add_object(yv)
        return yv
            
    def contains_elements(self):
        return len(self.objects) > 0

    def show_welcome_screen(self):
        self.canvas.create_text(self.width//2,self.height//6,fill="#ffffff",font="Times 64 italic bold", text="AUB ROBOTICS CLUB")
        #self.canvas.create_rectangle(self.width//2 - 150, self.height//2 - 150, self.width//2 + 150, self.height//2 - 50, fill='grey')
        self.canvas.create_rectangle(self.width//2 - 150, self.height//2 + 50, self.width//2 + 150, self.height//2 + 150, fill='grey')
        self.canvas.create_text(self.width//2,self.height//2+100,fill="#0000ff",font="Times 20 italic bold", text="Play")
        global Buttons
        global button_choice
        Buttons = []
        Buttons.append(Button((self.width//2 - 150, self.height//2 + 50), (self.width//2 + 150, self.height//2 + 150), PLAY_AGAIN))
        Buttons.append(Button((9*self.width//10 - 100, 9*self.height//10 - 100), ( 9*self.width//10 + 100, 9*self.height//10 + 50), QUIT))
        self.canvas.unbind("<Button 1>")
        self.canvas.bind("<Button 1>", lambda event, arg=self.cursor: select_choice(event, arg))
        button_choice = -1
        self.cursor.enable()
        while button_choice == -1:
            self.cursor.update()
            self.cursor.draw(self)
        self.reset()

    def show_end_screen(self):
        self.canvas.delete('all')
        self.canvas.create_text(self.width//2,self.height//6,fill="#ff0000",font="Times 64 italic bold", text="Game Over")
        self.canvas.create_rectangle(self.width//2 - 150, self.height//2 - 150, self.width//2 + 150, self.height//2 - 50, fill='grey')
        self.canvas.create_rectangle(self.width//2 - 150, self.height//2 + 50, self.width//2 + 150, self.height//2 + 150, fill='grey')
        self.canvas.create_rectangle(9*self.width//10 - 100, 9*self.height//10 - 100, 9*self.width//10 + 100, 9*self.height//10, fill='#ce6b6b')
        self.canvas.create_text(self.width//2,self.height//2-100,fill="#0000ff",font="Times 20 italic bold", text="Final Score: {}".format(self.score))
        self.canvas.create_text(self.width//2,self.height//2+100,fill="#0000ff",font="Times 20 italic bold", text="Play Again")
        self.canvas.create_text(9*self.width//10 ,9*self.height//10 - 50,fill="red",font="Times 20 italic bold", text="Quit")
        global Buttons
        global button_choice
        self.cursor.enable()
        Buttons = []
        Buttons.append(Button((self.width//2 - 150, self.height//2 + 50), (self.width//2 + 150, self.height//2 + 150), PLAY_AGAIN))
        Buttons.append(Button((9*self.width//10 - 100, 9*self.height//10 - 100), ( 9*self.width//10 + 100, 9*self.height//10 + 50), QUIT))
        self.canvas.unbind("<Button 1>")
        self.canvas.bind("<Button 1>", lambda event, arg=self.cursor: select_choice(event, arg))
        button_choice = -1
        while   button_choice == -1:
            self.cursor.update()
            self.cursor.draw(self)
        return button_choice
    
    def reset(self):
        self.score = 0
        self.canvas.delete('all')
        self.canvas.unbind("<Button 1>")
        self.add_cursor(self.cursor)

class Square(GameObj_Base):
    def __init__(self, center = None, color = None, height = 10, width = 10):
        self.points = np.array([[center[0]-width//2, center[1]-height//2],
                            [center[0]+width//2, center[1]+height//2]]) 
        GameObj_Base.__init__(self, self.points, center = center, metric=width, color=color)
    
    def draw(self, canvas):
        x = self.id
        pts = self.points
        if x == -1:
            self.id = canvas.create_rectangle(pts[0][0], pts[0][1], pts[1][0], pts[1][1], fill=self.get_color(), tags=('object', 'square'))
        if x != -1:
            canvas.move(x, self.speed[0], self.speed[1])
            canvas.itemconfig(x, fill=self.get_color())
        #     canvas.delete(x)

    def crosses(self, p1, error=0):
        pts = self.points
        return (not self.immune()) and p1[0] + error//2 > pts[0][0] and p1[0] - error//2 < pts[1][0] and p1[1] + error//2 > pts[0][1] and p1[1] - error//2< pts[1][1]

class Circle(GameObj_Base):
    def __init__(self, center = None, color = None, radius=10):
        self.points = np.array([[center[0]-radius, center[1]-radius],
                            [center[0]+radius, center[1]+radius]]) 
        GameObj_Base.__init__(self, self.points, center = center, metric=2*radius, color=color)
        self.radius = radius
        if color is None:
            self.color = '#ffffff'
    
    def draw(self, canvas):
        x = self.id
        pts = self.points
        if x == -1:
            self.id = canvas.create_oval(pts[0][0], pts[0][1], pts[1][0], pts[1][1], fill=self.get_color(), tags=('object', 'circle'))
        if x != -1:
            canvas.move(x, self.speed[0], self.speed[1])
            canvas.itemconfig(x, fill=self.get_color())
    
    def crosses(self, p1, error = 0):
        return (not self.immune()) and np.linalg.norm(self.center - p1) < self.radius + error//2

class Shard(GameObj_Base):
    def __init__(self, center = None, color = None, size=10, lifetime=400):
        self.points = np.array([[center[0], center[1]-size],
                            [center[0]-size/3, center[1]+size/3],
                            [center[0]+size/3, center[1]+size/3]])
        GameObj_Base.__init__(self, self.points, center = center, metric=size, color=color)
        self.lifetime = lifetime
        self.size = size
    
    def draw(self, canvas):
        x = self.id
        pts = np.ravel(self.points)
        if x == -1:
            self.id = canvas.create_polygon(tuple(pts), fill=self.get_color(), tags=('object', 'shard'))
        if x != -1:
            canvas.move(x, self.speed[0], self.speed[1])
            canvas.itemconfig(x, fill=self.get_color())

    def expired(self):
        return self.age > self.lifetime


class Yves(Square):
    def __init__(self, path, center=None, height=10, width=10):
        Square.__init__(self, center=center, height=height, width=width)
        self.img = ImageTk.PhotoImage(Image.open(path).resize((height, width), Image.ANTIALIAS))
        self.hp = 3
        self.worth = 5
        self.audio_file = '../effects/oof.wav'
    
    def draw(self, canvas):
        x = self.id
        pts = self.points
        if x == -1:
            self.id = canvas.create_image(self.center[0], self.center[1], image=self.img, tags=('object', 'square'))
        if x != -1:
            canvas.move(x, self.speed[0], self.speed[1])

    def play_sound(self, ah):
        ah.play_sound(self.audio_file)

class Cursor():
    def __init__(self, color=None):
        self.color = color
        if self.color is None:
            self.color = 'white'
        if self.color == "pride":
            self.color_array = [255, 0, 0]
            self.worth = 2
        self._enabled = 0
    
    def get_color(self):
        if self.color == "pride":
            c = parse_color(next_color(self.color_array, 5))
            return c
        else:
            return self.color

    def update(self):
        pass

    def enable(self):
        self._enabled = 1

    def disable(self):
        self._enabled = 0

    def enable_audio(self, value):
        pass


class LightSaber(Cursor):
    def __init__(self, color='white', buffer_size=64, thickness=2):
        Cursor.__init__(self, color)
        self.buffer_size = buffer_size
        self.points = collections.deque(maxlen=self.buffer_size)
        self.lines = queue.Queue()
        self.thickness = thickness
        if color == "pride":
            self.color_array = [255, 0, 0]
        self.events = {'<Motion>':self.on_motion}

    def on_motion(self, event):
        if self._enabled:
            self.points.append(np.array([event.x, event.y]))
            # self.disable()

    def draw(self, terrain):
        # for i in range(1, len(self.points)):
        #     if terrain.out_of_bounds(self.points[i-1]) or self.points[i-1] is None or terrain.out_of_bounds(self.points[i]) or self.points[i] is None:
        #         continue
        #     terrain.canvas.create_line(self.points[i-1][0], self.points[i-1][1], self.points[i][0], self.points[i][1], width=2, fill=self.color)
        if len(self.points) > 1:
            if not (terrain.out_of_bounds(self.points[-1]) or self.points[-1] is None or terrain.out_of_bounds(self.points[-2]) or self.points[-2] is None):
                line_id = terrain.canvas.create_line(self.points[-1][0], self.points[-1][1], self.points[-2][0], self.points[-2][1], width=self.thickness, fill=self.get_color())
                self.lines.put(line_id)
                if self.lines.qsize() > self.buffer_size:
                    line_id = self.lines.get()
                    terrain.canvas.delete(line_id)

    def front(self):
        if len(self.points) > 1:
            return self.points[-1]
        return np.array([0,0])

    def hits(self, obj):
        if len(self.points) > 1:
            return obj.crosses(self.front(), error=self.thickness)
        return 0

    def update(self):
        self.center = self.front()
        # print(self.center)


class CrossHair(Cursor):
    def __init__(self, color=None, radius=40, thickness=2):
        Cursor.__init__(self, color)
        self.ah = AudioHandler(audio_file='Canvas/src/cursor/phaser.wav')
        self.ah.build()
        self.radius = radius
        self.thickness=thickness
        self.center = np.array([0,0])
        self.state = 0
        self.pattern = 1 + 2*2**(-(np.linspace(-1, 1, 100))**2)
        self.components = []
        self.events = {'<1>':self.on_click, '<Motion>':self.on_motion}
        self.target = np.array([-1,-1])

    def on_motion(self, event):
        self.center = np.array([event.x, event.y])

    def on_click(self, event):
        if self.state == 0 or self.state > 50:
            self.state = 1
            self.target = np.array([self.center[0], self.center[1]])

    def enable_audio(self, value):
        self.ah.enabled = value

    def update(self):
        if self.state > 0:
            if self.state == 1:
                self.ah.play_random_effect()
            self.state +=1
        if self.state >= len(self.pattern):
            self.state = 0
        if self.state == 0 or self.state > 50:
            self.target = np.array([-1,-1])

    def draw(self, terrain):
        mult = self.pattern[self.state]
        dash_size = 2*self.radius*mult
        rad = self.radius*mult
        outer = terrain.canvas.create_oval(self.center[0]-rad//2, self.center[1]-rad//2, self.center[0]+rad//2, self.center[1]+rad//2, width = self.thickness, outline=self.get_color(), fill='')
        inner = terrain.canvas.create_oval(self.center[0]-rad//4, self.center[1]-rad//4, self.center[0]+rad//4, self.center[1]+rad//4, width = self.thickness, outline=self.get_color(), fill='')
        d1 = terrain.canvas.create_line(self.center[0]-dash_size//2, self.center[1], self.center[0] + dash_size//2, self.center[1], width = self.thickness, fill=self.get_color())
        d2 = terrain.canvas.create_line(self.center[0], self.center[1] - dash_size//2, self.center[0], self.center[1] + dash_size//2, width = self.thickness, fill=self.get_color())
        x = [outer, inner, d1, d2]
        for c in self.components:
            terrain.canvas.delete(c)
        self.components = x

    def hits(self, obj):
        # if self._enabled:
        return obj.crosses(self.target, error=self.radius//4) 
        # return 0

    def front(self):
        return self.center




