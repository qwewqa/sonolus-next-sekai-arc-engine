from sonolus.script.engine import PreviewMode

from sekai.lib.skin import Skin
from sekai.preview.initialization import PreviewInitialization

preview_mode = PreviewMode(
    archetypes=[PreviewInitialization],
    skin=Skin,
)
