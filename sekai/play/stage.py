from sonolus.script.archetype import PlayArchetype, callback

from sekai.lib.stage import draw_stage_and_accessories


class Stage(PlayArchetype):
    name = "Stage"

    def spawn_order(self) -> float:
        return -1e8

    def should_spawn(self) -> bool:
        return True

    @callback(order=2)
    def touch(self):
        pass

    def update_parallel(self):
        draw_stage_and_accessories()
