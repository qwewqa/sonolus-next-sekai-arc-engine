from sonolus.script.engine import Engine, EngineData
from sonolus.script.project import Project

from sekai.lib.options import Options
from sekai.lib.ui import ui_config
from sekai.level import load_levels
from sekai.play.mode import play_mode
from sekai.preview.mode import preview_mode
from sekai.tutorial.mode import tutorial_mode
from sekai.watch.mode import watch_mode

engine = Engine(
    name="sekai",
    title="PySekai",
    skin="csbs-pjsekai-extended-01",
    particle="csbs-pjsekai-v3",
    effect="csbs-pjsekai-fixed",
    background="darkblue",
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
    levels=load_levels,
)
