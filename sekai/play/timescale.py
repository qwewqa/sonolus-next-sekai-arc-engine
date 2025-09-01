from __future__ import annotations

from sonolus.script.archetype import (
    EntityRef,
    PlayArchetype,
    StandardImport,
    callback,
    imported,
    shared_memory,
)
from sonolus.script.runtime import time

from sekai.lib.timescale import (
    TIMESCALE_CHANGE_NAME,
    TIMESCALE_GROUP_NAME,
    ScaledTimeToFirstTime,
    TimeToScaledTime,
)


class TimescaleChange(PlayArchetype):
    name = TIMESCALE_CHANGE_NAME

    beat: StandardImport.BEAT
    timescale: StandardImport.TIMESCALE
    timescale_skip: StandardImport.TIMESCALE_SKIP
    timescale_group_ref: StandardImport.TIMESCALE_GROUP
    timescale_ease: StandardImport.TIMESCALE_EASE
    next_ref: EntityRef[TimescaleChange] = imported(name="next")

    def spawn_order(self) -> float:
        return 1e8

    def should_spawn(self) -> bool:
        return False


class TimescaleGroup(PlayArchetype):
    name = TIMESCALE_GROUP_NAME

    first_ref: EntityRef[TimescaleChange] = imported(name="first")

    current_scaled_time: float = shared_memory()

    time_to_scaled_time: TimeToScaledTime = shared_memory()
    scaled_time_to_first_time: ScaledTimeToFirstTime = shared_memory()

    def spawn_order(self) -> float:
        return -1e8

    def should_spawn(self) -> bool:
        return True

    @callback(order=-2)
    def preprocess(self):
        self.time_to_scaled_time.init(self.first_ref.index)
        self.scaled_time_to_first_time.init(self.first_ref.index)

    @callback(order=-2)
    def update_sequential(self):
        self.current_scaled_time = self.time_to_scaled_time.get(time())
