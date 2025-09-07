from sonolus.script.archetype import PreviewArchetype, callback

from sekai.lib import archetype_names
from sekai.lib.ui import init_ui


class PreviewInitialization(PreviewArchetype):
    name = archetype_names.INITIALIZATION

    @callback(order=-1)
    def preprocess(self):
        init_ui()
