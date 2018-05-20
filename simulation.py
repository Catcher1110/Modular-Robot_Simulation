#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gui
import vtkPart as vtkP

import threading
from multiprocessing import Process, Manager
from time import ctime, sleep

'''setDaemon(True)将线程声明为守护线程，
必须在start() 方法调用之前设置，如果不
设置为守护线程程序会被无限挂起。子
线程启动后，父线程也继续执行下去，
当父线程执行完最后一条语句print "all over %s" %ctime()后，
没有等待子线程，直接就退出了，同时子线程也一同结束。'''

if __name__=='__main__':
   manager = Manager()
   keyPress = manager.list()
   keyPress.append('e')
   keyPress.append(0)
   processes=[]
# 不加逗号会出问题！！！！！！！！！为什么？？？？？？？？
# 只包含一个元素的元组、列表必须在最后加逗号，否则会被认为是一个元素
   win = Process(target=gui.CreatWindows, args=(keyPress,))# 不加逗号会出问题！！！！！！！！！为什么？？？？？？？？
   sce = Process(target=vtkP.CreateScene, args=(keyPress,))
   processes.append(sce)
   processes.append(win)
   sce.daemon = True
   win.daemon = True
   win.start()
   sce.start()
# CreateScene(keyPress)
# CreatWindows(keyPress)
   while True:
       print(keyPress[0])
       print(keyPress[1])
       sleep(1)   #秒  可以是小数
