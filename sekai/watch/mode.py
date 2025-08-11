from sonolus.script.engine import WatchMode

from sekai.lib.buckets import Buckets
from sekai.lib.effect import Effects
from sekai.lib.particle import Particles
from sekai.lib.skin import Skin
from sekai.watch.update_spawn import update_spawn

watch_mode = WatchMode(
    archetypes=[],
    skin=Skin,
    effects=Effects,
    particles=Particles,
    buckets=Buckets,
    update_spawn=update_spawn,
)
