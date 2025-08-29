from sonolus.script.archetype import EntityRef, PlayArchetype, callback, entity_data, imported
from sonolus.script.runtime import time

from sekai.lib.sim_line import draw_sim_line
from sekai.play.note import BaseNote


class SimLine(PlayArchetype):
    name = "SimLine"

    a_ref: EntityRef[BaseNote] = imported(name="a")
    b_ref: EntityRef[BaseNote] = imported(name="b")

    spawn_time: float = entity_data()

    @callback(order=1)
    def preprocess(self):
        self.spawn_time = min(self.a.spawn_time, self.b.spawn_time)

    def spawn_order(self) -> float:
        return self.spawn_time

    def should_spawn(self) -> bool:
        return time() >= self.spawn_time

    def update_parallel(self):
        if self.a.is_despawned or self.b.is_despawned:
            self.despawn = True
            return
        draw_sim_line(
            left_lane=self.a.lane,
            left_progress=self.a.progress,
            left_target_time=self.a.target_time,
            right_lane=self.b.lane,
            right_progress=self.b.progress,
            right_target_time=self.b.target_time,
        )

    @property
    def a(self) -> BaseNote:
        return self.a_ref.get()

    @property
    def b(self) -> BaseNote:
        return self.b_ref.get()
