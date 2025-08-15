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
    CachedScaledTimeToFirstTime,
    CachedTimeToScaledTime,
)


class TimescaleChange(PlayArchetype):
    name = TIMESCALE_CHANGE_NAME

    beat: StandardImport.BEAT
    timescale: float = imported(name="timeScale")
    next: EntityRef[TimescaleChange] = imported(name="next")

    def spawn_order(self) -> float:
        return 1e8

    def should_spawn(self) -> bool:
        return False


class TimescaleGroup(PlayArchetype):
    name = TIMESCALE_GROUP_NAME

    first: EntityRef[TimescaleChange] = imported(name="first")

    current_scaled_time: float = shared_memory()

    time_to_scaled_time: CachedTimeToScaledTime = shared_memory()
    scaled_time_to_first_time: CachedScaledTimeToFirstTime = shared_memory()

    def spawn_order(self) -> float:
        return -1e8

    def should_spawn(self) -> bool:
        return True

    @callback(order=-1)
    def preprocess(self):
        self.time_to_scaled_time.init(self.first.index)
        self.scaled_time_to_first_time.init(self.first.index)

    @callback(order=-1)
    def update_sequential(self):
        self.current_scaled_time = self.time_to_scaled_time.get(time())
