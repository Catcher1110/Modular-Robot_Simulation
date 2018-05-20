#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vtk
from math import *
from vtk.util.colors import *
from Tkinter import *           # 导入 Tkinter 库
from time import ctime, sleep
import numpy as np
from compiler.ast import flatten
from time import sleep

#释义模板
#print(style.SetDefaultRenderer.__doc__)
#print('-----------------------------------------------')

finishedFlag=True
# Create a rendering window and renderer
renWin = vtk.vtkRenderWindow()  #这两条语句写在CreatScene中后，按键控制有问题！！！！为什么？？？



#定义模块数据结构--模块单元类     python中没有结构体，可以使用字典或者类替代
class modelUnit:
    ''' 这是模块单元类，存储了模块的各另加及装配体，并提供了相关方法 '''
    
    # 这些定义的是类数据属性，所有的类和实例共享
    
    # 模块零件     model1~model3 为固定面连接装置
    components = [r"model0.stl", r"model1.stl",
                r"model2.stl", r"model3.stl",
                r"model11.stl", r"model22.stl",
                r"model33.stl"]
    # 位置偏置   画模型图时，几何中心点(仿真时，模型的)和画图原点(仿真中模型的定位点)的偏置
    __posOffest = 3.5
    time = 0

    def __init__(self, num, phyID=0, topoID=0, conID=0, position=[0, 0, 0], rotation=[0, 0, 0]):
        '''
        一个RenderWindow中不能同时赋予两个render,所以需要创建两个assembly,赋给一个render
        '''        
        # 定义基本属性
        # 需提供查询
        self.phyID = 0
        self.topoID = 0
        self.conID = 0
        self.assembly = vtk.vtkAssembly()    # python中直接赋值(assembly1=assembly)是浅拷贝，原变量改变，拷贝变量也会改变
        self.actor = list()  # the list of links
        
        # 模块运动信息
        # 需提供查询
        self.component_angle = [0, 0, 0]             # 零件当前角度
        self.modelPosMatrixToAbs = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]   # 模块对于原点的位姿矩阵
        # 初始化，因为模块几何中心(Center Point 仿真中的运动中用于角度记录的点)不在
        self.coordinate=[position[0]+self.__posOffest, position[1]+self.__posOffest, position[2]+self.__posOffest]
        
        self.component_angle_target = [0, 0, 0]   # 零件旋转目标角
        self.component_angle_dir = [0, 0, 0]        # 零件旋转方向
        self.model_angle = [0, 0, 0]            # 模块当前角度 因为模块每次旋转的相对中心都会改变，所以每次旋转angle都要清零
        self.model_angle_target = [0, 0, 0]     # 模块旋转目标角
        self.rotateModelOrigin = [0, 0, 0]       # 模块旋转原点

        for idNum, filename in enumerate(self.components):
            self.actor.append(self.__LoadSTL(filename))
            if idNum == 0:
                self.actor[idNum].GetProperty().SetDiffuseColor(1, 1, 1)
            elif 1 <= idNum < 4:
                self.actor[idNum].GetProperty().SetDiffuseColor(0, 0, 1)
            elif 4 <= idNum < 7:
                self.actor[idNum].GetProperty().SetDiffuseColor(0, 1, 0)
            self.actor[idNum].GetProperty().SetDiffuse(.8)
            self.actor[idNum].GetProperty().SetSpecular(.5)
            self.actor[idNum].GetProperty().SetSpecularColor(1.0, 1.0, 1.0)
            self.actor[idNum].GetProperty().SetSpecularPower(30.0)
            # 给装配体添加零件
            self.assembly.AddPart(self.actor[idNum])
            # Add the actors to the scene
            # ren.AddActor(actor[id])
            
        # Also set the origin, position and orientation of assembly in space.
        # 设置装配体的原点（旋转平移以此为参照）
        self.assembly.SetOrigin(0, 0, 0)

        # 零件的局部坐标系会随装配体改变而改变
        # 初始化actor[]原点  （它的旋转平移以此为参照点）
        self.actor[0].SetOrigin(0, 0, 0)
        self.actor[1].SetOrigin(0, 0, 0)  
        self.actor[2].SetOrigin(0, 0, 0)
        self.actor[3].SetOrigin(0, 0, 0)
        self.actor[4].SetOrigin(0, 0, 0)
        self.actor[5].SetOrigin(0, 0, 0)
        self.actor[6].SetOrigin(0, 0, 0)

        coord = self.__CreateCoordinates()
        self.assembly.AddPart(coord)
        coord.SetOrigin(0, 0, 0)

        # 平移模块单元
        transform = vtk.vtkTransform()     
        transform.Translate(position[0] + 3.5, position[1] + 3.5, position[2] + 3.5)
        # transform.SetMatrix(self.modelMatrix1)
        self.assembly.SetUserTransform(transform)
        
        # self.assembly.AddPosition(position)
        
        # 旋转模块单元
        
        self.assembly.RotateX(rotation[0])
        self.assembly.RotateY(rotation[1])
        self.assembly.RotateZ(rotation[2])
        
        
    def __CreateCoordinates(self):    
        # create coordinate axes in the render window  创建坐标系
        axes = vtk.vtkAxesActor() 
        axes.SetTotalLength(20, 20, 20)  # Set the total length of the axes in 3 dimensions  坐标轴长度

        # Set the type of the shaft to a cylinder:0, line:1, or user defined geometry. 
        axes.SetShaftType(0) 

        axes.SetCylinderRadius(0.02) 
        axes.GetXAxisCaptionActor2D().SetWidth(0.03) 
        axes.GetYAxisCaptionActor2D().SetWidth(0.03) 
        axes.GetZAxisCaptionActor2D().SetWidth(0.03)

        axes.SetAxisLabels(1)  # Enable:1/disable:0 drawing the axis labels
        # 平移坐标系
        transform = vtk.vtkTransform()     
    #    transform.Translate(10,-2.5, 10)
        transform.Translate(0, 0, 0)
        axes.SetUserTransform(transform)
        # 设置坐标轴属性
        # axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(1,0,0)
        # axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().BoldOn() # disable text bolding

        return axes

    def getModelCoordinate(self):
        self.coordinate[0]=self.assembly.GetMatrix().GetElement(0,3)
        self.coordinate[1]=self.assembly.GetMatrix().GetElement(1,3)
        self.coordinate[2]=self.assembly.GetMatrix().GetElement(2,3)
        return self.coordinate

    def getComponentangle(self):
        return self.component_angle
    
    # 定义私有方法
    def __LoadSTL(self, filename):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        mapper = vtk.vtkPolyDataMapper() # maps polygonal data to graphics primitives
        mapper.SetInputConnection(reader.GetOutputPort())
        actor = vtk.vtkLODActor() 
        actor.SetMapper(mapper)
        return actor   # represents an entity in a rendered scene

    def moveSingleStep(self, origin, rotation, axes):
        if rotation > 0:
            singleStep = 1
            self.model_angle[axes] += 1
        else:
            singleStep = -1
            self.model_angle[axes] -= 1
        # 旋转坐标系相对绝对坐标系的转换矩阵(旋转坐标系在绝对坐标系中的位姿)
        transOriginToAbsList = [1, 0, 0, origin[0], 0, 1, 0, origin[1], 0, 0, 1, origin[2], 0, 0, 0, 1]
        for i in range(4):
            for j in range(4):
                # 取得模块在绝对坐标系中的位姿
                self.modelPosMatrixToAbs[4*i+j] = self.assembly.GetMatrix().GetElement(i, j)
        # print(self.modelPosMatrixToAbs)
        # 求得模块相对旋转坐标系位姿
        transOriginToAbsMat = self.__list2matrix(transOriginToAbsList)
        modelPosMatrixToRelaMat = transOriginToAbsMat.I*self.__list2matrix(self.modelPosMatrixToAbs)
        # 绕旋转坐标系的X轴旋转singleStep度
        if axes == 0:   # X轴
            modelPosMatrixToAbsNext = transOriginToAbsMat*np.mat([[1,0,0,0], [0,cos(radians(singleStep)), -sin(radians(singleStep)),0],[0,sin(radians(singleStep)),cos(radians(singleStep)),0],[0,0,0,1]])\
                               *modelPosMatrixToRelaMat
        elif axes == 1: # Y轴
            modelPosMatrixToAbsNext = transOriginToAbsMat*np.mat([[cos(radians(singleStep)),0,sin(radians(singleStep)),0],[0,1,0,0],[-sin(radians(singleStep)),0,cos(radians(singleStep)),0],[0,0,0,1]])\
                               *modelPosMatrixToRelaMat
        elif axes == 2: # Z轴
            modelPosMatrixToAbsNext = transOriginToAbsMat*np.mat([[cos(radians(singleStep)),-sin(radians(singleStep)),0,0],[sin(radians(singleStep)),cos(radians(singleStep)),0,0],[0,0,1,0],[0,0,0,1]])\
                               *modelPosMatrixToRelaMat

        # 计算需要转换的矩阵  或者直接把modelPosMatrixToAbsNext值赋给assembly.GetMatrix()
        transMatToNextPos = modelPosMatrixToAbsNext*self.__list2matrix(self.modelPosMatrixToAbs).I
        
        transform = vtk.vtkTransform()     
        transform.SetMatrix(self.__matrix2list(modelPosMatrixToAbsNext))
        self.assembly.SetUserTransform(transform)

        
    def __list2matrix(self, lis):  #转化为4*4矩阵
        tempList=[]
        for i in range(4):
            tempList.append([lis[4*i], lis[4*i+1], lis[4*i+2], lis[4*i+3]])
        mat=np.mat(tempList)
        return mat

    def __matrix2list(self, mat):  #转化为一维列表
        tempList=[]
        tempList= flatten(mat.tolist())
        return tempList
            
    # 沿着旋转轴方向看，正为顺时针
    def rotateAssembly(self, rotation):       #有默认值的参数必须放在后面
        if rotation[0] != self.model_angle[0]:
            if rotation[0] > 0:
                self.assembly.RotateX(1)
                self.model_angle[0] += 1
            elif rotation[0] < 0:
                self.assembly.RotateX(-1)
                self.model_angle[0] -= 1
        if rotation[1] != self.model_angle[1]:
            if rotation[1] > 0:
                self.assembly.RotateY(1)
                self.model_angle[1] += 1
            elif rotation[1] < 0:
                self.assembly.RotateY(-1)
                self.model_angle[1] -= 1
        if rotation[2] != self.model_angle[2]:
            if rotation[2] > 0:
                self.assembly.RotateZ(1)
                self.model_angle[2] += 1
            elif rotation[2] < 0:
                self.assembly.RotateZ(-1)
                self.model_angle[2] -= 1
        '''
        print(rotation)
        print(self.model_angle)
        '''
  
    # 控制模块faceID面零件绕axes轴旋转到targetPos处  direction=true顺时针
    def rotateComponentAbs(self, faceID, direction):
        faceID -= 4
        if direction == 1:      #顺时针
            self.component_angle[faceID] += 1
            if self.component_angle[faceID] > 359:
                    self.component_angle[faceID] = 0
            if faceID == 0:
                # 角度制 所给角度为绝对角度  绝对的
                self.actor[faceID+4].SetOrientation(0, -self.component_angle[faceID], 0)
            elif faceID == 1:
                self.actor[faceID+4].SetOrientation(0,0,-self.component_angle[faceID])
            elif faceID == 2:
                self.actor[faceID+4].SetOrientation(-self.component_angle[faceID],0,0)
        elif direction == 2:   # 逆时针
            self.component_angle[faceID] -= 1
            if self.component_angle[faceID] < 0:
                self.component_angle[faceID] = 359
            if faceID == 0:
                self.actor[faceID+4].SetOrientation(0, -self.component_angle[faceID], 0)
            elif faceID == 1:
                self.actor[faceID+4].SetOrientation(0, 0, -self.component_angle[faceID])
            elif faceID == 2:
                self.actor[faceID+4].SetOrientation(-self.component_angle[faceID], 0, 0)

    def setTarget(self, targetComponentPos, targetComponentDir, targetModelPos, rotateModelOrigin=[0, 0, 0]):
        '''给模块单元设置运动目标[100, 60, 0], [1, 2, 0], [90, 0, 0], [0, 0, -300]'''
        self.component_angle_target = targetComponentPos
        self.component_angle_dir = targetComponentDir
        self.model_angle_target = targetModelPos

        self.rotateModelOrigin = rotateModelOrigin

        self.model_angle = [0, 0, 0]     # 将模块整体旋转的角度归零

    def setTargetTran(self, targetPos):
        self.coordinate = [targetPos[0] + self.__posOffest, targetPos[1] + self.__posOffest,
                           targetPos[2] + self.__posOffest]

    def selfCheck(self):
        '''模块自检函数，未达到目标位置继续运动并返回false'''
        testRes=True
        for i in range(3):
            if self.component_angle[i]!=self.component_angle_target[i]:
                self.rotateComponentAbs(i+4,self.component_angle_dir[i])
                testRes=False
        #不同于for循环，这样有旋转顺序，按X、Y、Z顺序进行旋转
        if self.model_angle[0] != self.model_angle_target[0]: 
            self.moveSingleStep(self.rotateModelOrigin, self.model_angle_target[0], 0) #0X 1Y 2Z
            testRes=False
        elif self.model_angle[1] != self.model_angle_target[1]: 
            self.moveSingleStep(self.rotateModelOrigin, self.model_angle_target[1], 1) #1Y 1Y 2Z
            testRes=False
        elif self.model_angle[2] != self.model_angle_target[2]: 
            self.moveSingleStep(self.rotateModelOrigin, self.model_angle_target[2], 2) #2Z 1Y 2Z
            testRes=False
        return testRes   


# 10ms回调一次
class vtkTimerCallback():
    '''时间中断'''
    timer_count=0
    signalOfTimer=[]
    def __init__(self,signal):
        self.timer_count = 0
        self.signalOfTimer=signal

    def execute(self,obj,event):
        self.timer_count += 1
        if self.timer_count==400:
            self.timer_count=0
            
        #1s扫描
        if self.timer_count%100==0:
            pass
        #0.4s扫描     视觉暂留
        if self.timer_count%40==0:
            #model1.selfCheck()
            pass

        #0.1s扫描
        if self.timer_count%10==0:
            pass
        
        for i in range(len(model)):
            model[i].selfCheck()
            
        iren = obj
        iren.GetRenderWindow().Render()


# Customize   定制  vtkInteractorStyleTrackball(追踪球)Camera 
class MyInteractor(vtk.vtkInteractorStyleTrackballCamera):
    keys=[]          # 定义类的属性
    def __init__(self, dataset, parent=None):
        self.AddObserver("CharEvent",self.OnCharEvent)   # CharEvent是什么事件？？？？？
        self.AddObserver("KeyPressEvent",self.OnKeyPressEvent)
        self.keys=dataset    #方法中调用类的属性，必须在前面调价self.!!!!!!!!!!!!
    # Override 重写 the default key operations which currently handle trackball or joystick styles is provided
    # OnChar is triggered when an ASCII key is pressed. Some basic key presses are handled here 
    def OnCharEvent(self,obj,event):
        pass
    
    def OnKeyPressEvent(self, obj, event):
        # global angle
        # Get the compound key strokes for the event
        self.keys[0] = self.GetInteractor().GetKeySym()       # 获取所按按键
        # Output the key that was pressed
        print("Pressed: " ,  self.keys[0])
        
        if self.keys[0] == "j":
            model[0].setTarget([100, 60, 0], [1, 2, 0], [90, 0, 0], [0, 0, -200])
            # model[1].setTarget([100, 60, 0], [1, 2, 0], [0, 0, 0], [0, 0, -300])
            # model2.setTarget([200,100,300],[1,2,2],[0,230,0],[1,2,1],[100,0,0])
        if self.keys[0] == "k":
            model[0].setTarget([0, 0, 0], [2, 2, 0], [-90, 0, 0], [0, -200, 0])
            model[3].setTarget([0, 0, 0], [2, 2, 0], [-90, 0, 0], [0, -200, 0])
            #model2.setTarget([100,200,0],[2,1,0],[0,80,0],[1,1,1],[-300,0,0])
        if self.keys[0] == "s":
            # 初始化零件角度
            for i in range(len(model)):
                model[i].setTarget([330, 90, 90], [2, 1, 1], [0, 0, 0], [0, 0, 0])
            # print(len(model))
            # model[3].setTarget([0, 0, 0], [2, 2, 0], [-90, 0, 0], [0, -200, 0])
        # if self.keys[0] == "g":
        #     model[0].setTargetTran([160, 0, 0])
        if self.keys[0] == "x":
            controlByMatrix(1)
        if self.keys[0] == "z":
            controlByMatrix(0)
        if self.keys[0] == "c":
            controlByMatrix(2)
            # for moveId in self.keys[1]:
            #     model[moveId].setTarget(self.keys[2], self.keys[3], self.keys[4], model[self.keys[5]].getModelCoordinate())
        if self.keys[0] == "v":
            controlByMatrix(3)
        if self.keys[0] == "b":
            controlByMatrix(4)
        if self.keys[0] == "n":
            controlByMatrix(5)
        if self.keys[0] == "m":
            controlByMatrix(6)
        if self.keys[0] == "d":
            controlByMatrix(7)
        if self.keys[0] == "f":
            controlByMatrix(8)
        if self.keys[0] == "g":
            controlByMatrix(9)
        if self.keys[0] == "h":
            controlByMatrix(10)
            
        # Ask each renderer owned by this RenderWindow to render its image and synchronize 同步 this process  
        renWin.Render()
        return


def Command(moveIdList,rotationAngle,originId):
    '''moveIdList：旋转模块Id列表，rotationAngle：旋转角度，旋转顺序XYZ，originId旋转中心模块Id '''
    pass
    
        
def labelWidget(iren):
    '''利用widget给每一个模块添加label'''
    # Create the widget
    balloonRep = vtk.vtkBalloonRepresentation()
    balloonRep.SetBalloonLayoutToImageRight()

    balloonWidget = vtk.vtkBalloonWidget()
    balloonWidget.SetInteractor(iren)
    balloonWidget.SetRepresentation(balloonRep)
    '''
    balloonWidget.AddBalloon(sphereActor, "This is a sphere")
    balloonWidget.AddBalloon(regularPolygonActor, "This is a regular polygon")
    '''
    return balloonWidget


def CreateCoordinates():    
    # create coordinate axes in the render window  创建坐标系
    axes = vtk.vtkAxesActor() 
    axes.SetTotalLength(20, 20, 20)  # Set the total length of the axes in 3 dimensions  坐标轴长度

    # Set the type of the shaft to a cylinder:0, line:1, or user defined geometry. 
    axes.SetShaftType(0) 

    axes.SetCylinderRadius(0.02) 
    axes.GetXAxisCaptionActor2D().SetWidth(0.03) 
    axes.GetYAxisCaptionActor2D().SetWidth(0.03) 
    axes.GetZAxisCaptionActor2D().SetWidth(0.03)

    axes.SetAxisLabels(1)  #[0,0,0],[2,2,0],[0,0,180],model[1].getModelCoordinate() Enable:1/disable:0 drawing the axis labels
    #平移坐标系
    transform = vtk.vtkTransform()     
#    transform.Translate(10,-2.5, 10)
    transform.Translate(0,0,0) 
    axes.SetUserTransform(transform)
    #设置坐标轴属性
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(1,0,0)
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().BoldOn() # disable text bolding

    return axes
    

def CreateGround():
    # create plane source
    plane = vtk.vtkPlaneSource()  
    plane.SetXResolution(50)
    plane.SetYResolution(50)
    plane.SetCenter(0,0,0)
    plane.SetNormal(0,0,1)
    
    # mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(plane.GetOutputPort())
     
    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetRepresentationToWireframe()  #将平面以线框的形式显示
    # actor.GetProperty().SetOpacity(0.1)  # 1.0 is totally opaque and 0.0 is completely transparent
    actor.GetProperty().SetColor(light_grey)

    '''
    # Load in the texture map. A texture is any unsigned char image.
    bmpReader = vtk.vtkBMPReader()  
    bmpReader.SetFileName(r"base.stl\111.bmp")  
    texture = vtk.vtkTexture()  
    texture.SetInputConnection(bmpReader.GetOutputPort())  
    texture.InterpolateOn()  
    actor.SetTexture(texture)
    '''

    transform = vtk.vtkTransform()
    transform.Scale(2000, 2000, 100)   # 面的尺寸调节    创建一个比例矩阵（对角元素为x,y,z），即想x，y，z方向扩大对应倍
    # 因为是面，所以z的变化没有影响
    actor.SetUserTransform(transform)
    
    return actor
        

def controlByMatrix(mat):
    if mat == 0:
        for i in [0, 1, 2, 3, 5, 6, 7, 10, 11]:
            model[i].setTarget([330, 20, 90], [1, 2, 1], [0, 0, 0], model[i].getModelCoordinate())

        model[7].setTarget([330, 90, 20], [1, 1, 2], [0, 0, 0], model[7].getModelCoordinate())
        # model[0].setTarget(model[0].getComponentangle(), [2, 2, 0], [-90, 0, 0], model[0].getModelCoordinate())
        # model[1].setTarget(model[1].getComponentangle(), [2, 2, 0], [-90, 0, 0], model[0].getModelCoordinate())
    if mat == 1:
        model[1].setTarget([330, 110, 90], [2, 1, 1], [0, 0, 0], model[1].getModelCoordinate())
        for i in range(2, 5):
            model[i].setTarget(model[i].getComponentangle(), [1, 1, 1], [0, 0, -90], model[i].getModelCoordinate())
    if mat == 2:
        model[6].setTarget([330, 110, 90], [2, 1, 2], [0, 0, 0], model[6].getModelCoordinate())
        model[7].setTarget(model[7].getComponentangle(), [2, 2, 1], [0, 0, -90], model[7].getModelCoordinate())
        model[8].setTarget(model[8].getComponentangle(), [1, 1, 1], [0, 0, -90], model[7].getModelCoordinate())
        # print(model[7].getComponentangle())
    if mat == 3:
        model[8].setTarget([330, 90, 160], [2, 1, 1], [0, 0, 0], model[8].getModelCoordinate())
    if mat == 4:
        model[1].setTarget([330, 200, 90], [2, 1, 2], [0, 0, 0], model[1].getModelCoordinate())
    if mat == 5:
        model[6].setTarget([330, 200, 90], [2, 1, 2], [0, 0, 0], model[6].getModelCoordinate())
        for i in [2, 3, 4, 7, 8]:
            model[i].setTarget(model[i].getComponentangle(), [1, 1, 1], [0, 0, -90], model[7].getModelCoordinate())
    if mat == 6:
        model[8].setTarget([330, 90, 340], [2, 1, 1], [0, 0, 0], model[8].getModelCoordinate())
        for i in [2, 3, 4]:
            model[i].setTarget(model[i].getComponentangle(), [1, 1, 1], [180, 0, 0], model[2].getModelCoordinate())
    if mat == 7:
        model[6].setTarget([330, 290, 90], [2, 1, 2], [0, 0, 0], model[6].getModelCoordinate())
        for i in [2, 3, 4, 7, 8]:
            model[i].setTarget(model[i].getComponentangle(), [1, 1, 1], [0, 0, -90], model[7].getModelCoordinate())
    if mat == 8:
        model[4].setTarget([330, 20, 90], [1, 2, 1], [0, 0, 0], model[4].getModelCoordinate())
    if mat == 9:
        model[8].setTarget([330, 90, 50], [2, 1, 1], [0, 0, 0], model[8].getModelCoordinate())
    if mat == 10:
        model[6].setTarget([330, 200, 90], [2, 2, 2], [0, 0, 0], model[6].getModelCoordinate())
        model[7].setTarget(model[7].getComponentangle(), [2, 2, 1], [0, 0, 90], model[7].getModelCoordinate())
        model[8].setTarget(model[8].getComponentangle(), [1, 1, 1], [0, 0, 90], model[7].getModelCoordinate())


class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()

    def leftButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())

        # get the new
        self.NewPickedActor = picker.GetActor()

        # If something was selected
        if self.NewPickedActor:
            # If we picked something before, reset its property
            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)

            # Save the property of the picked actor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
            # Highlight the picked actor by changing its properties
            self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)

            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor

        self.OnLeftButtonDown()
        return


def CreateScene(key):
    # Create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()         #实例化vtkRenderWindowInteractor交互类
    iren.SetRenderWindow(renWin)
    
    ren = vtk.vtkRenderer()
    setabel=labelWidget(iren)
    
    # add the custom style
    stylePick = MouseInteractorHighLightActor()
    stylePick.SetDefaultRenderer(ren)
    iren.SetInteractorStyle(stylePick)
    
    global model
    model = list()
    # 166 距离正好贴合, 200 距离作为初始距离最佳
    pd = 166

    modelTemp = modelUnit(0, 0, 0, 0, [0, -2 * pd, pd], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(1, 0, 0, 0, [0, -2 * pd, 2 *pd], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(2, 0, 0, 0, [0, -2 * pd, 3 * pd], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(3, 0, 0, 0, [0, -2 * pd, 4 * pd], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(4, 0, 0, 0, [0, -2 * pd, 5 * pd], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(5, 0, 0, 0, [0, 0, pd], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(6, 0, 0, 0, [0, 0, 2 * pd], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(7, 0, 0, 0, [0, 0, 3 * pd], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(8, 0, 0, 0, [pd, 0, 3 * pd], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(9, 0, 0, 0, [0, 2 * pd, 0], [0, 90, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(10, 0, 0, 0, [0, -2 * pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(11, 0, 0, 0, [0, 0, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    '''modelTemp = modelUnit(1, 0, 0, 0, [pd, 0, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(2, 0, 0, 0, [2 * pd, 0, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(3, 0, 0, 0, [3 * pd, 0, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(4, 0, 0, 0, [0, -pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(5, 0, 0, 0, [pd, -pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(6, 0, 0, 0, [2 * pd, -pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(7, 0, 0, 0, [3 * pd, -pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(8, 0, 0, 0, [0, -2 * pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(9, 0, 0, 0, [pd, -2 * pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(10, 0, 0, 0, [2 * pd, -2 * pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(11, 0, 0, 0, [3 * pd, -2 * pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(12, 0, 0, 0, [0, -3 * pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(13, 0, 0, 0, [pd, -3 * pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(14, 0, 0, 0, [2 * pd, -3 * pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)

    modelTemp = modelUnit(15, 0, 0, 0, [3 * pd, -3 * pd, 0], [0, 0, 0])
    ren.AddActor(modelTemp.assembly)
    model.append(modelTemp)'''

    ren.AddActor(CreateCoordinates())
    # ren.AddActor(CreatUnit([200,200,0]))
    # renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)         
    
    style = MyInteractor(key)      #实例化自定义交互类
    style.SetDefaultRenderer(ren)
    iren.SetInteractorStyle(style)
    
    # Initialize must be called prior to creating timer events.
    iren.Initialize()
    # Sign up to receive TimerEvent
    tIrq = vtkTimerCallback(key)
    iren.AddObserver('TimerEvent', tIrq.execute)
    timerId = iren.CreateRepeatingTimer(10)   #10ms回调一次
    
    # creat ground
    ground = CreateGround()
    ren.AddActor(ground)

    # Set background color
    ren.SetBackground(.2, .2, .2)

    # Set window size
    renWin.SetSize(1000, 600)

    # Set up the camera to get a particular view of the scene
    camera = vtk.vtkCamera()
    camera.SetFocalPoint(0, 0, 0)
    camera.SetPosition(0, 0, 300)
    camera.ComputeViewPlaneNormal()
    camera.SetViewUp(0, 1, 0)
    camera.Zoom(0.5)
    ren.SetActiveCamera(camera)

    # Enable user interface interactor
    iren.Initialize()
    iren.Start()


if __name__=='__main__':
    CreateScene(['a', [0, 1], [100, 60, 0], [1, 2, 0], [90, 0, 0], 2])

