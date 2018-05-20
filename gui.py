#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *           # 导入 Tkinter 库


def change(key):
    key[1] += 10
    c2 = Label(root, text=key[0])
    c2.pack()
#    print(key[0])


def CreatWindows(keyPress):
    global root
    root = Tk()
    c1 = Checkbutton(root, text='1111')
    c1.pack()
    c1 = Checkbutton(root, text='2222')
    c1.pack()     #在这里设置断点，但是多线程调试进入时并不会在这里中断，为什么？？？？？？？？
    b1 = Button(root, text='change', command=lambda: change(keyPress)).pack()

    root.mainloop()


if __name__ == "__main__":
    CreatWindows([1,2])
