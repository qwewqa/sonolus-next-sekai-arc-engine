from sonolus.script.engine import PlayMode

from sekai.lib.buckets import Buckets
from sekai.lib.effect import Effects
from sekai.lib.particle import Particles
from sekai.lib.skin import Skin
from sekai.play.connector import ALL_CONNECTOR_ARCHETYPES
from sekai.play.initialization import Initialization
from sekai.play.input_manager import InputManager
from sekai.play.note import ALL_NOTE_ARCHETYPES
from sekai.play.sim_line import SimLine
from sekai.play.stage import Stage
from sekai.play.timescale import TimescaleChange, TimescaleGroup

play_mode = PlayMode(
    archetypes=[
        Initialization,
        Stage,
        InputManager,
        TimescaleGroup,
        TimescaleChange,
        *ALL_NOTE_ARCHETYPES,
        *ALL_CONNECTOR_ARCHETYPES,
        SimLine,
    ],
    skin=Skin,
    effects=Effects,
    particles=Particles,
    buckets=Buckets,
)
