from sonolus.script.engine import PlayMode

from sekai.lib.buckets import Buckets
from sekai.lib.effect import Effects
from sekai.lib.particle import Particles
from sekai.lib.skin import Skin

play_mode = PlayMode(
    archetypes=[],
    skin=Skin,
    effects=Effects,
    particles=Particles,
    buckets=Buckets,
)
