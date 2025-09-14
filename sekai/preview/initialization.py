from sonolus.script.archetype import PreviewArchetype, callback

from sekai.lib import archetype_names
from sekai.lib.ui import init_ui
from sekai.preview.layout import init_preview_layout
from sekai.preview.stage import draw_preview_background_dim, draw_preview_cover, draw_preview_stage


class PreviewInitialization(PreviewArchetype):
    name = archetype_names.INITIALIZATION

    @callback(order=1)
    def preprocess(self):
        init_ui()
        init_preview_layout()

    def render(self):
        draw_preview_stage()
        draw_preview_background_dim()
        draw_preview_cover()
