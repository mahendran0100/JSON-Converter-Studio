# JSON Converter Studio
# Copyright (C) 2026 S Mahendran
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE file for details.

import json
from pathlib import Path
from datetime import datetime

from qgis.PyQt.QtGui import QIcon, QFont, QColor
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import (
    QAction, QDialog, QFileDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QCheckBox, QComboBox, QTableWidget,
    QTableWidgetItem, QLineEdit, QMessageBox, QGroupBox, QTabWidget,
    QWidget, QPlainTextEdit
)
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPointXY, QgsField
)

from .json_engine import load_json_records, flatten_records, apply_mapping, detect_coordinates
from .plugins.csv_plugin import export_csv
from .plugins.xlsx_plugin import export_xlsx
from .plugins.geojson_plugin import export_geojson


class JSONConverterDialog(QDialog):
    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.setWindowTitle("JSON Converter Studio")
        self.resize(1250, 800)

        self.records = []
        self.rows = []
        self.columns = []
        self.original_columns = []
        self.mapping = {}
        self.log_lines = []
        self.build_ui()

    def build_ui(self):
        self.setMinimumSize(1180, 760)
        icon_path = str(Path(__file__).parent / "icon.svg")
        self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet("""
        QDialog { background:#F3F6FB; color:#172033; }
        QTabWidget::pane { background:#FFFFFF; border:1px solid #D8E1EE; border-radius:14px; }
        QTabBar::tab { background:#E7EEF8; color:#526176; padding:11px 22px;
                       margin-right:3px; border-top-left-radius:9px; border-top-right-radius:9px;
                       font-weight:700; }
        QTabBar::tab:selected { background:#FFFFFF; color:#2563EB; border-bottom:3px solid #2563EB; }
        QGroupBox { background:#FFFFFF; border:1px solid #D8E1EE; border-radius:14px;
                    margin-top:13px; padding:18px 12px 12px 12px; font-weight:800; }
        QGroupBox::title { subcontrol-origin:margin; left:14px; padding:0 8px;
                           color:#2563EB; background:#FFFFFF; }
        QLineEdit,QComboBox { background:#FFFFFF; border:1px solid #C9D4E2;
                              border-radius:8px; padding:8px 10px; min-height:20px; }
        QLineEdit:focus,QComboBox:focus { border:2px solid #60A5FA; }
        QCheckBox { spacing:8px; color:#334155; font-weight:600; }
        QTableWidget { background:#FFFFFF; alternate-background-color:#F7FAFC;
                       gridline-color:#E2E8F0; border:1px solid #D8E1EE;
                       border-radius:10px; selection-background-color:#DBEAFE; }
        QHeaderView::section { background:#172554; color:white; padding:9px;
                               border:none; font-weight:800; }
        QPushButton { color:white; border:none; border-radius:9px;
                      padding:10px 17px; font-weight:800; }
        QPushButton:hover { margin-top:-1px; }
        """)

        root=QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(11)

        # Header
        header=QWidget()
        header.setStyleSheet("QWidget{background:#0B1220;border-radius:18px;}")
        h=QHBoxLayout(header); h.setContentsMargins(18,15,18,15); h.setSpacing(14)

        ic=QLabel()
        ic.setPixmap(QIcon(icon_path).pixmap(66,66))
        ic.setStyleSheet("background:transparent;border:none;")
        h.addWidget(ic)

        tb=QVBoxLayout()
        t=QLabel("JSON Converter Studio")
        t.setStyleSheet("font-size:25px;font-weight:900;color:#FFFFFF;background:transparent;border:none;")
        tb.addWidget(t)
        st=QLabel("JSON  →  TABULAR  →  GIS  •  Professional QGIS Data Utility")
        st.setStyleSheet("font-size:11px;font-weight:700;color:#A7F3D0;background:transparent;border:none;")
        tb.addWidget(st)
        h.addLayout(tb); h.addStretch()

        badge=QLabel("V1.1.0  •  QGIS")
        badge.setStyleSheet("background:#2563EB;color:#FFFFFF;border-radius:11px;padding:9px 13px;font-weight:900;")
        h.addWidget(badge)
        root.addWidget(header)

        # KPI cards
        cards=QHBoxLayout(); cards.setSpacing(9)
        self.card_records=self._stat_card("RECORDS","0","#2563EB")
        self.card_columns=self._stat_card("FIELDS","0","#7C3AED")
        self.card_coordinates=self._stat_card("COORDINATES","—","#0F766E")
        self.card_status=self._stat_card("STATUS","Ready","#EA580C")
        for x in [self.card_records,self.card_columns,self.card_coordinates,self.card_status]:
            cards.addWidget(x)
        root.addLayout(cards)

        tabs=QTabWidget(); tabs.setDocumentMode(True); root.addWidget(tabs,1)

        # Convert
        convert=QWidget(); tabs.addTab(convert,"  ⚡  Convert  "); cv=QVBoxLayout(convert)
        cv.setContentsMargins(10,10,10,10)

        box=QGroupBox("①  INPUT DATA"); g=QGridLayout(box)
        self.path=QLineEdit(); self.path.setReadOnly(True); self.path.setPlaceholderText("Choose JSON file or folder...")
        g.addWidget(self.path,0,0,1,3)
        b=QPushButton("📂  Open JSON"); b.setObjectName("blue"); b.setStyleSheet("QPushButton{background:#2563EB;}QPushButton:hover{background:#1D4ED8;}"); b.clicked.connect(self.open_json); g.addWidget(b,0,3)
        b=QPushButton("📁  JSON Folder"); b.setStyleSheet("QPushButton{background:#0F766E;}QPushButton:hover{background:#115E59;}"); b.clicked.connect(self.open_folder); g.addWidget(b,0,4)
        cv.addWidget(box)

        box=QGroupBox("②  SMART PROCESSING"); row=QHBoxLayout(box)
        self.flatten=QCheckBox("Flatten nested JSON"); self.flatten.setChecked(True); self.flatten.stateChanged.connect(self.analyze); row.addWidget(self.flatten)
        self.dedupe=QCheckBox("Remove duplicates"); self.dedupe.stateChanged.connect(self.analyze); row.addWidget(self.dedupe)
        b=QPushButton("🔍  Analyze"); b.setStyleSheet("QPushButton{background:#7C3AED;}QPushButton:hover{background:#6D28D9;}"); b.clicked.connect(self.analyze); row.addWidget(b)
        b=QPushButton("✏  Column Mapping"); b.setStyleSheet("QPushButton{background:#EA580C;}QPushButton:hover{background:#C2410C;}"); b.clicked.connect(self.map_columns); row.addWidget(b); row.addStretch()
        cv.addWidget(box)

        box=QGroupBox("③  GEO LOCATION"); g=QGridLayout(box)
        g.addWidget(QLabel("Latitude"),0,0); self.lat=QComboBox(); g.addWidget(self.lat,0,1)
        g.addWidget(QLabel("Longitude"),0,2); self.lon=QComboBox(); g.addWidget(self.lon,0,3)
        b=QPushButton("📍  Auto Detect"); b.setStyleSheet("QPushButton{background:#0F766E;}QPushButton:hover{background:#115E59;}"); b.clicked.connect(self.detect); g.addWidget(b,0,4)
        cv.addWidget(box)

        box=QGroupBox("④  OUTPUT & QGIS"); row=QHBoxLayout(box)
        for text,slot,color in [
            ("📄  Export CSV",self.save_csv,"#2563EB"),
            ("📊  Export Excel",self.save_excel,"#16A34A"),
            ("🌍  Export GeoJSON",self.save_geojson,"#7C3AED"),
            ("🗺  Add Point Layer",self.add_layer,"#EA580C")]:
            b=QPushButton(text); b.setStyleSheet(f"QPushButton{{background:{color};}}QPushButton:hover{{background:#172033;}}"); b.clicked.connect(slot); row.addWidget(b)
        cv.addWidget(box)

        # Processing Log
        log_box = QGroupBox("⑤  PROCESSING LOG")
        log_layout = QVBoxLayout(log_box)

        log_toolbar = QHBoxLayout()
        log_title = QLabel("Live conversion activity")
        log_title.setStyleSheet("font-weight:800;color:#334155;")
        log_toolbar.addWidget(log_title)
        log_toolbar.addStretch()

        clear_log = QPushButton("Clear Log")
        clear_log.setStyleSheet(
            "QPushButton{background:#64748B;}QPushButton:hover{background:#475569;}"
        )
        clear_log.clicked.connect(self.clear_log)
        log_toolbar.addWidget(clear_log)

        save_log = QPushButton("Save Log")
        save_log.setStyleSheet(
            "QPushButton{background:#475569;}QPushButton:hover{background:#334155;}"
        )
        save_log.clicked.connect(self.save_log)
        log_toolbar.addWidget(save_log)

        log_layout.addLayout(log_toolbar)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(1000)
        self.log_view.setStyleSheet("""
            QPlainTextEdit {
                background:#0B1220;
                color:#D1FAE5;
                border:1px solid #1E293B;
                border-radius:9px;
                padding:9px;
                font-family:Consolas, "Courier New", monospace;
                font-size:10px;
            }
        """)
        log_layout.addWidget(self.log_view)
        cv.addWidget(log_box)
        cv.addStretch()

        self.log("INFO", "JSON Converter Studio started.")
        self.log("INFO", "Developed by S Mahendran.")

        # Preview
        preview=QWidget(); tabs.addTab(preview,"  👁  Preview  "); pv=QVBoxLayout(preview)
        sr=QHBoxLayout(); q=QLabel("🔎  Search records"); q.setStyleSheet("font-weight:800;color:#334155;"); sr.addWidget(q)
        self.search=QLineEdit(); self.search.setPlaceholderText("Search any field..."); self.search.textChanged.connect(self.preview); sr.addWidget(self.search,1)
        b=QPushButton("↻  Refresh"); b.setStyleSheet("QPushButton{background:#475569;}"); b.clicked.connect(self.preview); sr.addWidget(b); pv.addLayout(sr)
        self.table=QTableWidget(); self.table.setSortingEnabled(True); self.table.setAlternatingRowColors(True); self.table.setSelectionBehavior(QTableWidget.SelectRows); self.table.setEditTriggers(QTableWidget.NoEditTriggers); self.table.verticalHeader().setDefaultSectionSize(30); pv.addWidget(self.table,1)

        # Manual
        manual=QWidget(); tabs.addTab(manual,"  📘  User Manual  "); ml=QVBoxLayout(manual)
        mh=QLabel("JSON Converter Studio — User Manual"); mh.setStyleSheet("font-size:18px;font-weight:900;color:#172554;"); ml.addWidget(mh)
        text=QPlainTextEdit(); text.setReadOnly(True); text.setPlainText(
            "01  INPUT\nOpen a JSON file or a folder of JSON files.\n\n"
            "02  SMART PROCESSING\nFlatten nested JSON and optionally remove duplicates.\n\n"
            "03  COLUMN MAPPING\nRename fields before export or QGIS layer creation.\n\n"
            "04  GEO LOCATION\nUse Auto Detect or select Latitude / Longitude.\n\n"
            "05  PREVIEW\nSearch and inspect the first 100 records.\n\n"
            "06  OUTPUT\nCSV • Excel • GeoJSON • Direct QGIS Point Layer\n\n"
            "RECOMMENDED WORKFLOW\nJSON → Analyze → Mapping → Coordinates → Preview → Add Point Layer"
        ); ml.addWidget(text,1)

        self._update_stat_cards()

    def _stat_card(self,label,value,color):
        card=QWidget(); card.setMinimumHeight(72)
        card.setStyleSheet(f"QWidget{{background:#FFFFFF;border:1px solid #D8E1EE;border-left:5px solid {color};border-radius:12px;}}")
        l=QVBoxLayout(card); l.setContentsMargins(12,8,12,8)
        a=QLabel(label); a.setStyleSheet(f"color:{color};font-size:9px;font-weight:900;border:none;"); l.addWidget(a)
        v=QLabel(value); v.setStyleSheet("color:#172033;font-size:16px;font-weight:900;border:none;"); l.addWidget(v)
        card._value_label=v
        return card

    def _update_stat_cards(self):
        if hasattr(self,"card_records"):
            self.card_records._value_label.setText(f"{len(self.rows):,}")
            self.card_columns._value_label.setText(f"{len(self.columns):,}")
            lat=self.lat.currentText() if hasattr(self,"lat") else ""
            lon=self.lon.currentText() if hasattr(self,"lon") else ""
            self.card_coordinates._value_label.setText("✓ Detected" if lat and lon else "Select fields")
            self.card_status._value_label.setText("Ready to export" if self.rows else "Waiting for JSON")
    def log(self, level, message):
        """Write a timestamped message to the live processing log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}"
        self.log_lines.append(line)

        if hasattr(self, "log_view"):
            self.log_view.appendPlainText(line)
            cursor = self.log_view.textCursor()
            cursor.movePosition(cursor.End)
            self.log_view.setTextCursor(cursor)

    def clear_log(self):
        self.log_lines = []
        if hasattr(self, "log_view"):
            self.log_view.clear()
        self.log("INFO", "Processing log cleared.")

    def save_log(self):
        if not self.log_lines:
            QMessageBox.information(self, "Processing Log", "There is no log to save.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Processing Log",
            "JSON_Converter_Processing_Log.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        if not path:
            return

        try:
            Path(path).write_text(
                "\n".join(self.log_lines),
                encoding="utf-8"
            )
            self.log("SUCCESS", f"Processing log saved: {path}")
        except Exception as e:
            self.log("ERROR", f"Could not save log: {e}")
            QMessageBox.critical(self, "Log Error", str(e))

    def open_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open JSON", "", "JSON (*.json);;All files (*.*)")
        if path:
            self.load_paths([path])

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open JSON Folder")
        if not folder:
            return
        paths = [str(p) for p in sorted(Path(folder).glob("*.json"))]
        if not paths:
            QMessageBox.warning(self, "JSON Converter", "No JSON files found.")
            return
        self.load_paths(paths)

    def load_paths(self, paths):
        try:
            self.log("INFO", f"Loading {len(paths)} JSON file(s)...")
            records = []

            for path in paths:
                self.log("INFO", f"Reading: {path}")
                loaded = load_json_records(path)
                records.extend(loaded)
                self.log("SUCCESS", f"Loaded {len(loaded):,} record(s) from {Path(path).name}")

            self.records = records
            self.mapping = {}
            self.path.setText(
                paths[0] if len(paths) == 1 else f"{len(paths)} JSON files"
            )
            self.log("SUCCESS", f"Total records loaded: {len(self.records):,}")
            self.analyze()

        except json.JSONDecodeError as e:
            self.log("ERROR", f"Invalid JSON: {e}")
            QMessageBox.critical(
                self, "Invalid JSON",
                f"The selected JSON could not be parsed.\n\n{e}"
            )
        except Exception as e:
            self.log("ERROR", f"JSON loading failed: {e}")
            QMessageBox.critical(self, "JSON Error", str(e))

    def analyze(self):
        if not self.records:
            self.log("WARNING", "Analyze requested but no records are loaded.")
            return

        started = datetime.now()

        try:
            self.log("INFO", "Starting JSON analysis...")
            self.log(
                "INFO",
                f"Options: flatten={'ON' if self.flatten.isChecked() else 'OFF'}, "
                f"duplicates={'REMOVE' if self.dedupe.isChecked() else 'KEEP'}"
            )

            before_count = len(self.records)

            self.rows, self.columns = flatten_records(
                self.records,
                self.flatten.isChecked(),
                self.dedupe.isChecked()
            )

            self.original_columns = list(self.columns)

            if self.dedupe.isChecked():
                self.log(
                    "SUCCESS",
                    f"Duplicate processing complete: {before_count:,} → {len(self.rows):,} records"
                )
            else:
                self.log("SUCCESS", f"Records prepared: {len(self.rows):,}")

            if self.mapping:
                self.rows, self.columns = apply_mapping(
                    self.rows, self.original_columns, self.mapping
                )
                self.log("SUCCESS", f"Column mapping applied: {len(self.columns):,} fields")

            self.lat.clear()
            self.lon.clear()
            self.lat.addItems([str(c) for c in self.columns])
            self.lon.addItems([str(c) for c in self.columns])

            self.detect()
            self.preview()
            self._update_stat_cards()

            elapsed = (datetime.now() - started).total_seconds()
            self.log(
                "SUCCESS",
                f"Analysis completed: {len(self.rows):,} records, "
                f"{len(self.columns):,} fields in {elapsed:.2f}s"
            )

        except Exception as e:
            self.log("ERROR", f"Analysis failed: {e}")
            QMessageBox.critical(self, "Conversion Error", str(e))

    def detect(self):
        a, b = detect_coordinates(self.columns)

        if a:
            self.lat.setCurrentText(str(a))
        if b:
            self.lon.setCurrentText(str(b))

        detected = bool(a and b)

        if hasattr(self, "card_coordinates"):
            self.card_coordinates._value_label.setText(
                "✓ Detected" if detected else "Select fields"
            )

        if detected:
            self.log("SUCCESS", f"Coordinates detected: Latitude={a}, Longitude={b}")
        elif self.columns:
            self.log("WARNING", "Latitude/Longitude fields were not automatically detected.")

    def preview(self):
        self.table.setSortingEnabled(False)
        self.table.clear()

        if not self.columns:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in self.columns])

        needle = self.search.text().strip().lower()
        shown = []

        for row in self.rows:
            values = []
            for c in self.columns:
                v = row.get(c, "")
                if isinstance(v, (dict, list)):
                    v = json.dumps(v, ensure_ascii=False, default=str)
                v = "" if v is None else str(v)
                values.append(v[:500] + (" …" if len(v) > 500 else ""))

            if needle and needle not in " ".join(values).lower():
                continue

            shown.append(values)
            if len(shown) >= 100:
                break

        self.table.setRowCount(len(shown))

        for r, values in enumerate(shown):
            for c, value in enumerate(values):
                self.table.setItem(r, c, QTableWidgetItem(value))

        self.table.resizeColumnsToContents()
        for c in range(self.table.columnCount()):
            if self.table.columnWidth(c) > 280:
                self.table.setColumnWidth(c, 280)

        self.table.setSortingEnabled(True)

        if self.rows:
            self.log(
                "INFO",
                f"Preview refreshed: showing {len(shown):,} of {len(self.rows):,} records"
            )

    def map_columns(self):
        if not self.columns:
            QMessageBox.warning(self, "Mapping", "Analyze JSON first.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Column Mapping")
        dlg.resize(720, 620)
        layout = QVBoxLayout(dlg)
        grid = QGridLayout()
        layout.addLayout(grid, 1)

        entries = []
        for r, col in enumerate(self.original_columns):
            grid.addWidget(QLabel(str(col)), r, 0)
            e = QLineEdit(self.mapping.get(col, str(col)))
            grid.addWidget(e, r, 1)
            entries.append((col, e))

        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel")
        apply = QPushButton("Apply")
        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(apply)
        layout.addLayout(buttons)
        cancel.clicked.connect(dlg.reject)

        def do_apply():
            mapping = {}
            used = set()
            for old, entry in entries:
                new = entry.text().strip() or str(old)
                if new in used:
                    QMessageBox.warning(dlg, "Mapping", f"Duplicate name: {new}")
                    return
                used.add(new)
                mapping[old] = new
            self.mapping = mapping
            dlg.accept()

        apply.clicked.connect(do_apply)

        if dlg.exec_():
            self.log("SUCCESS", "Column mapping updated.")
            self.analyze()

    def save_csv(self):
        if not self.rows:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV (*.csv)")
        if path:
            try:
                export_csv(self.rows, self.columns, path)
                self.log("SUCCESS", f"CSV exported: {len(self.rows):,} records → {path}")
                QMessageBox.information(self, "Export", "CSV exported successfully.")
            except Exception as e:
                self.log("ERROR", f"CSV export failed: {e}")
                QMessageBox.critical(self, "Export Error", str(e))

    def save_excel(self):
        if not self.rows:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Excel", "", "Excel (*.xlsx)")
        if path:
            try:
                export_xlsx(self.rows, self.columns, path)
                self.log("SUCCESS", f"Excel exported: {len(self.rows):,} records → {path}")
                QMessageBox.information(self, "Export", "Excel exported successfully.")
            except Exception as e:
                self.log("ERROR", f"Excel export failed: {e}")
                QMessageBox.critical(self, "Export Error", str(e))

    def save_geojson(self):
        if not self.rows:
            return
        lat, lon = self.lat.currentText(), self.lon.currentText()
        if not lat or not lon:
            QMessageBox.warning(self, "GeoJSON", "Select Latitude and Longitude.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export GeoJSON", "", "GeoJSON (*.geojson)")
        if path:
            try:
                count = export_geojson(self.rows, lat, lon, path)
                self.log(
                    "SUCCESS",
                    f"GeoJSON exported: {count:,} valid point features → {path}"
                )
                QMessageBox.information(self, "GeoJSON", f"Exported {count:,} features.")
            except Exception as e:
                self.log("ERROR", f"GeoJSON export failed: {e}")
                QMessageBox.critical(self, "GeoJSON Error", str(e))

    def add_layer(self):
        if not self.rows:
            self.log("WARNING", "Add Point Layer requested but no records are available.")
            QMessageBox.warning(self, "QGIS Layer", "Analyze JSON first.")
            return

        lat, lon = self.lat.currentText(), self.lon.currentText()

        if not lat or not lon:
            self.log("ERROR", "Latitude/Longitude fields are not selected.")
            QMessageBox.warning(
                self, "QGIS Layer",
                "Select Latitude and Longitude fields."
            )
            return

        self.log("INFO", f"Creating QGIS Point Layer using Latitude={lat}, Longitude={lon}")

        layer_name = "JSON Converter - Points"
        if self.path.text() and not self.path.text().startswith("["):
            source_name = Path(self.path.text()).stem
            if source_name:
                layer_name = f"{source_name} - Points"

        layer = QgsVectorLayer(
            "Point?crs=EPSG:4326",
            layer_name,
            "memory"
        )

        if not layer.isValid():
            self.log("ERROR", "Could not create QGIS memory point layer.")
            QMessageBox.critical(self, "QGIS Layer", "Could not create the point layer.")
            return

        provider = layer.dataProvider()

        names = []
        fields = []

        for col in self.columns:
            base = (
                str(col)
                .replace(".", "_")
                .replace("[", "_")
                .replace("]", "_")
                .replace(" ", "_")
            )
            base = base[:50] or "field"

            name = base
            i = 2

            while name.lower() in names:
                suffix = "_" + str(i)
                name = base[:50-len(suffix)] + suffix
                i += 1

            names.append(name.lower())
            fields.append((col, name))

        provider.addAttributes([
            QgsField(name, QVariant.String)
            for _, name in fields
        ])
        layer.updateFields()

        features = []
        skipped = 0
        out_of_range = 0

        for row in self.rows:
            try:
                x = float(row.get(lon))
                y = float(row.get(lat))
            except (TypeError, ValueError):
                skipped += 1
                continue

            if not (-180 <= x <= 180 and -90 <= y <= 90):
                out_of_range += 1
                continue

            f = QgsFeature(layer.fields())
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))

            attrs = []

            for original, _ in fields:
                value = row.get(original, "")

                if isinstance(value, (dict, list)):
                    value = json.dumps(
                        value,
                        ensure_ascii=False,
                        default=str
                    )

                attrs.append("" if value is None else str(value))

            f.setAttributes(attrs)
            features.append(f)

        if features:
            provider.addFeatures(features)

        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)

        if not layer.extent().isEmpty():
            self.iface.mapCanvas().setExtent(layer.extent())
            self.iface.mapCanvas().refresh()

        self.log(
            "SUCCESS",
            f"Point layer created: {len(features):,} features"
        )
        self.log(
            "INFO",
            f"Invalid/missing coordinates skipped: {skipped:,}; "
            f"out-of-range coordinates skipped: {out_of_range:,}"
        )
        self.log(
            "SUCCESS",
            f"Layer added to QGIS: {layer_name} (EPSG:4326)"
        )

        QMessageBox.information(
            self,
            "QGIS Layer",
            f"Layer added successfully.\n\n"
            f"Layer: {layer_name}\n"
            f"Features: {len(features):,}\n"
            f"Invalid/missing coordinates: {skipped:,}\n"
            f"Out-of-range coordinates: {out_of_range:,}\n"
            f"CRS: EPSG:4326"
        )


class JSONConverterPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        icon = QIcon(str(Path(__file__).parent / "icon.svg"))
        self.action = QAction(icon, "JSON Converter Studio", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&JSON Converter Studio", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginMenu("&JSON Converter Studio", self.action)
            self.iface.removeToolBarIcon(self.action)
            self.action = None
        if self.dialog:
            self.dialog.close()
            self.dialog = None

    def run(self):
        if self.dialog is None:
            self.dialog = JSONConverterDialog(self.iface)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
