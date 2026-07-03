"""Helpers de test — charge les modules à nom non importable (tiret)."""
import importlib.util
import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def charger(rel_path, nom="mod"):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, rel_path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
