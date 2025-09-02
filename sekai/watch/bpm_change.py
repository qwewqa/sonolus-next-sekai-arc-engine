from sonolus.script.archetype import StandardArchetypeName, StandardImport, WatchArchetype


class WatchBpmChange(WatchArchetype):
    name = StandardArchetypeName.BPM_CHANGE

    beat: StandardImport.BEAT
    bpm: StandardImport.BPM
