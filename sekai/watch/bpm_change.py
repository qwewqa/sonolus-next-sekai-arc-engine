from sonolus.script.archetype import StandardImport, WatchArchetype

from sekai.lib import archetype_names


class WatchBpmChange(WatchArchetype):
    name = archetype_names.BPM_CHANGE

    beat: StandardImport.BEAT
    bpm: StandardImport.BPM
