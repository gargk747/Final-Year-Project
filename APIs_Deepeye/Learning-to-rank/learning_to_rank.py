#coding:utf-8
from functools import reduce
from re import X
import sys
from importlib import reload
import importlib
from xml.dom.minidom import Attr

from numpy import angle, double
importlib.reload(sys)
import MySQLdb
from instance import Instance
from table import Table
from view import Chart
from features import Type
import matplotlib.pyplot as plt
import pandas as pd
import pdvega
import ast

from mpl_toolkits.mplot3d import axes3d
import numpy as np
from matplotlib import style
style.use('ggplot')


#read data from database
dbArgs = sys.argv[1:6]
# print dbArgs
file1=open(r'C:\Users\gargk\Desktop\MNIT\Final Year Project\DeepEye\APIs_Deepeye\input.txt','r')
instance=Instance(sys.argv[6])
instance.addTable(Table(instance,False,'',''))
conn=MySQLdb.connect(host=dbArgs[0],port=int(dbArgs[1]),user=dbArgs[2],passwd=dbArgs[3],db=dbArgs[4],charset='utf8')
cur=conn.cursor()
instance.column_num=instance.tables[0].column_num=int((len(sys.argv)-8)/2)
for i in range(0,instance.column_num):
    instance.tables[0].names.append(sys.argv[8+i])
    instance.tables[0].types.append(Type.getType(sys.argv[8+i+instance.column_num].lower()))
instance.tables[0].origins=[i for i in range(instance.tables[0].column_num)]

instance.tuple_num=instance.tables[0].tuple_num=cur.execute(file1.readline())
instance.tables[0].D=list(map(list,cur.fetchall()))


#if table == none ===> exit
if len(list(instance.tables[0].D))==0:
    print ('{}')
    sys.exit(0)

#get all views and their score
instance.addTables(instance.tables[0].dealWithTable())
begin_id=1
while begin_id<instance.table_num:
    instance.tables[begin_id].dealWithTable()
    begin_id+=1
if instance.view_num==0:
    print ('{}')
    sys.exit(0)
instance.getScore()

#store views into database
#new_table_name='#'.join(sys.argv[1:])
#cur.execute('create table `'+new_table_name+'`(id int,data JSON)')
order1=order2=1
old_view=''
allVis = []
AttributeStr=file1.readline()
AttributeStr = ast.literal_eval(AttributeStr)

for i in range(instance.view_num):
    view=instance.tables[instance.views[i].table_pos].views[instance.views[i].view_pos]
    classify = str([])
    if view.series_num > 1:
        classify = str([v[0] for v in view.table.classes]).replace("u'", '\'').replace("'",'"')
    x_data=str(view.X)
    if view.fx.type==Type.numerical:
        x_data=str(view.X).replace("'",'"').replace('L','')
    elif view.fx.type==Type.categorical:
        x_data=str(view.X).replace("u'",'\'').replace("'",'"')
    else:
        len_x = len(view.X)
        x_data = '[' + reduce(lambda s1, s2: s1 + s2, [str(list(map(str, view.X[i]))) for i in range(len_x)]).replace(
            "'", '"')+']'
    y_data = str(view.Y)
    if view.fy.type == Type.numerical:
        y_data = y_data.replace('L', '')

    if old_view:
        order2 = 1
        order1 += 1

    data = '{"order1":' + str(order1) +',"describe":"' + view.table.describe + '","x_name":"' + view.fx.name + '","y_name":"' + view.fy.name + '","chart":"' + \
           Chart.chart[view.chart] + '","classify":' + classify + ',"x_data":' + x_data + ',"y_data":' + y_data + '}'
    
    # print(data)

    
    # print(view.fx.name)
    # print(view.fy.name)
    newFx=view.fx.name
    newFy=view.fy.name


    if('(' in view.fx.name):
        newFx=view.fx.name[4:-1]
    
    if('(' in view.fy.name):
        newFy=view.fy.name[4:-1]
    if([newFx,newFy] in AttributeStr):
        plt.title(view.table.describe)
        if(Chart.chart[view.chart] == "line"):
            plt.xlabel(view.fx.name)
            plt.ylabel(view.fy.name)
            print(view.fx.name)
            print(view.fy.name)
            plt.title(view.table.describe)
            plt.plot(x_data,y_data,color='maroon')

        elif(Chart.chart[view.chart]== "bar"):
            x_data=str(x_data)[3:-2]
            x_data=x_data.split('", "')
            x_data=list(x_data)
            # print(x_data)
            # print(y_data)
            y_data=str(y_data)[2:-2]
            y_data=y_data.split(', ')
            y_data=map(double,y_data)
            y_data=list(y_data)
            allVis.append([x_data,y_data])
            plt.xlabel(view.fx.name)
            plt.ylabel(view.fy.name)
            print(view.fx.name)
            print(view.fy.name)
            plt.title(view.table.describe)
            plt.bar(x_data,y_data,color='maroon',width = 0.5)
        
        elif(Chart.chart[view.chart]=='pie'):
            # x_data = x_data[0]
            # y_data = y_data[0]
            x_data = x_data[2:-2]
            y_data = y_data[2:-2]
            x_data = list(x_data.split(","))
            y_data = list(y_data.split(","))
            plt.xlabel(view.fx.name)
            plt.ylabel(view.fy.name)
            print(view.fx.name)
            print(view.fy.name)
            plt.title(view.table.describe)
            # print("X",x_data, " ","y",y_data)
            plt.pie(y_data,labels=x_data)
        
        elif(Chart.chart[view.chart]=='scatter'):
            x_data=str(x_data)
            x_data=x_data.replace("[","")
            x_data=x_data.replace("]","")
            x_data=x_data.split(', ')
            x_data=list(x_data)
            x_data=[float(i) for i in x_data]
            
            y_data=str(y_data)
            y_data=y_data.replace("[","")
            y_data=y_data.replace("]","")
            y_data=y_data.split(', ')
            y_data=list(y_data)
            y_data=[float(i) for i in y_data]
            plt.xlabel(view.fx.name)
            plt.ylabel(view.fy.name)
            print(view.fx.name)
            print(view.fy.name)
            plt.title(view.table.describe)
            plt.scatter(x_data, y_data, c ="blue")
        for i in AttributeStr:
            if(i[0]==newFx and i[1]==newFy and len(i)==3):
                fig=plt.figure(figsize = (10, 7))
                plt.title(view.table.describe)
                ax1 = plt.axes(projection ="3d")
                ax1.set_xlabel(view.fx.name)
                ax1.set_ylabel(view.fy.name)
                query = "SELECT `" + "` , `".join(i) + "` FROM " + sys.argv[6] +" Group BY `"+ i[1] + "` , `"+ i[2]+"`"
                cur.execute(query)
                dx3 =list(map(list,cur.fetchall()))
                xData=[]
                yData=[]
                zData=[]
                for j in dx3:
                    xData.append(j[0])
                    yData.append(j[1])
                    zData.append(j[2])
                # print("----------------x------------\n")
                # print(xData)
                # print("-----------y---------------\n")
                # print(yData)
                # print("--------z---------------------\n")
                # print(zData)
                z = np.zeros(len(xData))
                dx1 = np.ones(len(yData))
                dx2 = np.ones(len(yData))

                # dz = []
                # for j in dx3:
                #     dz.append(j[0])
                # print(dz,"AAAAAA")
                newXdata = []
                newYdata = []
                newZdata = []
                if(isinstance(xData[0],str)):
                    newXdata = list(set(xData))
                    for i in range(len(xData)):
                        xData[i] = newXdata.index(xData[i])
                if(isinstance(yData[0],str)):
                    newYdata = list(set(yData))
                    for i in range(len(yData)):
                        yData[i] = newYdata.index(yData[i])
                if(isinstance(zData[0],str)):
                    newZdata = list(set(zData))
                    for i in range(len(zData)):
                        zData[i] = newZdata.index(zData[i])
                ax1.scatter(xData, yData, zData, color="green")
                if(len(newXdata)!=0):
                    ax1.set(xticks = range(len(newXdata)), xticklabels = newXdata)
                if(len(newYdata)!=0):
                    ax1.set(yticks = range(len(newYdata)), yticklabels = newYdata)
                if(len(newZdata)!=0):
                    ax1.set(zticks = range(len(newZdata)), zticklabels = newZdata)     
                print(view.fx.name)
                print(view.fy.name)
                
                             
                plt.show()

        plt.grid()
        plt.show()
    # plt.show(block=False)
    # plt.pause(1)
    # plt.close()

    # for i in AttributeStr:
    #     if(len(i==3)):
    #         plt.p

    old_view = view

cur.close()
conn.close()



