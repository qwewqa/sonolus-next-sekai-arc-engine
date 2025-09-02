from sonolus.script.archetype import PlayArchetype, StandardArchetypeName, StandardImport


class BpmChange(PlayArchetype):
    name = StandardArchetypeName.BPM_CHANGE

    beat: StandardImport.BEAT
    bpm: StandardImport.BPM

    def spawn_order(self) -> float:
        return 1e8

    def should_spawn(self) -> bool:
        return False
