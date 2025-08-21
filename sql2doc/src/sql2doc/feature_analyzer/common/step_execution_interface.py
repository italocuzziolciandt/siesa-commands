from abc import ABC, abstractmethod
from feature_analyzer.models.data_wrapper_model import DataWrapperModel


class StepExecutionInterface(ABC):
    @abstractmethod
    def execute(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        pass
