from sonolus.script.archetype import PlayArchetype, entity_memory
from sonolus.script.runtime import time
from sonolus.script.sprite import Sprite

from sekai.lib import archetype_names
from sekai.lib.slot_effect import (
    draw_slot_effect,
    draw_slot_glow_effect,
    slot_effect_duration,
    slot_glow_effect_duration,
)


class SlotGlowEffect(PlayArchetype):
    name = archetype_names.SLOT_GLOW_EFFECT

    sprite: Sprite = entity_memory()
    start_time: float = entity_memory()
    lane: float = entity_memory()
    size: float = entity_memory()
    end_time: float = entity_memory()

    def initialize(self):
        self.end_time = self.start_time + slot_glow_effect_duration()

    def update_parallel(self):
        if time() > self.end_time:
            self.despawn = True
            return
        draw_slot_glow_effect(
            self.sprite,
            self.start_time,
            self.end_time,
            self.lane,
            self.size,
        )


class SlotEffect(PlayArchetype):
    name = archetype_names.SLOT_EFFECT

    sprite: Sprite = entity_memory()
    start_time: float = entity_memory()
    lane: float = entity_memory()
    end_time: float = entity_memory()

    def initialize(self):
        self.end_time = self.start_time + slot_effect_duration()

    def update_parallel(self):
        if time() > self.end_time:
            self.despawn = True
            return
        draw_slot_effect(
            self.sprite,
            self.start_time,
            self.end_time,
            self.lane,
        )


SLOT_EFFECT_ARCHETYPES = (
    SlotGlowEffect,
    SlotEffect,
)
