from sonolus.script.archetype import PlayArchetype, StandardImport

from sekai.lib import archetype_names


class BpmChange(PlayArchetype):
    name = archetype_names.BPM_CHANGE

    beat: StandardImport.BEAT
    bpm: StandardImport.BPM

    def spawn_order(self) -> float:
        return 1e8

    def should_spawn(self) -> bool:
        return False
