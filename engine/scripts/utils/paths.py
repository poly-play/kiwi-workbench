import os
from pathlib import Path

def get_project_root() -> Path:
    """Returns the root directory of the operations workbench."""
    # This script is in engine/scripts/utils/
    # parent -> engine/scripts
    # parent.parent -> engine
    # parent.parent.parent -> ROOT
    return Path(__file__).resolve().parent.parent.parent.parent

def get_knowledge_root() -> Path:
    return get_project_root() / "knowledge"

def get_data_root() -> Path:
    return get_project_root() / "data"

def get_store_root() -> Path:
    return get_data_root() / "store"

def get_tmp_root() -> Path:
    return get_data_root() / "tmp"

def get_output_root(domain: str, sub_domain: str = None) -> Path:
    path = get_data_root() / "outputs" / domain
    if sub_domain:
        path = path / sub_domain
    return path
