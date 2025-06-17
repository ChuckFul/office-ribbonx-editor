from xml.etree import ElementTree as ET
from typing import List

from .errors import XmlError
from .schema_loader import load_schema_text

# Mutually exclusive attribute sets as defined in the original C# implementation
MUTUALLY_EXCLUSIVE_ATTRIBUTES: List[set[str]] = [
    {"title", "getTitle"},
    {"enabled", "getEnabled"},
    {"visible", "getVisible"},
    {"label", "getLabel"},
    {"keytip", "getKeytip"},
    {"screentip", "getScreentip"},
    {"supertip", "getSupertip"},
    {"description", "getDescription"},
    {"altText", "getAltText"},
    {"showLabel", "getShowLabel"},
    {"helperText", "getHelperText"},
    {"showImage", "getShowImage"},
    {"size", "getSize"},
    {"id", "idMso", "idQ"},
    {"image", "imageMso", "getImage"},
    {"insertBeforeMso", "insertAfterMso", "insertBeforeQ", "insertAfterQ"},
]


def _target_namespace(schema_text: str) -> str:
    root = ET.fromstring(schema_text)
    return root.attrib.get("targetNamespace", "")


def _check_mutually_exclusive(element: ET.Element, lines: List[str], errors: List[XmlError]) -> None:
    if element.attrib:
        for group in MUTUALLY_EXCLUSIVE_ATTRIBUTES:
            found = [a for a in element.attrib if a in group]
            if len(found) > 1:
                attr = found[1]
                line = _element_line(element, lines)
                column = lines[line - 1].find(attr)
                errors.append(
                    XmlError(
                        line,
                        column + 1 if column >= 0 else 1,
                        f"Attributes {', '.join(sorted(group))} are mutually exclusive",
                    )
                )
                break
    for child in list(element):
        _check_mutually_exclusive(child, lines, errors)


def _element_line(element: ET.Element, lines: List[str]) -> int:
    local = element.tag.split('}', 1)[-1]
    open_tag = f"<{local}"
    for i, line in enumerate(lines, start=1):
        if open_tag in line:
            return i
    return 1


def validate_xml(xml_text: str, schema_version: str = "2009") -> List[XmlError]:
    """Validate a RibbonX XML string.

    Parameters
    ----------
    xml_text: str
        The XML content to validate.
    schema_version: str
        Either ``"2006"`` or ``"2009"`` to select the appropriate schema.

    Returns
    -------
    List[XmlError]
        A list of validation errors. The list is empty if the XML is valid.
    """
    errors: List[XmlError] = []

    lines = xml_text.splitlines()
    try:
        parser = ET.XMLParser()
        root = ET.fromstring(xml_text, parser=parser)
    except ET.ParseError as ex:
        line, col = ex.position
        errors.append(XmlError(line, col, ex.msg))
        return errors

    schema_text = load_schema_text(schema_version)
    target_ns = _target_namespace(schema_text)

    tag_ns = root.tag[root.tag.find("{") + 1 : root.tag.find("}")] if root.tag.startswith("{") else ""
    if tag_ns != target_ns:
        errors.append(
            XmlError(
                1,
                1,
                f"Wrong namespace '{tag_ns}' (expected '{target_ns}')",
            )
        )

    # Try schema validation using optional xmlschema library
    try:
        import xmlschema  # type: ignore

        schema = xmlschema.XMLSchema(schema_text)
        for err in schema.iter_errors(xml_text):
            line, col = err.position if err.position else (1, 1)
            errors.append(XmlError(line, col, err.reason))
    except Exception:
        # xmlschema not installed or initialization failed
        pass

    if not errors:
        _check_mutually_exclusive(root, lines, errors)

    return errors
