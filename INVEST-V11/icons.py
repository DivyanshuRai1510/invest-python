"""Hand-drawn stroke icons (24x24 grid) used across the site."""
from markupsafe import Markup

ICONS = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "bell": '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    "bookmark": '<path d="M6 3h12v18l-6-4-6 4z"/>',
    "star": '<path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3l-5.5 2.9 1-6.2-4.5-4.4 6.2-.9z"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/>',
    "pin": '<path d="M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
    "x": '<path d="M18 6L6 18M6 6l12 12"/>',
    "undo": '<path d="M9 14L4 9l5-5"/><path d="M4 9h11a5 5 0 0 1 0 10h-3"/>',
    "chevron": '<path d="M9 6l6 6-6 6"/>',
    "grid": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "handshake": '<path d="M3 12l4-4 4 2 3-2 4 4-4 4-2-2-2 2z"/><path d="M9 14l2 2"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "send": '<path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4z"/>',
    "upload": '<path d="M12 16V4"/><path d="M7 9l5-5 5 5"/><path d="M4 16v4h16v-4"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "trash": '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14h10l1-14"/>',
    "edit": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "download": '<path d="M12 4v12"/><path d="M7 11l5 5 5-5"/><path d="M4 20h16"/>',
    # sector icons
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    "pulse": '<path d="M22 12h-4l-3 8-6-16-3 8H2"/>',
    "leaf": '<path d="M4 20c0-9 6-14 16-14 0 10-5 16-14 16"/><path d="M4 20l8-8"/>',
    "card": '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M2.5 10h19M6 15h4"/>',
    "drop": '<path d="M12 2.5s6 6.2 6 11a6 6 0 0 1-12 0c0-4.8 6-11 6-11z"/>',
    "cylinder": '<ellipse cx="12" cy="5" rx="7" ry="2.5"/><path d="M5 5v14c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V5"/><path d="M5 12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5"/>',
    "battery": '<rect x="2" y="7" width="18" height="10" rx="2"/><path d="M22 11v2"/><path d="M11 9l-2 3h3l-2 3"/>',
    "car": '<path d="M5 16V11l2-5h10l2 5v5"/><path d="M3 16h18"/><circle cx="7.5" cy="16" r="1.5"/><circle cx="16.5" cy="16" r="1.5"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M10 21v-4h4v4"/>',
    "robot": '<rect x="5" y="8" width="14" height="11" rx="2"/><path d="M12 8V4"/><circle cx="12" cy="3" r="1"/><circle cx="9.5" cy="13" r="1.2"/><circle cx="14.5" cy="13" r="1.2"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z"/>',
    "book": '<path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v15H6.5A2.5 2.5 0 0 0 4 19.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
    "wifi": '<path d="M2 9a14 14 0 0 1 20 0"/><path d="M5.5 12.5a9 9 0 0 1 13 0"/><path d="M9 16a4.5 4.5 0 0 1 6 0"/><circle cx="12" cy="19.5" r="1"/>',
    "atom": '<circle cx="12" cy="12" r="2"/><ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-60 12 12)"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
}

CATEGORY_ICON = {
    "AI & ML": "chip", "HealthTech": "heart", "AgriTech": "leaf", "FinTech": "card",
    "Hydrogen Production": "drop", "Hydrogen Storage": "cylinder", "Fuel Cells": "battery",
    "Hydrogen Mobility": "car", "Hydrogen Infrastructure": "building", "Robotics": "robot",
    "Clean Energy": "bolt", "EdTech": "book", "IoT": "wifi", "DeepTech": "atom",
    "Sustainability": "globe",
}

CATEGORY_COLOR = {
    "AI & ML": ("#4f46e5", "#818cf8"), "HealthTech": ("#be123c", "#fb7185"),
    "AgriTech": ("#15803d", "#4ade80"), "FinTech": ("#b45309", "#fbbf24"),
    "Hydrogen Production": ("#0369a1", "#38bdf8"), "Hydrogen Storage": ("#0e7490", "#67e8f9"),
    "Fuel Cells": ("#0f766e", "#5eead4"), "Hydrogen Mobility": ("#1d4ed8", "#60a5fa"),
    "Hydrogen Infrastructure": ("#334155", "#94a3b8"), "Robotics": ("#7c3aed", "#c084fc"),
    "Clean Energy": ("#a16207", "#facc15"), "EdTech": ("#9d174d", "#f472b6"),
    "IoT": ("#0c4a6e", "#7dd3fc"), "DeepTech": ("#312e81", "#a5b4fc"),
    "Sustainability": ("#166534", "#86efac"),
}


def icon(name, cls="w-5 h-5"):
    body = ICONS.get(name, "")
    return Markup(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="%s" aria-hidden="true">%s</svg>'
        % (cls, body)
    )


def category_icon(category):
    return CATEGORY_ICON.get(category, "globe")


def category_gradient(category):
    a, b = CATEGORY_COLOR.get(category, ("#1e3a8a", "#3b82f6"))
    return f"linear-gradient(135deg, {a}, {b})"
