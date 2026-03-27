from prompt_engine import PromptSchedule


def get_preset(name: str):
    if name == "cyberpunk_night":
        schedule = PromptSchedule(
            "cyberpunk city",
            {
                0: "sunset lighting",
                4: "neon lights turning on",
                8: "night, rain, reflections",
            },
        )

        return {
            "prompt": "cyberpunk city",
            "prompt_schedule": schedule,
            "motion_level": "medium",
            "style": "cinematic",
            "motion_type": "zoom_in",
        }

    return None
