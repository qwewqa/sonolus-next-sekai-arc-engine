from sonolus.script.level import Level, LevelData

level = Level(
    name="sekai_level",
    title="PySekai Level",
    bgm=None,
    data=LevelData(
        bgm_offset=0,
        entities=[],
    ),
)


def load_levels():
    yield level
