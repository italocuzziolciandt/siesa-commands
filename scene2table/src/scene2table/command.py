import re
import time
import json
import os
from contrib.utilities.files import FileManager
from contrib.utilities.clients.prompter import PrompterClient, create_prompter
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        if os.path.isdir(file_scene):
            input_dir = file_scene
            entries = [f for f in os.listdir(input_dir)
                        if f.lower().startswith('summary') and f.lower().endswith('.json')]
            count = 0
            def process_entry(filename: str):
                path = os.path.join(input_dir, filename)
                raw = self.file_manager.read(location=path)
                scene = self.minify_json(raw)
                name = os.path.splitext(filename)[0]
                self._scene_to_table(scene, file_md, name)
                return filename

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(process_entry, fn): fn for fn in entries}
                for future in as_completed(futures):
                    fn = futures[future]
                    try:
                        future.result()
                        count += 1
                    except Exception as e:
                        print(f"Error processing {fn}: {e}", flush=True)
        else:
            raw = self.file_manager.read(location=file_scene)
            scene = self.minify_json(raw)
            name = os.path.splitext(os.path.basename(file_scene))[0]
            self._scene_to_table(scene, file_md, name)
            count = 1
        elapsed = time.time() - start_time
        print(f"Processed {count} scene(s) in {elapsed:.2f} seconds")

    def _scene_to_table(self, scene: str, file_md: str, scene_name: str) -> None:
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
        self.file_manager.write(location=f"{file_md}/{scene_name}/TIMELINE_REPORT.md", content=response_timeline)

        response_table = prompt.completion(
            _prompt_generate_table.format(
                input=response_timeline
            )
        )
        self.file_manager.write(location=f"{file_md}/{scene_name}/SUMMARY_TABLE.md", content=response_table)