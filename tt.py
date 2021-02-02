import turtle
import numpy as np
import time
import threading
from tkinter import *
from tkinter import ttk


# 点
class Point:
    """点类，包含坐标、序号和相邻点的信息"""
    canvas = None  # 画板对象

    def __init__(self, no, x, y):
        self.x = x
        self.y = y
        self.degree = 0
        self.neighbor = []
        self.no = no

    @staticmethod
    def insert(a, b):
        """连接两个点"""
        dis = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
        a.neighbor.append([b, dis])
        b.neighbor.append([a, dis])

    def get_no(self):
        """返回点的序号"""
        return self.no


class City(Point):
    """城市类点，有城市名"""
    def __init__(self, name, no, x, y):
        super().__init__(no, x, y)
        self.name = name

    def __str__(self):
        return str(self.no) + '.' + self.name


class Traffic(Point, threading.Thread):
    """交通岗类点，同时继承线程类，
    用于交通灯颜色切换"""
    Light = ["red", "green", "yellow"]
    flag = True  # 线程执行体的检测标志

    def __init__(self, no, x, y):
        Point.__init__(self, no, x, y)
        threading.Thread.__init__(self)
        self.light = np.random.randint(0, 3)  # 初识时随机一个颜色

    def __str__(self):
        return str(self.no)

    @staticmethod
    def open_thread():
        """允许线程执行"""
        Traffic.flag = True

    @staticmethod
    def close_thread():
        """停止线程"""
        Traffic.flag = False

    def run(self):
        """线程体"""
        while Traffic.flag:
            time.sleep(2.5)
            self.light = (self.light + 1) % 3
            Point.canvas.create_oval(self.x - 3, self.y - 3, self.x + 3, self.y + 3, fill=Traffic.Light[self.light])


class Application(Frame):
    """GUI应用主类"""
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.canvas = Canvas(self)  # 画板
        self.pen = turtle.RawTurtle(turtle.TurtleScreen(self.canvas))  # 海龟画图的画笔，绑定画板
        self.pen.up()
        self.pen.goto(23, -23)
        self.canvas.config(scrollregion=(0, 0, 1396, 600), width=1396, height=600)
        self.canvas.grid(row=0, column=0, columnspan=14)
        Point.canvas = self.canvas

        print(self.canvas.cget("width"))
        self.buttongroup = self.create_buttongroup()  # 生成所有按钮
        self.mouse_click_pos = (23, 23)
        self.canvas.create_oval(20, 20, 26, 26, fill="black", tags="mouseclick")  # 画板点击事件
        self.canvas.bind("<Button-1>", self.mouse_click)
        self.canvas.create_text(self.mouse_click_pos[0] + 1, self.mouse_click_pos[1] - 9,
                                text="Now", font=("Pursia", 10), tags="now")
        self.point_name = StringVar()
        self.point_name_input = Entry(self, bd=2, textvariable=self.point_name)
        self.point_name_input.grid(row=1, column=1, sticky=E, padx=8)
        self.point_set = set()
        self.points = []  # 点集
        self.point_map = {}  # 序号到点的映射
        self.point_name_set = []

        self.p1 = StringVar()
        self.p2 = StringVar()
        self.line_p1 = ttk.Combobox(self, textvariable=self.p1)
        self.line_p2 = ttk.Combobox(self, textvariable=self.p2)
        self.line_p1.grid(row=1, column=3, sticky=W)
        self.line_p2.grid(row=2, column=3, sticky=W)

        self.start = StringVar()
        self.start_pos = ttk.Combobox(self, textvariable=self.start)
        self.start_pos.grid(row=2, column=0, sticky=E, padx=8)

        self.end = StringVar()
        self.end_pos = ttk.Combobox(self, textvariable=self.end)
        self.end_pos.grid(row=3, column=0, sticky=E, padx=8)

        self.traffic_light = []

    def create_buttongroup(self):
        """生成所有按钮"""
        button_group = []
        self.btn1 = Button(self, text="生成地图", command=None)
        button_group.append(self.btn1)
        self.btn1.grid(row=1, column=0, sticky=W)

        self.btn2 = Button(self, text="添加节点", command=self.create_point)
        button_group.append(self.btn2)
        self.btn2.grid(row=1, column=1, sticky=W)

        self.btn3 = Button(self, text="设置小车", command=self.set_car)
        button_group.append(self.btn3)
        self.btn3.grid(row=2, column=0, sticky=W)

        self.btn4 = Button(self, text="开始运动", command=self.begin)
        button_group.append(self.btn4)
        self.btn4.grid(row=3, column=0, sticky=W)

        self.button_drawline = Button(self, text="连接", command=self.connect)
        button_group.append(self.button_drawline)
        self.button_drawline.grid(row=3, column=3, sticky=W)

        return button_group

    def mouse_click(self, event):
        """鼠标点击，画板上标记当前位置的点移动"""
        x, y = event.x, event.y
        self.mouse_click_pos = (x, y)
        self.canvas.coords("mouseclick", x - 7, y - 7, x - 1, y - 1)
        self.canvas.coords("now", x - 3, y - 14)

    def create_point(self):
        """在当前位置创建一个点"""
        x, y = self.mouse_click_pos[0], self.mouse_click_pos[1]
        if (x, y) in self.point_set:
            return
        p = City(self.point_name.get(), len(self.point_set), x, y) if self.point_name.get() != "" else \
            Traffic(len(self.point_set), x, y)
        color = "black"
        if isinstance(p, Traffic):
            self.traffic_light.append(p)
            color = Traffic.Light[p.light]
        self.point_map[p.get_no()] = p
        self.point_name.set("")
        self.point_set.add((x, y))
        self.points.append(p)
        self.point_name_set.append(str(p))
        self.line_p1["values"] = tuple(self.point_name_set)
        self.line_p2["values"] = self.line_p1["values"]
        self.start_pos["values"] = self.line_p1["values"]
        self.end_pos["values"] = self.line_p1["values"]
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color)
        self.canvas.create_text(x, y - 9, text=str(p), font=("Pursia", 10))

    def connect(self):
        """连接两个点"""
        if self.line_p1.get() == "" or self.line_p2.get() == "":
            return
        p1 = self.point_map[int(self.line_p1.get()[0])]
        if p1.degree == 4:
            return
        p2 = self.point_map[int(self.line_p2.get()[0])]
        if p2.degree == 4:
            return
        self.canvas.create_line(p1.x, p1.y, p2.x, p2.y)
        self.line_p1.set("")
        self.line_p2.set("")
        p1.degree += 1
        p2.degree += 1
        Point.insert(p1, p2)

    def set_car(self):
        """设置小车"""
        sp = self.point_map[int(self.start.get()[0])]
        self.pen.up()
        self.pen.goto(sp.x, -sp.y)

    def begin(self):
        """小车开始运动，遇红灯暂停"""
        if self.start.get() == "" or self.end.get() == "" or Traffic.flag is False:
            return
        self.graph = np.ones((len(self.point_set), len(self.point_set))) * np.inf
        for p in self.points:
            self.graph[p.no][p.no] = 0
            for neighbor in p.neighbor:
                self.graph[p.no][neighbor[0].no] = neighbor[1]
        for t in self.traffic_light:
            t.start()
        start = int(self.start.get()[0])
        end = int(self.end.get()[0])
        self.pen.pencolor("red")
        self.pen.speed(1)
        path = [-1] * len(self.points)
        path[start] = start
        all_path = []
        s = set()
        n = {i for i in range(len(self.points))}
        dist = self.graph[start]
        while len(n) > 0:
            m = list(n)[0]
            for v in n:
                if dist[v] < dist[m]:
                    m = v
            n.remove(m)
            s.add(m)
            for v in n:
                if dist[v] >= dist[m] + self.graph[m][v]:
                    dist[v] = dist[m] + self.graph[m][v]
                    path[v] = m
            print(path)
        while path[end] != end:
            all_path.append(end)
            end = path[end]
        self.pen.down()
        for station in all_path[::-1]:
            pos = self.point_map[station]
            self.pen.goto(pos.x, -pos.y)
            if isinstance(pos, Traffic) and pos.light == 0:
                time.sleep(2.5)
        Traffic.close_thread()
        self.pen.speed(6)


root = Tk()
root.geometry("1400x700+18+50")
root.title("交通网络程序")
app = Application(root)
root.mainloop()
