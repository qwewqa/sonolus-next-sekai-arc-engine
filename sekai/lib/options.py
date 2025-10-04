from enum import IntEnum

from sonolus.script.options import options, select_option, slider_option, toggle_option
from sonolus.script.text import StandardText


class SlotEffectStyle(IntEnum):
    DISSIPATE = 0
    VERTICAL = 1
    LANE = 2


class GuideAlphaCurve(IntEnum):
    LINEAR = 0
    SLOW_ROLLOFF = 1
    FAST_ROLLOFF = 2


class ArcMode(IntEnum):
    DISABLED = 0
    ARC = 1
    CONVEX = 2
    CONCAVE = 3
    WAVE = 4
    SWING = 5


class FlickMod(IntEnum):
    NONE = 0
    MORE_FLICKS = 1
    EVEN_MORE_FLICKS = 2
    NO_FLICKS = 3
    FLICK_TO_TRACE_FLICK = 4


class FlickDirectionMod(IntEnum):
    NONE = 0
    MIRRORED = 1
    FLIPPED = 2
    ALL_UP = 3
    ALL_OMNI = 4
    ALL_UP_OMNI = 5
    RANDOM = 6


class TraceMod(IntEnum):
    NONE = 0
    MORE_TRACES = 1
    EVEN_MORE_TRACES = 2


class SlideTailMod(IntEnum):
    NONE = 0
    ALL_TRACES = 1
    RELEASE_TRACES = 2
    RELEASE_FLICKS = 3


class CriticalMod(IntEnum):
    NONE = 0
    ALL_CRITICAL = 1
    ALL_NORMAL = 2


class FadeMod(IntEnum):
    NONE = 0
    FADE_IN = 1
    FADE_OUT = 2
    FADE_IN_OUT = 3


class SlideMod(IntEnum):
    NONE = 0
    MONORAIL = 1
    TRACE_TICKS = 2


@options
class Options:
    speed: float = slider_option(
        name=StandardText.SPEED,
        standard=True,
        advanced=True,
        default=1,
        min=0.5,
        max=2,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    note_speed: float = slider_option(
        name=StandardText.NOTE_SPEED,
        scope="Sekai",
        default=6,
        min=1,
        max=12,
        step=0.01,
    )
    mirror: bool = toggle_option(
        name=StandardText.MIRROR,
        default=False,
    )
    sfx_enabled: bool = toggle_option(
        name=StandardText.EFFECT,
        scope="Sekai",
        default=True,
    )
    auto_sfx: bool = toggle_option(
        name=StandardText.EFFECT_AUTO,
        scope="Sekai",
        default=False,
    )
    effect_duration: float = slider_option(
        name="Effect Duration",
        scope="Next Sekai Arc",
        default=1,
        min=0.1,
        max=2,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    note_effect_enabled: bool = toggle_option(
        name=StandardText.NOTE_EFFECT,
        scope="Sekai",
        default=True,
    )
    note_effect_size: float = slider_option(
        name=StandardText.NOTE_EFFECT_SIZE,
        scope="Sekai",
        default=1,
        min=0.1,
        max=2,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    marker_animation: bool = toggle_option(
        name=StandardText.MARKER_ANIMATION,
        scope="Sekai",
        default=True,
    )
    sim_line_enabled: bool = toggle_option(
        name=StandardText.SIMLINE,
        scope="Sekai",
        default=True,
    )
    sim_line_alpha: float = slider_option(
        name=StandardText.SIMLINE_ALPHA,
        scope="Sekai",
        default=1.0,
        min=0,
        max=1,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    connector_animation: bool = toggle_option(
        name=StandardText.CONNECTOR_ANIMATION,
        scope="Sekai",
        default=True,
    )
    slide_alpha: float = slider_option(
        name="Slide Alpha",
        scope="Sekai",
        default=0.8,
        min=0,
        max=1,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    guide_alpha: float = slider_option(
        name="Guide Alpha",
        scope="Sekai",
        default=0.5,
        min=0,
        max=1,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    guide_alpha_curve: GuideAlphaCurve = select_option(
        name="Guide Alpha Curve",
        scope="Next Sekai Arc",
        default=GuideAlphaCurve.LINEAR,
        values=[
            "Linear",
            "Slow Roll-off",
            "Fast Roll-off",
        ],
    )
    lane_effect_enabled: bool = toggle_option(
        name=StandardText.LANE_EFFECT,
        scope="Sekai",
        default=True,
    )
    slot_effect_enabled: bool = toggle_option(
        name=StandardText.SLOT_EFFECT,
        scope="Sekai",
        default=True,
    )
    slot_effect_size: float = slider_option(
        name=StandardText.SLOT_EFFECT_SIZE,
        scope="Sekai",
        default=1,
        min=0,
        max=2,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    slot_effect_style: SlotEffectStyle = select_option(
        name="Slot Effect Style",
        scope="Next Sekai Arc",
        default=SlotEffectStyle.DISSIPATE,
        values=[
            "Dissipate",
            "Vertical",
            "Lane",
        ],
    )
    slot_effect_spread: float = slider_option(
        name="Slot Effect Spread",
        scope="Next Sekai Arc",
        default=0.2,
        min=0,
        max=2,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    stage_cover: float = slider_option(
        name=StandardText.STAGE_COVER_VERTICAL,
        advanced=True,
        scope="Sekai",
        default=0,
        min=0,
        max=1,
        step=0.01,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    zoom: float = slider_option(
        name="Zoom",
        scope="Next Sekai Arc",
        default=1,
        min=0.5,
        max=2,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    width_scale: float = slider_option(
        name="Width Scale",
        scope="Next Sekai Arc",
        default=1,
        min=0.5,
        max=2,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    y_offset: float = slider_option(
        name="Y Offset",
        scope="Next Sekai Arc",
        default=0,
        min=-0.5,
        max=0.5,
        step=0.01,
    )
    hidden: float = slider_option(
        name=StandardText.HIDDEN,
        scope="Sekai",
        advanced=True,
        default=0,
        min=0,
        max=1,
        step=0.01,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    lock_stage_aspect_ratio: bool = toggle_option(
        name=StandardText.STAGE_ASPECTRATIO_LOCK,
        scope="Sekai",
        default=True,
    )
    hide_ui: bool = toggle_option(
        name="Hide UI",
        scope="Sekai",
        default=False,
    )
    show_lane: bool = toggle_option(
        name=StandardText.STAGE,
        scope="Sekai",
        default=True,
    )
    no_lane_dividers: bool = toggle_option(
        name="No Lane Dividers",
        scope="Sekai",
        default=False,
    )
    slide_quality: float = slider_option(
        name="Slide Quality",
        scope="Next Sekai",
        default=1,
        min=0.5,
        max=2,
        step=0.1,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    guide_quality: float = slider_option(
        name="Guide Quality",
        scope="Next Sekai",
        default=1,
        min=0.5,
        max=2,
        step=0.1,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    arc_quality: float = slider_option(
        name="Arc Quality",
        scope="Next Sekai Arc",
        default=1,
        min=0.5,
        max=2,
        step=0.1,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    note_margin: float = slider_option(
        name="Note Margin",
        scope="Next Sekai",
        default=0.0,
        min=0.0,
        max=0.2,
        step=0.01,
    )
    note_thickness: float = slider_option(
        name="Note Thickness",
        scope="Next Sekai",
        default=1.0,
        min=0.1,
        max=2.0,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
    )
    alternative_approach_curve: bool = toggle_option(
        name="Alternative Approach Curve",
        advanced=True,
        default=False,
        scope="Next Sekai",
    )
    lane_effects_from_judge_line: bool = toggle_option(
        name="Lane Effects From Judge Line",
        scope="Next Sekai Arc",
        default=False,
    )
    disable_timescale: bool = toggle_option(
        name="Disable Timescale",
        standard=True,
        advanced=True,
        default=False,
    )
    arc_mode: ArcMode = select_option(
        name="Arc Mode",
        scope="Next Sekai Arc",
        default=ArcMode.ARC,
        values=[
            "Disabled",
            "Arc",
            "Convex",
            "Concave",
            "Wave",
            "Swing",
        ],
        standard=True,
    )
    judgment_window_size: float = slider_option(
        name="Judgment Window Size",
        scope="Next Sekai Arc",
        default=1,
        min=0.1,
        max=2,
        step=0.05,
        unit=StandardText.PERCENTAGE_UNIT,
        standard=True,
    )
    additional_hitbox_leniency: float = slider_option(
        name="Additional Hitbox Leniency",
        scope="Next Sekai Arc",
        default=0,
        min=0,
        max=4,
        step=0.1,
        standard=True,
    )
    flick_mod: FlickMod = select_option(
        name="Flick Mod",
        scope="Next Sekai Arc",
        default=FlickMod.NONE,
        values=[
            "None",
            "More Flicks",
            "Even More Flicks",
            "No Flicks",
            "Flicks to Trace Flicks",
        ],
        standard=True,
    )
    flick_direction_mod: FlickDirectionMod = select_option(
        name="Flick Direction Mod",
        scope="Next Sekai Arc",
        default=FlickDirectionMod.NONE,
        values=[
            "None",
            "Mirrored",
            "Flipped",
            "All Up",
            "All Omni",
            "All Up Omni",
            "Random",
        ],
        standard=True,
    )
    trace_mod: TraceMod = select_option(
        name="Trace Mod",
        scope="Next Sekai Arc",
        default=TraceMod.NONE,
        values=[
            "None",
            "More Traces",
            "Even More Traces",
        ],
        standard=True,
    )
    slide_tail_mod: SlideTailMod = select_option(
        name="Slide Tail Mod",
        scope="Next Sekai Arc",
        default=SlideTailMod.NONE,
        values=[
            "None",
            "All Traces",
            "Releases to Traces",
        ],
        standard=True,
    )
    critical_mod: CriticalMod = select_option(
        name="Critical Mod",
        scope="Next Sekai Arc",
        default=CriticalMod.NONE,
        values=[
            "None",
            "All Critical",
            "No Critical",
        ],
        standard=True,
    )
    fade_mod: FadeMod = select_option(
        name="Fade Mod",
        scope="Next Sekai Arc",
        default=FadeMod.NONE,
        values=[
            "None",
            "Fade In",
            "Fade Out",
            "Fade In Out",
        ],
        standard=True,
    )
    slide_mod: SlideMod = select_option(
        name="Slide Mod",
        scope="Next Sekai Arc",
        default=SlideMod.NONE,
        values=[
            "None",
            "Monorail",
            "Trace Ticks",
        ],
        standard=True,
    )
