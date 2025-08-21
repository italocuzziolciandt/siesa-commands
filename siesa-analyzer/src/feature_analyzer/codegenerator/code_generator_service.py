import logging
from feature_analyzer.codegenerator.code_generator_service_interface import (
    CodeGeneratorServiceInterface,
)
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from prompter.base import ConfigAuthentication
from feature_analyzer.codegenerator.business.business_regular_code_generator_from_procedure import (
    BusinessRegularCodeGeneratorFromProcedure,
)
from generativeai.prompter_factory import PrompterFactory
from generativeai.prompter_interface import PrompterInterface
from feature_analyzer.codegenerator.entities.entities_code_generator_from_tables_content import (
    EntitiesCodeGeneratorFromTablesContent,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CodeGeneratorService(CodeGeneratorServiceInterface):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        self.logger.info("Starting code generation process...")
        code_generators = [
            EntitiesCodeGeneratorFromTablesContent(),
            BusinessRegularCodeGeneratorFromProcedure(max_dependency_depth=0),
        ]

        for code_generator in code_generators:
            self.logger.info(
                f"Using code generator: {code_generator.__class__.__name__}"
            )
            data_wrapper = code_generator.generate(data_wrapper)

        self.logger.info("Code generation process completed.")

        return data_wrapper
