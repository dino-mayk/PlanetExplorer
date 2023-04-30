import sqlite3
import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic


class HomeScreen(QtWidgets.QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui/HomeScreen.ui', self)
        self.setWindowTitle('Главное меню')

        self.planets.clicked.connect(self.openPlanetsList)
        self.satellites.clicked.connect(self.openSatellitesList)

    def openPlanetsList(self):
        self.close()
        self.open = PlanetsList(self, None)
        self.open.show()

    def openSatellitesList(self):
        self.close()
        self.open = SatellitesList(self, None)
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
        self.submitButton.clicked.connect(self.updateResults)
        self.backButton.clicked.connect(self.back)

        self.updateResults()

    def addPlanet(self):
        self.close()
        self.open = AddPlanet(self, None)
        self.open.show()

    def updatePlanet(self):
        if len(self.result) > 0:
            number, ok_pressed = QtWidgets.QInputDialog.getInt(
                self, "Введите номер строки планеты", "Введите номер строки планеты, которую хотите изменить",
                1, 1, len(self.result), 1)
            if ok_pressed:
                self.close()
                self.open = UpdatePlanet(self, self.result[number - 1][1])
                self.open.show()

    def deletePlanet(self):
        if len(self.result) > 0:
            number, ok_pressed = QtWidgets.QInputDialog.getInt(
                self,
                "Введите номер строки планеты",
                "Введите номер строки планеты, которую хотите удалить",
                1,
                1,
                len(self.result),
                1,
            )

            if ok_pressed:
                try:
                    con = sqlite3.connect('solar_system_planets.db')
                    cur = con.cursor()
                    cur.execute(f"""DELETE FROM features WHERE id = {self.result[number - 1][1]}""")
                    cur.execute(f"""DELETE FROM planets WHERE id = {self.result[number - 1][1]}""")
                    cur.execute(f"""DELETE FROM satellites WHERE planet_id = {self.result[number - 1][1]}""")
                    con.commit()
                    con.close()
                    self.updateResults()
                except Exception:
                    pass

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setBrush(QtCore.Qt.blue)
        painter.drawRect(self.rect())

    def updateResults(self):
        con = sqlite3.connect('solar_system_planets.db')
        cur = con.cursor()

        if self.searchWidget.text() != '' and self.searchWidget.text() != 'Ничего не найдено':
            self.planets = cur.execute(f"""SELECT * FROM planets WHERE name like '{self.searchWidget.text().strip().capitalize()}%'""").fetchall()
        else:
            self.planets = cur.execute(f"""SELECT * FROM planets WHERE name like '{self.alphabesearchWidget.currentText()}%'""").fetchall()

        self.result = []

        for planet in self.planets:
            id = planet[0]
            name = planet[1]

            self.feature = cur.execute(
                f"""SELECT * FROM features WHERE id = {id}"""
            ).fetchone()
            self.result.append((name, *self.feature))

        con.close()

        if len(self.result) == 0:
            self.searchWidget.setText('Ничего не найдено')
            self.tableWidget.setColumnCount(0)
            self.tableWidget.setRowCount(0)

        else:
            self.searchWidget.setText('')
            self.tableWidget.setRowCount(len(self.result))
            self.tableWidget.setColumnCount(len(self.result[0]))
            self.tableWidget.setHorizontalHeaderLabels(
                [
                    'Название',
                    'Id',
                    'Номер планеты',
                    'Масса',
                    'Диаметр',
                    'Плотность',
                    'Гравитация',
                    'Скорость убегания',
                    'День',
                    'Перигелий',
                    'Афелий',
                    'Период',
                    'Скорость орбиты',
                    'Наклон',
                    'Температура',
                    'Давление',
                    'Магнитный(1-да, 0-нет)',
                    'Атмосфера',
                ]
            )
            self.tableWidget.verticalHeader().setDefaultSectionSize(50)
            self.tableWidget.verticalHeader().setMaximumSectionSize(50)
            self.tableWidget.verticalHeader().setMinimumSectionSize(50)

            self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
            self.tableWidget.horizontalHeader().setMaximumSectionSize(200)
            self.tableWidget.horizontalHeader().setMinimumSectionSize(100)
            for i, elem in enumerate(self.result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))
            self.tableWidget.resizeColumnsToContents()

    def back(self):
        self.close()
        self.open = HomeScreen(self, None)
        self.open.show()


class AddPlanet(QtWidgets.QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui/addOrUpdatePlanet.ui', self)
        self.setWindowTitle('Добавление новой планеты')
        self.setFixedSize(350, 570)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        self.backButton.clicked.connect(self.back)
        self.submitButton.clicked.connect(self.add)

        self.error = QtWidgets.QStatusBar(self)
        self.error.move(0, 550)
        self.error.resize(500, 20)

    def add(self):
        con = sqlite3.connect('solar_system_planets.db')
        cur = con.cursor()

        id = int(cur.execute("""SELECT id FROM features""").fetchall()[-1][0]) + 1

        try:
            cur.execute(f"""INSERT INTO features(id, planet_id, mass, diameter, density, gravity, escape_v, day, perihelion, aphelion, o_period, orbital_v, tilt, temperature, pressure, magnetic, atmosphere) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (id, id, self.massLineEdit.text(), self.diameterLineEdit.text(), self.densityLineEdit.text(), self.gravityLineEdit.text(), self.escape_vLineEdit.text(), self.dayLineEdit.text(), self.perihelionLineEdit.text(), self.aphelionLineEdit.text(), self.o_periodLineEdit.text(), self.orbital_vLineEdit.text(), self.tiltLineEdit.text(), self.temperatureLineEdit.text(), self.pressureLineEdit.text(), self.magneticcheckBox.isChecked(), self.atmosphereLineEdit.text(), ))
            cur.execute(f"""INSERT INTO planets(id, name) VALUES(?, ?)""", (id, self.nameLineEdit.text()))
            con.commit()
            con.close()
            self.back()
        except Exception:
            self.error.setStyleSheet(
                "QStatusBar{padding-left:8px;background:rgb(255,0,0);color:black;font-weight:bold;}"
            )
            self.error.showMessage('Вы ввели некорректные данные')

    def back(self):
        self.close()
        self.open = PlanetsList(self, None)
        self.open.show()


class UpdatePlanet(QtWidgets.QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

        self.id = args[-1]

    def initUI(self):
        uic.loadUi('ui/addOrUpdatePlanet.ui', self)
        self.setWindowTitle('Изменение планеты')
        self.setFixedSize(350, 570)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        self.backButton.clicked.connect(self.back)
        self.submitButton.clicked.connect(self.update)

        self.error = QtWidgets.QStatusBar(self)
        self.error.move(0, 550)
        self.error.resize(500, 20)

    def update(self):
        try:
            con = sqlite3.connect('solar_system_planets.db')
            cur = con.cursor()

            cur.execute("""UPDATE features SET id=?, planet_id=?, mass=?, diameter=?, density=?, gravity=?, escape_v=?, day=?, perihelion=?, aphelion=?, o_period=?, orbital_v=?, tilt=?, temperature=?, pressure=?, magnetic=?, atmosphere=? WHERE id=?""", (self.id, self.id, self.massLineEdit.text(), self.diameterLineEdit.text(), self.densityLineEdit.text(), self.gravityLineEdit.text(), self.escape_vLineEdit.text(), self.dayLineEdit.text(), self.perihelionLineEdit.text(), self.aphelionLineEdit.text(), self.o_periodLineEdit.text(), self.orbital_vLineEdit.text(), self.tiltLineEdit.text(), self.temperatureLineEdit.text(), self.pressureLineEdit.text(), self.magneticcheckBox.isChecked(), self.atmosphereLineEdit.text(), self.id))
            cur.execute(f"""UPDATE planets SET name=? WHERE id=?""", (self.nameLineEdit.text(), self.id, ))

            con.commit()
            con.close()
            self.back()

        except Exception:
            self.error.setStyleSheet("QStatusBar{padding-left:8px;background:rgb(255,0,0);color:black;font-weight:bold;}")
            self.error.showMessage('Вы ввели некорректные данные')

    def back(self):
        self.close()
        self.open = PlanetsList(self, None)
        self.open.show()


class SatellitesList(QtWidgets.QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi("ui/SatellitesList.ui", self)
        self.setWindowTitle('Список спутников')

        self.addButton.clicked.connect(self.addSatellite)
        self.updateButton.clicked.connect(self.updateSatellite)
        self.deleteButton.clicked.connect(self.deleteSatellite)
        self.submitButton.clicked.connect(self.updateResults)
        self.backButton.clicked.connect(self.back)

        self.updateResults()

    def addSatellite(self):
        self.close()
        self.open = AddPlanet(self, None)
        self.open.show()

    def updateSatellite(self):
        if len(self.result) > 0:
            number, ok_pressed = QtWidgets.QInputDialog.getInt(
                self, "Введите номер строки планеты", "Введите номер строки планеты, которую хотите изменить",
                1, 1, len(self.result), 1)
            if ok_pressed:
                self.close()
                self.open = UpdatePlanet(self, self.result[number - 1][1])
                self.open.show()

    def deleteSatellite(self):
        if len(self.result) > 0:
            number, ok_pressed = QtWidgets.QInputDialog.getInt(
                self,
                "Введите номер строки планеты",
                "Введите номер строки планеты, которую хотите удалить",
                1,
                1,
                len(self.result),
                1,
            )

            if ok_pressed:
                try:
                    con = sqlite3.connect('solar_system_planets.db')
                    cur = con.cursor()
                    cur.execute(f"""DELETE FROM features WHERE id = {self.result[number - 1][1]}""")
                    cur.execute(f"""DELETE FROM planets WHERE id = {self.result[number - 1][1]}""")
                    cur.execute(f"""DELETE FROM satellites WHERE planet_id = {self.result[number - 1][1]}""")
                    con.commit()
                    con.close()
                    self.updateResults()
                except Exception:
                    pass

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setBrush(QtCore.Qt.blue)
        painter.drawRect(self.rect())

    def updateResults(self):
        con = sqlite3.connect('solar_system_planets.db')
        cur = con.cursor()

        if self.searchWidget.text() != '' and self.searchWidget.text() != 'Ничего не найдено':
            self.result = cur.execute(f"""SELECT * FROM satellites WHERE name like '{self.searchWidget.text().strip().capitalize()}%'""").fetchall()
        else:
            self.result = cur.execute(f"""SELECT * FROM satellites WHERE name like '{self.alphabesearchWidget.currentText()}%'""").fetchall()

        con.close()

        if len(self.result) == 0:
            self.searchWidget.setText('Ничего не найдено')
            self.tableWidget.setColumnCount(0)
            self.tableWidget.setRowCount(0)

        else:
            self.searchWidget.setText('')
            self.tableWidget.setRowCount(len(self.result))
            self.tableWidget.setColumnCount(len(self.result[0]))
            self.tableWidget.setHorizontalHeaderLabels(['Id', 'Название'])
            self.tableWidget.verticalHeader().setDefaultSectionSize(50)
            self.tableWidget.verticalHeader().setMaximumSectionSize(50)
            self.tableWidget.verticalHeader().setMinimumSectionSize(50)

            self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
            self.tableWidget.horizontalHeader().setMaximumSectionSize(200)
            self.tableWidget.horizontalHeader().setMinimumSectionSize(100)
            for i, elem in enumerate(self.result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))
            self.tableWidget.resizeColumnsToContents()

    def back(self):
        self.close()
        self.open = HomeScreen(self, None)
        self.open.show()


"""class AddSatellite(QtWidgets.QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui/addOrUpdatePlanet.ui', self)
        self.setWindowTitle('Добавление новой планеты')
        self.setFixedSize(350, 570)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        self.backButton.clicked.connect(self.back)
        self.submitButton.clicked.connect(self.add)

        self.error = QtWidgets.QStatusBar(self)
        self.error.move(0, 550)
        self.error.resize(500, 20)

    def add(self):
        con = sqlite3.connect('solar_system_planets.db')
        cur = con.cursor()

        id = int(cur.execute("""SELECT id FROM features""").fetchall()[-1][0]) + 1

        try:
            cur.execute(f"""INSERT INTO features(id, planet_id, mass, diameter, density, gravity, escape_v, day, perihelion, aphelion, o_period, orbital_v, tilt, temperature, pressure, magnetic, atmosphere) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (id, id, self.massLineEdit.text(), self.diameterLineEdit.text(), self.densityLineEdit.text(), self.gravityLineEdit.text(), self.escape_vLineEdit.text(), self.dayLineEdit.text(), self.perihelionLineEdit.text(), self.aphelionLineEdit.text(), self.o_periodLineEdit.text(), self.orbital_vLineEdit.text(), self.tiltLineEdit.text(), self.temperatureLineEdit.text(), self.pressureLineEdit.text(), self.magneticcheckBox.isChecked(), self.atmosphereLineEdit.text(), ))
            cur.execute(f"""INSERT INTO planets(id, name) VALUES(?, ?)""", (id, self.nameLineEdit.text()))
            con.commit()
            con.close()
            self.back()
        except Exception:
            self.error.setStyleSheet(
                "QStatusBar{padding-left:8px;background:rgb(255,0,0);color:black;font-weight:bold;}"
            )
            self.error.showMessage('Вы ввели некорректные данные')

    def back(self):
        self.close()
        self.open = PlanetsList(self, None)
        self.open.show()


class UpdateSatellite(QtWidgets.QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

        self.id = args[-1]

    def initUI(self):
        uic.loadUi('ui/addOrUpdatePlanet.ui', self)
        self.setWindowTitle('Изменение планеты')
        self.setFixedSize(350, 570)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        self.backButton.clicked.connect(self.back)
        self.submitButton.clicked.connect(self.update)

        self.error = QtWidgets.QStatusBar(self)
        self.error.move(0, 550)
        self.error.resize(500, 20)

    def update(self):
        try:
            con = sqlite3.connect('solar_system_planets.db')
            cur = con.cursor()

            cur.execute("""UPDATE features SET id=?, planet_id=?, mass=?, diameter=?, density=?, gravity=?, escape_v=?, day=?, perihelion=?, aphelion=?, o_period=?, orbital_v=?, tilt=?, temperature=?, pressure=?, magnetic=?, atmosphere=? WHERE id=?""", (self.id, self.id, self.massLineEdit.text(), self.diameterLineEdit.text(), self.densityLineEdit.text(), self.gravityLineEdit.text(), self.escape_vLineEdit.text(), self.dayLineEdit.text(), self.perihelionLineEdit.text(), self.aphelionLineEdit.text(), self.o_periodLineEdit.text(), self.orbital_vLineEdit.text(), self.tiltLineEdit.text(), self.temperatureLineEdit.text(), self.pressureLineEdit.text(), self.magneticcheckBox.isChecked(), self.atmosphereLineEdit.text(), self.id))
            cur.execute(f"""UPDATE planets SET name=? WHERE id=?""", (self.nameLineEdit.text(), self.id, ))

            con.commit()
            con.close()
            self.back()

        except Exception:
            self.error.setStyleSheet("QStatusBar{padding-left:8px;background:rgb(255,0,0);color:black;font-weight:bold;}")
            self.error.showMessage('Вы ввели некорректные данные')

    def back(self):
        self.close()
        self.open = PlanetsList(self, None)
        self.open.show()"""


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('img/icon.ico'))
    ex = HomeScreen()
    ex.show()
    sys.exit(app.exec())
