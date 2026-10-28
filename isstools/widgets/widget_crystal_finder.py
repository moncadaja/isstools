"""
Crystal Finder Widget for XLive
Provides UI to search for best analyzer crystals for emission lines
"""

from qtpy import QtCore, QtWidgets, QtGui
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QComboBox, QPushButton, QTableWidget,
                            QTableWidgetItem, QSpinBox, QGroupBox, QHeaderView)
from xas.atlas import get_best_crystals_for_emission, crystal_library, CRYSTAL_GEOMETRIES


class NumericItem(QTableWidgetItem):
    """Table cell that displays formatted text but sorts by its numeric value."""

    def __init__(self, value, text):
        super().__init__(text)
        self.setData(Qt.UserRole, float(value))

    def __lt__(self, other):
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)


class UICrystalFinder(QWidget):
    """
    Widget for finding best analyzer crystals for a given element and emission line.
    Uses xas.atlas.get_best_crystals_for_emission() to find and display results.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi()

    def setupUi(self):
        """Create the UI layout programmatically"""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Input group
        input_group = QGroupBox("Search Parameters")
        input_layout = QHBoxLayout()

        # Element input
        element_label = QLabel("Element:")
        self.element_input = QLineEdit()
        self.element_input.setPlaceholderText("e.g., Fe, Cu, 26")
        self.element_input.setMaximumWidth(150)
        self.element_input.setToolTip("Enter element symbol or atomic number")

        # Emission line selector
        line_label = QLabel("Emission Line:")
        self.line_combo = QComboBox()
        self.line_combo.addItems(['Ka1', 'Ka2', 'Kb1', 'Kb2', 'Kb3', 'La1', 'La2', 'Lb1', 'Lb2', 'Lb3', 'Lb4', 'Lg1'])
        self.line_combo.setMaximumWidth(120)
        self.line_combo.setToolTip("Select emission line")

        # Number of results
        results_label = QLabel("Number of Results:")
        self.results_spinbox = QSpinBox()
        self.results_spinbox.setMinimum(1)
        self.results_spinbox.setMaximum(20)
        self.results_spinbox.setValue(5)
        self.results_spinbox.setMaximumWidth(80)
        self.results_spinbox.setToolTip("Maximum number of crystals to display")

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setMaximumWidth(100)
        self.search_button.clicked.connect(self.search_crystals)
        self.search_button.setDefault(True)

        # Add widgets to input layout
        input_layout.addWidget(element_label)
        input_layout.addWidget(self.element_input)
        input_layout.addSpacing(20)
        input_layout.addWidget(line_label)
        input_layout.addWidget(self.line_combo)
        input_layout.addSpacing(20)
        input_layout.addWidget(results_label)
        input_layout.addWidget(self.results_spinbox)
        input_layout.addSpacing(20)
        input_layout.addWidget(self.search_button)
        input_layout.addStretch()

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # Results info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        main_layout.addWidget(self.info_label)

        # Results table
        results_group = QGroupBox("Crystal Results")
        results_layout = QVBoxLayout()

        self.results_table = QTableWidget()
        self.columns = ['Rank', 'Crystal', 'Bragg Angle (°)', 'Reflectivity', 'ΔE (eV)', 'In Library'] + list(CRYSTAL_GEOMETRIES)
        self.results_table.setColumnCount(len(self.columns))
        self.results_table.setHorizontalHeaderLabels(self.columns)
        self.results_table.horizontalHeaderItem(5).setToolTip('Base crystal available in the library (any geometry)')
        for col, geometry in enumerate(CRYSTAL_GEOMETRIES, start=6):
            self.results_table.horizontalHeaderItem(col).setToolTip(f'Number of {geometry} crystals of the base cut at ISS')

        # Configure table appearance
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSortingEnabled(True)
        self.results_table.horizontalHeader().setSortIndicatorShown(True)

        # Set column widths
        header = self.results_table.horizontalHeader()
        for col in range(len(self.columns)):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Crystal

        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        # Status label at bottom
        self.status_label = QLabel("Enter element and emission line, then click Search")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        main_layout.addWidget(self.status_label)

        # Connect Enter key in element input to search
        self.element_input.returnPressed.connect(self.search_crystals)

    def search_crystals(self):
        """
        Execute the crystal search using xas.atlas.get_best_crystals_for_emission
        """
        element = self.element_input.text().strip()
        emission_line = self.line_combo.currentText()
        n_results = self.results_spinbox.value()

        # Validate input
        if not element:
            self.status_label.setText("⚠ Please enter an element")
            self.status_label.setStyleSheet("color: #e5484d;")
            self.info_label.setText("")
            return

        try:
            self.status_label.setText("Searching...")
            self.status_label.setStyleSheet("color: #3b82f6;")
            QtWidgets.QApplication.processEvents()  # Update UI

            # Call the xas.atlas function
            result = get_best_crystals_for_emission(
                element,
                emission_line,
                crystal_library=crystal_library,
                n_results=n_results
            )

            # Check for errors
            if result['error']:
                self.status_label.setText(f"⚠ Error: {result['error']}")
                self.status_label.setStyleSheet("color: #e5484d;")
                self.info_label.setText("")
                self.results_table.setRowCount(0)
                return

            # Display results
            self.display_results(result)
            self.status_label.setText(f"Found {len(result['crystals'])} crystals")
            self.status_label.setStyleSheet("color: #2eaa5e;")

        except Exception as e:
            self.status_label.setText(f"⚠ Error: {str(e)}")
            self.status_label.setStyleSheet("color: #e5484d;")
            self.info_label.setText("")
            self.results_table.setRowCount(0)

    def display_results(self, result):
        """
        Display the crystal search results in the table

        Parameters
        ----------
        result : dict
            Result dictionary from get_best_crystals_for_emission
        """
        # Update info label
        info_text = f"{result['element']} {result['emission_line']} @ {result['energy']:.1f} eV"
        self.info_label.setText(info_text)

        # Clear and populate table (sorting is paused while rows are written)
        crystals = result['crystals']
        self.results_table.setSortingEnabled(False)
        self.results_table.setRowCount(len(crystals))

        for row, crystal in enumerate(crystals):
            rank_item = NumericItem(crystal['rank'], str(crystal['rank']))
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row, 0, rank_item)

            crystal_item = QTableWidgetItem(crystal['hkl_str'])
            if crystal['library_crystal'] and crystal['library_crystal'] != crystal['hkl_str']:
                crystal_item.setToolTip(f"higher order of {crystal['library_crystal']}")
            self.results_table.setItem(row, 1, crystal_item)

            for col, key, fmt in ((2, 'bragg_angle', '.2f'), (3, 'reflectivity', '.4f'), (4, 'energy_resolution', '.3f')):
                item = NumericItem(crystal[key], f"{crystal[key]:{fmt}}")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.results_table.setItem(row, col, item)

            in_lib_item = NumericItem(int(crystal['in_library']), "Yes" if crystal['in_library'] else "No")
            in_lib_item.setTextAlignment(Qt.AlignCenter)
            if crystal['in_library']:
                in_lib_item.setBackground(QtGui.QColor(200, 255, 200))
                in_lib_item.setForeground(QtGui.QColor('black'))
            self.results_table.setItem(row, 5, in_lib_item)

            for col, geometry in enumerate(CRYSTAL_GEOMETRIES, start=6):
                count = crystal['inventory'].get(geometry, 0)
                count_item = NumericItem(count, str(count) if count else '-')
                count_item.setTextAlignment(Qt.AlignCenter)
                if count:
                    count_item.setBackground(QtGui.QColor(200, 200, 255))
                    count_item.setForeground(QtGui.QColor('black'))
                self.results_table.setItem(row, col, count_item)

        self.results_table.setSortingEnabled(True)
        self.results_table.sortItems(0, Qt.AscendingOrder)
