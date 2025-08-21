import logging
from feature_analyzer.codegenerator.business.business_code_generator_from_procedure import BusinessCodeGeneratorFromProcedure
from feature_analyzer.models.code_result_model import ClassImplementation
from typing import Optional
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from feature_analyzer.models.code_result_model import (
    CodeResultModel,
    ClassImplementation,
)


class ProcedureDependencyProcessor:
    """
    Handles the processing of dependencies for class implementations.
    This class is responsible for recursively processing dependencies to a specified depth.
    """

    def __init__(
        self,
        code_generator: BusinessCodeGeneratorFromProcedure,
        max_dependency_depth: int,
    ):
        """
        Initializes the DependencyProcessor with a CodeGenerator and the maximum dependency depth.

        Args:
            code_generator (CodeGenerator): The CodeGenerator instance to use for generating code for dependencies.
            max_dependency_depth (int): The maximum depth to process dependencies.
        """
        self.code_generator = code_generator
        self.max_dependency_depth = max_dependency_depth
        self.logger = logging.getLogger(__name__)

    def process_dependencies(
        self,
        class_implementations: list[ClassImplementation],
        data_wrapper: DataWrapperModel,
        all_class_implementations: list[ClassImplementation],
        current_depth: int,
    ):
        """
        Recursively processes dependencies of class implementations to a specified depth.

        Args:
            class_implementations (List[ClassImplementation]): The list of class implementations to process dependencies for.
            data_wrapper (DataWrapperModel): The data wrapper containing necessary context and information.
            all_class_implementations (List[ClassImplementation]): The list to store all generated class implementations.
            current_depth (int): The current depth of dependency processing.
        """
        if current_depth > self.max_dependency_depth:
            log_message = (
                f"Dependency depth exceeded. Stopping at depth {current_depth}."
            )
            self.logger.info(log_message)
            return  # Stop recursion

        for class_implementation in class_implementations:
            for dependency in class_implementation.next_implementation:
                # Find the ProcedureAnalysisResultModel for the dependency
                dependency_procedure = self._find_dependency_procedure(
                    data_wrapper, dependency.procedure_name
                )

                if not dependency_procedure:
                    log_message = f"Warning: Procedure {dependency.procedure_name} not found in analysis results."
                    self.logger.warning(log_message)
                    continue  # Skip if the dependency procedure is not found

                self.logger.info(
                    f"Generating code for dependency: {dependency.procedure_name} at depth {current_depth}"
                )

                # Generate code for the dependency, passing the parent class content
                dependency_code_result_model: CodeResultModel = (
                    self.code_generator.generate_code_for_procedure_with_agent_as_structured(
                        dependency_procedure,
                        class_to_be_implemented=dependency.class_to_be_implemented,
                        parent_class_content=class_implementation.content,  # Parent content
                    )
                )
                all_class_implementations.extend(
                    dependency_code_result_model.class_implementations
                )

                # Recursively process the dependencies of the dependency, incrementing the depth
                self.process_dependencies(
                    dependency_code_result_model.class_implementations,
                    data_wrapper,
                    all_class_implementations,
                    current_depth=current_depth + 1,
                )

    def _find_dependency_procedure(
        self, data_wrapper: DataWrapperModel, procedure_name: str
    ) -> Optional[ProcedureAnalysisResultModel]:
        """
        Helper method to find a dependency procedure in the data wrapper by its name.

        Args:
            data_wrapper (DataWrapperModel): The data wrapper containing the procedure analysis results.
            procedure_name (str): The name of the procedure to find.

        Returns:
            Optional[ProcedureAnalysisResultModel]: The found procedure analysis result model, or None if not found.
        """
        return next(
            (
                proc
                for proc in data_wrapper.output_procedure_analysis_result
                if proc.procedure_name == procedure_name
            ),
            None,
        )
