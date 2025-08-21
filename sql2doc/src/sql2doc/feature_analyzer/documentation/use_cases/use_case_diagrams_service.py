from concurrent.futures import ThreadPoolExecutor
from feature_analyzer.models.data_wrapper_model import DataWrapperModel
from common.feature_toggle import feature_toggle_instance
from feature_analyzer.documentation.use_cases.prompts.sequence_diagram_prompt import (
    SequenceDiagramPrompt,
)
from feature_analyzer.documentation.use_cases.prompts.flow_diagram_prompt import (
    FlowDiagramPrompt,
)
from common.app_config import app_config_instance
from opentelemetry.trace import Status, StatusCode
from feature_analyzer.documentation.use_cases.base_use_case_generator_service import (
    BaseUseCaseGeneratorService,
)


class UseCaseDiagramsService(BaseUseCaseGeneratorService):
    max_workers: int = 2

    def analyze(self, data_wrapper: DataWrapperModel) -> DataWrapperModel:
        try:
            use_case_document = data_wrapper.output_use_cases_doc_full_content

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_sequence_diagram = executor.submit(
                    self.__generate_sequence_diagram,
                    data_wrapper,
                    use_case_document,
                )

                future_flow_diagram = executor.submit(
                    self.__generate_flow_diagram,
                    data_wrapper,
                    use_case_document,
                )

                future_sequence_diagram.result()
                future_flow_diagram.result()

        except Exception as error:
            self.logger.error(f"Error on generating the use cases diagrams: {error}.")

        return data_wrapper

    def __generate_sequence_diagram(
        self, data_wrapper: DataWrapperModel, use_case_document: str
    ) -> None:
        if not feature_toggle_instance.is_use_case_sequence_diagram_enabled():
            self.logger.info("Use Cases sequence diagram generation is disabled.")
            return

        self.logger.info("Generating use cases sequence diagram...")
        with app_config_instance.tracer.start_as_current_span(
            "UseCasesSequenceDiagram",
            openinference_span_kind="chain",
        ) as span:
            try:
                span.set_input(value=use_case_document)

                prompt = SequenceDiagramPrompt(use_cases_content=use_case_document)
                sequence_diagram = (
                    self.prompter.get_content_from_invoke_llm_with_messages(
                        prompt.get_messages()
                    )
                )

                data_wrapper.output_sequence_diagram_full_content = sequence_diagram

                span.set_output(sequence_diagram)
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))

    def __generate_flow_diagram(
        self, data_wrapper: DataWrapperModel, use_case_document: str
    ) -> None:
        if not feature_toggle_instance.is_use_case_flow_diagram_enabled():
            self.logger.info("Use Cases flow diagram generation is disabled.")
            return

        self.logger.info("Generating use cases flow diagram...")
        with app_config_instance.tracer.start_as_current_span(
            "UseCasesFlowDiagram",
            openinference_span_kind="chain",
        ) as span:
            try:
                span.set_input(value=use_case_document)

                prompt = FlowDiagramPrompt(use_cases_content=use_case_document)
                flow_diagram = self.prompter.get_content_from_invoke_llm_with_messages(
                    prompt.get_messages()
                )

                data_wrapper.output_flow_diagram_full_content = flow_diagram

                span.set_output(flow_diagram)
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
