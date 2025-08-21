from enum import Enum


class Feature(Enum):
    DATABASE_MODEL_GENERATION = "database_model_generation"
    USE_CASE_DOC_FROM_PROCEDURE_GENERATION = "use_case_doc_from_procedure_generation"
    USE_CASE_DOC_FROM_APP_FILE_GENERATION = "use_case_doc_from_app_file_generation"
    USE_CASE_DOC_FLOW_DIAGRAM_GENERATION = "use_case_doc_flow_diagram_generation"
    USE_CASE_DOC_SEQUENCE_DIAGRAM_GENERATION = (
        "use_case_doc_sequence_diagram_generation"
    )
    USE_CASE_DOC_FLOW_CONSOLIDATION = "use_case_doc_flow_consolidation"
    BACKEND_ENTITIES_CODE_GENERATION = "backend_entities_code_generation"
    BACKEND_DBCONTEXT_CODE_GENERATION = "backend_dbcontext_code_generation"
    BACKEND_BUSINESS_CODE_GENERATION = "backend_business_code_generation"


class FeatureToggle:
    _instance = None
    _features: dict[Feature, bool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FeatureToggle, cls).__new__(cls)
            cls._instance._features = {
                Feature.DATABASE_MODEL_GENERATION: True,
                Feature.USE_CASE_DOC_FROM_PROCEDURE_GENERATION: True,
                Feature.USE_CASE_DOC_FROM_APP_FILE_GENERATION: True,
                Feature.USE_CASE_DOC_FLOW_DIAGRAM_GENERATION: True,
                Feature.USE_CASE_DOC_SEQUENCE_DIAGRAM_GENERATION: True,
                Feature.USE_CASE_DOC_FLOW_CONSOLIDATION: True,
                Feature.BACKEND_ENTITIES_CODE_GENERATION: False,
                Feature.BACKEND_DBCONTEXT_CODE_GENERATION: False,
                Feature.BACKEND_BUSINESS_CODE_GENERATION: False,
            }
        return cls._instance

    def is_database_model_generation_enabled(self) -> bool:
        return self._features.get(Feature.DATABASE_MODEL_GENERATION, False)

    def is_use_case_from_procedure_enabled(self) -> bool:
        return self._features.get(Feature.USE_CASE_DOC_FROM_PROCEDURE_GENERATION, False)

    def is_use_case_from_app_file_enabled(self) -> bool:
        return self._features.get(Feature.USE_CASE_DOC_FROM_APP_FILE_GENERATION, False)

    def is_use_case_flow_diagram_enabled(self) -> bool:
        return self._features.get(Feature.USE_CASE_DOC_FLOW_DIAGRAM_GENERATION, False)

    def is_use_case_sequence_diagram_enabled(self) -> bool:
        return self._features.get(
            Feature.USE_CASE_DOC_SEQUENCE_DIAGRAM_GENERATION, False
        )

    def is_use_case_flow_consolidation_enabled(self) -> bool:
        return self._features.get(Feature.USE_CASE_DOC_FLOW_CONSOLIDATION, False)

    def is_backend_entities_code_enabled(self) -> bool:
        return self._features.get(Feature.BACKEND_ENTITIES_CODE_GENERATION, False)

    def is_backend_dbcontext_code_enabled(self) -> bool:
        return self._features.get(Feature.BACKEND_DBCONTEXT_CODE_GENERATION, False)

    def is_backend_business_code_enabled(self) -> bool:
        return self._features.get(Feature.BACKEND_BUSINESS_CODE_GENERATION, False)

    def enable_feature(self, feature_name: Feature) -> None:
        if feature_name in self._features:
            self._features[feature_name] = True
        else:
            raise ValueError(f"Feature '{feature_name}' does not exist.")

    def disable_feature(self, feature_name: Feature) -> None:
        if feature_name in self._features:
            self._features[feature_name] = False
        else:
            raise ValueError(f"Feature '{feature_name}' does not exist.")

    def is_feature_enabled(self, feature_name: Feature) -> bool:
        return self._features.get(feature_name, False)


# Singleton instance
feature_toggle_instance = FeatureToggle()
