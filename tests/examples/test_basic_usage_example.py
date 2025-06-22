"""Test that basic_usage.py example works correctly."""

from pathlib import Path
import subprocess
import sys


class TestBasicUsageExample:
    """Test basic_usage.py example execution."""

    def test_basic_usage_example_runs_successfully(self) -> None:
        """Test that the basic usage example runs without errors."""

        # Get the path to the example
        example_path = (
            Path(__file__).parent.parent.parent / "examples" / "basic_usage.py"
        )
        assert example_path.exists(), f"Example file not found: {example_path}"

        # Run the example
        result = subprocess.run(
            [sys.executable, str(example_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check that it ran successfully
        assert result.returncode == 0, f"Example failed with error: {result.stderr}"

        # Check for expected output patterns
        output = result.stdout
        assert "🚀 OpusGenie DI Basic Usage Example" in output
        assert "Testing Singleton Components:" in output
        assert "Testing Dependency Injection:" in output
        assert "Testing Transient Components:" in output
        assert "Context Summary:" in output
        assert "✅ Basic usage example completed successfully!" in output

        # Verify specific functionality
        assert "Same instance? True" in output  # Singleton behavior
        assert "Different instances? True" in output  # Transient behavior

    def test_basic_usage_example_output_format(self) -> None:
        """Test that the basic usage example produces correctly formatted output."""

        example_path = (
            Path(__file__).parent.parent.parent / "examples" / "basic_usage.py"
        )

        result = subprocess.run(
            [sys.executable, str(example_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        output = result.stdout

        # Check for section headers
        assert "📦 Testing Singleton Components:" in output
        assert "🔗 Testing Dependency Injection:" in output
        assert "🔄 Testing Transient Components:" in output
        assert "📊 Context Summary:" in output

        # Check for data consistency
        assert "Data from database" in output
        assert "Notification sent:" in output
        assert "Context: global" in output
