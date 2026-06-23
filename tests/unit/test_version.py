"""Verify the package version is the expected Stage 0 value."""

from mars777_cop_thief import __version__
from mars777_cop_thief.shared.version import __version__ as module_version


def test_package_version_is_1_00():
    assert __version__ == "1.00"


def test_version_module_matches_package():
    assert module_version == "1.00"
