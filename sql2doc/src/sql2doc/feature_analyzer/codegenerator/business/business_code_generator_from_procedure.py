import logging
from pydantic import BaseModel
from sql2doc.feature_analyzer.codegenerator.prompts import (
    CSharpSDKBusinessFromProcedurePrompt,
)
from sql2doc.feature_analyzer.codegenerator.prompts.csharp_sdk_business_from_procedure_agent_prompt import (
    CSharpSDKBusinessFromProcedureAgentPrompt,
)
from sql2doc.feature_analyzer.models.procedure_analysis_result_model import (
    ProcedureAnalysisResultModel,
)
from sql2doc.generativeai.prompter_interface import PrompterInterface


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BusinessCodeGeneratorFromProcedure:
    """
    Responsible for generating code from a given procedure using prompts and a language model.
    This class encapsulates the logic for generating code for individual procedures.
    """

    def __init__(self, prompter: PrompterInterface):
        """
        Initializes the CodeGenerator with a Prompter instance.

        Args:
            prompter (Prompter): The Prompter instance used to interact with the language model.
        """
        self.prompter = prompter
        self.logger = logging.getLogger(__name__)

    def generate_code_for_procedure_with_singleshot_as_structured(
        self,
        procedure: ProcedureAnalysisResultModel,
        class_to_be_implemented: str,
        parent_class_content: str = "",
    ) -> BaseModel:
        """
        Generates code for a given procedure by using a language model to generate code based on a prompt.

        Args:
            data_wrapper (DataWrapperModel): The data wrapper containing necessary context and information.
            procedure (ProcedureAnalysisResultModel): The procedure for which to generate code.
            class_to_be_implemented (str): The name of the class to be implemented.
            parent_class_content (str, optional): The content of the parent class. Defaults to "".

        Returns:
            CodeResultModel: The generated code result model.
        """
        self.logger.info(f"Generating code for procedure: {procedure.procedure_name}")

        # Construct the prompt using the provided information
        services_prompt = CSharpSDKBusinessFromProcedurePrompt(
            procedure_name=procedure.procedure_name,
            procedure_content=procedure.procedure_orignal_content,
            procedure_mermaid_representation=procedure.llm_mermaid_representation,
            parent_class_content=parent_class_content,
            class_to_be_implemented=class_to_be_implemented,
        )

        # Get the structured output from the language model using the constructed prompt
        return self.prompter.get_structured_output_from_llm(
            services_prompt.get_messages()
        )

    def generate_code_for_procedure_with_agent_as_structured(
        self,
        procedure: ProcedureAnalysisResultModel,
        class_to_be_implemented: str,
        parent_class_content: str = "",
    ) -> BaseModel:
        """
        Generates code for a given procedure by using a language model to generate code based on a prompt.

        Args:
            data_wrapper (DataWrapperModel): The data wrapper containing necessary context and information.
            procedure (ProcedureAnalysisResultModel): The procedure for which to generate code.
            class_to_be_implemented (str): The name of the class to be implemented.
            parent_class_content (str, optional): The content of the parent class. Defaults to "".

        Returns:
            CodeResultModel: The generated code result model.
        """
        self.logger.info(f"Generating code for procedure: {procedure.procedure_name}")

        # Construct the prompt using the provided information
        services_prompt = CSharpSDKBusinessFromProcedureAgentPrompt(
            procedure_name=procedure.procedure_name,
            procedure_content=procedure.procedure_orignal_content,
            procedure_mermaid_representation=procedure.llm_mermaid_representation,
            parent_class_content=parent_class_content,
            class_to_be_implemented=class_to_be_implemented,
        )

        return self.prompter.get_structured_output_from_llm(
            services_prompt.get_messages()
        )

    def generate_code_for_procedure_with_singleshot_as_str(
        self,
        procedure: ProcedureAnalysisResultModel,
        class_to_be_implemented: str,
        parent_class_content: str = "",
    ) -> str:
        """
        Generates code for a given procedure by using a language model to generate code based on a prompt.

        Args:
            data_wrapper (DataWrapperModel): The data wrapper containing necessary context and information.
            procedure (ProcedureAnalysisResultModel): The procedure for which to generate code.
            class_to_be_implemented (str): The name of the class to be implemented.
            parent_class_content (str, optional): The content of the parent class. Defaults to "".

        Returns:
            CodeResultModel: The generated code result model.
        """
        self.logger.info(f"Generating code for procedure: {procedure.procedure_name}")

        # Construct the prompt using the provided information
        services_prompt = CSharpSDKBusinessFromProcedurePrompt(
            procedure_name=procedure.procedure_name,
            procedure_content=procedure.procedure_orignal_content,
            procedure_mermaid_representation=procedure.llm_mermaid_representation,
            parent_class_content=parent_class_content,
            class_to_be_implemented=class_to_be_implemented,
        )

        return self.prompter.get_content_from_invoke_llm_with_messages(
            services_prompt.get_messages()
        )

    def generate_code_for_procedure_with_agent_as_str(
        self,
        procedure: ProcedureAnalysisResultModel,
        class_to_be_implemented: str,
        parent_class_content: str = "",
    ) -> str:
        """
        Generates code for a given procedure by using a language model to generate code based on a prompt.

        Args:
            data_wrapper (DataWrapperModel): The data wrapper containing necessary context and information.
            procedure (ProcedureAnalysisResultModel): The procedure for which to generate code.
            class_to_be_implemented (str): The name of the class to be implemented.
            parent_class_content (str, optional): The content of the parent class. Defaults to "".

        Returns:
            CodeResultModel: The generated code result model.
        """
        self.logger.info(f"Generating code for procedure: {procedure.procedure_name}")

        # Construct the prompt using the provided information
        services_prompt = CSharpSDKBusinessFromProcedureAgentPrompt(
            procedure_name=procedure.procedure_name,
            procedure_content=procedure.procedure_orignal_content,
            procedure_mermaid_representation=procedure.llm_mermaid_representation,
            parent_class_content=parent_class_content,
            class_to_be_implemented=class_to_be_implemented,
        )

        return self.prompter.get_content_from_invoke_llm_with_messages(
            services_prompt.get_messages()
        )
