from abc import ABC, abstractmethod
from feature_analyzer.models.data_wrapper_model import DataWrapperModel


class PhaseExecutionInterface(ABC):
    @abstractmethod
    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        pass

    @abstractmethod
    def get_loading_log_message(self) -> str:
        pass

    @abstractmethod
    def get_finished_log_message(self) -> str:
        pass
