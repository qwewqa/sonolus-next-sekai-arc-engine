from __future__ import annotations

from sonolus.script.archetype import (
    EntityRef,
    StandardImport,
    WatchArchetype,
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


class WatchTimescaleChange(WatchArchetype):
    name = TIMESCALE_CHANGE_NAME

    beat: StandardImport.BEAT
    timescale: StandardImport.TIMESCALE
    timescale_skip: StandardImport.TIMESCALE_SKIP
    timescale_group: StandardImport.TIMESCALE_GROUP
    timescale_ease: StandardImport.TIMESCALE_EASE
    next_ref: EntityRef[WatchTimescaleChange] = imported(name="next")


class WatchTimescaleGroup(WatchArchetype):
    name = TIMESCALE_GROUP_NAME

    first_ref: EntityRef[WatchTimescaleChange] = imported(name="first")

    current_scaled_time: float = shared_memory()

    time_to_scaled_time: TimeToScaledTime = shared_memory()
    scaled_time_to_first_time: ScaledTimeToFirstTime = shared_memory()
    scaled_time_to_first_time_2: ScaledTimeToFirstTime = shared_memory()

    def spawn_time(self) -> float:
        return -1e8

    def despawn_time(self) -> float:
        return 1e8

    @callback(order=-2)
    def preprocess(self):
        self.time_to_scaled_time.init(self.first_ref.index)
        self.scaled_time_to_first_time.init(self.first_ref.index)
        self.scaled_time_to_first_time_2.init(self.first_ref.index)

    @callback(order=-2)
    def update_sequential(self):
        self.current_scaled_time = self.time_to_scaled_time.get(time())
