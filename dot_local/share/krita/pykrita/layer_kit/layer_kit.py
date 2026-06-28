# Layer Kit — Krita Python Plugin (Krita 5.2+)
#
# This plugin patches the existing built-in "Layers" docker (KisLayerBox)
# by locating its internal Qt widgets/layouts and inserting/hiding controls.
#
# Layout structure from Krita's WdgLayerBox.ui:
# - hbox1: Bottom bar with bnAdd, bnDuplicate, bnLower, bnRaise, bnProperties, spacer, bnDelete
# - hbox2: Top bar with cmbComposite (blending mode), bnLayerFilters
# - opacityLayout: Opacity row with opacityLabel, doubleOpacity, configureLayerDockerToolbar
# - horizontalLayout: Contains listLayers (NodeView)

from __future__ import annotations

import os
import re
from typing import Optional, List, Dict, Tuple, Set

from krita import Extension, Krita

from PyQt6.QtCore import Qt, QTimer, QObject, QSize, QEvent
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDockWidget,
    QToolButton,
    QHBoxLayout,
    QDoubleSpinBox,
    QTreeView,
    QAbstractItemView,
    QWidget,
)
from PyQt6.QtCore import QItemSelectionModel


def _plugin_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _icon_path(filename: str) -> str:
    return os.path.join(_plugin_dir(), "icons", filename)


def _load_icon(filename: str) -> QIcon:
    path = _icon_path(filename)
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()


def _safe_set_visible(w: Optional[QWidget], visible: bool) -> None:
    if w is None:
        return
    w.setVisible(visible)
    w.setEnabled(visible)


def _find_action_by_ids(action_ids: List[str]):
    """Return first QAction found by id among action_ids, else None."""
    inst = Krita.instance()
    for aid in action_ids:
        try:
            act = inst.action(aid)
        except Exception:
            act = None
        if act is not None:
            return act
    return None


def _find_action_by_text(needles: List[str]):
    """
    Best-effort action lookup by visible text.
    needles: list of substrings that must all appear (case-insensitive) in action.text().
    """
    inst = Krita.instance()
    actions = None
    try:
        actions = inst.actions()
    except Exception:
        actions = None
    if not actions:
        return None

    needles_l = [n.lower() for n in needles]
    for act in actions:
        try:
            text = (act.text() or "").lower()
        except Exception:
            continue
        if all(n in text for n in needles_l):
            return act
    return None


class MoveLayerToolButton(QToolButton):
    """
    Custom QToolButton that handles both left-click (normal move) and 
    right-click (move to absolute top/bottom of layer tree).
    
    Left-click: Move layer one position up/down
    Right-click: Move layer to absolute top/bottom of entire layer stack
    """
    
    def __init__(self, patcher: 'LayersDockerPatcher', is_move_up: bool, parent: QWidget = None):
        super().__init__(parent)
        self._patcher = patcher
        self._is_move_up = is_move_up
        
        # Configure button appearance to match Krita's style
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Set tooltip
        if is_move_up:
            self.setToolTip("Move Layer Up\nRight-click: Move to Top of Layer Stack")
            self.setObjectName("btnMoveUp_LayerKit")
        else:
            self.setToolTip("Move Layer Down\nRight-click: Move to Bottom of Layer Stack")
            self.setObjectName("btnMoveDown_LayerKit")
    
    def set_icon_from_button(self, original_button: QToolButton) -> None:
        """Copy icon and size from original button."""
        if original_button is None:
            return
        try:
            icon = original_button.icon()
            if not icon.isNull():
                self.setIcon(icon)
            icon_size = original_button.iconSize()
            if not icon_size.isEmpty():
                self.setIconSize(icon_size)
            # Match size policies
            self.setMinimumSize(original_button.minimumSize())
            self.setMaximumSize(original_button.maximumSize())
            size_hint = original_button.sizeHint()
            if size_hint.isValid():
                self.setFixedSize(size_hint)
        except Exception:
            pass
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse button press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Left-click: normal move up/down one position
            self._do_single_move()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # Right-click: move to absolute top/bottom
            if self._is_move_up:
                self._patcher._move_to_top()
            else:
                self._patcher._move_to_bottom()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release - consume to prevent unwanted behavior."""
        event.accept()
    
    def contextMenuEvent(self, event) -> None:
        """Override to prevent context menu from appearing on right-click."""
        event.accept()
    
    def _do_single_move(self) -> None:
        """Perform a single move up or down."""
        if self._is_move_up:
            action = _find_action_by_ids([
                "move_layer_up",
                "raise_layer",
                "layer_raise",
                "RaiseLayers",
            ])
            if action is None:
                action = _find_action_by_text(["raise", "layer"])
        else:
            action = _find_action_by_ids([
                "move_layer_down",
                "lower_layer",
                "layer_lower",
                "LowerLayers",
            ])
            if action is None:
                action = _find_action_by_text(["lower", "layer"])
        
        if action is not None:
            try:
                action.trigger()
            except Exception:
                pass


class ClippingMaskUndoMonitor(QObject):
    """
    Event-based monitor for detecting when a clipping mask's quick group is undone.
    
    Uses Qt model signals (rowsRemoved, layoutChanged) and Krita's notifier
    to detect when the layer structure changes. When the monitored node's parent
    changes (indicating the quick group was undone), restores the original
    alpha inheritance state.
    
    This provides a clean single-undo experience where both the grouping and
    the alpha inheritance change are effectively reversed together.
    """
    
    def __init__(
        self,
        patcher: 'LayersDockerPatcher',
        node_uid,
        node_name: str,
        node_type: str,
        parent_uid,
        original_alpha_state: bool,
        tree_view: Optional[QTreeView] = None,
        parent: QObject = None
    ):
        super().__init__(parent)
        self._patcher = patcher
        self._node_uid = node_uid
        self._node_name = node_name
        self._node_type = node_type
        self._parent_uid = parent_uid
        self._original_alpha_state = original_alpha_state
        self._tree_view = tree_view
        self._model = None
        self._connected = False
        self._stopped = False
    
    def start_monitoring(self) -> None:
        """Start event-based monitoring for undo detection."""
        if self._connected or self._stopped:
            return
        
        # Connect to the layer tree view's model signals
        if self._tree_view is not None:
            self._connect_to_model()
        
        # Connect to Krita's notifier for image changes
        self._connect_to_notifier()
        
        self._connected = True
    
    def _connect_to_model(self) -> None:
        """Connect to the tree view's model signals for structure changes."""
        if self._tree_view is None:
            return
        
        try:
            model = self._tree_view.model()
            if model is not None:
                self._model = model
                # Connect to signals that fire when layer structure changes
                model.rowsRemoved.connect(self._on_structure_changed)
                model.rowsInserted.connect(self._on_structure_changed)
                model.layoutChanged.connect(self._on_structure_changed)
        except Exception:
            pass
    
    def _connect_to_notifier(self) -> None:
        """Connect to Krita's notifier for image modification events."""
        try:
            notifier = Krita.instance().notifier()
            if notifier is not None:
                # imageUpdated fires on many changes including undo
                if hasattr(notifier, 'imageUpdated'):
                    notifier.imageUpdated.connect(self._on_structure_changed)
        except Exception:
            pass
    
    def _on_structure_changed(self, *args) -> None:
        """Handle structure change signals - check if undo occurred."""
        if self._stopped:
            return
        
        try:
            self._check_for_undo()
        except Exception:
            pass
    
    def _check_for_undo(self) -> None:
        """Check if the quick group has been undone by examining the node's parent."""
        if self._stopped:
            return
        
        app = Krita.instance()
        doc = app.activeDocument()
        if doc is None:
            return
        
        # Find the node
        current_node = None
        if self._node_uid is not None:
            try:
                current_node = doc.nodeByUniqueID(self._node_uid) if callable(getattr(doc, "nodeByUniqueID", None)) else None
            except Exception:
                pass
        
        if current_node is None and self._node_name is not None:
            current_node = self._patcher._find_node_by_name_and_type(doc, self._node_name, self._node_type)
        
        if current_node is None:
            # Node not found, stop monitoring
            self._stop_monitoring()
            return
        
        # Check if the node's parent has changed
        current_parent = None
        try:
            current_parent = current_node.parentNode() if callable(getattr(current_node, "parentNode", None)) else None
        except Exception:
            pass
        
        if current_parent is None:
            # Node has no parent, undo likely happened
            self._restore_and_stop(current_node)
            return
        
        # Check if the parent is still the same group
        current_parent_uid = None
        try:
            current_parent_uid = current_parent.uniqueId() if callable(getattr(current_parent, "uniqueId", None)) else None
        except Exception:
            pass
        
        # Check parent type
        current_parent_type = ""
        try:
            current_parent_type = (current_parent.type() if callable(getattr(current_parent, "type", None)) else "").lower()
        except Exception:
            pass
        
        # If parent changed (different UID) or parent is no longer a group, undo happened
        parent_changed = (self._parent_uid is not None and current_parent_uid is not None and self._parent_uid != current_parent_uid)
        parent_not_group = "group" not in current_parent_type or current_parent_type == "rootlayer"
        
        if parent_changed or parent_not_group:
            # Undo detected - restore original alpha state
            self._restore_and_stop(current_node)
    
    def _restore_and_stop(self, node) -> None:
        """Restore alpha state and stop monitoring."""
        if self._stopped:
            return
        
        # Restore the original alpha inheritance state
        self._patcher._restore_alpha_state(node, self._original_alpha_state)
        
        # Stop monitoring
        self._stop_monitoring()
    
    def _stop_monitoring(self) -> None:
        """Disconnect all signals and stop monitoring."""
        if self._stopped:
            return
        
        self._stopped = True
        self._connected = False
        
        # Disconnect from model signals
        if self._model is not None:
            try:
                self._model.rowsRemoved.disconnect(self._on_structure_changed)
            except Exception:
                pass
            try:
                self._model.rowsInserted.disconnect(self._on_structure_changed)
            except Exception:
                pass
            try:
                self._model.layoutChanged.disconnect(self._on_structure_changed)
            except Exception:
                pass
            self._model = None
        
        # Disconnect from notifier
        try:
            notifier = Krita.instance().notifier()
            if notifier is not None and hasattr(notifier, 'imageUpdated'):
                try:
                    notifier.imageUpdated.disconnect(self._on_structure_changed)
                except Exception:
                    pass
        except Exception:
            pass
        
        # Remove from patcher's list
        if hasattr(self._patcher, '_undo_monitors'):
            try:
                self._patcher._undo_monitors.remove(self)
            except (ValueError, AttributeError):
                pass


class GroupLayerLabeler(QObject):
    """
    Monitors the document and automatically:
    1. Applies Krita's color label to group layers (using native setColorLabel() method)
    2. Renames newly created groups to use sequential numbering independent of paint layers

    Color label indices in Krita:
    0 = None (no color)
    1 = Blue
    2 = Green
    3 = Yellow
    4 = Orange
    5 = Brown
    6 = Red
    7 = Purple
    8 = Grey

    Group Renaming Logic:
    - Krita by default names layers/groups with a shared counter (Paint layer 1, Group 2, Paint layer 3...)
    - This class detects new groups matching the default pattern "Group N"
    - It renames them to use a separate sequence (Group 1, Group 2, Group 3...)
    - User-renamed groups (not matching "Group N" pattern) are left untouched

    Detection Method:
    - Uses Qt's QAbstractItemModel.rowsInserted signal from the layer tree view
    - This is event-based and fires immediately when layers are added (no polling)
    - Falls back to processing all groups on initial setup
    """

    # Default color label for group layers (8 = Grey)
    GROUP_LABEL_COLOR = 8

    # Regex pattern to match Krita's default group naming: "Group" followed by space and number
    # This pattern matches: "Group 1", "Group 47", etc.
    DEFAULT_GROUP_NAME_PATTERN = re.compile(r'^Group\s+(\d+)$', re.IGNORECASE)

    def __init__(self, tree_view: Optional[QTreeView] = None, parent: QObject = None):
        super().__init__(parent)
        self._labeled_nodes: Set[str] = set()  # Track nodes we've already labeled by uniqueId
        self._renamed_nodes: Set[str] = set()  # Track nodes we've already processed for renaming
        self._tree_view: Optional[QTreeView] = tree_view
        self._model = None  # Store reference to connected model
        self._connected = False
        self._notifier_connected = False

    def start_monitoring(self) -> None:
        """Start event-based monitoring for new group layers using model signals."""
        if self._connected:
            return

        # Connect to the layer tree view's model rowsInserted signal
        if self._tree_view is not None:
            self._connect_to_model()

        # Connect to Krita's notifier for document/view changes
        self._connect_to_notifier()

        # Do an initial check to process any existing groups
        QTimer.singleShot(100, self._check_and_process_groups)

    def _connect_to_notifier(self) -> None:
        """Connect to Krita's notifier for document and view change events."""
        if self._notifier_connected:
            return

        try:
            notifier = Krita.instance().notifier()
            if notifier is not None:
                # Reconnect to model when a new document is created
                notifier.imageCreated.connect(self._on_image_created)
                # Also handle view creation for document switching
                notifier.viewCreated.connect(self._on_view_created)
                self._notifier_connected = True
        except Exception:
            pass

    def _on_image_created(self, doc) -> None:
        """Handle imageCreated signal - reconnect to model and process groups."""
        # Delay to allow the UI to update
        QTimer.singleShot(5, self._reconnect_and_process)

    def _on_view_created(self, view) -> None:
        """Handle viewCreated signal - reconnect to model for the new view."""
        # Delay to allow the UI to update
        QTimer.singleShot(5, self._reconnect_and_process)

    def _reconnect_and_process(self) -> None:
        """Reconnect to the model and process groups."""
        if self._tree_view is not None:
            self._connect_to_model()
        self._check_and_process_groups()

    def _connect_to_model(self) -> None:
        """Connect to the tree view's model rowsInserted signal."""
        if self._tree_view is None:
            return

        try:
            model = self._tree_view.model()
            if model is not None and model != self._model:
                # Disconnect from old model if exists
                if self._model is not None:
                    try:
                        self._model.rowsInserted.disconnect(self._on_rows_inserted)
                    except Exception:
                        pass

                # Connect to new model's rowsInserted signal
                model.rowsInserted.connect(self._on_rows_inserted)
                self._model = model
                self._connected = True
        except Exception:
            pass

    def _on_rows_inserted(self, parent, first: int, last: int) -> None:
        """
        Handle rowsInserted signal from the layer tree model.
        This is called whenever new layers/nodes are added to the tree.

        Args:
            parent: QModelIndex of the parent item
            first: First row index of inserted items
            last: Last row index of inserted items (inclusive)
        """
        # Process immediately - the node is fully initialized when rowsInserted fires.
        # Using a timer here would cause a visible flash as the view repaints before we rename.
        self._check_and_process_groups()

    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        # Disconnect from model signals
        if self._model is not None:
            try:
                self._model.rowsInserted.disconnect(self._on_rows_inserted)
            except Exception:
                pass
            self._model = None
        self._connected = False

        # Disconnect from notifier signals
        if self._notifier_connected:
            try:
                notifier = Krita.instance().notifier()
                if notifier is not None:
                    try:
                        notifier.imageCreated.disconnect(self._on_image_created)
                    except Exception:
                        pass
                    try:
                        notifier.viewCreated.disconnect(self._on_view_created)
                    except Exception:
                        pass
            except Exception:
                pass
            self._notifier_connected = False
    
    def _check_and_process_groups(self) -> None:
        """Check all documents and process (label + rename) group layers."""
        try:
            app = Krita.instance()
            docs = app.documents()
            if not docs:
                return
            
            for doc in docs:
                self._process_groups_in_document(doc)
        except Exception:
            pass
    
    def _process_groups_in_document(self, doc) -> None:
        """Process all group layers in a document: apply labeling and auto-rename new groups."""
        if doc is None:
            return
        
        try:
            root = doc.rootNode()
            if root is None:
                return
            
            # First pass: collect all groups and find the highest existing group number
            all_groups = []
            self._collect_all_groups(root, all_groups)
            
            # Find the highest numbered group that follows the "Group N" pattern
            highest_group_num = self._find_highest_group_number(all_groups)
            
            # Second pass: process each group (label + rename if needed)
            for group_node in all_groups:
                self._process_single_group(group_node, doc, highest_group_num)
                
        except Exception:
            pass
    
    def _collect_all_groups(self, node, groups_list: List) -> None:
        """Recursively collect all group layer nodes."""
        if node is None:
            return
        
        try:
            children = node.childNodes() if callable(getattr(node, "childNodes", None)) else []
        except Exception:
            children = []
        
        for child in children:
            try:
                node_type = child.type() if callable(getattr(child, "type", None)) else ""
                node_type_lower = (node_type or "").lower()
                
                is_group = ("group" in node_type_lower) and ("mask" not in node_type_lower)
                
                if is_group:
                    groups_list.append(child)
                
                # Recurse into children (groups can contain groups)
                self._collect_all_groups(child, groups_list)
                
            except Exception:
                continue
    
    def _find_highest_group_number(self, groups: List) -> int:
        """
        Find the highest number N from all groups named "Group N".
        Returns 0 if no numbered groups exist.
        """
        highest = 0
        
        for group in groups:
            try:
                name = group.name() if callable(getattr(group, "name", None)) else ""
                if not name:
                    continue
                
                match = self.DEFAULT_GROUP_NAME_PATTERN.match(name.strip())
                if match:
                    num = int(match.group(1))
                    if num > highest:
                        highest = num
            except Exception:
                continue
        
        return highest
    
    def _get_node_uid(self, node) -> Optional[str]:
        """Get a unique identifier for a node."""
        node_uid = None
        if callable(getattr(node, "uniqueId", None)):
            try:
                uid = node.uniqueId()
                # uniqueId returns a QUuid, convert to string
                node_uid = str(uid.toString()) if hasattr(uid, 'toString') else str(uid)
            except Exception:
                node_uid = None
        
        # Fallback identifier using name + type + some identifier
        if node_uid is None:
            try:
                node_name = node.name() if callable(getattr(node, "name", None)) else ""
                node_type = node.type() if callable(getattr(node, "type", None)) else ""
                node_uid = f"{node_name}_{node_type}_{id(node)}"
            except Exception:
                node_uid = str(id(node))
        
        return node_uid
    
    def _process_single_group(self, group_node, doc, current_highest: int) -> None:
        """Process a single group node: apply color label and rename if it's a new default-named group."""
        try:
            node_uid = self._get_node_uid(group_node)
            if node_uid is None:
                return
            
            # Get current group name
            current_name = group_node.name() if callable(getattr(group_node, "name", None)) else ""
            
            # === RENAMING LOGIC ===
            # Check if this group needs renaming (new group with default name)
            if node_uid not in self._renamed_nodes:
                # Check if name matches Krita's default pattern "Group N"
                match = self.DEFAULT_GROUP_NAME_PATTERN.match(current_name.strip()) if current_name else None
                
                if match:
                    # This is a default-named group - check if it needs renaming
                    current_num = int(match.group(1))
                    
                    # Calculate what the next sequential number should be
                    # We need to find the highest number among ALL other groups (excluding this one)
                    other_highest = self._find_highest_excluding(doc, group_node)
                    expected_next = other_highest + 1
                    
                    # If the current number is higher than expected, this is likely a new group
                    # that inherited Krita's global counter and needs renaming
                    if current_num > expected_next:
                        new_name = f"Group {expected_next}"
                        try:
                            if callable(getattr(group_node, "setName", None)):
                                group_node.setName(new_name)
                                # Update the document to reflect changes
                                if callable(getattr(doc, "refreshProjection", None)):
                                    doc.refreshProjection()
                        except Exception:
                            pass
                
                # Mark as processed for renaming
                self._renamed_nodes.add(node_uid)
            
            # === LABELING LOGIC ===
            # Check if already labeled by us
            if node_uid not in self._labeled_nodes:
                # Check current color label
                current_label = 0
                if callable(getattr(group_node, "colorLabel", None)):
                    try:
                        current_label = group_node.colorLabel()
                    except Exception:
                        current_label = 0
                
                # Only set label if not already set (0 = no color)
                if current_label == 0:
                    if callable(getattr(group_node, "setColorLabel", None)):
                        try:
                            group_node.setColorLabel(self.GROUP_LABEL_COLOR)
                            self._labeled_nodes.add(node_uid)
                        except Exception:
                            pass
                else:
                    # Already has a label, just track it
                    self._labeled_nodes.add(node_uid)
                    
        except Exception:
            pass
    
    def _find_highest_excluding(self, doc, exclude_node) -> int:
        """
        Find the highest group number, excluding a specific node.
        This is used to determine what number a new group should have.
        """
        if doc is None:
            return 0
        
        try:
            root = doc.rootNode()
            if root is None:
                return 0
            
            exclude_uid = self._get_node_uid(exclude_node)
            highest = 0
            
            def scan_nodes(parent):
                nonlocal highest
                if parent is None:
                    return
                
                try:
                    children = parent.childNodes() if callable(getattr(parent, "childNodes", None)) else []
                except Exception:
                    return
                
                for child in children:
                    try:
                        node_type = child.type() if callable(getattr(child, "type", None)) else ""
                        node_type_lower = (node_type or "").lower()
                        
                        is_group = ("group" in node_type_lower) and ("mask" not in node_type_lower)
                        
                        if is_group:
                            child_uid = self._get_node_uid(child)
                            
                            # Skip the excluded node
                            if child_uid != exclude_uid:
                                name = child.name() if callable(getattr(child, "name", None)) else ""
                                if name:
                                    match = self.DEFAULT_GROUP_NAME_PATTERN.match(name.strip())
                                    if match:
                                        num = int(match.group(1))
                                        if num > highest:
                                            highest = num
                        
                        # Recurse into children
                        scan_nodes(child)
                        
                    except Exception:
                        continue
            
            scan_nodes(root)
            return highest
            
        except Exception:
            return 0


class LayersDockerPatcher(QObject):
    """
    Encapsulates patching logic for one KisLayerBox docker instance.
    Uses layout names from Krita's WdgLayerBox.ui for reliable widget insertion.
    """

    def __init__(self, docker: QDockWidget, parent: QObject = None):
        super().__init__(parent)
        self.docker = docker
        self.tree: Optional[QTreeView] = None
        self._labeler: Optional[GroupLayerLabeler] = None
        self._patched_buttons = set()  # Track what we've already added
        
        # Store references to our custom buttons to prevent garbage collection
        self._move_up_button: Optional[QToolButton] = None
        self._move_down_button: Optional[QToolButton] = None
        self._original_raise: Optional[QToolButton] = None
        self._original_lower: Optional[QToolButton] = None

    def apply(self) -> None:
        self._add_group_button()
        self._add_clipping_mask_button()
        self._patch_move_buttons()
        self._install_group_layer_labeling()

    def _add_group_button(self) -> None:
        """Add the 'Add Group Layer' button to the right of bnAdd in hbox1 (bottom bar)."""
        btn_name = "btnAddGroupLayer_LayerKit"
        
        # Check if already added
        if btn_name in self._patched_buttons:
            return
        existing = self.docker.findChild(QToolButton, btn_name)
        if existing is not None:
            self._patched_buttons.add(btn_name)
            return

        # Find the bottom bar layout by name (hbox1 from WdgLayerBox.ui)
        hbox1 = self.docker.findChild(QHBoxLayout, "hbox1")
        
        # Find bnAdd for reference
        bn_add = self.docker.findChild(QToolButton, "bnAdd")
        if bn_add is None:
            return
            
        # If layout not found by name, get it from bnAdd's parent
        if hbox1 is None:
            parent_w = bn_add.parentWidget()
            if parent_w is None:
                return
            hbox1 = parent_w.layout()
            if hbox1 is None:
                return

        add_index = self._index_of_widget(hbox1, bn_add)
        
        # Get the parent widget for the new button
        parent_widget = bn_add.parentWidget()
        if parent_widget is None:
            return

        btn = QToolButton(parent_widget)
        btn.setObjectName(btn_name)
        btn.setAutoRaise(True)
        btn.setIcon(_load_icon("folder.png"))
        btn.setIconSize(QSize(20, 20))
        btn.setToolTip("Add Group Layer")
        btn.setMinimumSize(28, 28)

        def on_click():
            act = _find_action_by_ids([
                "add_new_group_layer",
                "add_group_layer",
                "layer_add_group",
                "add_group",
            ])
            if act is None:
                act = _find_action_by_text(["add", "group", "layer"])
            if act is not None:
                act.trigger()

        btn.clicked.connect(on_click)

        # Insert right after bnAdd (index + 1)
        if add_index != -1:
            hbox1.insertWidget(add_index + 1, btn)
        else:
            # Fallback: insert at position 1
            hbox1.insertWidget(1, btn)
        
        self._patched_buttons.add(btn_name)

    def _patch_move_buttons(self) -> None:
        """
        Hide the original bnRaise and bnLower buttons and replace them with
        custom MoveLayerToolButton instances that support right-click for
        move-to-top and move-to-bottom functionality.
        
        The buttons are placed after bnDuplicate in order: Move Up, then Move Down.
        This matches the visual expectation (up arrow before down arrow).
        
        Original Krita layout (from WdgLayerBox.ui):
        hbox1: bnAdd, bnDuplicate, bnLower, bnRaise, bnProperties, spacer, bnDelete
        
        After patching (visible buttons):
        hbox1: bnAdd, bnDuplicate, [MoveUp], [MoveDown], bnProperties, spacer, bnDelete
        """
        patch_name = "moveButtonsReplaced_LayerKit"
        
        # Check if already patched
        if patch_name in self._patched_buttons:
            return
        if self.docker.property(patch_name) is True:
            self._patched_buttons.add(patch_name)
            return
        
        # Find the original move buttons by object name
        bn_raise = self.docker.findChild(QToolButton, "bnRaise")  # Move Up
        bn_lower = self.docker.findChild(QToolButton, "bnLower")  # Move Down
        
        if bn_raise is None and bn_lower is None:
            return  # No buttons found, can't patch
        
        # Find bnDuplicate as our reference point for positioning
        bn_duplicate = self.docker.findChild(QToolButton, "bnDuplicate")
        
        # Find hbox1 layout by name first (same approach as _add_group_button)
        hbox1 = self.docker.findChild(QHBoxLayout, "hbox1")
        
        # Get the parent widget that contains the buttons
        parent_widget = None
        if bn_duplicate is not None:
            parent_widget = bn_duplicate.parentWidget()
        elif bn_raise is not None:
            parent_widget = bn_raise.parentWidget()
        elif bn_lower is not None:
            parent_widget = bn_lower.parentWidget()
        
        if parent_widget is None:
            return
        
        # If hbox1 not found by name, get layout from parent widget
        if hbox1 is None:
            hbox1 = parent_widget.layout()
        
        if hbox1 is None:
            return
        
        # Find the index of bnDuplicate to use as insertion reference
        duplicate_index = -1
        if bn_duplicate is not None:
            duplicate_index = self._index_of_widget(hbox1, bn_duplicate)
        
        # Hide the original buttons
        if bn_raise is not None:
            self._original_raise = bn_raise
            bn_raise.hide()
            bn_raise.setEnabled(False)
        
        if bn_lower is not None:
            self._original_lower = bn_lower
            bn_lower.hide()
            bn_lower.setEnabled(False)
        
        # Determine insertion position (right after bnDuplicate)
        # If bnDuplicate not found, try to find where the original buttons were
        if duplicate_index >= 0:
            insert_pos = duplicate_index + 1
        else:
            # Fallback: find position of first original button in hbox1
            insert_pos = -1
            if bn_lower is not None:
                insert_pos = self._index_of_widget(hbox1, bn_lower)
            if insert_pos < 0 and bn_raise is not None:
                insert_pos = self._index_of_widget(hbox1, bn_raise)
            if insert_pos < 0:
                insert_pos = 2  # Default fallback position after bnAdd and bnDuplicate
        
        # Create Move Up button first (it should appear first, leftmost)
        self._move_up_button = MoveLayerToolButton(
            patcher=self,
            is_move_up=True,
            parent=parent_widget
        )
        
        # Copy icon from original bnRaise button
        if bn_raise is not None:
            self._move_up_button.set_icon_from_button(bn_raise)
        
        # Insert Move Up button into hbox1
        hbox1.insertWidget(insert_pos, self._move_up_button)
        self._move_up_button.show()
        
        # Create Move Down button (it should appear second, to the right of Move Up)
        self._move_down_button = MoveLayerToolButton(
            patcher=self,
            is_move_up=False,
            parent=parent_widget
        )
        
        # Copy icon from original bnLower button
        if bn_lower is not None:
            self._move_down_button.set_icon_from_button(bn_lower)
        
        # Insert Move Down button right after Move Up (insert_pos + 1)
        hbox1.insertWidget(insert_pos + 1, self._move_down_button)
        self._move_down_button.show()
        
        self._patched_buttons.add(patch_name)
        self.docker.setProperty(patch_name, True)

    def _move_to_top(self) -> None:
        """
        Move the currently selected layer to the very top of the ENTIRE layer tree.
        
        Uses Krita's raise_layer action repeatedly to properly handle groups with
        their subcontents and multiple layer selections.
        """
        app = Krita.instance()
        doc = app.activeDocument()
        if doc is None:
            return
        
        try:
            node = doc.activeNode()
        except Exception:
            node = None
        if node is None:
            return
        
        try:
            root = doc.rootNode()
        except Exception:
            root = None
        if root is None:
            return
        
        # Get root level children
        try:
            root_children = root.childNodes() if callable(getattr(root, "childNodes", None)) else []
        except Exception:
            root_children = []
        
        if not root_children:
            return
        
        # Get unique ID of current node
        node_uid = None
        try:
            if callable(getattr(node, "uniqueId", None)):
                node_uid = node.uniqueId()
        except Exception:
            pass
        
        # Check if already at absolute top (is the last child of root)
        top_node = root_children[-1]
        try:
            top_uid = top_node.uniqueId() if callable(getattr(top_node, "uniqueId", None)) else None
            if node_uid is not None and top_uid is not None and node_uid == top_uid:
                return  # Already at top
        except Exception:
            pass
        
        # Use raise_layer action repeatedly to move to absolute top
        raise_action = _find_action_by_ids([
            "move_layer_up",
            "raise_layer",
            "layer_raise",
            "RaiseLayers",
        ])
        if raise_action is None:
            raise_action = _find_action_by_text(["raise", "layer"])
        
        if raise_action is None:
            return
        
        max_moves = len(root_children) + 50  # Safety limit
        
        for _ in range(max_moves):
            try:
                raise_action.trigger()
                
                # Check if we've reached top
                doc_now = app.activeDocument()
                if doc_now is None:
                    break
                    
                current_node = doc_now.activeNode()
                if current_node is None:
                    break
                
                root_now = doc_now.rootNode()
                if root_now is None:
                    break
                    
                children_now = root_now.childNodes() if callable(getattr(root_now, "childNodes", None)) else []
                if not children_now:
                    break
                
                # Check if current node is now at top (last child)
                current_uid = current_node.uniqueId() if callable(getattr(current_node, "uniqueId", None)) else None
                last_uid = children_now[-1].uniqueId() if callable(getattr(children_now[-1], "uniqueId", None)) else None
                
                if current_uid is not None and last_uid is not None and current_uid == last_uid:
                    break  # Reached top
                    
            except Exception:
                break

    def _move_to_bottom(self) -> None:
        """
        Move the currently selected layer to the very bottom of the ENTIRE layer tree.
        
        Note: Krita's Python API addChildNode(child, above) works as follows:
        - When 'above' is None, it actually adds at childCount() (TOP of stack)
        - When 'above' is a node, it places 'child' above that node
        
        To place at the absolute bottom, we need a workaround since we can't
        directly specify "below" a node. We'll use repeated lower_layer action
        as a fallback since the direct API doesn't support true bottom placement.
        """
        app = Krita.instance()
        doc = app.activeDocument()
        if doc is None:
            return
        
        try:
            node = doc.activeNode()
        except Exception:
            node = None
        if node is None:
            return
        
        try:
            root = doc.rootNode()
        except Exception:
            root = None
        if root is None:
            return
        
        # Get root level children
        try:
            root_children = root.childNodes() if callable(getattr(root, "childNodes", None)) else []
        except Exception:
            root_children = []
        
        if not root_children:
            return
        
        # Get unique ID of current node
        node_uid = None
        try:
            if callable(getattr(node, "uniqueId", None)):
                node_uid = node.uniqueId()
        except Exception:
            pass
        
        # Check if already at absolute bottom (is the first child of root)
        bottom_node = root_children[0]
        try:
            bottom_uid = bottom_node.uniqueId() if callable(getattr(bottom_node, "uniqueId", None)) else None
            if node_uid is not None and bottom_uid is not None and node_uid == bottom_uid:
                return  # Already at bottom
        except Exception:
            pass
        
        # Strategy: Move node to root level first (if nested), then use
        # Krita's lower_layer action repeatedly to move to bottom.
        # This is because addChildNode(node, None) actually adds at TOP.
        
        # First, check if node is nested inside a group - if so, move to root
        try:
            parent = node.parentNode() if callable(getattr(node, "parentNode", None)) else None
            parent_uid = None
            if parent is not None and callable(getattr(parent, "uniqueId", None)):
                parent_uid = parent.uniqueId()
            
            root_uid = None
            if callable(getattr(root, "uniqueId", None)):
                root_uid = root.uniqueId()
            
            is_at_root = (parent_uid is not None and root_uid is not None and parent_uid == root_uid)
            
            if not is_at_root and parent is not None:
                # Node is nested, need to move to root first
                if callable(getattr(node, "remove", None)):
                    node.remove()
                
                # Add to root - but addChildNode(node, None) puts at TOP
                # So we add at top first, then lower repeatedly
                if callable(getattr(root, "addChildNode", None)):
                    root.addChildNode(node, None)  # This puts it at top
                
                if callable(getattr(doc, "refreshProjection", None)):
                    doc.refreshProjection()
                
                if callable(getattr(doc, "setActiveNode", None)):
                    doc.setActiveNode(node)
        except Exception:
            pass
        
        # Now use lower_layer action repeatedly to move to absolute bottom
        lower_action = _find_action_by_ids([
            "move_layer_down",
            "lower_layer",
            "layer_lower",
            "LowerLayers",
        ])
        if lower_action is None:
            lower_action = _find_action_by_text(["lower", "layer"])
        
        if lower_action is None:
            return
        
        # Get fresh root children count after potential move
        try:
            root_children = root.childNodes() if callable(getattr(root, "childNodes", None)) else []
        except Exception:
            root_children = []
        
        max_moves = len(root_children) + 50  # Safety limit
        
        for _ in range(max_moves):
            try:
                lower_action.trigger()
                
                # Check if we've reached bottom
                doc_now = app.activeDocument()
                if doc_now is None:
                    break
                    
                current_node = doc_now.activeNode()
                if current_node is None:
                    break
                
                root_now = doc_now.rootNode()
                if root_now is None:
                    break
                    
                children_now = root_now.childNodes() if callable(getattr(root_now, "childNodes", None)) else []
                if not children_now:
                    break
                
                # Check if current node is now at bottom (first child)
                current_uid = current_node.uniqueId() if callable(getattr(current_node, "uniqueId", None)) else None
                first_uid = children_now[0].uniqueId() if callable(getattr(children_now[0], "uniqueId", None)) else None
                
                if current_uid is not None and first_uid is not None and current_uid == first_uid:
                    break  # Reached bottom
                    
            except Exception:
                break

    def _add_clipping_mask_button(self) -> None:
        """Add the 'Clipping Mask' button to the left of the opacity slider in opacityLayout."""
        btn_name = "btnClippingMask_LayerKit"
        
        # Check if already added
        if btn_name in self._patched_buttons:
            return
        existing = self.docker.findChild(QToolButton, btn_name)
        if existing is not None:
            self._patched_buttons.add(btn_name)
            return

        # Find the opacity layout by name (opacityLayout from WdgLayerBox.ui)
        opacity_layout = self.docker.findChild(QHBoxLayout, "opacityLayout")
        
        # Find doubleOpacity for reference
        spin = self.docker.findChild(QDoubleSpinBox, "doubleOpacity")
        if spin is None:
            # Try soft search
            for cand in self.docker.findChildren(QDoubleSpinBox):
                if "opacity" in (cand.objectName() or "").lower():
                    spin = cand
                    break
        if spin is None:
            return
        
        # If layout not found by name, get it from spin's parent
        if opacity_layout is None:
            parent_w = spin.parentWidget()
            if parent_w is None:
                return
            opacity_layout = parent_w.layout()
            if opacity_layout is None:
                return

        spin_index = self._index_of_widget(opacity_layout, spin)
        
        # Get parent widget for button
        parent_widget = spin.parentWidget()
        if parent_widget is None:
            return

        btn = QToolButton(parent_widget)
        btn.setObjectName(btn_name)
        btn.setAutoRaise(True)
        btn.setIcon(_load_icon("clippingmask.png"))
        btn.setIconSize(QSize(22, 22))
        btn.setToolTip("Clipping Mask (Alpha Inheritance + Quick Group)")
        btn.setMinimumSize(28, 28)
        btn.setMaximumSize(32, 32)

        btn.clicked.connect(self._do_clipping_mask_sequence)

        # Insert before the opacity slider
        if spin_index != -1:
            opacity_layout.insertWidget(spin_index, btn)
        else:
            opacity_layout.insertWidget(0, btn)
        
        self._patched_buttons.add(btn_name)

    def _has_layer_below(self, node) -> bool:
        """
        Check if there is a layer/group below the given node in the layer stack.
        Uses the tree view's model to check for siblings below.
        
        Returns True if there's a layer below, False otherwise.
        """
        if self.tree is None:
            self.tree = self._find_layer_tree_view()
        if self.tree is None:
            return False
        
        try:
            sm = self.tree.selectionModel()
            if sm is None:
                return False
            
            current = sm.currentIndex()
            if not current.isValid():
                current = self.tree.currentIndex()
            if not current.isValid():
                return False
            
            model = current.model()
            parent = current.parent()
            row = current.row()
            
            # In Krita's layer view, row+1 is the layer below (toward higher indices)
            below = model.index(row + 1, current.column(), parent)
            if not below.isValid():
                below = model.index(row + 1, 0, parent)
            
            return below.isValid()
        except Exception:
            return False

    def _do_clipping_mask_sequence(self) -> None:
        """
        Implements:
          1) Check if there is a layer below the current node (abort if not)
          2) Enable inherit alpha on current node (without undo entry)
          3) Add layer below to selection (multi-select)
          4) Quick Group the two layers
          5) Ensure the top (clipped) layer is the active/selected layer (only)
          6) Monitor for undo via signals and restore alpha inheritance state if group is dissolved
        """
        app = Krita.instance()
        doc = app.activeDocument()
        if doc is None:
            return
        try:
            node = doc.activeNode()
        except Exception:
            node = None
        if node is None:
            return

        # Ensure we have the tree view for selection manipulation (needed for layer below check)
        if self.tree is None:
            self.tree = self._find_layer_tree_view()

        # 0) Check if there is a layer below the current node
        # If there's no layer below, the clipping mask cannot work, so we abort
        if not self._has_layer_below(node):
            # No layer below - cannot create clipping mask, silently abort
            return

        # Store node info for finding it later and for undo monitoring
        node_name = None
        node_type = None
        node_uid = None
        original_alpha_state = False
        try:
            node_name = node.name() if callable(getattr(node, "name", None)) else None
            node_type = node.type() if callable(getattr(node, "type", None)) else None
            node_uid = node.uniqueId() if callable(getattr(node, "uniqueId", None)) else None
            original_alpha_state = node.inheritAlpha() if callable(getattr(node, "inheritAlpha", None)) else False
        except Exception:
            pass

        # 1) Turn on alpha inheritance for current node
        # Uses direct API call (no undo entry) so we can manage undo ourselves
        self._trigger_inherit_alpha_action(node)

        # 2) Add the layer below as selected
        self._select_below_additive()

        # 3) Quick group selected layers
        self._trigger_quick_group_action()

        # 4) Restore active node selection to the original top layer
        # 5) Start event-based monitoring for undo to restore alpha state
        def restore_selection_and_monitor():
            try:
                doc_now = app.activeDocument()
                if doc_now is None:
                    return
                
                target_node = None
                
                # Try to find the node by name
                if node_name is not None:
                    target_node = self._find_node_by_name_and_type(doc_now, node_name, node_type)
                
                if target_node is not None:
                    # Set as active node
                    self._set_active_node(doc_now, target_node)
                    
                    # Clear selection and select only this node
                    if self.tree is not None:
                        sm = self.tree.selectionModel()
                        if sm is not None:
                            sm.clearSelection()
                    
                    self._select_only_node_in_view(target_node)
                    self._set_active_node(doc_now, target_node)
                    
                    # Start event-based monitoring for undo
                    # Uses model signals and Krita notifier instead of polling
                    self._start_undo_monitor(
                        doc_now, target_node, node_uid, node_name, node_type, original_alpha_state
                    )
                
                if self.tree is not None:
                    self.tree.viewport().update()
            except Exception:
                pass

        QTimer.singleShot(150, restore_selection_and_monitor)

    def _start_undo_monitor(self, doc, node, node_uid, node_name, node_type, original_alpha_state) -> None:
        """
        Monitor for undo of the quick group operation using event-based signals.
        
        When the clipping mask is created, the node ends up inside a group layer.
        If the user undoes, the quick group is reversed and the node will no longer
        be inside a group. When we detect this via signals, we restore the original alpha state.
        
        This provides a clean single-undo experience where both the grouping and
        the alpha inheritance change are effectively reversed together.
        """
        app = Krita.instance()
        
        # Get the parent of the node after grouping - it should be a group layer
        parent_after_group = None
        try:
            parent_after_group = node.parentNode() if callable(getattr(node, "parentNode", None)) else None
        except Exception:
            parent_after_group = None
        
        if parent_after_group is None:
            return
        
        # Check if parent is actually a group (not root)
        parent_type = ""
        try:
            parent_type = (parent_after_group.type() if callable(getattr(parent_after_group, "type", None)) else "").lower()
        except Exception:
            parent_type = ""
        
        # If parent is not a group layer, no monitoring needed
        if "group" not in parent_type:
            return
        
        parent_uid = None
        try:
            parent_uid = parent_after_group.uniqueId() if callable(getattr(parent_after_group, "uniqueId", None)) else None
        except Exception:
            parent_uid = None
        
        # Create an undo monitor that uses event-based detection
        monitor = ClippingMaskUndoMonitor(
            patcher=self,
            node_uid=node_uid,
            node_name=node_name,
            node_type=node_type,
            parent_uid=parent_uid,
            original_alpha_state=original_alpha_state,
            tree_view=self.tree
        )
        monitor.start_monitoring()
        
        # Store reference to prevent garbage collection
        if not hasattr(self, '_undo_monitors'):
            self._undo_monitors = []
        self._undo_monitors.append(monitor)

    def _restore_alpha_state(self, node, original_state: bool) -> None:
        """Restore the alpha inheritance state to its original value."""
        try:
            if callable(getattr(node, "setInheritAlpha", None)):
                current_state = node.inheritAlpha() if callable(getattr(node, "inheritAlpha", None)) else False
                if current_state != original_state:
                    node.setInheritAlpha(original_state)
        except Exception:
            pass

    def _trigger_quick_group_action(self) -> bool:
        act = _find_action_by_ids([
            "create_quick_group",
            "quick_group",
            "quick_group_layers",
            "layer_quick_group",
            "group_layers",
        ])
        if act is None:
            act = _find_action_by_text(["quick", "group"])
        if act is None:
            act = _find_action_by_text(["group", "layers"])
        if act is None:
            return False
        try:
            act.trigger()
            return True
        except Exception:
            return False

    def _trigger_inherit_alpha_action(self, node) -> bool:
        """
        Enable inherit alpha on the given node using direct API call.
        
        We intentionally use the direct setInheritAlpha() call instead of Krita's
        built-in action. This ensures that the alpha inheritance change is NOT
        added to the undo stack as a separate action.
        
        When combined with quick group, this means:
        - Only the quick group action is in the undo stack
        - When user undoes, the group is dissolved
        - The layer retains alpha inheritance, but since it's no longer in a group,
          the alpha inheritance has no visual effect (it only affects layers within groups)
        
        This provides a cleaner single-undo experience for the clipping mask feature.
        """
        # Check if alpha inheritance is already enabled
        already_enabled = False
        try:
            if callable(getattr(node, "inheritAlpha", None)):
                already_enabled = node.inheritAlpha()
        except Exception:
            pass
        
        if already_enabled:
            # Already enabled, no need to change
            return True
        
        # Use direct API call - this does NOT create an undo entry,
        # which is intentional so that undo only needs to reverse the quick group
        try:
            if callable(getattr(node, "setInheritAlpha", None)):
                node.setInheritAlpha(True)
                return True
        except Exception:
            pass
        
        return False

    def _set_active_node(self, doc, node) -> None:
        try:
            if callable(getattr(doc, "setActiveNode", None)):
                doc.setActiveNode(node)
                return
        except Exception:
            pass
        try:
            view = Krita.instance().activeWindow().activeView()
        except Exception:
            view = None
        if view is not None:
            try:
                if callable(getattr(view, "setCurrentNode", None)):
                    view.setCurrentNode(node)
            except Exception:
                pass

    def _find_node_by_name_and_type(self, doc, name: str, node_type: Optional[str]):
        """Recursively search for a node matching the given name and type."""
        if doc is None or name is None:
            return None
        
        def search_nodes(parent_node):
            if parent_node is None:
                return None
            try:
                children = parent_node.childNodes() if callable(getattr(parent_node, "childNodes", None)) else []
            except Exception:
                children = []
            
            for child in children:
                try:
                    child_name = child.name() if callable(getattr(child, "name", None)) else None
                    child_type = child.type() if callable(getattr(child, "type", None)) else None
                except Exception:
                    continue
                
                if child_name == name:
                    if node_type is None or child_type == node_type:
                        return child
                
                # Recursively search in groups
                try:
                    child_type_lower = (child_type or "").lower()
                except Exception:
                    child_type_lower = ""
                
                if "group" in child_type_lower:
                    result = search_nodes(child)
                    if result is not None:
                        return result
            
            return None
        
        try:
            root = doc.rootNode() if callable(getattr(doc, "rootNode", None)) else None
            return search_nodes(root)
        except Exception:
            return None

    def _select_below_additive(self) -> bool:
        if self.tree is None:
            return False
        try:
            sm = self.tree.selectionModel()
        except Exception:
            return False
        if sm is None:
            return False

        current = sm.currentIndex()
        if not current.isValid():
            current = self.tree.currentIndex()
        if not current.isValid():
            return False

        model = current.model()
        parent = current.parent()
        row = current.row()
        below = model.index(row + 1, current.column(), parent)
        if not below.isValid():
            below = model.index(row + 1, 0, parent)
        if not below.isValid():
            return False

        try:
            sm.select(below, QItemSelectionModel.Select | QItemSelectionModel.Rows)
            return True
        except Exception:
            return False

    def _select_only_node_in_view(self, node) -> None:
        if self.tree is None:
            return
        sm = self.tree.selectionModel()
        if sm is None:
            return

        target = self._find_index_for_node(node)
        if target is None or not target.isValid():
            return
        try:
            sm.clearSelection()
            sm.setCurrentIndex(target, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        except Exception:
            pass

    def _find_index_for_node(self, node):
        if self.tree is None:
            return None
        model = self.tree.model()
        if model is None:
            return None

        node_uid = None
        try:
            if callable(getattr(node, "uniqueId", None)):
                node_uid = node.uniqueId()
        except Exception:
            node_uid = None

        def matches(idx) -> bool:
            for role in range(int(Qt.ItemDataRole.UserRole), int(Qt.ItemDataRole.UserRole) + 100):
                try:
                    v = idx.data(role)
                except Exception:
                    continue
                if v is None:
                    continue
                if v is node:
                    return True
                if callable(getattr(v, "uniqueId", None)) and node_uid is not None:
                    try:
                        if v.uniqueId() == node_uid:
                            return True
                    except Exception:
                        pass
                if callable(getattr(v, "name", None)) and callable(getattr(node, "name", None)):
                    try:
                        if v.name() == node.name():
                            if callable(getattr(v, "type", None)) and callable(getattr(node, "type", None)):
                                if v.type() == node.type():
                                    return True
                    except Exception:
                        pass
            return False

        # BFS traversal
        stack = [model.index(r, 0) for r in range(model.rowCount())]
        while stack:
            idx = stack.pop(0)
            if not idx.isValid():
                continue
            if matches(idx):
                return idx
            try:
                rc = model.rowCount(idx)
            except Exception:
                rc = 0
            if rc:
                for r in range(rc):
                    stack.append(model.index(r, 0, idx))
        return None

    @staticmethod
    def _index_of_widget(layout, widget: QWidget) -> int:
        """Find the index of a widget in a layout."""
        if layout is None or widget is None:
            return -1
        try:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is None:
                    continue
                w = item.widget()
                if w is widget:
                    return i
        except Exception:
            pass
        return -1

    def _find_layer_tree_view(self) -> Optional[QTreeView]:
        """Find the layer tree view in the docker."""
        # First try by name - listLayers from WdgLayerBox.ui
        tree = self.docker.findChild(QTreeView, "listLayers")
        if tree is not None:
            return tree
            
        # Fallback to searching
        candidates = self.docker.findChildren(QTreeView)
        if not candidates:
            return None

        scored = []
        for tv in candidates:
            try:
                cn = (tv.metaObject().className() or "").lower()
            except Exception:
                cn = ""
            on = (tv.objectName() or "").lower()
            score = 0
            if "nodeview" in cn:
                score += 10
            if "kis" in cn and "tree" in cn:
                score += 5
            if "node" in cn or "layer" in cn:
                score += 4
            if "list" in on:
                score += 3
            try:
                if tv.selectionMode() == QAbstractItemView.ExtendedSelection:
                    score += 2
            except Exception:
                pass
            scored.append((score, tv))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None

    def _install_group_layer_labeling(self) -> None:
        """Install automatic color labeling for group layers using Krita's native system."""
        # Find tree for reference (used by other methods and for event-based detection)
        self.tree = self._find_layer_tree_view()

        # Avoid double-initialization
        if self.docker.property("layer_kit_labeler") is True:
            return

        # Pass the tree view to enable event-based detection via rowsInserted signal
        self._labeler = GroupLayerLabeler(tree_view=self.tree, parent=self.docker)
        self._labeler.start_monitoring()
        self.docker.setProperty("layer_kit_labeler", True)


class LayerKitExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

        self._patchers: Dict[int, LayersDockerPatcher] = {}
        self._retry_counts: Dict[int, int] = {}

        notifier = Krita.instance().notifier()
        notifier.windowCreated.connect(self._on_window_created)

        # Patch already-open windows with a delay
        QTimer.singleShot(500, self._apply_to_all_windows)

    def setup(self):
        pass

    def createActions(self, window):
        """Create keyboard-bindable actions for Layer Kit functionality."""
        # Move to Top of Layer Stack action
        action_move_top = window.createAction(
            "layer_kit_move_to_top",
            "Move to Top of Layer Stack",
            "Scripts/Layer Kit"
        )
        action_move_top.triggered.connect(self._action_move_to_top)

        # Move to Bottom of Layer Stack action
        action_move_bottom = window.createAction(
            "layer_kit_move_to_bottom",
            "Move to Bottom of Layer Stack",
            "Scripts/Layer Kit"
        )
        action_move_bottom.triggered.connect(self._action_move_to_bottom)

        # Create Clipping Mask action
        action_clipping_mask = window.createAction(
            "layer_kit_create_clipping_mask",
            "Create Clipping Mask",
            "Scripts/Layer Kit"
        )
        action_clipping_mask.triggered.connect(self._action_create_clipping_mask)

    def _get_active_patcher(self) -> Optional[LayersDockerPatcher]:
        """Get the patcher for the currently active window's docker."""
        try:
            win = Krita.instance().activeWindow()
            if win is None:
                return None
            qwin = win.qwindow()
            if qwin is None:
                return None
            docker = qwin.findChild(QDockWidget, "KisLayerBox")
            if docker is None:
                return None
            docker_id = int(id(docker))
            return self._patchers.get(docker_id)
        except Exception:
            return None

    def _action_move_to_top(self) -> None:
        """Action handler for Move to Top of Layer Stack."""
        patcher = self._get_active_patcher()
        if patcher is not None:
            patcher._move_to_top()
        else:
            # Fallback: create a temporary patcher-like move operation
            self._fallback_move_to_top()

    def _action_move_to_bottom(self) -> None:
        """Action handler for Move to Bottom of Layer Stack."""
        patcher = self._get_active_patcher()
        if patcher is not None:
            patcher._move_to_bottom()
        else:
            # Fallback: create a temporary patcher-like move operation
            self._fallback_move_to_bottom()

    def _action_create_clipping_mask(self) -> None:
        """Action handler for Create Clipping Mask."""
        patcher = self._get_active_patcher()
        if patcher is not None:
            patcher._do_clipping_mask_sequence()

    def _fallback_move_to_top(self) -> None:
        """Fallback move to top when no patcher is available."""
        app = Krita.instance()
        doc = app.activeDocument()
        if doc is None:
            return

        try:
            node = doc.activeNode()
        except Exception:
            node = None
        if node is None:
            return

        try:
            root = doc.rootNode()
        except Exception:
            root = None
        if root is None:
            return

        try:
            root_children = root.childNodes() if callable(getattr(root, "childNodes", None)) else []
        except Exception:
            root_children = []

        if not root_children:
            return

        # Use raise_layer action repeatedly
        raise_action = _find_action_by_ids([
            "move_layer_up", "raise_layer", "layer_raise", "RaiseLayers",
        ])
        if raise_action is None:
            raise_action = _find_action_by_text(["raise", "layer"])
        if raise_action is None:
            return

        max_moves = len(root_children) + 50
        for _ in range(max_moves):
            try:
                raise_action.trigger()
                doc_now = app.activeDocument()
                if doc_now is None:
                    break
                current_node = doc_now.activeNode()
                if current_node is None:
                    break
                root_now = doc_now.rootNode()
                if root_now is None:
                    break
                children_now = root_now.childNodes() if callable(getattr(root_now, "childNodes", None)) else []
                if not children_now:
                    break
                current_uid = current_node.uniqueId() if callable(getattr(current_node, "uniqueId", None)) else None
                last_uid = children_now[-1].uniqueId() if callable(getattr(children_now[-1], "uniqueId", None)) else None
                if current_uid is not None and last_uid is not None and current_uid == last_uid:
                    break
            except Exception:
                break

    def _fallback_move_to_bottom(self) -> None:
        """Fallback move to bottom when no patcher is available."""
        app = Krita.instance()
        doc = app.activeDocument()
        if doc is None:
            return

        try:
            node = doc.activeNode()
        except Exception:
            node = None
        if node is None:
            return

        try:
            root = doc.rootNode()
        except Exception:
            root = None
        if root is None:
            return

        try:
            root_children = root.childNodes() if callable(getattr(root, "childNodes", None)) else []
        except Exception:
            root_children = []

        if not root_children:
            return

        # Use lower_layer action repeatedly
        lower_action = _find_action_by_ids([
            "move_layer_down", "lower_layer", "layer_lower", "LowerLayers",
        ])
        if lower_action is None:
            lower_action = _find_action_by_text(["lower", "layer"])
        if lower_action is None:
            return

        max_moves = len(root_children) + 50
        for _ in range(max_moves):
            try:
                lower_action.trigger()
                doc_now = app.activeDocument()
                if doc_now is None:
                    break
                current_node = doc_now.activeNode()
                if current_node is None:
                    break
                root_now = doc_now.rootNode()
                if root_now is None:
                    break
                children_now = root_now.childNodes() if callable(getattr(root_now, "childNodes", None)) else []
                if not children_now:
                    break
                current_uid = current_node.uniqueId() if callable(getattr(current_node, "uniqueId", None)) else None
                first_uid = children_now[0].uniqueId() if callable(getattr(children_now[0], "uniqueId", None)) else None
                if current_uid is not None and first_uid is not None and current_uid == first_uid:
                    break
            except Exception:
                break

    def _on_window_created(self, *args):
        QTimer.singleShot(500, self._apply_to_all_windows)

    def _apply_to_all_windows(self) -> None:
        try:
            windows = Krita.instance().windows()
        except Exception:
            windows = []
        for w in windows:
            self._apply_to_window(w)

    def _apply_to_window(self, window) -> None:
        try:
            qwin = window.qwindow()
        except Exception:
            qwin = None

        if qwin is None:
            return

        docker = qwin.findChild(QDockWidget, "KisLayerBox")
        if docker is None:
            self._schedule_retry(window)
            return

        if docker.property("layer_kit_patched") is True:
            return

        patcher = LayersDockerPatcher(docker, docker)
        try:
            patcher.apply()
            docker.setProperty("layer_kit_patched", True)
            self._patchers[int(id(docker))] = patcher
        except Exception:
            self._schedule_retry(window)

    def _schedule_retry(self, window) -> None:
        try:
            key = int(id(window))
        except Exception:
            return
        count = self._retry_counts.get(key, 0)
        if count >= 10:
            return
        self._retry_counts[key] = count + 1
        QTimer.singleShot(500, self._apply_to_all_windows)