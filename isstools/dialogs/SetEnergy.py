from qtpy import uic, QtGui, QtCore
import importlib.resources

ui_path = str(importlib.resources.files('isstools') / 'dialogs/SetEnergy.ui')

class SetEnergy(*uic.loadUiType(ui_path)):

    def __init__(self, offset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('Set energy')
        self.lineEdit.setText('{}'.format(offset))

    def getValues(self):
        return self.lineEdit.text()
