import os
from langchain_core.tools import tool
from typing import Annotated
import logging
from feature_analyzer.models.data_wrapper_model import DataWrapperModel

logger = logging.getLogger(__name__)

data_wrapper: DataWrapperModel = None


def initialize_data_wrapper(data_wrapper_model: DataWrapperModel) -> None:
    """Initializes the global data wrapper model."""
    global data_wrapper
    data_wrapper = data_wrapper_model
    logging.info("DataWrapperModel initialized.")


@tool
def write_class_content_to_file(
    class_name: Annotated[str, "Name of the class"],
    class_content: Annotated[str, "Content of the class"],
) -> None:
    """Writes the content of a class to a file."""
    global data_wrapper

    output_path = os.path.join(
        data_wrapper.output_timestamped_dir, "entities", f"{class_name}.cs"
    )

    # Ensure the "entities" directory exists
    entities_dir = os.path.join(data_wrapper.output_timestamped_dir, "entities")
    try:
        os.makedirs(entities_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating 'entities' directory: {e}")
        return

    try:
        with open(output_path, "w") as file:
            file.write(class_content)
    except Exception as e:
        logger.error(f"Error writing entity {class_name} to file {output_path}: {e}")


@tool
def log_step(
    step_name: Annotated[str, "Name of the step"],
) -> None:
    """Logs the completion of a step."""
    logger = logging.getLogger(__name__)
    logger.info(f"Step completed: {step_name}")


@tool
def write_partial_result(
    step_name: Annotated[str, "Name of the step"],
    partial_result: Annotated[str, "Partial result of the step"],
) -> None:
    """For each step executed, use this tool to write the partial result."""

    ## HARD CODED AS EXAMPLE
    output_path = "/Users/felipecp/Documents/Projects/Siesa/Agents/outputs"
    global incremental_value

    with open(f"{output_path}/{step_name}_{incremental_value}.md", "a") as file:
        file.write(partial_result + "\n")

    incremental_value += 1
