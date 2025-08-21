from abc import ABC, abstractmethod
from feature_analyzer.models.data_wrapper_model import DataWrapperModel


class CodeGeneratorServiceInterface(ABC):
    @abstractmethod
    def generate(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        pass
