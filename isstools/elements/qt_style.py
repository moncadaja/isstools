"""Application-wide look for the ISS Qt GUIs.

conda-forge's Qt6 ships no desktop theme plugin, so PyQt6 falls back to the
built-in *Fusion* style. Fusion 6 paints push buttons in the window colour
with a hair-line border, which makes a dense GUI like XLive look as if every
control were disabled. :func:`apply_iss_style` restores raised, clearly
bordered buttons and tabs while leaving per-widget stylesheets (status
indicators and the like) untouched.

Set ``ISS_QT_STYLESHEET=0`` in the environment to opt out.
"""
import os

from qtpy import QtWidgets

ISS_STYLESHEET = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fdfdfd, stop:1 #d4d4d4);
    border: 1px solid #7f7f7f;
    border-radius: 3px;
    padding: 1px 4px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #e2e2e2);
}
QPushButton:pressed, QPushButton:checked {
    background: #bcbcbc;
    border-color: #5a5a5a;
}
QPushButton:flat, QPushButton:flat:hover {
    /* flat buttons are invisible click targets (e.g. over the sample-stage coordinate picture) */
    background: transparent;
    border: none;
}
QPushButton:disabled {
    background: #ececec;
    color: #9c9c9c;
    border-color: #c6c6c6;
}
QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #e8e8e8);
    border: 1px solid #7f7f7f;
    border-bottom: none;
    padding: 4px 10px;
}
QTabBar::tab:!selected {
    background: #d0d0d0;
    border: 1px solid #9a9a9a;
    border-bottom: none;
    padding: 4px 10px;
    margin-top: 2px;
}
"""


def apply_iss_style(app=None, force=False):
    """Install the ISS stylesheet on ``app`` (default: the running QApplication).

    Only acts when the application uses the Fusion style (the Qt6 fallback)
    unless ``force`` is true; does nothing if ``ISS_QT_STYLESHEET=0``.
    Returns True when the stylesheet was applied.
    """
    if os.environ.get('ISS_QT_STYLESHEET', '1') == '0':
        return False
    app = app or QtWidgets.QApplication.instance()
    if app is None:
        return False
    if not force and app.style().objectName().lower() != 'fusion':
        return False
    if ISS_STYLESHEET.strip() in app.styleSheet():
        return True
    app.setStyleSheet(app.styleSheet() + ISS_STYLESHEET)
    return True
