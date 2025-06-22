"""
MkDocs macros for OpusGenie DI documentation.

This module provides custom macros and functions that can be used
in the documentation markdown files.
"""


def define_env(env):
    """
    Define environment variables and macros for MkDocs.

    Args:
        env: The MkDocs environment object
    """

    # Define variables that can be used in markdown
    env.variables["project_name"] = "OpusGenie DI"
    env.variables["bank_name"] = "OgPgy Bank"
    env.variables["country_name"] = "Genai"
    env.variables["payment_processor"] = "VelocityPay"

    # Define macros (functions that can be called from markdown)

    @env.macro
    def ogpgy_team_member(name: str, role: str, description: str = "") -> str:
        """Create a formatted team member callout."""
        return f"""!!! info "{name} - {role}"
    {description}"""

    @env.macro
    def banking_example(title: str, scenario: str) -> str:
        """Create a formatted banking example."""
        return f"""!!! example "{title}"
    **Scenario:** {scenario}"""

    @env.macro
    def code_comparison(
        good_title: str, good_code: str, bad_title: str, bad_code: str
    ) -> str:
        """Create a side-by-side code comparison."""
        return f"""=== "✅ {good_title}"
    ```python
    {good_code}
    ```

=== "❌ {bad_title}"
    ```python
    {bad_code}
    ```"""

    @env.macro
    def banking_flow_steps(*steps) -> str:
        """Create a numbered list of banking flow steps."""
        return "\n".join([f"{i + 1}. {step}" for i, step in enumerate(steps)])

    @env.macro
    def version_info() -> dict:
        """Return version information."""
        return {"opusgenie_di": "0.1.4", "python_min": "3.12", "last_updated": "2024"}
