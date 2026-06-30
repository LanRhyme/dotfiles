#!/usr/bin/env python3
"""aether-hub: 集中管理 Aether 系统配置与应用"""
import os
import sys
import subprocess
import shlex
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QScrollArea, QFrame, 
                             QMenu, QComboBox, QStackedWidget, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtProperty, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QColor, QPainter, QPainterPath, QPen, QBrush, QAction

BG = "#1c1b17"
BG_CARD = "#2c2b26"
BG_HOVER = "#37362f"
FG = "#f3f3f2"
FG_DIM = "#b5b4b0"
FG_MUTED = "#6c6a62"
ACCENT = "#8d8768"
BORDER = "#3d3b34"

class DesktopEntry:
    def __init__(self, filename):
        self.filename = filename
        
        self.user_path = os.path.join(os.path.expanduser("~/.local/share/applications"), filename)
        self.sys_path = os.path.join("/usr/share/applications", filename)
        self.flatpak_path = os.path.join("/var/lib/flatpak/exports/share/applications", filename)
        
        self.base_path = ""
        if os.path.exists(self.sys_path):
            self.base_path = self.sys_path
        elif os.path.exists(self.flatpak_path):
            self.base_path = self.flatpak_path
        elif os.path.exists(self.user_path):
            self.base_path = self.user_path
            
        self.name = self.filename
        self.icon = ""
        self.exec_cmd = ""
        self.is_system_hidden = False
        self.is_user_hidden = False
        
        if self.base_path:
            self.load()
            
    def load(self):
        self.name, self.icon, self.exec_cmd, self.is_system_hidden = self._parse_file(self.base_path)
        
        if self.base_path != self.user_path and os.path.exists(self.user_path):
            _, _, _, self.is_user_hidden = self._parse_file(self.user_path)
        else:
            self.is_user_hidden = self.is_system_hidden
            
    def is_hidden(self):
        return self.is_user_hidden
        
    def set_hidden(self, hidden):
        if hidden:
            content = ""
            source = self.user_path if os.path.exists(self.user_path) else self.base_path
            with open(source, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "NoDisplay=true" not in content:
                content = content.replace("[Desktop Entry]", "[Desktop Entry]\nNoDisplay=true", 1)
            
            os.makedirs(os.path.dirname(self.user_path), exist_ok=True)
            with open(self.user_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.is_user_hidden = True
        else:
            if os.path.exists(self.user_path):
                lines = []
                with open(self.user_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.strip() != "NoDisplay=true":
                            lines.append(line)
                with open(self.user_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            self.is_user_hidden = False

    def _parse_file(self, path):
        name = ""
        name_full = ""
        name_short = ""
        icon = ""
        exec_cmd = ""
        no_display = False
        
        sys_lang = os.environ.get("LANG", "en_US").split(".")[0]
        lang_short = sys_lang.split("_")[0]
        
        name_key_full = f"Name[{sys_lang}]"
        name_key_short = f"Name[{lang_short}]"
        
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                in_desktop_entry = False
                for line in f:
                    line = line.strip()
                    if line == "[Desktop Entry]":
                        in_desktop_entry = True
                        continue
                    elif line.startswith("[") and in_desktop_entry:
                        in_desktop_entry = False
                        
                    if not in_desktop_entry:
                        continue
                        
                    if line.startswith("Name="):
                        if not name: name = line[5:]
                    elif line.startswith(name_key_full + "="):
                        if not name_full: name_full = line[len(name_key_full)+1:]
                    elif line.startswith(name_key_short + "="):
                        if not name_short: name_short = line[len(name_key_short)+1:]
                    elif line.startswith("Icon="):
                        if not icon: icon = line[5:]
                    elif line.startswith("Exec="):
                        if not exec_cmd: exec_cmd = line[5:]
                    elif line.startswith("NoDisplay="):
                        no_display = (line[10:].lower() == "true")
        except Exception:
            pass
            
        final_name = name_full or name_short or name
        if not final_name:
            final_name = os.path.basename(path).replace(".desktop", "")
            
        return final_name, icon, exec_cmd, no_display

class MD3Switch(QWidget):
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(52, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = False
        self._position = 0.0
        
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.valueChanged.connect(self._set_position)
        
    @pyqtProperty(float)
    def position(self):
        return self._position
        
    def _set_position(self, pos):
        self._position = pos
        self.update()
        
    def isChecked(self):
        return self._checked
        
    def setChecked(self, checked, animate=False):
        if self._checked != checked:
            self._checked = checked
            if animate:
                self.anim.stop()
                self.anim.setStartValue(self._position)
                self.anim.setEndValue(1.0 if self._checked else 0.0)
                self.anim.start()
            else:
                self._position = 1.0 if self._checked else 0.0
                self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked, animate=True)
            self.toggled.emit(self._checked)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        r1, g1, b1 = QColor(BG_CARD).getRgb()[:3]
        r2, g2, b2 = QColor(ACCENT).getRgb()[:3]
        bg_color = QColor(int(r1 + (r2 - r1)*self._position), int(g1 + (g2 - g1)*self._position), int(b1 + (b2 - b1)*self._position))
        
        br1, bg1, bb1 = QColor(FG_MUTED).getRgb()[:3]
        border_color = QColor(int(br1 + (r2 - br1)*self._position), int(bg1 + (g2 - bg1)*self._position), int(bb1 + (b2 - bb1)*self._position))
        
        path = QPainterPath()
        path.addRoundedRect(1, 1, self.width()-2, self.height()-2, 15, 15)
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(bg_color))
        painter.drawPath(path)
        
        thumb_radius = 6 + 4 * self._position
        start_x = 7.0
        end_x = self.width() - thumb_radius * 2 - 5
        thumb_x = start_x + (end_x - start_x) * self._position
        thumb_y = self.height() / 2 - thumb_radius
        
        tr1, tg1, tb1 = QColor(FG_DIM).getRgb()[:3]
        tr2, tg2, tb2 = QColor(BG).getRgb()[:3]
        thumb_color = QColor(int(tr1 + (tr2 - tr1)*self._position), int(tg1 + (tg2 - tg1)*self._position), int(tb1 + (tb2 - tb1)*self._position))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(thumb_color))
        painter.drawEllipse(int(thumb_x), int(thumb_y), int(thumb_radius*2), int(thumb_radius*2))

class AppCard(QFrame):
    def __init__(self, app_entry, parent_list):
        super().__init__()
        self.app = app_entry
        self.parent_list = parent_list
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("AppCard")
        self.setStyleSheet(f"""
            QFrame#AppCard {{ background-color: {BG_CARD}; border-radius: 16px; border: 1px solid transparent; }}
            QFrame#AppCard:hover {{ background-color: {BG_HOVER}; border: 1px solid {BORDER}; }}
            QLabel {{ background-color: transparent; }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        icon = QIcon.fromTheme(self.app.icon) if self.app.icon else QIcon.fromTheme("application-x-executable")
        if icon.isNull():
            icon = QIcon.fromTheme("application-x-executable")
        self.icon_label.setPixmap(icon.pixmap(48, 48))
        layout.addWidget(self.icon_label)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.name_label = QLabel(self.app.name)
        self.name_label.setStyleSheet(f"color: {FG}; font-size: 15px; font-weight: bold;")
        self.name_label.setWordWrap(False)
        
        self.id_label = QLabel(self.app.filename)
        self.id_label.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px;")
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.id_label)
        layout.addLayout(info_layout, 1)
        
        self.status_label = QLabel("已隐藏")
        self.status_label.setStyleSheet(f"background-color: {BG_HOVER}; color: {FG_DIM}; border-radius: 10px; padding: 2px 8px; font-size: 10px; font-weight: bold;")
        self.status_label.setVisible(self.app.is_hidden())
        layout.addWidget(self.status_label)
        
        self.toggle_switch = MD3Switch()
        self.toggle_switch.setChecked(self.app.is_hidden(), animate=False)
        self.toggle_switch.toggled.connect(self.on_toggle)
        layout.addWidget(self.toggle_switch)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def on_toggle(self, checked):
        self.app.set_hidden(checked)
        self.status_label.setVisible(checked)
        self.parent_list.update_status()
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_switch.setChecked(not self.toggle_switch.isChecked(), animate=True)
            self.on_toggle(self.toggle_switch.isChecked())
        super().mouseReleaseEvent(event)
        
    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 8px; padding: 4px; }} 
            QMenu::item {{ color: {FG}; padding: 8px 24px; border-radius: 4px; background: transparent; }} 
            QMenu::item:selected {{ background-color: {BG_HOVER}; }}
        """)
        
        run_action = QAction("运行应用", self)
        edit_action = QAction("编辑 Desktop 文件", self)
        open_folder_action = QAction("打开所在目录", self)
        
        run_action.triggered.connect(self.run_app)
        edit_action.triggered.connect(self.edit_app)
        open_folder_action.triggered.connect(self.open_folder)
        
        menu.addAction(run_action)
        menu.addAction(edit_action)
        menu.addAction(open_folder_action)
        menu.exec(self.mapToGlobal(pos))
        
    def run_app(self):
        if self.app.exec_cmd:
            cmd = self.app.exec_cmd.split("%")[0].strip()
            try:
                subprocess.Popen(shlex.split(cmd))
            except Exception as e:
                pass
                
    def edit_app(self):
        target = self.app.user_path if os.path.exists(self.app.user_path) else self.app.base_path
        subprocess.Popen(['xdg-open', target])
        
    def open_folder(self):
        target = self.app.user_path if os.path.exists(self.app.user_path) else self.app.base_path
        subprocess.Popen(['xdg-open', os.path.dirname(target)])

class FlowLayoutWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.items = []
        self._item_width = 320
        self._item_height = 80
        self._spacing = 16
        self.setStyleSheet("background-color: transparent;")

    def add_widget(self, widget):
        widget.setParent(self)
        widget.setFixedSize(self._item_width, self._item_height)
        widget.show()
        self.items.append(widget)
        
    def clear(self):
        for w in self.items:
            w.setParent(None)
            w.deleteLater()
        self.items = []
        
    def resizeEvent(self, event):
        self.recalculate()
        super().resizeEvent(event)
        
    def recalculate(self):
        if not self.items:
            self.setMinimumHeight(0)
            return
            
        w = self.width()
        cols = max(1, (w + self._spacing) // (self._item_width + self._spacing))
        
        row = 0
        col = 0
        
        total_grid_w = cols * self._item_width + (cols - 1) * self._spacing
        offset_x = max(0, (w - total_grid_w) // 2)
        
        for item in self.items:
            x = offset_x + col * (self._item_width + self._spacing)
            y = row * (self._item_height + self._spacing)
            item.move(x, y)
            
            col += 1
            if col >= cols:
                col = 0
                row += 1
                
        total_rows = row + (1 if col > 0 else 0)
        h = total_rows * (self._item_height + self._spacing)
        self.setMinimumHeight(h)

class AppHiderPage(QWidget):
    def __init__(self):
        super().__init__()
        self.apps_cache = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        toolbar = QHBoxLayout()
        toolbar.setSpacing(16)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(" 搜索应用名称...")
        self.search_bar.setFixedHeight(48)
        self.search_bar.setStyleSheet(f"""
            QLineEdit {{ background-color: {BG_CARD}; color: {FG}; border-radius: 24px; padding: 0 24px; font-size: 15px; border: 1px solid transparent; }}
            QLineEdit:focus {{ border: 1px solid {ACCENT}; background-color: {BG_HOVER}; }}
        """)
        self.search_bar.textChanged.connect(self.refresh_list)
        toolbar.addWidget(self.search_bar, 1)
        
        self.sort_cb = QComboBox()
        self.sort_cb.setFixedHeight(48)
        self.sort_cb.addItems(["默认排序 (名称)", "隐藏优先", "显示优先"])
        self.sort_cb.setStyleSheet(f"""
            QComboBox {{ background-color: {BG_CARD}; color: {FG_DIM}; border-radius: 24px; padding: 0 24px; border: none; font-weight: bold; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{ background-color: {BG_CARD}; color: {FG}; border-radius: 12px; selection-background-color: {BG_HOVER}; outline: none; }}
        """)
        self.sort_cb.currentIndexChanged.connect(self.refresh_list)
        toolbar.addWidget(self.sort_cb)
        
        self.btn_refresh = QPushButton("刷新数据")
        self.btn_refresh.setFixedHeight(48)
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{ background-color: {BG_CARD}; color: {FG_DIM}; border-radius: 24px; padding: 0 24px; font-weight: bold; border: none; }}
            QPushButton:hover {{ background-color: {BG_HOVER}; color: {FG}; }}
        """)
        self.btn_refresh.clicked.connect(self.load_apps)
        toolbar.addWidget(self.btn_refresh)
        
        layout.addLayout(toolbar)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: transparent; }}
            QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 30px; }}
            QScrollBar::handle:vertical:hover {{ background: {FG_MUTED}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        """)
        
        self.flow_widget = FlowLayoutWidget()
        self.scroll.setWidget(self.flow_widget)
        layout.addWidget(self.scroll, 1)
        
        self.status = QLabel("")
        self.status.setStyleSheet(f"color: {FG_MUTED}; font-size: 13px; font-weight: bold; background-color: transparent;")
        self.status.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.status)
        
        self.load_apps()
        
    def load_apps(self):
        self.apps_cache = []
        seen_files = set()
        
        search_dirs = [
            os.path.expanduser("~/.local/share/applications"),
            "/usr/share/applications",
            "/var/lib/flatpak/exports/share/applications"
        ]
        
        for d in search_dirs:
            if not os.path.exists(d): continue
            for f in sorted(os.listdir(d)):
                if not f.endswith(".desktop"): continue
                if f in seen_files: continue
                seen_files.add(f)
                
                entry = DesktopEntry(f)
                if not entry.name:
                    continue
                
                # Filter purely system hidden apps unless overriden
                if entry.base_path != entry.user_path and entry.is_system_hidden and not os.path.exists(entry.user_path):
                    continue
                    
                self.apps_cache.append(entry)
        self.refresh_list()
        
    def refresh_list(self):
        self.flow_widget.clear()
        query = self.search_bar.text().lower()
        sort_idx = self.sort_cb.currentIndex()
        
        filtered = []
        for app in self.apps_cache:
            if query and query not in app.name.lower() and query not in app.filename.lower():
                continue
            filtered.append(app)
            
        if sort_idx == 0:
            filtered.sort(key=lambda x: x.name.lower())
        elif sort_idx == 1:
            filtered.sort(key=lambda x: (not x.is_hidden(), x.name.lower()))
        elif sort_idx == 2:
            filtered.sort(key=lambda x: (x.is_hidden(), x.name.lower()))
            
        for app in filtered:
            card = AppCard(app, self)
            self.flow_widget.add_widget(card)
            
        self.flow_widget.recalculate()
        self.update_status()
        
    def update_status(self):
        total = len(self.apps_cache)
        hidden_count = sum(1 for app in self.apps_cache if app.is_hidden())
        visible = total - hidden_count
        self.status.setText(f"显示 {visible} 个应用 · 隐藏 {hidden_count} 个 · 共 {total} 个")

class NiriConfigPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel("Niri 窗口管理器配置")
        title.setStyleSheet(f"color: {FG}; font-size: 26px; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        subtitle = QLabel("快速定位并编辑 ~/.config/niri 目录下的模块化配置文件。保存文件后 Niri 会自动应用更改。")
        subtitle.setStyleSheet(f"color: {FG_MUTED}; font-size: 13px; background: transparent;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(24)
        
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(16)
        
        configs = [
            ("主配置文件", "config.kdl", "preferences-system"),
            ("自启动应用", "cfg/autostart.kdl", "system-run"),
            ("快捷键映射", "cfg/keybinds.kdl", "preferences-desktop-keyboard"),
            ("输入设备", "cfg/input.kdl", "preferences-desktop-mouse"),
            ("显示与屏幕", "cfg/display.kdl", "preferences-desktop-display"),
            ("窗口布局", "cfg/layout.kdl", "view-grid"),
            ("窗口规则", "cfg/rules.kdl", "preferences-system-windows"),
            ("动画与特效", "cfg/animation.kdl", "applications-multimedia"),
            ("颜色主题", "cfg/colors.kdl", "preferences-desktop-color"),
            ("其他高级设置", "cfg/misc.kdl", "preferences-other"),
            ("专属定制配置", "noctalia.kdl", "preferences-other")
        ]
        
        row, col = 0, 0
        for name, path, icon in configs:
            card = self.create_config_card(name, path, icon)
            grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        layout.addWidget(grid_widget)
        
    def create_config_card(self, name, rel_path, icon_name):
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border-radius: 16px; border: 1px solid transparent; }}
            QFrame:hover {{ background-color: {BG_HOVER}; border: 1px solid {BORDER}; }}
        """)
        card.setFixedHeight(80)
        
        h = QHBoxLayout(card)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(16)
        
        icon = QLabel()
        icon.setFixedSize(40, 40)
        qicon = QIcon.fromTheme(icon_name)
        if qicon.isNull(): qicon = QIcon.fromTheme("text-x-generic")
        icon.setPixmap(qicon.pixmap(40, 40))
        icon.setStyleSheet("background: transparent;")
        
        v = QVBoxLayout()
        v.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        v.setSpacing(4)
        title = QLabel(name)
        title.setStyleSheet(f"color: {FG}; font-size: 15px; font-weight: bold; background: transparent;")
        path_lbl = QLabel(rel_path)
        path_lbl.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px; background: transparent;")
        v.addWidget(title)
        v.addWidget(path_lbl)
        
        h.addWidget(icon)
        h.addLayout(v, 1)
        
        def open_file(e, rp=rel_path):
            full_path = os.path.expanduser(f"~/.config/niri/{rp}")
            if not os.path.exists(os.path.dirname(full_path)):
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
            if not os.path.exists(full_path):
                open(full_path, "w").close()
            subprocess.Popen(["xdg-open", full_path])
            
        card.mouseReleaseEvent = open_file
        return card

class QuickActionsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel("常用工具与快速操作")
        title.setStyleSheet(f"color: {FG}; font-size: 26px; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        subtitle = QLabel("在此处快速执行系统管理、环境调整与监控操作。")
        subtitle.setStyleSheet(f"color: {FG_MUTED}; font-size: 13px; background: transparent;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(24)
        
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(16)
        
        actions = [
            ("重载 Niri 配置", "niri msg action reload-config", "view-refresh"),
            ("重载 Fcitx5 输入法", "fcitx5-remote -r || fcitx5 -r -d", "preferences-desktop-keyboard"),
            ("重启 Shell/UI 环境", "killall noctalia; noctalia &", "system-run")
        ]
        
        row, col = 0, 0
        for name, cmd, icon in actions:
            card = self.create_action_card(name, cmd, icon)
            grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        layout.addWidget(grid_widget)
        
    def create_action_card(self, name, cmd, icon_name):
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border-radius: 16px; border: 1px solid transparent; }}
            QFrame:hover {{ background-color: {BG_HOVER}; border: 1px solid {BORDER}; }}
        """)
        card.setFixedHeight(80)
        
        h = QHBoxLayout(card)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(16)
        
        icon = QLabel()
        icon.setFixedSize(40, 40)
        qicon = QIcon.fromTheme(icon_name)
        if qicon.isNull(): qicon = QIcon.fromTheme("system-run")
        icon.setPixmap(qicon.pixmap(40, 40))
        icon.setStyleSheet("background: transparent;")
        
        v = QVBoxLayout()
        v.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        v.setSpacing(4)
        title = QLabel(name)
        title.setStyleSheet(f"color: {FG}; font-size: 15px; font-weight: bold; background: transparent;")
        cmd_lbl = QLabel(cmd)
        cmd_lbl.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px; background: transparent;")
        v.addWidget(title)
        v.addWidget(cmd_lbl)
        
        h.addWidget(icon)
        h.addLayout(v, 1)
        
        def run_action(e, c=cmd):
            try:
                if c.startswith("xdg-open"):
                    subprocess.Popen(shlex.split(c))
                elif c.startswith("niri"):
                    subprocess.Popen(shlex.split(c))
                else:
                    # just spawn it in terminal if it's btop, else normally
                    if c == "btop":
                        subprocess.Popen(["kitty", "-e", "btop"])
                    else:
                        subprocess.Popen(shlex.split(c))
            except Exception:
                pass
                
        card.mouseReleaseEvent = run_action
        return card

class Sidebar(QFrame):
    pageChanged = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet(f"QFrame {{ background-color: {BG_CARD}; border-right: 1px solid {BORDER}; }}")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 24, 12, 24)
        self.layout.setSpacing(6)
        
        title = QLabel("Aether Hub")
        title.setStyleSheet(f"color: {FG_MUTED}; font-size: 13px; font-weight: bold; padding: 0 16px 8px 16px; background-color: transparent; border: none;")
        self.layout.addWidget(title)
        
        self.btns = []
        
    def add_page(self, text, active=False):
        btn = QPushButton("  " + text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {FG_DIM}; border-radius: 20px;
                padding: 10px 16px; text-align: left; font-weight: bold; border: none; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {BG_HOVER}; color: {FG}; }}
            QPushButton:checked {{ background-color: {BG_HOVER}; color: {ACCENT}; }}
        """)
        idx = len(self.btns)
        btn.clicked.connect(lambda _, i=idx: self.on_btn_clicked(i))
        self.layout.addWidget(btn)
        self.btns.append(btn)
        
    def on_btn_clicked(self, idx):
        for i, b in enumerate(self.btns):
            b.setChecked(i == idx)
        if not any(b.isChecked() for b in self.btns):
            self.btns[idx].setChecked(True)
        self.pageChanged.emit(idx)
        
    def finish_setup(self):
        self.layout.addStretch()

class AetherHubWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aether Hub")
        self.resize(1000, 750)
        self.setMinimumSize(700, 500)
        self.setStyleSheet(f"QMainWindow {{ background-color: {BG}; }}")
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        self.stacked = QStackedWidget()
        self.stacked.setStyleSheet(f"QStackedWidget {{ background-color: {BG}; }}")
        main_layout.addWidget(self.stacked, 1)
        
        self.app_hider_page = AppHiderPage()
        self.niri_page = NiriConfigPage()
        self.actions_page = QuickActionsPage()
        
        self.stacked.addWidget(self.app_hider_page)
        self.stacked.addWidget(self.niri_page)
        self.stacked.addWidget(self.actions_page)
        
        self.sidebar.pageChanged.connect(self.stacked.setCurrentIndex)
        
        self.sidebar.add_page("应用可见性", active=True)
        self.sidebar.add_page("Niri 窗口管理器")
        self.sidebar.add_page("常用工具操作")
        self.sidebar.finish_setup()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AetherHubWindow()
    window.show()
    sys.exit(app.exec())
