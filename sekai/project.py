from sonolus.script.engine import Engine, EngineData
from sonolus.script.project import Project

from sekai.lib.converter import convert_pjsekai_extended_level_data
from sekai.lib.options import Options
from sekai.lib.ui import ui_config
from sekai.play.mode import play_mode
from sekai.preview.mode import preview_mode
from sekai.tutorial.mode import tutorial_mode
from sekai.watch.mode import watch_mode

engine = Engine(
    name="next-sekai-arc",
    title="Next SEKAI Arc",
    data=EngineData(
        ui=ui_config,
        options=Options,
        play=play_mode,
        watch=watch_mode,
        preview=preview_mode,
        tutorial=tutorial_mode,
    ),
)

project = Project(
    engine=engine,
    converters={
        None: convert_pjsekai_extended_level_data,
    },
)
