import sys
import re
import os


from graphviz import Digraph
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QLabel
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
        self.ui.HeadLabel.setGeometry(0, 0, 1020, 50)

        self.ui.min_button.clicked.connect(self.minimize)
        self.ui.close_button.clicked.connect(self.close)
        self.ui.close_button_2.clicked.connect(self.close_all_menus)
        self.ui.close_button_3.clicked.connect(self.close_all_menus)
        self.ui.close_button_7.clicked.connect(self.close_all_menus)
        self.ui.close_button_8.clicked.connect(self.close_all_menus)
        self.ui.close_button_9.clicked.connect(self.close_all_menus)
        self.ui.pushButton.clicked.connect(self.add_node)
        self.ui.pushButton_2.clicked.connect(self.open_connection_menu)
        self.ui.pushButton_3.clicked.connect(self.open_add_distance_menu)
        self.ui.pushButton_4.clicked.connect(self.open_add_distance_to_target_menu)
        self.ui.pushButton_5.clicked.connect(self.open_change_color_menu)
        self.ui.pushButton_8.clicked.connect(self.open_change_name_menu)
        
        self.ui.pushButton_9.clicked.connect(self.clear_graph)        
        self.ui.pushButton_6.clicked.connect(self.change_node_name)
        self.ui.pushButton_7.clicked.connect(self.add_connection)
        self.ui.pushButton_16.clicked.connect(self.add_distance)
        self.ui.pushButton_17.clicked.connect(self.add_distance_to_target)
        self.ui.pushButton_15.clicked.connect(self.change_color_original)
        self.ui.pushButton_10.clicked.connect(self.open_file)
        
        self.ui.listWidget.itemSelectionChanged.connect(self.change_color_yellow)
        self.ui.listWidget_2.itemSelectionChanged.connect(self.change_color_green)
        self.ui.listWidget_3.itemSelectionChanged.connect(self.change_color_white)

        #--------------------------------------------------------#
        self.dot = Digraph(comment='Моя диаграмма')
        self.node_count = 0
        self.edge_count = 0
        self.colors_count = 0
        self.vertices = {}
        self.edges = {}
        self.colors = {}

        self.FILE_ADD = False
        self.CLEAR_GRAPH = False
        #--------------------------------------------------------#

    # Main methods--------------------------#
    def open_change_name_menu(self):
        self.close_all_menus()
        self.ui.text_edit_menu.raise_()        
        self.ui.comboBox_4.clear()
        node_names = self.get_nodes_names()
        for node_name in node_names:
            self.ui.comboBox_4.addItem(node_name)

    def open_connection_menu(self):
        self.close_all_menus()
        self.ui.connection_menu.raise_()        
        self.ui.comboBox_2.clear()
        self.ui.comboBox_3.clear()
        node_names = self.get_nodes_names()
        for node_name in node_names:
            self.ui.comboBox_2.addItem(node_name)
            self.ui.comboBox_3.addItem(node_name)

    def open_change_color_menu(self):
        self.close_all_menus()
        self.ui.change_color_menu.raise_()        
        self.ui.listWidget.clear()
        self.ui.listWidget_2.clear()
        self.ui.listWidget_3.clear()
        node_names = self.get_nodes_names()
        self.ui.listWidget.addItems(node_names)
        self.ui.listWidget_2.addItems(node_names)
        self.ui.listWidget_3.addItems(node_names)

    def open_add_distance_menu(self):
        self.close_all_menus()
        self.ui.add_distance_menu.raise_()        
        self.ui.comboBox_5.clear()
        self.ui.comboBox_6.clear()
        node_names = self.get_nodes_names()
        for node_name in node_names:
            self.ui.comboBox_5.addItem(node_name)
            self.ui.comboBox_6.addItem(node_name)

    def open_add_distance_to_target_menu(self):
        self.close_all_menus()
        self.ui.add_distance_to_target_menu.raise_()        
        self.ui.comboBox_7.clear()
        node_names = self.get_nodes_names()
        for node_name in node_names:
            self.ui.comboBox_7.addItem(node_name)

    def change_node_name(self):
        old_node_name = self.ui.comboBox_4.currentText()
        new_node_name = self.ui.textEdit.toPlainText()

        # Проверка на дубликат
        for key, val in self.vertices.items():
            if new_node_name == val[0]:
                self.notification("name exists")
                return
        for key, val in self.edges.items():
            if new_node_name == val[0] or new_node_name == val[1]:
                self.notification("name exists")
                return  
        for key, val in self.colors.items():
            if new_node_name == val[0] :
                self.notification("name exists")
                return

        # Замена имени на новое
        for key, val in self.vertices.items():
            if val[0] == old_node_name: 
                self.vertices[key] = [new_node_name]
        for key, val in self.edges.items():
            if val[0] == old_node_name:
                self.edges[key] = [new_node_name, val[1]]
            elif val[1] == old_node_name:
                self.edges[key] = [val[0], new_node_name]
        for key, val in self.colors.items():
            if val[0] == old_node_name:
                self.colors[key] = [new_node_name, val[1]]

        self.update_all_menus()
        self.render_and_show()

    def add_connection(self):
        self.edge_count += 1
        node_1 = self.ui.comboBox_2.currentText()
        node_2 = self.ui.comboBox_3.currentText() 
        self.edges[self.edge_count] = [node_1, node_2]

        self.vertices = {key: val for key, val in self.vertices.items() if val not in [node_1, node_2]}
        self.render_and_show()

    def change_color_yellow(self):
        self.colors_count += 1
        selected_item = self.ui.listWidget.selectedItems()
        if selected_item:
            node_name = selected_item[0].text()
            colors_copy = self.colors.copy()
            for key, val in colors_copy.items():
                if val[0] == node_name and (val[1] == "green" or val[1] == "white"):
                    del self.colors[key]
            else:
                self.colors[self.colors_count] = [node_name, "yellow"]
            self.vertices = {key: val for key, val in self.vertices.items() if val != node_name}                    
            self.colors = dict((key, val) for i, (key, val) in enumerate(self.colors.items()) if val not in list(self.colors.values())[:i])
            self.render_and_show()

    def change_color_green(self):
        self.colors_count += 1
        selected_item = self.ui.listWidget_2.selectedItems()
        if selected_item:
            node_name = selected_item[0].text()
            colors_copy = self.colors.copy()
            for key, val in colors_copy.items():
                if val[0] == node_name and (val[1] == "yellow" or val[1] == "white"):
                    del self.colors[key]
            else:
                self.colors[self.colors_count] = [node_name, "green"]
            self.vertices = {key: val for key, val in self.vertices.items() if val != node_name}                    
            self.colors = dict((key, val) for i, (key, val) in enumerate(self.colors.items()) if val not in list(self.colors.values())[:i])
            self.render_and_show()

    def change_color_white(self):
        self.colors_count += 1
        selected_item = self.ui.listWidget_3.selectedItems()
        if selected_item:
            node_name = selected_item[0].text()
            colors_copy = self.colors.copy()
            for key, val in colors_copy.items():
                if val[0] == node_name and (val[1] == "yellow" or val[1] == "green"):
                    del self.colors[key]
            else:
                self.colors[self.colors_count] = [node_name, "white"]
            self.vertices = {key: val for key, val in self.vertices.items() if val != node_name}                    
            self.colors = dict((key, val) for i, (key, val) in enumerate(self.colors.items()) if val not in list(self.colors.values())[:i])
            self.render_and_show()

    def change_color_original(self):
        for key, val in self.colors.items():
            if val[1] != "white":
                self.colors[key] = [val[0], "white"]                
        self.render_and_show()

    def add_distance(self):
        node_1 = self.ui.comboBox_5.currentText()
        node_2 = self.ui.comboBox_6.currentText() 
        length = self.ui.textEdit_2.toPlainText()

        for key, val in self.edges.items():
            if val[0] == node_1 and val[1] == node_2:
                self.edges[key] = [val[0], val[1], length]
                break
        else:
            self.notification("no edges")
            return
        self.render_and_show()

    def add_distance_to_target(self):
        node = self.ui.comboBox_7.currentText()
        length = self.ui.textEdit_3.toPlainText()
        
        for key, val in self.vertices.items():
            if val[0] == node:
                self.vertices[key] = [val[0], length]
                self.render_and_show()
                return
        for key, val in self.colors.items():
            if val[0] == node:
                self.colors[key] = [val[0], val[1], length]
                break

        self.render_and_show()

    def add_node(self):
        if self.CLEAR_GRAPH:
            self.notification("overwrite")
            self.CLEAR_GRAPH = False
            self.FILE_ADD = False
            return
        self.node_count += 1        
        self.vertices[self.node_count] = [f"Узел {self.node_count}"]
        self.render_and_show()
        self.update_all_menus()

    def open_file(self):
        try:
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть файл', '.', 'Все файлы (*)')
            if file_name:
                with open(file_name, 'r' , encoding='utf-8') as file:
                    content = file.read()
                    self.parse_content(content) 
            self.FILE_ADD = True
        except:
            self.notification("file error")

    def parse_content(self, content):
        lines = [line.strip().replace('\t', '').replace('"', '')
                for line in content.split('\n')[2:-1]]

        # Заполнение self.vertices
        for line in lines:
            if '->' not in line and line not in {'rankdir=LR', '}'} and 'fillcolor' not in line:
                if 'xlabel' in line:
                    node, number = line.split(' [xlabel=')[0].strip(), re.search(r'>\d+<', line).group(0).strip('><')
                    for key, val in self.vertices.items():
                        if val[0] == node:
                            self.vertices[key] = [node, number]
                            break
                    else:
                        self.vertices[self.node_count] = [node, number]
                        self.node_count += 1
                else:
                    node = line
                    if node not in (val[0] for val in self.vertices.values()):
                        self.vertices[self.node_count] = [node]
                        self.node_count += 1

        # Заполнение self.edges
        for line in lines:
            if '->' in line:
                node_1, node_2 = map(str.strip, line.split('->'))
                if '[' in node_2:
                    node_2, label = node_2.split('[')
                    label = label.replace(']', '').replace('label=', '').strip()
                    self.edges[self.edge_count] = [node_1, node_2.strip(), label]
                else:
                    self.edges[self.edge_count] = [node_1, node_2]
                self.edge_count += 1

        # Заполнение self.colors
        for line in lines:
            if '[' in line and '->' not in line:
                node, color_part = line.split('[')
                color = next(part.split('=')[1] for part in color_part.replace(']', '')
                            .split() if 'fillcolor' in part)
                self.colors[self.colors_count] = [node.strip(), color]
                self.colors_count += 1
        self.render_and_show()
    # Main methods--------------------------#

    # Support methods-----------------------#
    def get_nodes_names(self):
        node_names = set()
        for val in self.vertices.values():
            node_names.add(val[0])
        for val in self.edges.values():
            if len(val) == 2:
                node_names.update(val)
            elif len(val) == 3:
                node_names.update(val[:2])
        for val in self.colors.values():
            node_names.add(val[0])
        node_names = list(node_names)
        node_names.sort(key=lambda x: (not x.startswith("Узел "), int(re.search(r'\d+', x).group(0)) if re.search(r'\d+', x) else float('inf'), x))
        return node_names

    def clear_graph(self):
        if self.FILE_ADD:
            self.CLEAR_GRAPH = True
        self.dot.clear()
        self.node_count = 0
        self.edge_count = 0
        self.colors_count = 0
        self.vertices = {}
        self.edges = {}
        self.colors = {}
        self.ui.work_label_1.setPixmap(QPixmap())
        self.notification("wipe")
        self.close_all_menus()

    def render_and_show(self):
        self.dot.clear()

        for key, val in self.vertices.items():
            if len (val) == 1:
                self.dot.node(val[0])
            elif len(val) == 2:
                self.dot.node(val[0])
                self.dot.node(val[0], xlabel=f"<<font color=\"red\">{val[1]}</font>>")
        for edge in self.edges.values():
            if len(edge) == 2:
                self.dot.edge(edge[0], edge[1])
            elif len(edge) == 3:
                self.dot.edge(edge[0], edge[1], label=edge[2])
        for val in self.colors.values():
            if len(val) == 2:
                self.dot.node(val[0], style="filled", fillcolor=val[1])
            elif len(val) == 3:
                self.dot.node(val[0], style="filled", fillcolor=val[1])
                self.dot.node(val[0], xlabel=f"<<font color=\"red\">{val[2]}</font>>")

        self.dot.attr(rankdir='LR')
        self.dot.render('graph', format='png')
        self.ui.work_label_1.setPixmap(QPixmap('graph.png'))

    def delete_node(self, node_name=None):
        self.dot.body = [line for line in self.dot.body if f'label="{node_name}"' not in line]
        self.dot.body = sorted(self.dot.body, key=lambda x: x.split('"')[1] if '"' in x else x.split('[')[0])

    def update_all_menus(self):
        node_names = self.get_nodes_names()
        # Connection menu
        self.ui.comboBox_2.clear()
        self.ui.comboBox_3.clear()
        for node_name in node_names:
            self.ui.comboBox_2.addItem(node_name)
            self.ui.comboBox_3.addItem(node_name)
        # Color menu
        self.ui.listWidget.clear()
        self.ui.listWidget_2.clear()
        self.ui.listWidget.addItems(node_names)
        self.ui.listWidget_2.addItems(node_names)
        # Distance menu
        self.ui.comboBox_5.clear()
        self.ui.comboBox_6.clear()
        for node_name in node_names:
            self.ui.comboBox_5.addItem(node_name)
            self.ui.comboBox_6.addItem(node_name)
        # Name menu
        self.ui.comboBox_4.clear()
        for node_name in node_names:
            self.ui.comboBox_4.addItem(node_name)
        # Target distance menu
        self.ui.comboBox_7.clear()
        for node_name in node_names:
            self.ui.comboBox_7.addItem(node_name)

    def minimize(self):
        self.setWindowState(Qt.WindowState.WindowMinimized)

    def notification(self, option=None):
        options_dict = {
            "screenshot": "Скриншот был добавлен в буфер обмена",
            "wipe": "Рабочая область очищена",
            "name exists": "Данное имя уже существует",
            "no edges": "Вершины не соединены",
            "file error": "Открыт неподходящий",
            "overwrite": "Данное действие перезапишет файл, вы уверены?"
        }
        for key, val in options_dict.items():
            if option == key:
                self.ui.notification_frame.raise_()
                self.ui.plainTextEdit.setPlainText(val)                
                QTimer.singleShot(3000, self.ui.notification_frame.lower)

    def close_all_menus(self):
        self.ui.text_edit_menu.lower()
        self.ui.connection_menu.lower()
        self.ui.change_color_menu.lower()
        self.ui.add_distance_menu.lower()
        self.ui.add_distance_to_target_menu.lower()
    # Support methods-----------------------#


if __name__ == "__main__":
    os.environ["PATH"] += os.pathsep + "./Graphviz/bin"
    app = QApplication(sys.argv)
    mywindow = Interface()
    mywindow.show()
    sys.exit(app.exec())