from sonolus.script.archetype import PlayArchetype, entity_memory
from sonolus.script.interval import remap, unlerp
from sonolus.script.runtime import time
from sonolus.script.sprite import Sprite

from sekai.lib.layer import LAYER_SLOT_GLOW_EFFECT, get_z
from sekai.lib.layout import layout_slot_effect, layout_slot_glow_effect

SLOT_GLOW_EFFECT_DURATION = 0.25
SLOT_EFFECT_DURATION = 0.5


class SlotGlowEffect(PlayArchetype):
    name = "_SlotGlowEffect"

    sprite: Sprite = entity_memory()
    start_time: float = entity_memory()
    lane: float = entity_memory()
    size: float = entity_memory()
    end_time: float = entity_memory()

    def initialize(self):
        self.end_time = self.start_time + SLOT_GLOW_EFFECT_DURATION

    def update_parallel(self):
        if time() > self.end_time:
            self.despawn = True
            return
        progress = unlerp(self.start_time, self.end_time, time())
        layout = layout_slot_glow_effect(self.lane, self.size, progress)
        z = get_z(LAYER_SLOT_GLOW_EFFECT, -self.start_time, self.lane)
        a = remap(0, 1, 1, 0, progress)
        self.sprite.draw(layout, z=z, a=a)


class SlotEffect(PlayArchetype):
    name = "_SlotEffect"

    sprite: Sprite = entity_memory()
    start_time: float = entity_memory()
    lane: float = entity_memory()
    end_time: float = entity_memory()

    def initialize(self):
        self.end_time = self.start_time + SLOT_EFFECT_DURATION

    def update_parallel(self):
        if time() > self.end_time:
            self.despawn = True
            return
        progress = unlerp(self.start_time, self.end_time, time())
        layout = layout_slot_effect(self.lane)
        z = get_z(LAYER_SLOT_GLOW_EFFECT, -self.start_time, self.lane)
        a = remap(0, 1, 1, 0, progress)
        self.sprite.draw(layout, z=z, a=a)


SLOT_EFFECT_ARCHETYPES = (
    SlotGlowEffect,
    SlotEffect,
)
