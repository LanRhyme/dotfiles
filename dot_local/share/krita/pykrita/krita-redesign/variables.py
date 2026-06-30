"""
    Plugin for Krita UI Redesign, Copyright (C) 2020 Kapyia, Pedro Reis

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from krita import *
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette

highlight = "8d8768"
background = "21201c"
alternate = "2c2b26"
inactive_text_color = "9f9f9f"
active_text_color = "f3f3f2"

small_tab_size = 14

no_borders_style = " QToolBar { border: none; } "
nu_toolbox_style = f"""
            QWidget {{ 
                background-color: #01{alternate};
            }}
            
            .QScrollArea {{ 
                background-color: #00{background};
            }}
            
            QScrollArea * {{ 
                background-color: #00000000;
            }}
            
            QScrollArea QToolTip {{
                background-color: #{active_text_color};                         
            }}
            
            QAbstractButton {{
                background-color: #aa{background};
                border: none;
                border-radius: 12px;
            }}
            
            QAbstractButton:checked {{
                background-color: #cc{highlight};
            }}
            
            QAbstractButton:hover {{
                background-color: #{highlight};
            }}
            
            QAbstractButton:pressed {{
                background-color: #{alternate};
            }}
        """
nu_toggle_button_style = f"""
        QToolButton {{
            background-color: #aa{background};
            border: none;
            border-radius: 12px;
        }}
        
        QToolButton:hover {{
            background-color: #{highlight};
        }}
        
        QToolButton:pressed {{
            background-color: #{alternate};
        }}
        """

nu_tool_options_style = f"""
        #toolOptionsPad {{
            background-color: #{background};
            border-radius: 18px;
            border: 1px solid #{alternate};
        }}
        #toolOptionsPad > QWidget, #toolOptionsPad QScrollArea, #toolOptionsPad QScrollArea > QWidget {{
            background-color: transparent;
        }}
        """
small_tab_style = f"QTabBar::tab {{ height: {small_tab_size}px; }}"

""" FLAT THEME """

flat_tab_base_style = ""
flat_tab_big_style = ""
flat_tab_small_style = ""
flat_main_window_style = ""
flat_tool_button_style = ""
flat_push_button_style = ""
flat_dock_style = ""
flat_toolbar_style = ""
flat_menu_bar_style = ""
flat_combo_box_style = ""
flat_toolbox_style = ""
flat_status_bar_style = ""
flat_tree_view_style = ""
flat_overview_docker_style = ""

def buildFlatTheme():
    global flat_tab_base_style
    global flat_tab_big_style
    global flat_tab_small_style
    global flat_main_window_style
    global flat_button_style
    global flat_dock_style
    global flat_toolbar_style
    global flat_menu_bar_style
    global flat_combo_box_style
    global flat_toolbox_style
    global flat_status_bar_style
    global flat_tree_view_style
    global flat_overview_docker_style

    flat_overview_docker_style = f"""
        * {{
            background: #{background};
        }} 

        * > QSpinBox {{
            border: none;
            background-color: #{alternate};
            border-radius: 12px;
            padding: 4px;
        }}
        
        KisZoomWidget QSlider::groove:horizontal {{
            height: 6px;
            border-radius: 3px;
        }}
        KisZoomWidget QSlider::handle:horizontal {{
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
            background: #{highlight};
        }}
    """

    flat_tab_base_style = f"""
        QScrollBar:vertical {{ 
            width: 8px; 
            background: transparent;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #{alternate};
            min-height: 20px;
            border-radius: 4px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{ 
            height: 8px; 
            background: transparent;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: #{alternate};
            min-width: 20px;
            border-radius: 4px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        QTabBar {{
            background-color: #{alternate};
            border: none;
            qproperty-drawBase: 0;
            qproperty-expanding: 1;
        }}
    
        QTabBar::tab:!selected {{
            background: #{alternate};
            border-bottom: 2px solid #{alternate};
            border-top: 2px solid #{alternate};
            margin-top: 2px;
            color: #{inactive_text_color};
            padding: 2px 12px;
        }}

        QTabBar::tab:selected {{
            background: #{background};
            border-bottom: 2px solid #{highlight};
            border-top: 2px solid #{background};
            margin-top: 2px;
            color: #{active_text_color};
            padding: 2px 12px;
        }}

        QTabBar::tab:hover {{
           color: #{active_text_color};
        }}
       """
    flat_tab_big_style = f"""QTabBar::tab {{
            border-top-right-radius: 12px;
            border-top-left-radius: 12px;
        }}"""
    flat_tab_small_style = f""" 
        QTabBar::tab {{
            border-top:0px;
            border-bottom: 0px;
            border-top-right-radius: 12px;
            border-top-left-radius: 12px;
            height: {small_tab_size}px;
        }}"""

    flat_main_window_style = f"""
        QHeaderView {{
            background: #{alternate};
        }}
        
        QLineEdit {{
            background: #{alternate};
            border: none;
            border-radius: 12px;
            padding: 4px 12px;
        }}
        
        QTabWidget::pane {{
            border: none;
            background: #{background};
            border-radius: 16px;
        }}

        QSlider::groove:horizontal {{
            background: #{alternate};
            height: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: #{highlight};
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}
        QSlider::handle:horizontal:hover {{
            background: #{active_text_color};
        }}
        QSlider::sub-page:horizontal {{
            background: #{highlight};
            border-radius: 3px;
        }}
        QSlider::add-page:horizontal {{
            background: #{alternate};
            border-radius: 2px;
        }}
        
        QuickSettingsDocker QListView {{
            qproperty-iconSize: 32px 32px;
            qproperty-gridSize: 36px 48px;
            font-size: 10px;
        }}
        QuickSettingsDocker QListView::item {{
            margin: 0px;
            padding: 0px;
        }}

        QStatusBar > * {{
            border: none;
        }}

        KisDoubleSliderSpinBox {{
            background: #{alternate};
            border: none;
            border-radius: 12px;
        }} 
        
        QStatusBar > QPushButton:hover {{
            background: #{highlight};
        }}
        
        QCheckBox, QRadioButton {{
            color: #{active_text_color};
            spacing: 6px;
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 14px;
            height: 14px;
            border-radius: 4px;
            background-color: #{background};
            border: 2px solid #{alternate};
        }}
        QRadioButton::indicator {{
            border-radius: 8px;
        }}
        QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
            border: 2px solid #{highlight};
        }}
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: #{highlight};
            border: 2px solid #{highlight};
        }}
        QProgressBar {{
            background-color: #{alternate};
            border: none;
            border-radius: 6px;
            text-align: center;
            color: #{background};
        }}
        QProgressBar::chunk {{
            background-color: #{highlight};
            border-radius: 6px;
        }}
        QGroupBox {{
            border: 1px solid #{alternate};
            border-radius: 12px;
            margin-top: 14px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 4px;
            left: 10px;
            color: #{inactive_text_color};
        }}
        
        KisWelcomePageWidget {{
            background-color: #{background};
        }}
        KisWelcomePageWidget QListView, QQuickWidget#welcomePage {{
            background-color: #{alternate};
            border-radius: 24px;
            padding: 16px;
            margin: 8px;
        }}
        """
    flat_button_style = f"""QAbstractButton {{
            background: #{background};
            border: none;
            border-radius: 12px;
        }}

        QAbstractButton:checked {{
            background: #{alternate};
            border: none;
        }}

        QAbstractButton:hover {{
            background: #{alternate};
            border: none;
        }}

        QAbstractButton[popupMode="1"] {{
            padding-right: 13px;
            border: none;
        }}

        QPushButton {{
            background: #{background};
            border-radius: 12px;
            border: 1px solid #{alternate};
        }}
        
        """

    flat_dock_style = f""" 
        QAbstractScrollArea {{
            background: #{background};
            border: none;
            border-radius: 12px;
        }}
    
        QDockWidget {{
            titlebar-close-icon: url(:/light_deletelayer.svg);
            titlebar-normal-icon: url(:/light_duplicatelayer.svg);
            border-radius: 16px;
            margin: 2px;
        }}

        QDockWidget::close-button, QDockWidget::float-button {{
            border: none;
            border-radius: 6px;
            background: transparent;
        }}
        
        QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
            background: #{alternate};
        }}

        QDockWidget > * {{
            background-color: #{background};
            border: none;
            border-bottom-right-radius: 16px;
            border-bottom-left-radius: 16px;
            titlebar-close-icon: url(/:16_dark_tab-close.svg);
        }}

        QDockWidget::title {{
            background-color: #{background};
            border: none;
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
            padding: 6px;
        }}"""
    flat_toolbar_style = f"""QToolBar {{
            background-color: #{background};
            border: none;
            border-radius: 12px;
            margin: 4px;
            padding: 4px;
        }}
        QToolBar > QToolButton {{
            border-radius: 8px;
            padding: 4px;
        }}
        """
    flat_menu_bar_style = f"""QMenuBar {{
        background-color: #{background};
        }}
        QMenu, QToolTip, .KisPopupPalette, QDialog {{
            background-color: #{background};
            border: 1px solid #{alternate};
            border-radius: 18px;
        }}
        QMenu::item {{
            padding: 4px 10px;
            border-radius: 8px;
            margin: 2px 4px;
        }}
        QMenu::item:selected {{
            background-color: #{highlight};
        }}
        """
    flat_combo_box_style = f"""QComboBox {{ 
            background: #{alternate};
            border: none;
            border-radius: 12px;
            padding: 4px 12px;
        }}

        QComboBox:hover {{
            background: #{highlight};
            color: #{background};
        }}
        
        QComboBox::drop-down {{
            border: none;
            border-radius: 12px;
        }}
        
        QComboBox::down-arrow {{
            image: url(:16_light_draw-arrow-down.svg);
            width: 9px;
        }}"""
    flat_toolbox_style = "* > QToolButton {border: none;}"
    flat_status_bar_style = f"""
        QStatusBar {{ 
            background-color: #{background}; 
            max-height: 28px;
            padding: 0px;
        }}
        QStatusBar QLabel, QStatusBar QPushButton, QStatusBar QToolButton {{
            font-size: 11px;
            margin: 0px;
            padding: 0px 4px;
        }}
        QStatusBar KisDoubleSliderSpinBox {{
            font-size: 11px;
            max-height: 18px;
            min-height: 18px;
        }}
        QStatusBar KisDoubleSliderSpinBox QLineEdit {{
            font-size: 11px;
            padding: 0px;
        }}
        QStatusBar::item {{
            border: none;
            padding: 0px;
        }}
        QStatusBar KisAngleSelector, QStatusBar KisAngleGauge, QStatusBar QDial {{
            max-width: 0px;
            max-height: 0px;
            margin: 0px;
            padding: 0px;
            border: none;
        }}
    """
    flat_tree_view_style = f"""QTreeView, QListView, KisResourceItemListView, QListWidget, QTableView, #WdgPresetChooser {{
        background-color: #{background}; 
        border: none;
        padding: 8px;
        border-radius: 16px;
        outline: none;
    }}
    KisResourceItemListView::item, QListView::item, QListWidget::item, QTableView::item {{
        border-radius: 12px;
        padding: 6px;
        margin: 2px;
        border: 1px solid transparent;
        background-color: transparent;
    }}
    KisResourceItemListView::item:selected, QListView::item:selected, QListWidget::item:selected, QTableView::item:selected {{
        background-color: #{highlight} !important;
        border: 1px solid #{highlight} !important;
    }}
    KisResourceItemListView::item:hover, QListView::item:hover, QListWidget::item:hover, QTableView::item:hover {{
        background-color: #{alternate} !important;
        border: 1px solid #{alternate} !important;
    }}
    """
