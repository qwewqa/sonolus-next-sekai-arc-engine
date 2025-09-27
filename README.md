# Next SEKAI Arc Sonolus Engine

A variant of the [Next SEKAI engine](https://github.com/Next-SEKAI/sonolus-next-sekai-engine)

## Quick Dev Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Run `uv sync`.
3. Add resources (full exported scp files) such as skins and levels to the `/resources` folder.
4. [Ensure your venv is activated](https://docs.astral.sh/uv/pip/environments/#using-a-virtual-environment).
5. Run `sonolus-py dev -O2`.

## Custom Resources

### Skin Sprites

| Name                                   |
|----------------------------------------|
| `Sekai Stage`                          |
| `Sekai Stage Surface`                  |
| `Sekai Note Cyan Left`                 |
| `Sekai Note Cyan Middle`               |
| `Sekai Note Cyan Right`                |
| `Sekai Note Green Left`                |
| `Sekai Note Green Middle`              |
| `Sekai Note Green Right`               |
| `Sekai Note Red Left`                  |
| `Sekai Note Red Middle`                |
| `Sekai Note Red Right`                 |
| `Sekai Note Yellow Left`               |
| `Sekai Note Yellow Middle`             |
| `Sekai Note Yellow Right`              |
| `Sekai Diamond Green`                  |
| `Sekai Diamond Yellow`                 |
| `Sekai Slide Connection Green`         |
| `Sekai Slide Connection Green Active`  |
| `Sekai Slide Connection Yellow`        |
| `Sekai Slide Connection Yellow Active` |
| `Sekai Slot Cyan`                      |
| `Sekai Slot Green`                     |
| `Sekai Slot Red`                       |
| `Sekai Slot Yellow`                    |
| `Sekai Slot Yellow Flick`              |
| `Sekai Slot Yellow Slider`             |
| `Sekai Slot Glow Cyan`                 |
| `Sekai Slot Glow Green`                |
| `Sekai Slot Glow Red`                  |
| `Sekai Slot Glow Yellow`               |
| `Sekai Slot Glow Yellow Flick`         |
| `Sekai Slot Glow Yellow Slider Tap`    |
| `Sekai Slot Glow Green Slider Hold`    |
| `Sekai Slot Glow Yellow Slider Hold`   |
| `Sekai Flick Arrow Red Up 1`           |
| `Sekai Flick Arrow Red Up 2`           |
| `Sekai Flick Arrow Red Up 3`           |
| `Sekai Flick Arrow Red Up 4`           |
| `Sekai Flick Arrow Red Up 5`           |
| `Sekai Flick Arrow Red Up 6`           |
| `Sekai Flick Arrow Red Up Left 1`      |
| `Sekai Flick Arrow Red Up Left 2`      |
| `Sekai Flick Arrow Red Up Left 3`      |
| `Sekai Flick Arrow Red Up Left 4`      |
| `Sekai Flick Arrow Red Up Left 5`      |
| `Sekai Flick Arrow Red Up Left 6`      |
| `Sekai Flick Arrow Red Down 1`         |
| `Sekai Flick Arrow Red Down 2`         |
| `Sekai Flick Arrow Red Down 3`         |
| `Sekai Flick Arrow Red Down 4`         |
| `Sekai Flick Arrow Red Down 5`         |
| `Sekai Flick Arrow Red Down 6`         |
| `Sekai Flick Arrow Red Down Left 1`    |
| `Sekai Flick Arrow Red Down Left 2`    |
| `Sekai Flick Arrow Red Down Left 3`    |
| `Sekai Flick Arrow Red Down Left 4`    |
| `Sekai Flick Arrow Red Down Left 5`    |
| `Sekai Flick Arrow Red Down Left 6`    |
| `Sekai Flick Arrow Yellow Up 1`        |
| `Sekai Flick Arrow Yellow Up 2`        |
| `Sekai Flick Arrow Yellow Up 3`        |
| `Sekai Flick Arrow Yellow Up 4`        |
| `Sekai Flick Arrow Yellow Up 5`        |
| `Sekai Flick Arrow Yellow Up 6`        |
| `Sekai Flick Arrow Yellow Up Left 1`   |
| `Sekai Flick Arrow Yellow Up Left 2`   |
| `Sekai Flick Arrow Yellow Up Left 3`   |
| `Sekai Flick Arrow Yellow Up Left 4`   |
| `Sekai Flick Arrow Yellow Up Left 5`   |
| `Sekai Flick Arrow Yellow Up Left 6`   |
| `Sekai Flick Arrow Yellow Down 1`      |
| `Sekai Flick Arrow Yellow Down 2`      |
| `Sekai Flick Arrow Yellow Down 3`      |
| `Sekai Flick Arrow Yellow Down 4`      |
| `Sekai Flick Arrow Yellow Down 5`      |
| `Sekai Flick Arrow Yellow Down 6`      |
| `Sekai Flick Arrow Yellow Down Left 1` |
| `Sekai Flick Arrow Yellow Down Left 2` |
| `Sekai Flick Arrow Yellow Down Left 3` |
| `Sekai Flick Arrow Yellow Down Left 4` |
| `Sekai Flick Arrow Yellow Down Left 5` |
| `Sekai Flick Arrow Yellow Down Left 6` |
| `Sekai Trace Note Green Left`          |
| `Sekai Trace Note Green Middle`        |
| `Sekai Trace Note Green Right`         |
| `Sekai Trace Note Yellow Left`         |
| `Sekai Trace Note Yellow Middle`       |
| `Sekai Trace Note Yellow Right`        |
| `Sekai Trace Note Red Left`            |
| `Sekai Trace Note Red Middle`          |
| `Sekai Trace Note Red Right`           |
| `Sekai Trace Diamond Green`            |
| `Sekai Trace Diamond Yellow`           |
| `Sekai Trace Diamond Red`              |
| `Sekai Guide Green`                    |
| `Sekai Guide Yellow`                   |
| `Sekai Guide Red`                      |
| `Sekai Guide Purple`                   |
| `Sekai Guide Cyan`                     |
| `Sekai Guide Blue`                     |
| `Sekai Guide Neutral`                  |
| `Sekai Guide Black`                    |
| `Sekai Trace Note Purple Left`         |
| `Sekai Trace Note Purple Middle`       |
| `Sekai Trace Note Purple Right`        |
| `Sekai Black Background`               |

### Effect Clips

| Name                   |
|------------------------|
| `Sekai Tick`           |
| `Sekai Critical Tap`   |
| `Sekai Critical Flick` |
| `Sekai Critical Hold`  |
| `Sekai Critical Tick`  |
| `Sekai Trace`          |
| `Sekai Critical Trace` |

### Particle Effects

| Name                                   |
|----------------------------------------|
| `Sekai Note Lane Linear`               |
| `Sekai Critical Lane Linear`           |
| `Sekai Critical Flick Lane Linear`     |
| `Sekai Slot Linear Tap Cyan`           |
| `Sekai Slot Linear Slide Tap Green`    |
| `Sekai Slot Linear Alternative Red`    |
| `Sekai Slot Linear Tap Yellow`         |
| `Sekai Slot Linear Slide Tap Yellow`   |
| `Sekai Slot Linear Alternative Yellow` |
| `Sekai Trace Note Circular Green`      |
| `Sekai Trace Note Linear Green`        |
| `Sekai Critical Slide Circular Yellow` |
| `Sekai Critical Slide Linear Yellow`   |
| `Sekai Critical Flick Circular Yellow` |
| `Sekai Critical Flick Linear Yellow`   |
| `Sekai Trace Note Circular Yellow`     |
| `Sekai Trace Note Linear Yellow`       |
| `Sekai Normal Slide Trail Linear`      |
| `Sekai Slot Linear Slide Green`        |
| `Sekai Critical Slide Trail Linear`    |
| `Sekai Slot Linear Slide Yellow`       |
