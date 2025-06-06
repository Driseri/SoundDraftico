# Точка входа в приложение
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow

if __name__ == "__main__":
    # Создаем экземпляр приложения Qt
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication([])
    app.setFont(QFont("Segoe UI Variable", 10))
    # Инициализируем и отображаем главное окно
    window = MainWindow()
    window.show()
    # Запускаем цикл обработки событий
    app.exec()
