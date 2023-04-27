import sqlite3
import sys

from PyQt5 import QtGui, QtWidgets, uic, QtCore


class HomeScreen(QtWidgets.QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui/HomeScreen.ui', self)
        self.setWindowTitle('Главное меню')

        self.planets.clicked.connect(self.openPlanetsList)
        # self.planets.clicked.connect(self.openPlanetsList)

    def openPlanetsList(self):
        self.close()
        self.open = PlanetsList(self, None)
        self.open.show()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        pixmap = QtGui.QPixmap('img/background.jpg')
        painter.drawPixmap(self.rect(), pixmap)


class PlanetsList(QtWidgets.QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi("ui/PlanetsList.ui", self)
        self.setWindowTitle('Список планет')

        self.addButton.clicked.connect(self.addPlanet)
        self.updateButton.clicked.connect(self.updatePlanet)
        self.deleteButton.clicked.connect(self.deletePlanet)
        self.submitButton.clicked.connect(self.updatePlanet)
        self.backButton.clicked.connect(self.back)

        self.updateResults()

    def addPlanet(self):
        self.close()
        self.open = AddPlanet(self)
        self.open.show()

    def updatePlanet(self):
        if len(self.result) > 0:
            number, ok_pressed = QInputDialog.getInt(
                self, "Введите номер планеты", "Введите номер планеты, которую хотите изменить",
                1, 1, len(self.result), 1)
            if ok_pressed:
                self.close()
                self.open = updatePlanet(self, (self.data, self.search.text(), self.abc.currentText(), number))
                self.open.show()

    def deletePlanet(self):
        if len(self.result) > 0:
            number, ok_pressed = QInputDialog.getInt(
                self, "Введите номер планеты", "Введите номер планеты, которую хотите удалить",
                1, 1, len(self.result), 1)
            if ok_pressed:
                con = sqlite3.connect('solar_system_planets.db')
                cur = con.cursor()
                cur.execute(f"""DELETE FROM features  WHERE id = {self.result[number - 1][0]}""")
                con.commit()
                con.close()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setBrush(QtCore.Qt.green)
        painter.drawRect(self.rect())

    def updateResults(self):
        con = sqlite3.connect('solar_system_planets.db')
        cur = con.cursor()

        if self.searchWidget.text() != '' and self.search.text() != 'Ничего не найдено':
            self.result = cur.execute(f"""SELECT * FROM planets WHERE name like '{self.searchWidget.text().strip().capitalize()}%'""").fetchall()
        else:
            self.result = cur.execute(f"""SELECT * FROM planets WHERE name like '{self.alphabesearchWidge.currentText()}%'""").fetchall()
        con.close()

        if len(self.result) == 0:
            self.searchWidget.setText('Ничего не найдено')
        else:
            self.searchWidget.setText('')

    def back(self):
        self.close()
        self.open = HomeScreen(self, None)
        self.open.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('img/icon.ico'))
    ex = HomeScreen()
    ex.show()
    sys.exit(app.exec())
