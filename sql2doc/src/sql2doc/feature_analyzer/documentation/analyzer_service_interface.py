from abc import ABC, abstractmethod
from sql2doc.feature_analyzer.models.data_wrapper_model import DataWrapperModel


class AnalyzeServiceInterface(ABC):
    @abstractmethod
    def analyze(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        pass
