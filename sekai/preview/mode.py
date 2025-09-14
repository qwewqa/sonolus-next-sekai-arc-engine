from sonolus.script.engine import PreviewMode

from sekai.lib.skin import Skin
from sekai.preview.connector import PreviewConnector
from sekai.preview.initialization import PreviewInitialization
from sekai.preview.note import PREVIEW_NOTE_ARCHETYPES

preview_mode = PreviewMode(
    archetypes=[
        PreviewInitialization,
        # BpmChange,
        # TimescaleGroup,
        # TimescaleChange,
        *PREVIEW_NOTE_ARCHETYPES,
        PreviewConnector,
        # SimLine,
    ],
    skin=Skin,
)
