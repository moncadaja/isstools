from qtpy import uic, QtGui, QtCore
import importlib.resources

ui_path = str(importlib.resources.files('isstools') / 'dialogs/GetEmailAddress.ui')

class GetEmailAddress(*uic.loadUiType(ui_path)):

    def __init__(self, offset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('Email address')
        self.lineEdit.setText('{}'.format(offset))

    def getValue(self):
        return self.lineEdit.text()
