from sonolus.script.archetype import PlayArchetype, StandardImport, callback, imported, shared_memory
from sonolus.script.runtime import time

from sekai.lib.timescale import (
    TIMESCALE_CHANGE_NAME,
    TIMESCALE_GROUP_NAME,
    extended_time_to_scaled_time,
)


class TimescaleChange(PlayArchetype):
    name = TIMESCALE_CHANGE_NAME

    beat: StandardImport.BEAT
    timescale: float = imported(name="timeScale")
    next_index: int = imported(name="next")

    def spawn_order(self) -> float:
        return 1e8

    def should_spawn(self) -> bool:
        return False


class TimescaleGroup(PlayArchetype):
    name = TIMESCALE_GROUP_NAME

    first_index: int = imported(name="first")

    current_scaled_time: float = shared_memory()

    def spawn_order(self) -> float:
        return -1e8

    def should_spawn(self) -> bool:
        return True

    @callback(order=-1)
    def update_sequential(self):
        self.current_scaled_time = extended_time_to_scaled_time(self.index, time())
        # debug_log(extended_scaled_time_to_first_time(self.index, self.current_scaled_time))
        # debug_log(self.current_scaled_time)
