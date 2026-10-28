import json

import importlib.resources
from qtpy import uic
from xraydb import xray_line

from isstools.dialogs.PeriodicTable import PeriodicTableWidget
from isstools.elements.elements import elements_lines_dict, get_spectrometer_line_dict

ui_path = str(importlib.resources.files('isstools') / 'ui/ui_energy_selector_with_periodic_table.ui')
ui_path_emission = str(importlib.resources.files('isstools') / 'ui/ui_emission_line_selector_with_periodic_table.ui')


def _select_combo_text(combo, text):
    index = combo.findText(text)
    if index >= 0:
        combo.setCurrentIndex(index)
    return index >= 0


class UIEnergySelectorWithPeriodicTable(*uic.loadUiType(ui_path)):
    """Element button (opens the periodic table) + edge/line combo + E0 field.

    ``emission=True`` offers fluorescence lines instead of absorption edges.
    Read ``element`` / ``edge`` / ``e0``; set programmatically with ``set_values``.
    """

    def __init__(self, emission=None, default_element='Ti', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        if emission:
            json_name = 'fluorescence_lines.json'
            self.label_edge_line.setText('Line')
        else:
            json_name = 'absorption_edges2.json'
            self.label_edge_line.setText('Edge')
        with open(str(importlib.resources.files('isstools') / json_name)) as fp:
            self.elements_data = json.load(fp)
        self.accessible_elements = [item['symbol'] for item in self.elements_data]

        self.pushButton_element.pressed.connect(self.show_periodic_table)
        self.comboBox_edge.currentIndexChanged.connect(self.update_e0_value)
        self.set_element(default_element)

    @property
    def element(self):
        return self.pushButton_element.text()

    @property
    def edge(self):
        return self.comboBox_edge.currentText()

    @property
    def e0(self):
        return float(self.edit_E0.text())

    def get_energy_list(self, symbol):
        for item in self.elements_data:
            if item['symbol'] == symbol:
                return {k: v for k, v in item.items() if k not in ('symbol', 'name')}
        return {}

    def update_combo_edge(self, symbol):
        self.energy_dict = self.get_energy_list(symbol)
        self.comboBox_edge.clear()
        self.comboBox_edge.addItems(self.energy_dict.keys())

    def update_e0_value(self):
        energy = self.energy_dict.get(self.comboBox_edge.currentText())
        if energy is not None:
            self.edit_E0.setText(str(int(energy)))

    def show_periodic_table(self):
        self.periodic_table_window = PeriodicTableWidget(accessible_elements=self.accessible_elements)
        self.periodic_table_window.element_selected.connect(self.set_element)
        self.periodic_table_window.show()

    def set_element(self, symbol):
        self.pushButton_element.setText(symbol)
        self.update_combo_edge(symbol)

    set_element_from_table = set_element

    def set_edge(self, edge):
        return _select_combo_text(self.comboBox_edge, edge)

    def set_values(self, element, edge, e0):
        """Populate from stored scan parameters; E0 is kept verbatim even if the edge is unknown."""
        self.set_element(element)
        if not self.set_edge(edge):
            self.comboBox_edge.setCurrentIndex(-1)
        self.edit_E0.setText(str(int(e0)))


def emission_lines_from_xraydb():
    """{element: [(line, energy_eV), ...]} for the lines ISS uses in emission scans."""
    return {element: [(line, xray_line(element, line).energy) for line in sorted(lines)]
            for element, lines in elements_lines_dict.items()}


def emission_lines_from_spectrometer_table(emin=4500, emax=30000):
    """{element: [(line_or_edge, energy_eV), ...]} from fluorescence_lines2.json within the energy window."""
    df = get_spectrometer_line_dict()
    elements = df[(df.energy > emin) & (df.energy < emax)].element.unique().tolist()
    table = {}
    for element in elements:
        rows = df[df.element == element]
        table[element] = list(zip(rows.symbol.tolist(), rows.energy.tolist()))
    return table


class UIEmissionLineSelectorWithPeriodicTable(*uic.loadUiType(ui_path_emission)):
    """Element button (periodic table) + emission line combo + energy field.

    ``line_table`` maps element -> [(line, energy_eV), ...] and defines both
    the selectable elements and the line names. When ``settings`` (a QSettings)
    is given, the choice is remembered under ``<settings_prefix>_*`` keys.
    Read ``element`` / ``line`` / ``energy``; set programmatically with ``set_values``.
    """

    def __init__(self, line_table, settings=None, settings_prefix='johann_emission',
                 default_element='Fe', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.line_table = line_table
        self.accessible_elements = list(line_table.keys())
        self.settings = settings
        self.settings_prefix = settings_prefix

        element = default_element if default_element in line_table else self.accessible_elements[0]
        line = None
        if settings is not None:
            saved_element = settings.value(f'{settings_prefix}_element_symbol', defaultValue='', type=str)
            if saved_element in line_table:
                element = saved_element
                line = settings.value(f'{settings_prefix}_line_symbol', defaultValue='', type=str)

        self.pushButton_element.pressed.connect(self.show_periodic_table)
        self.set_element(element)
        if line:
            self.set_line(line)
        self.comboBox_line.currentIndexChanged.connect(self.update_e_value)
        self.update_e_value()

    @property
    def element(self):
        return self.pushButton_element.text()

    @property
    def line(self):
        return self.comboBox_line.currentText()

    @property
    def energy(self):
        return float(self.edit_E.text())

    def update_combo_line(self, symbol):
        self.comboBox_line.clear()
        self.comboBox_line.addItems([line for line, _ in self.line_table.get(symbol, [])])

    def update_e_value(self):
        for line, energy in self.line_table.get(self.element, []):
            if line == self.line:
                self.edit_E.setText(f'{energy:.1f}')
                break
        self._save_settings()

    def _save_settings(self):
        if self.settings is None:
            return
        self.settings.setValue(f'{self.settings_prefix}_element_symbol', self.element)
        self.settings.setValue(f'{self.settings_prefix}_line_symbol', self.line)
        self.settings.setValue(f'{self.settings_prefix}_energy_nom', self.edit_E.text())

    def show_periodic_table(self):
        self.periodic_table_window = PeriodicTableWidget(accessible_elements=self.accessible_elements)
        self.periodic_table_window.element_selected.connect(self.set_element)
        self.periodic_table_window.show()

    def set_element(self, symbol):
        self.pushButton_element.setText(symbol)
        self.update_combo_line(symbol)
        self.update_e_value()

    def set_line(self, line):
        return _select_combo_text(self.comboBox_line, line)

    def set_values(self, element, line, energy):
        """Populate from stored scan parameters; the energy is kept verbatim even if the line is unknown."""
        self.set_element(element)
        if not self.set_line(line):
            self.comboBox_line.setCurrentIndex(-1)
        self.edit_E.setText(str(int(energy)))
        self._save_settings()
