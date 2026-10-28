"""Application-wide themes for the ISS Qt GUIs.

conda-forge's Qt6 ships no desktop theme plugin, so PyQt6 falls back to the
built-in *Fusion* style, whose default look makes a dense GUI like XLive read
as if every control were disabled. This module defines a few complete themes
(palette + stylesheet + matplotlib colours) on top of Fusion that can be
switched at runtime with :func:`apply_theme`.

Set ``ISS_QT_STYLESHEET=0`` in the environment to opt out of theming.
"""
import os

from qtpy import QtGui, QtWidgets

CLASSIC_STYLESHEET = """
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
ISS_STYLESHEET = CLASSIC_STYLESHEET

MODERN_STYLESHEET = """
QToolTip {
    background: %(surface2)s; color: %(text)s;
    border: 1px solid %(border)s; border-radius: 4px; padding: 3px;
}
QPushButton {
    background: %(surface)s; color: %(text)s;
    border: 1px solid %(border)s; border-radius: 4px; padding: 1px 6px;
}
QPushButton:hover { background: %(surface2)s; border-color: %(accent)s; }
QPushButton:pressed { background: %(accent_pressed)s; color: %(selection_text)s; border-color: %(accent_pressed)s; }
QPushButton:checked { background: %(accent)s; color: %(selection_text)s; border-color: %(accent)s; }
QPushButton:checked:hover { background: %(accent_hover)s; }
QPushButton:flat, QPushButton:flat:hover { background: transparent; border: none; }
QPushButton:disabled { background: %(bg)s; color: %(text_dim)s; border-color: %(border)s; }

QTabWidget::pane { border: 1px solid %(border)s; border-radius: 4px; top: -1px; }
QTabBar::tab {
    background: %(surface2)s; color: %(text_dim)s;
    border: 1px solid %(border)s; border-bottom: none;
    border-top-left-radius: 5px; border-top-right-radius: 5px;
    padding: 5px 12px; margin-right: 2px; margin-top: 3px;
}
QTabBar::tab:hover { color: %(text)s; }
QTabBar::tab:selected {
    background: %(bg)s; color: %(text)s;
    border-top: 2px solid %(accent)s; margin-top: 0px;
}

QLineEdit {
    background: %(base)s; color: %(text)s;
    border: 1px solid %(border)s; border-radius: 4px; padding: 1px 4px;
    selection-background-color: %(accent)s; selection-color: %(selection_text)s;
}
QLineEdit:focus { border-color: %(accent)s; }
QLineEdit:disabled { background: %(bg)s; color: %(text_dim)s; }
/* spin boxes and combo boxes stay Fusion-native (palette-coloured) so their arrows keep rendering;
   their inner line edits must not pick up the bordered QLineEdit look */
QAbstractSpinBox QLineEdit, QComboBox QLineEdit {
    border: none; border-radius: 0; padding: 0; background: transparent;
}
QComboBox QAbstractItemView {
    background: %(base)s; color: %(text)s; border: 1px solid %(border)s;
    selection-background-color: %(accent)s; selection-color: %(selection_text)s;
}

QTextEdit, QPlainTextEdit, QListView, QTreeView, QTableView {
    background: %(base)s; color: %(text)s;
    border: 1px solid %(border)s; border-radius: 4px;
    alternate-background-color: %(alt_base)s;
    selection-background-color: %(accent)s; selection-color: %(selection_text)s;
}
QTableView { gridline-color: %(border)s; }
QTableView QTableCornerButton::section { background: %(surface2)s; border: 1px solid %(border)s; }
QHeaderView::section {
    background: %(surface2)s; color: %(text)s;
    border: none; border-right: 1px solid %(border)s; border-bottom: 1px solid %(border)s;
    padding: 3px 6px;
}

QGroupBox {
    border: 1px solid %(border)s; border-radius: 6px;
    margin-top: 10px; padding-top: 4px;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    left: 10px; padding: 0 4px; color: %(text_dim)s;
}

QProgressBar {
    background: %(base)s; color: %(text)s;
    border: 1px solid %(border)s; border-radius: 4px; text-align: center;
}
QProgressBar::chunk { background: %(accent)s; border-radius: 3px; }

QSlider::groove:horizontal { height: 4px; background: %(surface2)s; border-radius: 2px; }
QSlider::handle:horizontal {
    width: 14px; margin: -5px 0; background: %(accent)s; border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: %(accent_hover)s; }
QSlider::groove:vertical { width: 4px; background: %(surface2)s; border-radius: 2px; }
QSlider::handle:vertical {
    height: 14px; margin: 0 -5px; background: %(accent)s; border-radius: 7px;
}

QScrollBar:vertical { background: transparent; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: %(border)s; min-height: 24px; border-radius: 5px; }
QScrollBar::handle:vertical:hover { background: %(text_dim)s; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: %(border)s; min-width: 24px; border-radius: 5px; }
QScrollBar::handle:horizontal:hover { background: %(text_dim)s; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }

QMenuBar { background: %(bg)s; color: %(text)s; }
QMenuBar::item:selected { background: %(surface2)s; border-radius: 4px; }
QMenu { background: %(surface)s; color: %(text)s; border: 1px solid %(border)s; padding: 4px; }
QMenu::item { padding: 4px 24px 4px 12px; border-radius: 3px; }
QMenu::item:selected { background: %(accent)s; color: %(selection_text)s; }
QMenu::separator { height: 1px; background: %(border)s; margin: 4px 8px; }

QSplitter::handle { background: %(border)s; }
QStatusBar { background: %(bg)s; color: %(text_dim)s; }
"""


class Theme:
    def __init__(self, name, qss, colors=None, mpl=None):
        self.name = name
        self.colors = colors
        self.qss = qss % colors if colors else qss
        # figure background, axes background, text/tick colour, spine colour, grid colour
        self.mpl = mpl or ('white', 'white', 'black', 'black', '#b0b0b0')

    def palette(self):
        if self.colors is None:
            return QtWidgets.QStyleFactory.create('Fusion').standardPalette()
        c = {k: QtGui.QColor(v) for k, v in self.colors.items()}
        p = QtGui.QPalette()
        for role, color in [
            (QtGui.QPalette.Window, c['bg']),
            (QtGui.QPalette.WindowText, c['text']),
            (QtGui.QPalette.Base, c['base']),
            (QtGui.QPalette.AlternateBase, c['alt_base']),
            (QtGui.QPalette.ToolTipBase, c['surface2']),
            (QtGui.QPalette.ToolTipText, c['text']),
            (QtGui.QPalette.Text, c['text']),
            (QtGui.QPalette.Button, c['surface']),
            (QtGui.QPalette.ButtonText, c['text']),
            (QtGui.QPalette.BrightText, QtGui.QColor('#ff5555')),
            (QtGui.QPalette.Highlight, c['accent']),
            (QtGui.QPalette.HighlightedText, c['selection_text']),
            (QtGui.QPalette.Link, c['accent']),
            (QtGui.QPalette.PlaceholderText, c['text_dim']),
            (QtGui.QPalette.Light, c['surface2']),
            (QtGui.QPalette.Midlight, c['surface']),
            (QtGui.QPalette.Mid, c['border']),
            (QtGui.QPalette.Dark, c['shadow']),
            (QtGui.QPalette.Shadow, c['shadow']),
        ]:
            p.setColor(role, color)
        for role in (QtGui.QPalette.Text, QtGui.QPalette.ButtonText, QtGui.QPalette.WindowText):
            p.setColor(QtGui.QPalette.Disabled, role, c['text_dim'])
        p.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, c['border'])
        return p


_LIGHT = dict(bg='#f3f4f6', surface='#ffffff', surface2='#e9ebef', border='#c6cbd3',
              text='#1f2328', text_dim='#6b7280', base='#ffffff', alt_base='#f7f8fa',
              accent='#2563eb', accent_hover='#3b82f6', accent_pressed='#1d4ed8',
              selection_text='#ffffff', shadow='#9ca3af')
_DARK = dict(bg='#2b2d30', surface='#3a3d41', surface2='#45494e', border='#5a5f66',
             text='#e8eaed', text_dim='#9aa0a6', base='#1f2023', alt_base='#26282b',
             accent='#4f8cff', accent_hover='#6ea0ff', accent_pressed='#3b74e0',
             selection_text='#ffffff', shadow='#17181a')
_NORD = dict(bg='#2e3440', surface='#3b4252', surface2='#434c5e', border='#4c566a',
             text='#eceff4', text_dim='#a3adc2', base='#272c36', alt_base='#2e3440',
             accent='#88c0d0', accent_hover='#8fbcbb', accent_pressed='#81a1c1',
             selection_text='#2e3440', shadow='#20242c')

THEMES = {
    'Classic': Theme('Classic', CLASSIC_STYLESHEET),
    'Modern Light': Theme('Modern Light', MODERN_STYLESHEET, _LIGHT,
                          mpl=(_LIGHT['bg'], '#ffffff', _LIGHT['text'], _LIGHT['text_dim'], _LIGHT['border'])),
    'Modern Dark': Theme('Modern Dark', MODERN_STYLESHEET, _DARK,
                         mpl=(_DARK['bg'], _DARK['base'], _DARK['text'], _DARK['text_dim'], _DARK['border'])),
    'Nord': Theme('Nord', MODERN_STYLESHEET, _NORD,
                  mpl=(_NORD['bg'], _NORD['base'], _NORD['text'], _NORD['text_dim'], _NORD['border'])),
}
DEFAULT_THEME = 'Modern Light'


def _restyle_matplotlib(theme, app):
    import matplotlib
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

    fig_bg, ax_bg, text, spine, grid = theme.mpl
    matplotlib.rcParams.update({
        'figure.facecolor': fig_bg, 'axes.facecolor': ax_bg, 'axes.edgecolor': spine,
        'axes.labelcolor': text, 'xtick.color': text, 'ytick.color': text, 'text.color': text,
        'grid.color': grid, 'legend.facecolor': ax_bg, 'legend.edgecolor': spine,
    })
    for widget in app.allWidgets():
        if not isinstance(widget, FigureCanvasQTAgg):
            continue
        fig = widget.figure
        fig.set_facecolor(fig_bg)
        for ax in fig.axes:
            ax.set_facecolor(ax_bg)
            ax.tick_params(colors=text, which='both')
            for sp in ax.spines.values():
                sp.set_edgecolor(spine)
            ax.xaxis.label.set_color(text)
            ax.yaxis.label.set_color(text)
            ax.title.set_color(text)
            legend = ax.get_legend()
            if legend is not None:
                legend.get_frame().set_facecolor(ax_bg)
                legend.get_frame().set_edgecolor(spine)
                for t in legend.get_texts():
                    t.set_color(text)
        widget.draw_idle()


def apply_theme(name, app=None):
    """Switch the running QApplication to the named theme (see ``THEMES``).

    Does nothing and returns False if ``ISS_QT_STYLESHEET=0`` or no
    QApplication exists.
    """
    if os.environ.get('ISS_QT_STYLESHEET', '1') == '0':
        return False
    app = app or QtWidgets.QApplication.instance()
    if app is None:
        return False
    theme = THEMES[name]
    app.setStyle('Fusion')
    app.setPalette(theme.palette())
    app.setStyleSheet(theme.qss)
    _restyle_matplotlib(theme, app)
    return True


def apply_iss_style(app=None, force=False):
    """Backwards-compatible entry point: apply the Classic theme."""
    return apply_theme('Classic', app)
