from PySide6 import QtWidgets, QtCore
from new4test import Ui_MainWindow as form_class


class Pantalla(QtWidgets.QMainWindow, form_class):
    """
    Clase básica que carga la interfaz generada por QtDesigner.
    Utiliza herencia múltiple para extender QMainWindow [7], [8].
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    # 1. Instanciar los componentes [25]
    pantalla = Pantalla()

    # 2. Conectarlos mediante el Presenter (Agregación) [26], [20]


    pantalla.show()
    sys.exit(app.exec())
