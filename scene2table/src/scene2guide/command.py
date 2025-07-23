import re
import time
from contrib.utilities.files import FileManager
from prompter.base import ConfigAuthentication, Prompter

from .prompts import _sys_prompt, _prompt_generate_timeline_report, _prompt_generate_table


class Service:
    def __init__(self, config_authentication: ConfigAuthentication) -> None:
        self.config_authentication = config_authentication
        self.file_manager = FileManager()
        self.model = 'flow-openai-gpt-4.1'

    def run(self, file_scene: str, file_md: str) -> None:
        start_time = time.time()
        scene = self.file_manager.read(location=file_scene)

        self._scene_to_table(scene, file_md)
        print(f"Scene file processed in {time.time() - start_time:.2f} seconds")

    def _scene_to_table(self, scene: str, file_md: str) -> None:
        prompt = Prompter(
            syscontent=_sys_prompt,
            config_authentication=self.config_authentication,
            model=self.model,
        )

        response_timeline = prompt.user(
            _prompt_generate_timeline_report.format(
                input=scene
            ),
            nocache=True,
        )
        self.file_manager.write(location=f"{file_md}/TIMELINE_REPORT.md", content=response_timeline)

        response_table = prompt.user(
            _prompt_generate_table.format(
                input=response_timeline
            ),
            nocache=True,
        )
        self.file_manager.write(location=f"{file_md}/SUMMARY_TABLE.md", content=response_table)