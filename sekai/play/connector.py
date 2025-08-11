from sonolus.script.archetype import PlayArchetype

from sekai.lib.connector import SlideConnectorKind


class SlideConnector(PlayArchetype):
    pass


class Guide(PlayArchetype):
    name = "Guide"


NormalSlideConnector = SlideConnector.derive("NormalSlideConnector", is_scored=False, key=SlideConnectorKind.NORMAL)
CriticalSlideConnector = SlideConnector.derive(
    "CriticalSlideConnector", is_scored=False, key=SlideConnectorKind.CRITICAL
)

ALL_CONNECTOR_ARCHETYPES = (
    NormalSlideConnector,
    CriticalSlideConnector,
    Guide,
)
