import re
import time
import json
from contrib.utilities.files import FileManager
from contrib.utilities.clients.prompter import PrompterClient, create_prompter

from .prompts import _sys_prompt, _prompt_generate_timeline_report, _prompt_generate_table


class Service:
    def __init__(self) -> None:
        self.file_manager = FileManager()
        self.model = 'flow-openai-gpt-4.1'
    
    @staticmethod
    def minify_json(content: str) -> str:
        try:
            obj = json.loads(content)
            return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
        except json.JSONDecodeError:
            return content

    def run(self, file_scene: str, file_md: str) -> None:
        start_time = time.time()
        raw_scene = self.file_manager.read(location=file_scene)
        scene = self.minify_json(raw_scene)
        self._scene_to_table(scene, file_md)
        print(f"Scene file processed in {time.time() - start_time:.2f} seconds")

    def _scene_to_table(self, scene: str, file_md: str) -> None:
        prompt: PrompterClient = create_prompter(
            system_prompt=_sys_prompt,
            name="_scene_to_table",
            transient=True,
            model=self.model,
        )

        response_timeline = prompt.completion(
            _prompt_generate_timeline_report.format(
                input=scene
            )
        )
        self.file_manager.write(location=f"{file_md}/TIMELINE_REPORT.md", content=response_timeline)

        response_table = prompt.completion(
            _prompt_generate_table.format(
                input=response_timeline
            )
        )
        self.file_manager.write(location=f"{file_md}/SUMMARY_TABLE.md", content=response_table)