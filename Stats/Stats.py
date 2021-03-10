import sys 
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar 
import matplotlib.pyplot as plt 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from ExtractData import return_daily_data, return_weekly_data

class Window(QDialog): 
       
    def __init__(self, parent=None): 
        super(Window, self).__init__(parent) 
    
        self.figure = plt.figure()  
        self.canvas = FigureCanvas(self.figure)  
        self.toolbar = NavigationToolbar(self.canvas, self) 
        
        self.button1 = QPushButton('DAILY')
        self.button2 = QPushButton('WEEKLY')
        self.plot1()
 
        self.button1.clicked.connect(self.plot1) 
        self.button2.clicked.connect(self.plot2)

        main_layout = QVBoxLayout() 
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas) 
           
        sublayout = QHBoxLayout()  
        sublayout.addWidget(self.button1)
        sublayout.addWidget(self.button2)

        main_layout.addLayout(sublayout)
        
        self.setLayout(main_layout) 

    def plot1(self):   
        
        self.button1.setEnabled(False)
        self.button2.setEnabled(True)
        self.figure.clear()

        ax = self.figure.add_subplot()

        dates, outcomes = return_daily_data(10)
        
        x = np.arange(len(dates))
        width = 0.2

        rects1 = ax.bar(x - 3*width/2, outcomes[0], width, label = 'Answered')
        rects2 = ax.bar(x - width/2, outcomes[1], width, label = 'No Answer')
        rects3 = ax.bar(x + width/2, outcomes[2], width, label = 'Busy')
        rects4 = ax.bar(x + 3*width/2, outcomes[3], width, label = 'Failed')
   
        ax.set_ylabel('Number of Calls')
        ax.set_title('Calls Outcome')
        ax.set_xticks(x)
        ax.set_xticklabels(dates[:10])
        ax.xaxis_date()
        ax.legend() 

        self.figure.autofmt_xdate()

        self.figure.tight_layout()

        plt.grid(linestyle='--', linewidth=0.3)
   
        self.canvas.draw() 
   
    def plot2(self):

        self.button1.setEnabled(True)
        self.button2.setEnabled(False)

        self.figure.clear()

        ax = self.figure.add_subplot()

        dates, outcomes = return_weekly_data(6)

        x = np.arange(len(dates))
        width = 0.2

        rects1 = ax.bar(x - 3*width/2, outcomes[0], width, label = 'Answered')
        rects2 = ax.bar(x - width/2, outcomes[1], width, label = 'No Answer')
        rects3 = ax.bar(x + width/2, outcomes[2], width, label = 'Busy')
        rects4 = ax.bar(x + 3*width/2, outcomes[3], width, label = 'Failed')

        ax.set_ylabel('Number of Calls')
        ax.set_title('Calls Outcome')
        ax.set_xticks(x)
        ax.set_xticklabels(dates[:10])
        ax.xaxis_date()
        ax.legend()

        self.figure.autofmt_xdate()

        self.figure.tight_layout()

        plt.grid(linestyle='--', linewidth=0.3)
        
        self.canvas.draw()

if __name__ == '__main__':  
    app = QApplication(sys.argv) 
    main = Window()  
    main.show() 
    sys.exit(app.exec_()) 
