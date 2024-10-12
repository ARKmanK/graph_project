import sys
import graphviz
import re


from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout
from des_widget import Ui_Form
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap


class DraggableLabel(QLabel):
    """
    Класс, отвечающий за распознование движения мыши, чтобы добавить возможность передвигать окно виджета, не использую стандартную "заголовочную панель" Windows.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset = None

    def mousePressEvent(self, event):
        self.offset = event.position()

    def mouseMoveEvent(self, event):
        if self.offset is not None:
            x = event.globalPosition().x()
            y = event.globalPosition().y()
            x_w = self.offset.x()
            y_w = self.offset.y()
            
            self.parent().move(int(x - x_w), int(y - y_w))


class Interface(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.ui.HeadLabel = DraggableLabel(self)        
        self.ui.HeadLabel.setGeometry(0, 0, 840, 50)

        self.ui.min_button.clicked.connect(self.minimize)
        self.ui.close_button.clicked.connect(self.close)
        self.ui.screenshot_button.clicked.connect(self.screenshot)
        self.ui.pushButton.clicked.connect(self.add_node)
        self.ui.pushButton_2.clicked.connect(self.open_connection_menu)
        #self.ui.pushButton_3.clicked.connect(self.add_node)
        self.ui.pushButton_4.clicked.connect(self.clear_graph)
        self.ui.pushButton_5.clicked.connect(self.open_change_name_menu)
        self.ui.pushButton_6.clicked.connect(self.change_node_name)
        self.ui.pushButton_7.clicked.connect(self.add_connection)

        #--------------------------------------------------------#
        self.dot = graphviz.Digraph(comment='Моя диаграмма')
        self.node_count = 0 
        #--------------------------------------------------------#


    def minimize(self):        

        self.setWindowState(Qt.WindowState.WindowMinimized)

    def screenshot(self):
        pass

    def notification(self, option=None):
        options_dict = {
            "screenshot": "Скриншот был добавлен в буфер обмена",
            "wipe": "Рабочая область очищена"
        }
        for key, val in options_dict.items():
            if option == key:
                self.ui.notification_frame.raise_()
                self.ui.plainTextEdit.setPlainText(val)                
                QTimer.singleShot(4000, self.ui.notification_frame.lower)

    def close_all_menus(self):
        self.ui.text_edit_menu.lower()
        self.ui.connection_menu.lower()

    def add_node(self):
        self.node_count += 1
        self.dot.node(str(self.node_count), f'Узел {self.node_count}')
        self.dot.render('graph', format='png')
        self.ui.work_label_1.setPixmap(QPixmap('graph.png'))

    def open_change_name_menu(self):
        self.close_all_menus()
        self.ui.text_edit_menu.raise_()
        node_names = self.get_nodes_names() 
        for node_name in node_names:
            self.ui.comboBox_4.addItem(node_name)

    def change_node_name(self):
        old_node_name = self.ui.comboBox_4.currentText()
        new_node_name = self.ui.textEdit.toPlainText()
        new_dot = graphviz.Digraph()
        for line in self.dot.body:
            new_dot.body.append(line)

        for i, line in enumerate(new_dot.body):
            match = re.search(r'\d+\s+\[label="{}"'.format(old_node_name), line)
            if match:
                new_line = line.replace(old_node_name, new_node_name)
                new_dot.body[i] = new_line

        new_dot.render('graph', format='png')
        self.ui.work_label_1.setPixmap(QPixmap('graph.png'))

    def get_nodes_names(self):
        body = self.dot.body
        node_names = []
        for line in body:
            match = re.search(r'\d+\s+\[label="(.*?)"\]', line)
            if match:
                node_name = match.group(1)
                node_names.append(node_name)
        return node_names

    def open_connection_menu(self):
        self.close_all_menus()
        self.ui.connection_menu.raise_()
        node_names = self.get_nodes_names()
        for node_name in node_names:
            self.ui.comboBox_2.addItem(node_name)
            self.ui.comboBox_3.addItem(node_name)

    def add_connection(self):
        node_1 = self.ui.comboBox_2.currentText()
        node_2 = self.ui.comboBox_3.currentText() 
        self.dot.edge(node_1, node_2)
        new_body = []
        for line in self.dot.body:
            if not (re.search(r'label="{}"'.format(node_1), line) or
                    re.search(r'label="{}"'.format(node_2), line)):
                new_body.append(line)
        self.dot.body = new_body
        self.dot.body = sorted(self.dot.body, key=lambda x: (int(re.search(r'\d+', x).group(0)), x))          
        self.dot.render('graph', format='png')
        self.ui.work_label_1.setPixmap(QPixmap('graph.png'))

    def clear_graph(self):
        self.dot.clear()
        self.ui.work_label_1.setPixmap(QPixmap())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = Interface()
    mywindow.show()
    sys.exit(app.exec())