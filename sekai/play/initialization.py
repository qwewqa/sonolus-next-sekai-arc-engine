from sonolus.script.archetype import PlayArchetype, callback

from sekai.lib.layout import init_layout
from sekai.lib.ui import init_ui


class Initialization(PlayArchetype):
    name = "Initialization"

    @callback(order=-1)
    def preprocess(self):
        init_layout()
        init_ui()

    def spawn_order(self) -> float:
        return 1e8

    def should_spawn(self) -> bool:
        return False
