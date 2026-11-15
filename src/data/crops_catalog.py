"""
Crops Catalog aligned with Project Blueprint (GEMINI.md).
Features 5 target crops: Banana, Coffee, Sugar Cane, Pineapple, Avocado.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

DATA_FILE = Path(__file__).parent / "crops_data.json"


def load_crops_data() -> List[Dict[str, Any]]:
    """Loads crops configuration from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


CROPS_LIST = load_crops_data()
CROPS_CATALOG: Dict[str, Dict[str, Any]] = {
    c["crop"].lower().replace(" ", "_"): c for c in CROPS_LIST
}


def get_crop_by_name(crop_name: str) -> Dict[str, Any]:
    """Retrieve crop profile by standard name."""
    norm = crop_name.lower().replace(" ", "_")
    return CROPS_CATALOG.get(norm, CROPS_LIST[0] if CROPS_LIST else {})
