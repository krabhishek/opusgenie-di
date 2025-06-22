"""Test that multi_context.py example works correctly."""

from pathlib import Path
import subprocess
import sys


class TestMultiContextExample:
    """Test multi_context.py example execution."""

    def test_multi_context_example_runs_successfully(self) -> None:
        """Test that the multi-context example runs without errors."""

        # Get the path to the example
        example_path = (
            Path(__file__).parent.parent.parent / "examples" / "multi_context.py"
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
        assert "🚀 OpusGenie DI Multi-Context Example" in output
        assert "Building contexts from modules..." in output
        assert "Testing Infrastructure Context:" in output
        assert "Testing Business Context with Cross-Context Dependencies:" in output
        assert "Testing Context Isolation:" in output
        assert "Context Summaries:" in output
        assert "✅ Multi-context example completed successfully!" in output

    def test_multi_context_example_context_isolation(self) -> None:
        """Test that the multi-context example demonstrates proper context isolation."""

        example_path = (
            Path(__file__).parent.parent.parent / "examples" / "multi_context.py"
        )

        result = subprocess.run(
            [sys.executable, str(example_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        output = result.stdout

        # Check for context isolation behavior
        assert "Context isolation working" in output
        assert "Cross-context import working" in output

        # Check for proper context building
        assert "Built 2 contexts:" in output

        # Check for specific context names
        assert "infrastructure_context" in output
        assert "business_context" in output

    def test_multi_context_example_dependency_resolution(self) -> None:
        """Test that the multi-context example shows proper dependency resolution."""

        example_path = (
            Path(__file__).parent.parent.parent / "examples" / "multi_context.py"
        )

        result = subprocess.run(
            [sys.executable, str(example_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        output = result.stdout

        # Check for data flow across contexts
        assert "Data from database" in output
        assert "Cached data" in output
        assert "status': 'processed'" in output

        # Check for proper component resolution
        assert "Database data:" in output
        assert "Cache data:" in output
        assert "Processed data:" in output
