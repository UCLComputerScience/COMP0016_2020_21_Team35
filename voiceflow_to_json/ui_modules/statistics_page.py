from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QWidget, QDateEdit
from PyQt5.QtCore import Qt, QDateTime

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime
from datetime import datetime

from voiceflow_to_json.statistics.extract_data import return_daily_data, return_monthly_data, return_period_data

from voiceflow_to_json.ui_modules.shared_buttons import BackButton


class StatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.date = datetime.today()
        self.date = self.date.strftime('%Y-%m-%d')

        self.l1 = QLabel('Please choose the period of time for which to diplay the data: ')
        self.buttonDaily = QPushButton('daily')
        self.buttonMonthly = QPushButton('monthly')
        self.buttonPeriod = QPushButton('set period')

        self.buttonDaily.clicked.connect(self.daily)
        self.buttonMonthly.clicked.connect(self.monthly)
        self.buttonPeriod.clicked.connect(self.period)

        sublayoutTime = QHBoxLayout()
        sublayoutTime.addWidget(self.l1)
        sublayoutTime.addWidget(self.buttonDaily)
        sublayoutTime.addWidget(self.buttonMonthly)
        sublayoutTime.addWidget(self.buttonPeriod)
        sublayoutTime.setAlignment(Qt.AlignRight);

        self.l2 = QLabel('Select the date: ')
        self.l3 = QLabel('   Select the end date: ')

        self.dateedit = QDateEdit(calendarPopup=True)
        self.dateedit.setDateTime(QDateTime.currentDateTime())
        self.startDate = QDateEdit(calendarPopup=True)
        self.startDate.setDateTime(QDateTime.currentDateTime())
        self.endDate = QDateEdit(calendarPopup=True)
        self.endDate.setDateTime(QDateTime.currentDateTime())

        self.l3.hide()
        self.startDate.hide()
        self.endDate.hide()

        self.monthList = QDateEdit()
        self.monthList.setDisplayFormat("MMM")
        self.monthList.setDateTime(QDateTime.currentDateTime())
        self.monthList.hide()

        self.yearList = QDateEdit()
        self.yearList.setDisplayFormat("yyyy")
        self.yearList.setDateTime(QDateTime.currentDateTime())
        self.yearList.hide()

        self.l4 = QLabel("'Start date' should be before 'end date'!")
        self.l4.setStyleSheet("QWidget {color : rgba(255,0,0,255);}")
        self.l4.hide()

        sublayoutSelectDate = QHBoxLayout()
        sublayoutSelectDate.addWidget(self.l2)
        sublayoutSelectDate.addWidget(self.dateedit)
        sublayoutSelectDate.addWidget(self.monthList)
        sublayoutSelectDate.addWidget(self.yearList)
        sublayoutSelectDate.addWidget(self.startDate)
        sublayoutSelectDate.addWidget(self.l3)
        sublayoutSelectDate.addWidget(self.endDate)
        sublayoutSelectDate.setAlignment(Qt.AlignRight);

        self.button_show_layout = QHBoxLayout()
        self.buttonShow = QPushButton('Show Analytics')
        self.buttonShow.clicked.connect(self.update)
        self.button_show_layout.addWidget(QLabel())
        self.button_show_layout.addWidget(QLabel())
        self.button_show_layout.addWidget(self.buttonShow)

        sublayoutTimeSelect = QVBoxLayout()
        sublayoutTimeSelect.addLayout(sublayoutTime)
        sublayoutTimeSelect.addLayout(sublayoutSelectDate)
        sublayoutTimeSelect.addWidget(self.l4, alignment=Qt.AlignRight)
        sublayoutTimeSelect.addLayout(self.button_show_layout)

        self.button1 = QPushButton('Hourly Call Summary')
        self.button2 = QPushButton('Initial Calling Outcome')
        self.button3 = QPushButton('Redirected Calls')
        self.button4 = QPushButton('IVR Call Drop Rate')

        self.outcomes, self.time, self.redirect = return_daily_data(self.date)
        self.graph = 1
        self.period = 'daily'
        self.day = datetime.today().strftime('%d %B %Y')
        self.month = datetime.today().strftime('%B')
        self.year = datetime.today().strftime('%Y')
        self.fromDate = datetime.today().strftime('%d %B %Y')
        self.toDate = datetime.today().strftime('%d %B %Y')
        self.plot1()

        self.button1.clicked.connect(self.plot1)
        self.button2.clicked.connect(self.plot2)
        self.button3.clicked.connect(self.plot3)
        self.button4.clicked.connect(self.plot4)

        sublayout1 = QHBoxLayout()
        sublayout1.addWidget(self.button1)
        sublayout1.addWidget(self.button2)

        sublayout2 = QHBoxLayout()
        sublayout2.addWidget(self.button3)
        sublayout2.addWidget(self.button4)

        sublayout = QVBoxLayout()
        sublayout.addLayout(sublayout1)
        sublayout.addLayout(sublayout2)

        back_button_creator = BackButton()
        self.back_button = back_button_creator.create_back_button()
        back_layout = back_button_creator.create_back_layout(self.back_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.toolbar)
        main_layout.addLayout(sublayoutTimeSelect)
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(sublayout)
        main_layout.addLayout(back_layout)

        self.setLayout(main_layout)

    def update(self):
        self.l4.hide()
        if self.period == 'daily':
            date = self.dateedit.date().toPyDate().strftime('%Y-%m-%d')
            self.outcomes, self.time, self.redirect = return_daily_data(date)
            self.day = self.dateedit.date().toPyDate().strftime('%d %B %Y')
            print(self.day)
        elif self.period == 'monthly':
            month = self.monthList.date().toPyDate().strftime('%m')
            year = self.yearList.date().toPyDate().strftime('%Y')
            self.outcomes, self.time, self.redirect = return_monthly_data(year + '-' + month)
            self.month = self.monthList.date().toPyDate().strftime('%B')
            self.year = self.yearList.date().toPyDate().strftime('%Y')
        elif self.period == 'period':
            start = self.startDate.date().toPyDate()
            end = self.endDate.date().toPyDate()
            if start > end:
                self.l4.show()
            else:
                self.outcomes, self.time, self.redirect = return_period_data(start, end)
            self.fromDate = self.startDate.date().toPyDate().strftime('%d %B %Y')
            self.toDate = self.endDate.date().toPyDate().strftime('%d %B %Y')
        if self.graph == 1:
            self.plot1()
        elif self.graph == 2:
            self.plot2()
        elif self.graph == 3:
            self.plot3()
        else:
            self.plot4()

    def daily(self):
        self.period = 'daily'
        self.dateedit.show()
        self.monthList.hide()
        self.l2.setText('Select the date: ')
        self.l3.hide()
        self.startDate.hide()
        self.endDate.hide()
        self.update()
        self.monthList.hide()
        self.yearList.hide()

    def monthly(self):
        self.period = 'monthly'
        self.dateedit.hide()
        self.monthList.show();
        self.l2.setText('Select the month: ')
        self.l3.hide()
        self.startDate.hide()
        self.endDate.hide()
        self.update()
        self.monthList.show()
        self.yearList.show()

    def period(self):
        self.period = 'period'
        self.dateedit.hide()
        self.monthList.hide()
        self.l2.setText('Select the start date: ')
        self.l3.show()
        self.startDate.show()
        self.endDate.show()
        self.update()
        self.monthList.hide()
        self.yearList.hide()

    def plot1(self):

        COLOR = 'dimgrey'
        matplotlib.rcParams['text.color'] = COLOR
        matplotlib.rcParams['axes.labelcolor'] = COLOR
        matplotlib.rcParams['xtick.color'] = COLOR
        matplotlib.rcParams['ytick.color'] = COLOR
        matplotlib.rcParams['lines.color'] = COLOR

        self.graph = 1
        self.figure.clear()

        ax = self.figure.add_subplot()

        hours = ['Before 08:00', '08:00 - 10:00', '10:00 - 12:00', '12:00 - 14:00', '14:00 - 16:00',
                 '16:00 - 18:00', 'After 18:00']

        plt.plot(hours, self.time, marker='o')

        if self.period == 'daily':
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                plt.title('There were no incoming calls on  ' + self.day, color='black')
            else:
                plt.title('Hourly call summary on  ' + self.day, color='black')
        elif self.period == 'monthly':
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                plt.title('There were no incoming calls on  ' + self.month + ' ' + self.year, color='black')
            else:
                plt.title('Hourly call summary on  ' + self.month + ' ' + self.year, color='black')
        else:
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                plt.title('There were no incoming calls from  ' + self.fromDate + '  to  ' + self.toDate,
                          color='black')
            else:
                plt.title('Hourly call summary from  ' + self.fromDate + '  to  ' + self.toDate, color='black')

        plt.ylabel('Number of calls')

        self.figure.tight_layout()
        self.figure.autofmt_xdate()

        plt.grid(linestyle='--', linewidth=0.3)

        self.canvas.draw()

    def plot2(self):

        self.graph = 2
        self.figure.clear()

        ax = self.figure.add_subplot()

        possible_outcomes = ('Answered', 'No answer', 'Busy', 'Failed')
        y_pos = np.arange(len(possible_outcomes))

        ax.barh(possible_outcomes, self.outcomes[:4])

        if self.period == 'daily':
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                ax.set_title('There were no incoming calls on  ' + self.day, color='black')
            else:
                ax.set_title('Outcome of all incoming calls on  ' + self.day, color='black')
        elif self.period == 'monthly':
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                ax.set_title('There were no incoming calls on  ' + self.month + ' ' + self.year, color='black')
            else:
                ax.set_title('Outcome of all incoming calls on  ' + self.month + ' ' + self.year, color='black')
        else:
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                ax.set_title('There were no incoming calls from  ' + self.fromDate + '  to  ' + self.toDate,
                             color='black')
            else:
                ax.set_title('Outcome of all incoming calls from  ' + self.fromDate + '  to  ' + self.toDate,
                             color='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(possible_outcomes)
        ax.invert_yaxis()
        ax.set_xlabel('Number of calls')

        self.figure.tight_layout()

        plt.grid(linestyle='--', linewidth=0.3)

        self.canvas.draw()

    def plot3(self):

        self.graph = 3
        self.figure.clear()

        ax = self.figure.add_subplot()

        keys = list(self.redirect.keys())
        values = list(self.redirect.values())

        ax.bar(keys, values, width=0.4)
        ax.set_ylabel('Number of Calls')

        if self.period == 'daily':
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                ax.set_title('There were no incoming calls on  ' + self.day, color='black')
            else:
                ax.set_title('Redirected calls on  ' + self.day, color='black')
        elif self.period == 'monthly':
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                ax.set_title('There were no incoming calls on  ' + self.month + ' ' + self.year, color='black')
            else:
                ax.set_title('Redirected calls on  ' + self.month + ' ' + self.year, color='black')
        else:
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                ax.set_title('There were no incoming calls from  ' + self.fromDate + '  to  ' + self.toDate,
                             color='black')
            else:
                ax.set_title('Redirected calls from  ' + self.fromDate + '  to  ' + self.toDate, color='black')

        self.figure.tight_layout()

        plt.grid(linestyle='--', linewidth=0.3)

        self.canvas.draw()

    def plot4(self):

        self.graph = 4
        self.figure.clear()

        ax = self.figure.add_subplot()

        total_calls = self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3]
        percentages = [0, 0]
        if total_calls != 0:
            dropped_percent = self.outcomes[4] * 100 / total_calls
            percentages = [100 - dropped_percent, dropped_percent]
        labels = ['Successful IVR Calls', 'Dropped IVR Calls']
        explode = (0, 0.1)

        ax.pie(percentages, explode=explode, labels=labels, autopct='%1.1f%%', textprops={'color': "k"},
                           shadow=True, startangle=-45)
        ax.axis('equal')

        if self.period == 'daily':
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                ax.set_title('There were no incoming calls on  ' + self.day, color='black')
            else:
                ax.set_title('Call setup success rate on  ' + self.day, color='black')
        elif self.period == 'monthly':
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                ax.set_title('There were no incoming calls on  ' + self.month + ' ' + self.year, color='black')
            else:
                ax.set_title('IVR call drop rate on  ' + self.month + ' ' + self.year, color='black')
        else:
            if self.outcomes[0] + self.outcomes[1] + self.outcomes[2] + self.outcomes[3] == 0:
                ax.set_title('There were no incoming calls from  ' + self.fromDate + '  to  ' + self.toDate,
                             color='black')
            else:
                ax.set_title('Call setup success rate from  ' + self.fromDate + '  to  ' + self.toDate,
                             color='black')
        self.canvas.draw()