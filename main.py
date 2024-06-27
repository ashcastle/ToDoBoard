import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QInputDialog, QPushButton, QLabel, QFormLayout, QDialog, QDialogButtonBox
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag, QIcon

class TodoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadTasks()

    def initUI(self):
        self.setWindowTitle('To Do Board')
        self.setGeometry(100, 100, 900, 400)

        mainLayout = QHBoxLayout()

        self.todoListWidget = self.createListWidget('계획')
        self.inProgressListWidget = self.createListWidget('진행 중')
        self.doneListWidget = self.createListWidget('완료')

        mainLayout.addLayout(self.createSection('계획', self.todoListWidget))
        mainLayout.addLayout(self.createSection('진행 중', self.inProgressListWidget))
        mainLayout.addLayout(self.createSectionWithTrash('완료', self.doneListWidget))

        self.setLayout(mainLayout)

    def createSection(self, title, listWidget):
        layout = QVBoxLayout()
        label = QLabel(title)
        addButton = QPushButton(f'{title} 할 일 추가')
        addButton.clicked.connect(lambda: self.addTask(listWidget))

        layout.addWidget(label)
        layout.addWidget(listWidget)
        layout.addWidget(addButton)

        return layout

    def createSectionWithTrash(self, title, listWidget):
        layout = QVBoxLayout()
        label = QLabel(title)
        addButton = QPushButton(f'{title} 할 일 추가')
        addButton.clicked.connect(lambda: self.addTask(listWidget))

        trashIcon = QLabel()
        trashIcon.setPixmap(QIcon.fromTheme("user-trash").pixmap(48, 48))
        trashIcon.setAcceptDrops(True)
        trashIcon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trashIcon.dragEnterEvent = self.dragEnterEvent
        trashIcon.dropEvent = self.trashDropEvent

        layout.addWidget(label)
        layout.addWidget(listWidget)
        layout.addWidget(addButton)
        layout.addWidget(trashIcon)

        return layout

    def createListWidget(self, label):
        listWidget = CustomListWidget()
        listWidget.setAcceptDrops(True)
        listWidget.setDragEnabled(True)
        listWidget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        listWidget.setObjectName(label)
        listWidget.itemDoubleClicked.connect(self.editTask)
        return listWidget

    def addTask(self, listWidget):
        text, ok = QInputDialog.getText(self, '할 일 추가', '할 일을 입력하세요:')
        if ok and text:
            item = QListWidgetItem(text)
            listWidget.addItem(item)
            self.saveTasks()

    def editTask(self, item):
        listWidget = item.listWidget()
        text, ok = QInputDialog.getText(self, '할 일 수정', '할 일을 수정하세요:', text=item.text())
        if ok and text:
            item.setText(text)
            self.saveTasks()

    def loadTasks(self):
        if os.path.exists('tasks.json'):
            try:
                with open('tasks.json', 'r') as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        self.populateListWidget(self.todoListWidget, data.get('todo', []))
                        self.populateListWidget(self.inProgressListWidget, data.get('inProgress', []))
                        self.populateListWidget(self.doneListWidget, data.get('done', []))
                    else:
                        self.initializeEmptyTasks()
            except json.JSONDecodeError:
                self.initializeEmptyTasks()
        else:
            self.initializeEmptyTasks()

    def initializeEmptyTasks(self):
        with open('tasks.json', 'w') as file:
            data = {'todo': [], 'inProgress': [], 'done': []}
            json.dump(data, file)

    def populateListWidget(self, listWidget, tasks):
        for task in tasks:
            item = QListWidgetItem(task)
            listWidget.addItem(item)

    def saveTasks(self):
        data = {
            'todo': self.getTasks(self.todoListWidget),
            'inProgress': self.getTasks(self.inProgressListWidget),
            'done': self.getTasks(self.doneListWidget)
        }
        with open('tasks.json', 'w') as file:
            json.dump(data, file)

    def getTasks(self, listWidget):
        return [listWidget.item(i).text() for i in range(listWidget.count())]

    def closeEvent(self, event):
        self.saveTasks()
        event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def trashDropEvent(self, event):
        if event.mimeData().hasText():
            source = event.source()
            if source:
                item = source.takeItem(source.currentRow())
                del item
                self.saveTasks()
            event.acceptProposedAction()

class CustomListWidget(QListWidget):
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            mimeData = QMimeData()
            mimeData.setText(item.text())

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            source = event.source()
            if source:
                item = source.takeItem(source.currentRow())
                self.addItem(item)
                parentWidget = self.parentWidget()
                if isinstance(parentWidget, TodoApp):
                    parentWidget.saveTasks()
            event.acceptProposedAction()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TodoApp()
    ex.show()
    sys.exit(app.exec())