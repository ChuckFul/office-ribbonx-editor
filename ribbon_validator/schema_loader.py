from importlib import resources
from pathlib import Path

SCHEMAS = {
    '2006': 'customUI.xsd',
    '2009': 'customui14.xsd',
}


def get_schema_path(version: str) -> Path:
    """Return the path to the requested schema inside the package."""
    if version not in SCHEMAS:
        raise ValueError(f"Unknown schema version: {version}")
    return Path(resources.files(__package__) / 'schemas' / SCHEMAS[version])


def load_schema_text(version: str) -> str:
    path = get_schema_path(version)
    return path.read_text(encoding='utf-8')
