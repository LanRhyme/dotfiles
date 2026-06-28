"""
    label-box adds a color label box on the layer docker like CSP
    Copyright (C) 2022  LunarKreatures

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

# For autocomplete
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .PyKrita import *
else:
    from krita import *
    
from PyQt6.QtWidgets import QHBoxLayout, QComboBox, QWidget
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QTimer
from .kritaUtils import getCurrentLayer, getSelectedLayers

# Colors for the color labels, copied from krita code in KisNodeViewColorScheme.cpp
transparentColor = QColor(Qt.GlobalColor.transparent) #0
blueColor = QColor(91,173,220) #1
greenColor = QColor(151,202,63) #2
yellowColor = QColor(247,229,61) #3
orangeColor = QColor(255,170,63) #4
brownColor = QColor(177,102,63) #5
redColor = QColor(238,50,51) #6
purpleColor = QColor(191,106,209) #7
greyColor = QColor(118,119,114) #8

class LabelBox(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.comboBox = self.buildComboBox()
        self.icons = []
        for i in range(self.comboBox.count()):
            self.icons.append(self.comboBox.itemIcon(i))
            
        application = Krita.instance()
        appNotifier  = application.notifier()
        appNotifier.windowCreated.connect(self.addElement)

    def setup(self):
        pass

    def createActions(self, window):
        pass

    def addElement(self):
        layerDocker = next((w for w in Krita.instance().dockers() if w.objectName() == 'KisLayerBox'), None)
        if not layerDocker: return
        
        layout = layerDocker.findChild(QHBoxLayout,'hbox2')
        if layout:
            layout.insertWidget(0,self.comboBox)
            self.comboBox.activated.connect(self.updateLayerColorLabel)
            
        # Optional: Shrink blending mode combobox to prevent overlap if docker is too narrow
        cmb = layerDocker.findChild(QWidget, 'cmbCompositeOp')
        if not cmb:
            cmb = layerDocker.findChild(QWidget, 'cmbComposite')
        if cmb:
            cmb.setMinimumWidth(0)

        appNotifier = Krita.instance().notifier()
        appNotifier.imageCreated.connect(self.connectImageSignals)
        
        window = Krita.instance().activeWindow()
        if window:
            window.activeViewChanged.connect(self.onSelectionChanged)
            
        for doc in Krita.instance().documents():
            self.connectDocumentSignals(doc)
            
        self.selectionTimer = QTimer()
        self.selectionTimer.timeout.connect(self.onSelectionChanged)
        self.selectionTimer.start(250)

    def connectImageSignals(self, image):
        self.onSelectionChanged()

    def connectDocumentSignals(self, doc):
        if not doc: return
        node_inserted = getattr(doc, "nodeInserted", None)
        if hasattr(node_inserted, "connect"):
            node_inserted.connect(self.onSelectionChanged)
        node_removed = getattr(doc, "nodeRemoved", None)
        if hasattr(node_removed, "connect"):
            node_removed.connect(self.onSelectionChanged)

    def onSelectionChanged(self):
        try:
            selectedLayers = getSelectedLayers()
            if len(selectedLayers) > 1:
                self.comboBox.setCurrentIndex(0)
                return
            if len(selectedLayers) == 1:
                layer = selectedLayers[0]
            else:
                layer = getCurrentLayer()
                
            if layer is None:
                self.comboBox.setCurrentIndex(0)
                return
                
            colorLabelIndex = layer.colorLabel()
            if 0 <= colorLabelIndex <= 8:
                # Block signals so setting current index doesn't trigger color change
                self.comboBox.blockSignals(True)
                self.comboBox.setCurrentIndex(colorLabelIndex)
                self.comboBox.blockSignals(False)
            else:
                self.comboBox.setCurrentIndex(0)
        except Exception:
            pass

    def updateLayerColorLabel(self, index):
        selectedLayers = getSelectedLayers()
        if len(selectedLayers) == 0:
            currentLayer = getCurrentLayer()
            if currentLayer:
                currentLayer.setColorLabel(index)
        else:
            for layer in selectedLayers:
                layer.setColorLabel(index)

    def buildComboBox(self)->QComboBox:
        comboBox = QComboBox()
        comboBox.setAccessibleName('colorLabelBox')
        comboBox.setObjectName('colorLabelBox')
        comboBox.setFixedSize(22, 22)
        
        # Completely bypass krita-redesign's QComboBox CSS that adds huge padding and arrows
        comboBox.setStyleSheet("QComboBox#colorLabelBox { min-width: 22px; max-width: 22px; padding: 0px; margin: 0px; border: none; background: transparent; } QComboBox#colorLabelBox::drop-down { border: none; width: 0px; } QComboBox#colorLabelBox::down-arrow { image: none; }")

        colors = [transparentColor,blueColor,greenColor,yellowColor,orangeColor,brownColor,redColor,purpleColor,greyColor]

        for i, color in enumerate(colors):
            colorFill = QPixmap(16, 16)
            if i == 0:
                colorFill.fill(transparentColor)
                painter = QPainter(colorFill)
                pen = QPen()
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawRect(0,0,16,16)
                painter.end()
            else:
                colorFill.fill(color)
                
            colorIcon = QIcon(colorFill)
            comboBox.addItem(colorIcon,'')
            
        return comboBox
