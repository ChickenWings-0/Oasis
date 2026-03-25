from typing import Dict


class PromptSchedule:
    def __init__(self, base_prompt: str, keyframes: Dict[int, str]):
        self.base_prompt = base_prompt
        self.keyframes = keyframes

    def get_prompt(self, frame_index: int):
        keys = sorted(self.keyframes.keys())

        for k in reversed(keys):
            if frame_index >= k:
                return f"{self.base_prompt}, {self.keyframes[k]}"

        return self.base_prompt
