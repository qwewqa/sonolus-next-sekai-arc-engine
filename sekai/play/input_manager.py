from sonolus.script.archetype import PlayArchetype
from sonolus.script.array import Dim
from sonolus.script.containers import ArraySet
from sonolus.script.globals import level_memory


@level_memory
class InputState:
    old_disallowed_empties: ArraySet[int, Dim[16]]
    new_disallowed_empties: ArraySet[int, Dim[16]]


class InputManager(PlayArchetype):
    name = "InputManager"
