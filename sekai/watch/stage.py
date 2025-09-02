from sonolus.script.archetype import WatchArchetype, entity_memory
from sonolus.script.runtime import is_skip

from sekai.lib.stage import draw_stage_and_accessories, play_lane_particle


class WatchStage(WatchArchetype):
    name = "_Stage"

    def spawn_time(self) -> float:
        return -1e8

    def despawn_time(self) -> float:
        return 1e8

    def update_parallel(self):
        draw_stage_and_accessories()


class WatchScheduledLaneEffect(WatchArchetype):
    name = "_ScheduledLaneEffect"

    lane: float = entity_memory()
    target_time: float = entity_memory()

    def spawn_time(self) -> float:
        return self.target_time

    def despawn_time(self) -> float:
        return self.target_time + 1

    def initialize(self):
        if is_skip():
            return
        play_lane_particle(self.lane)
