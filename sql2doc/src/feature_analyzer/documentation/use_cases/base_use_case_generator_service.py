from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from generativeai.prompter_interface import PrompterInterface
from typing import Callable, TypeVar
from generativeai.prompter_factory import PrompterFactory
from common.app_config import app_config_instance
from abc import ABC

# Define a generic type for the items in the list
T = TypeVar("T")


class BaseUseCaseGeneratorService(ABC):
    prompter: PrompterInterface
    logger: logging.Logger

    def __init__(self, max_workers: int = 10):
        self.prompter = PrompterFactory.create_prompter(
            config_auth=app_config_instance.get_config_auth(),
            model=app_config_instance.use_case_analysis_llm_model,
            use_agent=True,
        )
        self.logger = logging.getLogger(__name__)
        self.max_workers = max_workers

    def _process_in_parallel(
        self, items: list[T], processing_function: Callable[[T], None]
    ) -> None:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(processing_function, item): item for item in items
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    item = futures[future]  # Recover item in case of error.
                    self.logger.error(f"Error processing item: {item}. Error: {e}")
