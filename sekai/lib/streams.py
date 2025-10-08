from sonolus.script.array import Dim
from sonolus.script.containers import VarArray
from sonolus.script.stream import Stream, StreamGroup, streams

from sekai.lib.connector import ConnectorKind, ConnectorVisualState
from sekai.lib.layout import FlickDirection


@streams
class Streams:
    empty_input_lanes: Stream[VarArray[float, Dim[16]]]
    connector_visual_states: StreamGroup[ConnectorVisualState, Dim[1_000_000]]
    connector_effect_kinds: StreamGroup[ConnectorKind, Dim[1_000_000]]
    flick_direction_overrides: Stream[FlickDirection]
    note_kind_overrides: Stream[int]
