from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor



def set_axes_labels(ax, xlabel=None, ylabel=None, title=None):
    """Set labels and remember them on the axis so update_figure() restores them after clearing."""
    labels = getattr(ax, '_iss_labels', {})
    for key, value in (('xlabel', xlabel), ('ylabel', ylabel), ('title', title)):
        if value is not None:
            labels[key] = value
    ax._iss_labels = labels
    apply_axes_labels(ax)


def apply_axes_labels(ax):
    labels = getattr(ax, '_iss_labels', None)
    if not labels:
        return
    if 'xlabel' in labels:
        ax.set_xlabel(labels['xlabel'])
    if 'ylabel' in labels:
        ax.set_ylabel(labels['ylabel'])
    if 'title' in labels:
        ax.set_title(labels['title'])


def channel_unit(channel_name):
    if channel_name.startswith('apb'):
        return 'mV'
    if channel_name.startswith('em_'):
        return 'V'
    return 'counts'


def detector_channel_label(channel, channel_den='1'):
    if channel_den in (None, '1', ''):
        return f'{channel}, {channel_unit(channel)}'
    return f'{channel} / {channel_den}, ratio'


def motor_egu(motor_dictionary, name=None, description=None):
    """Engineering unit of the motor whose ophyd name or description matches ('' if unknown)."""
    for motor_dict in (motor_dictionary or {}).values():
        obj = motor_dict.get('object')
        if (name is not None and obj is not None and obj.name == name) or \
           (description is not None and motor_dict.get('description') == description):
            try:
                return obj.egu or ''
            except Exception:
                return ''
    return ''


def with_unit(text, unit):
    return f'{text}, {unit}' if unit else text


def motor_label(motor_dictionary, name=None, description=None):
    """'<description>, <egu>' for the motor whose ophyd name or description matches; None if unknown."""
    for motor_dict in (motor_dictionary or {}).values():
        obj = motor_dict.get('object')
        if (name is not None and obj is not None and obj.name == name) or \
           (description is not None and motor_dict.get('description') == description):
            label = motor_dict.get('description') or name
            return with_unit(label, motor_egu(motor_dictionary, name=name, description=description))
    return None


def update_figure(axes, toolbar, canvas):
    start = 0
    step = -0.05
    for ax in axes:
        ax.clear()
        # cursor = Cursor(ax, useblit=True, color='green', linewidth=0.75)
    for i, ax in enumerate(axes):
        offset = start + i * step
        ax.spines['left'].set_position(('axes', offset))
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_label_position("left")
        ax.yaxis.tick_left()
        ax.tick_params(axis='y', rotation=90)
        apply_axes_labels(ax)
    axes[-1].spines['right'].set_visible(True)


    toolbar.update()
    canvas.draw_idle()
    axes[-1].grid(alpha=0.4)


def update_figure_with_colorbar(axes, toolbar, canvas,figure):
    if len(figure.axes) >1:
        figure.axes[-1].remove()
    for ax in axes:
        ax.clear()
        apply_axes_labels(ax)

    toolbar.update()
    canvas.draw_idle()
    axes[-1].grid(alpha=0.4)


def setup_figure(parent, layout):
    figure = Figure()
    figure.set_facecolor(color='#FcF9F6')
    canvas = FigureCanvas(figure)
    figure.ax = figure.add_subplot(111)
    toolbar = NavigationToolbar(canvas, parent, coordinates=True)
    layout.addWidget(toolbar)
    layout.addWidget(canvas)
    canvas.draw_idle()
    cursor = Cursor(figure.ax, useblit=True, color='green', linewidth=0.75)
    figure.ax.grid(alpha=0.4)
    #figure.tight_layout()

    return figure, canvas,toolbar



