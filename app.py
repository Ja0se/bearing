from asyncio.windows_events import NULL
import sys
from PySide2.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QHeaderView, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.figure import Figure
from PySide2.QtUiTools import loadUiType

import pandas as pd

from tkinter import filedialog, messagebox

import numpy as np


import threading

import tensorflow as tf
from lib.CLSTM import CLSTM


ui = loadUiType("ui/viewer.ui")[0]



class MainWindow(QMainWindow, ui):
    net = None
    batch_size = 128

    dataset = NULL

    x_train_data = NULL
    y_train_data = NULL

    x_test_data = NULL

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setupUi(self)
        
        self.setTrainTableWidthSize()

        self.setWidgetLoss()

        self.setWidgetAccuracy()        

        self.setWidgetTest()
        self.btnLoadTrainFile.clicked.connect(self.loadTrainFile)

        self.btnTrain.clicked.connect(self.trainData)


        self.btnLoadTestFile.clicked.connect(self.loadTestFile)

        self.btnTest.clicked.connect(self.testData)

    def setWidgetLoss(self) :
        canvas = FigureCanvas(Figure(figsize=(4, 3)))
        vbox = QVBoxLayout(self.wdgtLoss)
        vbox.addWidget(canvas)

        self.figLoss = canvas.figure


    def setWidgetAccuracy(self) :
        canvas = FigureCanvas(Figure(figsize=(4, 3)))
        vbox = QVBoxLayout(self.wdgtAcc)
        vbox.addWidget(canvas)

        self.figAcc = canvas.figure


    def setWidgetTest(self) :
        canvas = FigureCanvas(Figure(figsize=(4, 3)))
        vbox = QVBoxLayout(self.wdgtTest)
        vbox.addWidget(canvas)

        self.figTest = canvas.figure


    def setTrainTableWidthSize(self) :
        for index in range(0, self.twTrainData.horizontalHeader().count()) :
            self.twTrainData.horizontalHeader().setSectionResizeMode(index, QHeaderView.ResizeToContents)

    

    def loadTrainFile(self) :
        # files 변수에 선택 파일 경로 넣기
        files = filedialog.askopenfilenames(initialdir="/",\
                 title = "파일을 선택 해 주세요",\
                    filetypes = (("*.csv","*csv"),("*.xlsx","*xlsx"),("*.xls","*xls")))

        # 파일 선택 안했을 때 메세지 출력
        if files == '':
            messagebox.showwarning("경고", "파일을 추가 하세요") 

        #dir_path에 파일경로 하나씩 넣어서 읽기
        for dir_path in files:                                             
            #train_data = pd.read_csv(dir_path, sep=',', header= 0, encoding='euc-kr')
            train_data = pd.read_csv(dir_path, sep=',', header= 0)

            self.showTrainData(train_data)

            self.x_train_data, self.y_train_data = self.preProcess4TrainData(train_data)

    def preProcess4TrainData(self, data) :
        data.loc[data['합불판정'] == 'OK', '합불판정'] = 0
        data.loc[data['합불판정'] == 'NG', '합불판정'] = 1
        
        data = data.loc[:, ['검사측정값', '합불판정']]

        data['shift_1'] = data['검사측정값'].shift(1)
        
        data['합불판정'] = data['합불판정'].shift(-1)

        data.columns = ['Width','Label','Prev']

        x_train_data = data.dropna().drop('Label', axis=1)
        y_train_data = data.dropna()[['Label']]


        x_train_data = x_train_data.values
        y_train_data = y_train_data.values


        x_train_data = np.asarray(x_train_data).astype(np.float32)
        x_train_data = np.resize(x_train_data,(x_train_data.shape[0], 1, x_train_data.shape[1]))

        y_train_data = np.asarray(y_train_data).astype(np.float32)

        return x_train_data, y_train_data



    def preProcess4TestData(self, data) :
        data = data.loc[:, ['검사측정값']]
        data['shift_1'] = data['검사측정값'].shift(1)
        data.columns = ['Width','Prev']

        x_test_data = data.dropna()

        x_test_data = x_test_data.values

        x_test_data = np.asarray(x_test_data).astype(np.float32)
        x_test_data = np.resize(x_test_data,(x_test_data.shape[0], 1, x_test_data.shape[1]))

        return x_test_data


    def showTrainData(self, df) : 
        self.twTrainData.setRowCount(df.shape[0]) 

        for index, row in df.iterrows():
            self.twTrainData.setItem(index, 0, QTableWidgetItem(str(row[0])))
            self.twTrainData.setItem(index, 1, QTableWidgetItem(str(row[1])))
            self.twTrainData.setItem(index, 2, QTableWidgetItem(str(row[2])))
            self.twTrainData.setItem(index, 3, QTableWidgetItem(str(row[3])))
            self.twTrainData.setItem(index, 4, QTableWidgetItem(str(row[4])))
            self.twTrainData.setItem(index, 5, QTableWidgetItem(str(row[5])))
            self.twTrainData.setItem(index, 6, QTableWidgetItem(str(row[6])))
            self.twTrainData.setItem(index, 7, QTableWidgetItem(str(row[7])))
            self.twTrainData.setItem(index, 8, QTableWidgetItem(str(row[8])))

    def thdTrainData(self) :
        self.net = CLSTM(self.x_train_data, self.y_train_data, self.figLoss, self.figAcc)

        self.net.train()

    def trainData(self) :

        t = threading.Thread(target=self.thdTrainData)
        t.start()

    def loadTestFile(self) :
        # files 변수에 선택 파일 경로 넣기
        files = filedialog.askopenfilenames(initialdir="/",\
                 title = "파일을 선택 해 주세요",\
                    filetypes = (("*.csv","*csv"),("*.xlsx","*xlsx"),("*.xls","*xls")))

        # 파일 선택 안했을 때 메세지 출력
        if files == '':
            messagebox.showwarning("경고", "파일을 추가 하세요") 

        #dir_path에 파일경로 하나씩 넣어서 읽기
        for dir_path in files:                                             
            #train_data = pd.read_csv(dir_path, sep=',', header= 0, encoding='euc-kr')
            test_data = pd.read_csv(dir_path, sep=',', header= 0)

            self.showTestData(test_data)

            self.x_test_data = self.preProcess4TestData(test_data)


    def showTestData(self, df) : 
        self.twTestData.setRowCount(df.shape[0]) 

        for index, row in df.iterrows():
            self.twTestData.setItem(index, 0, QTableWidgetItem(str(row[0])))
            self.twTestData.setItem(index, 1, QTableWidgetItem(str(row[1])))
            self.twTestData.setItem(index, 2, QTableWidgetItem(str(row[2])))
            self.twTestData.setItem(index, 3, QTableWidgetItem(str(row[3])))
            self.twTestData.setItem(index, 4, QTableWidgetItem(str(row[4])))
            self.twTestData.setItem(index, 5, QTableWidgetItem(str(row[5])))
            self.twTestData.setItem(index, 6, QTableWidgetItem(str(row[6])))


    def thdTestData(self) :
        x_list = []
        y_list = []

        for indx, x in enumerate(self.x_test_data) :

            x = tf.expand_dims(x, axis=0)

            y = self.net.predict(x)

            x_list.append(indx)
            y_list.append(y.max())

            self.figTest.subplots().plot(x_list, y_list)
                
            self.figTest.canvas.draw()
            self.figTest.clf()


    def testData(self) :
        t = threading.Thread(target=self.thdTestData)
        t.start()

        

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    app.exec_()