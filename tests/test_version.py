import io
import sys
from expense_tracker.version import versions, __version__


def test_versions_output():
    """Test that versions() function prints version information."""

    # Redirect stdout to capture the output
    captured_output = io.StringIO()
    sys.stdout = captured_output

    versions()

    # Restore stdout
    sys.stdout = sys.__stdout__

    output = captured_output.getvalue()

    # Check that the output contains the version string
    assert f"expense_tracker: {__version__}" in output
    assert "python:" in output
    assert "platform:" in output


def test_version_string():
    """Test that __version__ is a string."""
    assert isinstance(__version__, str)
