from abc import ABC, abstractmethod
from sql2doc.feature_analyzer.models.data_wrapper_model import DataWrapperModel


class CodeGeneratorServiceInterface(ABC):
    @abstractmethod
    def generate(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        pass
