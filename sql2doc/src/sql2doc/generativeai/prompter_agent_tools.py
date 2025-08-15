import os
from langchain_core.tools import tool
from typing import Annotated
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

incremental_value = 0


@tool
def log_step(
    step_name: Annotated[str, "Name of the step"],
) -> None:
    """Logs the completion of a step."""
    logger = logging.getLogger(__name__)
    logger.info(f"Step completed: {step_name}")


@tool
def print_generated_code_context_description(
    code_context_description: Annotated[
        str, "Small description of the generated code context"
    ],
) -> None:
    """Prints the description of the generated code context to the console. It should be a small description of the generated code context, like the method name, class name, or any other relevant information."""
    logger = logging.getLogger(__name__)
    logger.info(f"Generated code: {code_context_description}")


@tool
def write_partial_result(
    step_name: Annotated[str, "Name of the step"],
    partial_result: Annotated[str, "Partial result of the step"],
) -> None:
    """For each step executed, use this tool to write the partial result."""

    output_path = "/Users/felipecp/Documents/Projects/Siesa/Agents/outputs"
    global incremental_value

    with open(f"{output_path}/{step_name}_{incremental_value}.md", "a") as file:
        file.write(partial_result + "\n")

    incremental_value += 1
