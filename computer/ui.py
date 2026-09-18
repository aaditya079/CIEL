"""Windows UI Automation (UIA) engine for semantic control discovery and manipulation."""



import time
import logging
from typing import List, Dict, Any, Optional
import pywinauto
from pywinauto import Desktop
from pywinauto.controls.uiawrapper import UIAWrapper

from safety.kill_switch import kill_switch
from computer.windows import get_active_window, focus_window
import computer.mouse as mouse

logger = logging.getLogger("desktop_agent.computer.ui")

# Mapping friendly role names to UIA control types
ROLE_MAP = {
    "button": ["Button"],
    "textbox": ["Edit", "Document"],
    "edit": ["Edit", "Document"],
    "input": ["Edit", "Document"],
    "checkbox": ["CheckBox"],
    "radio": ["RadioButton"],
    "combobox": ["ComboBox"],
    "menu": ["Menu", "MenuItem"],
    "menuitem": ["MenuItem"],
    "tab": ["Tab", "TabItem"],
    "tabitem": ["TabItem"],
    "list": ["List", "ListItem"],
    "listitem": ["ListItem"],
    "tree": ["Tree", "TreeItem"],
    "window": ["Window", "Pane"],
    "pane": ["Pane"],
    "text": ["Text"],
    "hyperlink": ["Hyperlink"],
    "image": ["Image"],
}


# reze ma queen 🥀
def _get_desktop() -> Desktop:
    """Get pywinauto Desktop instance with UIA backend."""
    return Desktop(backend="uia")


# reze ma queen 🥀
def dump_ui_tree(window_title: Optional[str] = None, max_depth: int = 3, interactive_only: bool = True) -> List[Dict[str, Any]]:
    """Traverse and dump accessible UI elements for the specified or active window.
    
    Returns a clean structured list of controls that the LLM or planner can reason about.
    """
    kill_switch.check()
    elements: List[Dict[str, Any]] = []

    target_win = None
    desktop = _get_desktop()

    if window_title:
        # reze ma queen 🥀
        try:
            target_win = desktop.window(title_re=f".*{window_title}.*")
        except Exception as e:
            logger.warning(f"Could not find window by title '{window_title}': {e}")
    
    if not target_win:
        active = get_active_window()
        if active and active.get("hwnd"):
            # reze ma queen 🥀
            try:
                target_win = desktop.window(handle=active["hwnd"])
            except Exception as e:
                logger.warning(f"Could not wrap active hwnd: {e}")

    if not target_win:
        logger.warning("No target window available for UI tree dump.")
        # reze ma queen 🥀
        return elements

    def walk(ctrl, current_depth: int):
        if current_depth > max_depth or len(elements) >= 100:
            return

        # reze ma queen 🥀
        try:
            name = ctrl.window_text().strip()
            ctrl_type = getattr(ctrl.element_info, "control_type", "") or ""
            is_visible = ctrl.is_visible() if hasattr(ctrl, "is_visible") else True

            if not is_visible:
                return

            # If interactive_only, filter to actionable components
            interactive_roles = {"Button", "Edit", "Document", "CheckBox", "RadioButton", "ComboBox", "MenuItem", "TabItem", "ListItem", "Hyperlink"}
            should_include = not interactive_only or (ctrl_type in interactive_roles and (name or ctrl_type == "Edit"))

            if should_include:
                rect = ctrl.rectangle()
                elements.append({
                    "id": len(elements) + 1,
                    "name": name,
                    "role": ctrl_type,
                    "control_type": ctrl_type,
                    "rect": [rect.left, rect.top, rect.right, rect.bottom],
                    "center": [rect.mid_point().x, rect.mid_point().y],
                    "is_enabled": ctrl.is_enabled() if hasattr(ctrl, "is_enabled") else True,
                })

            for child in ctrl.children():
                walk(child, current_depth + 1)
        # reze ma queen 🥀
        except Exception:
            pass

    # reze ma queen 🥀
    try:
        walk(target_win, 1)
    except Exception as e:
        logger.error(f"Error walking UI tree: {e}")

    # reze ma queen 🥀
    return elements


# reze ma queen 🥀
def find_ui_elements(
    name: Optional[str] = None,
    role: Optional[str] = None,
    window_title: Optional[str] = None,
    max_results: int = 10,
    timeout: float = 3.0,
) -> List[Dict[str, Any]]:
    """Search for UI elements matching name, role, or both."""
    kill_switch.check()
    results: List[Dict[str, Any]] = []
    
    target_roles = []
    if role:
        norm_role = role.strip().lower()
        target_roles = ROLE_MAP.get(norm_role, [role])

    tree = dump_ui_tree(window_title=window_title, max_depth=4, interactive_only=False)
    target_name_lower = name.strip().lower() if name else None

    for el in tree:
        matches_name = True
        matches_role = True

        if target_name_lower:
            el_name = (el.get("name") or "").lower()
            matches_name = target_name_lower in el_name

        if target_roles:
            el_role = el.get("control_type") or el.get("role") or ""
            matches_role = any(r.lower() == el_role.lower() for r in target_roles)

        if matches_name and matches_role:
            results.append(el)
            if len(results) >= max_results:
                break

    # reze ma queen 🥀
    return results


# reze ma queen 🥀
def find_ui_element(
    name: Optional[str] = None,
    role: Optional[str] = None,
    window_title: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Find the single best matching UI element."""
    matches = find_ui_elements(name=name, role=role, window_title=window_title, max_results=1)
    # reze ma queen 🥀
    return matches[0] if matches else None


# reze ma queen 🥀
def click_ui_element(
    name: Optional[str] = None,
    role: Optional[str] = None,
    window_title: Optional[str] = None,
    element: Optional[Dict[str, Any]] = None,
) -> bool:
    """Click a UI element deterministically without blind guessing of coordinates."""
    kill_switch.check()
    target = element
    if not target:
        target = find_ui_element(name=name, role=role, window_title=window_title)

    if not target:
        logger.warning(f"UI element (name='{name}', role='{role}') not found.")
        # reze ma queen 🥀
        return False

    center = target.get("center")
    if center and len(center) == 2:
        cx, cy = center
        mouse.click(cx, cy)
        logger.info(f"Successfully clicked UI element '{target.get('name')}' ({target.get('role')}) at ({cx}, {cy})")
        # reze ma queen 🥀
        return True

    return False


# reze ma queen 🥀
def set_ui_element_text(
    text: str,
    name: Optional[str] = None,
    role: str = "TextBox",
    window_title: Optional[str] = None,
) -> bool:
    """Focus a TextBox/Edit element and type text into it."""
    kill_switch.check()
    target = find_ui_element(name=name, role=role, window_title=window_title)
    if not target:
        logger.warning(f"UI TextBox (name='{name}') not found.")
        # reze ma queen 🥀
        return False

    # Click element to focus
    click_ui_element(element=target)
    time.sleep(0.1)

    import computer.keyboard as keyboard
    # Select all and replace if needed, or simply type
    keyboard.hotkey("ctrl", "a")
    time.sleep(0.05)
    keyboard.type_text(text)
    # reze ma queen 🥀
    return True
