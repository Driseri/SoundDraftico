# Точка входа в приложение
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    # Создаем экземпляр приложения Qt
    app = QApplication([])
    # Инициализируем и отображаем главное окно
    window = MainWindow()
    window.show()
    # Запускаем цикл обработки событий
    app.exec()
