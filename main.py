import sys

from PyQt5 import QtWidgets, QtGui, uic


class HomeScreen(QtWidgets.QWidget):

    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        uic.loadUi('ui/HomeScreen.ui', self)
        self.setWindowTitle('Главное меню')
        self.planets.clicked.connect(self.openPlanets)

    def openPlanets(self):
        self.close()
        self.open = Planets(self, self.data)
        self.open.show()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        pixmap = QtGui.QPixmap('img/background.jpg')
        painter.drawPixmap(self.rect(), pixmap)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('img/icon.ico'))
    ex = HomeScreen()
    ex.show()
    sys.exit(app.exec())
