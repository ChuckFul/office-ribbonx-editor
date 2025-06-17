import pytest

from ribbon_validator.validator import validate_xml

BASIC_CONTENT = """
<customUI xmlns="http://schemas.microsoft.com/office/{ns}/customui">
    <ribbon {ribbon_attr}>
        <tabs>
            <tab {tab_attr}>
                <group {group_attr}>
                    <button {button_attr} />
                </group>
            </tab>
        </tabs>
    </ribbon>
</customUI>
"""


def test_empty():
    errors = validate_xml("", "2009")
    assert errors


@pytest.mark.parametrize(
    "ns,version,expected",
    [
        ("2006/01", "2006", True),
        ("2009/07", "2009", True),
        ("2006/01", "2009", False),
    ],
)
def test_namespace(ns, version, expected):
    xml = BASIC_CONTENT.format(
        ns=ns,
        ribbon_attr="",
        tab_attr="id=\"t\"",
        group_attr="id=\"g\"",
        button_attr="id=\"b\"",
    )
    result = not validate_xml(xml, version)
    assert result is expected


def test_mutually_exclusive():
    xml = BASIC_CONTENT.format(
        ns="2009/07",
        ribbon_attr="",
        tab_attr="id=\"t\"",
        group_attr="id=\"g\"",
        button_attr="title=\"A\" getTitle=\"B\"",
    )
    errors = validate_xml(xml, "2009")
    assert errors
    assert any("mutually exclusive" in e.message for e in errors)
