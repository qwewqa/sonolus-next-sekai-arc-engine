from typing import assert_never

from sonolus.script.array import Array, Dim
from sonolus.script.interval import clamp
from sonolus.script.record import Record
from sonolus.script.sprite import Sprite, StandardSprite, skin, sprite

from sekai.lib.layout import FlickDirection


@skin
class Skin:
    cover: StandardSprite.STAGE_COVER

    lane: StandardSprite.LANE
    judgment_line: StandardSprite.JUDGMENT_LINE
    stage_left_border: StandardSprite.STAGE_LEFT_BORDER
    stage_right_border: StandardSprite.STAGE_RIGHT_BORDER

    sekai_stage: Sprite = sprite("Sekai Stage")

    sim_line: StandardSprite.SIMULTANEOUS_CONNECTION_NEUTRAL

    normal_note_left: Sprite = sprite("Sekai Note Cyan Left")
    normal_note_middle: Sprite = sprite("Sekai Note Cyan Middle")
    normal_note_right: Sprite = sprite("Sekai Note Cyan Right")
    normal_note_fallback: StandardSprite.NOTE_HEAD_CYAN

    slide_note_left: Sprite = sprite("Sekai Note Green Left")
    slide_note_middle: Sprite = sprite("Sekai Note Green Middle")
    slide_note_right: Sprite = sprite("Sekai Note Green Right")
    slide_note_fallback: StandardSprite.NOTE_HEAD_GREEN
    slide_note_end_fallback: StandardSprite.NOTE_TAIL_GREEN

    flick_note_left: Sprite = sprite("Sekai Note Red Left")
    flick_note_middle: Sprite = sprite("Sekai Note Red Middle")
    flick_note_right: Sprite = sprite("Sekai Note Red Right")
    flick_note_fallback: StandardSprite.NOTE_HEAD_RED
    flick_note_end_fallback: StandardSprite.NOTE_TAIL_RED

    critical_note_left: Sprite = sprite("Sekai Note Yellow Left")
    critical_note_middle: Sprite = sprite("Sekai Note Yellow Middle")
    critical_note_right: Sprite = sprite("Sekai Note Yellow Right")
    critical_note_fallback: StandardSprite.NOTE_HEAD_YELLOW
    critical_note_end_fallback: StandardSprite.NOTE_TAIL_YELLOW

    normal_slide_tick_note: Sprite = sprite("Sekai Diamond Green")
    normal_slide_tick_note_fallback: StandardSprite.NOTE_TICK_GREEN

    critical_slide_tick_note: Sprite = sprite("Sekai Diamond Yellow")
    critical_slide_tick_note_fallback: StandardSprite.NOTE_TICK_YELLOW

    normal_slide_connector_normal: Sprite = sprite("Sekai Slide Connection Green")
    normal_slide_connector_active: Sprite = sprite("Sekai Slide Connection Green Active")
    normal_slide_connector_fallback: StandardSprite.NOTE_CONNECTION_GREEN_SEAMLESS

    critical_slide_connector_normal: Sprite = sprite("Sekai Slide Connection Yellow")
    critical_slide_connector_active: Sprite = sprite("Sekai Slide Connection Yellow Active")
    critical_slide_connector_fallback: StandardSprite.NOTE_CONNECTION_YELLOW_SEAMLESS

    normal_slot: Sprite = sprite("Sekai Slot Cyan")
    slide_slot: Sprite = sprite("Sekai Slot Green")
    flick_slot: Sprite = sprite("Sekai Slot Red")
    critical_slot: Sprite = sprite("Sekai Slot Yellow")
    critical_flick_slot: Sprite = sprite("Sekai Slot Yellow Flick")
    critical_slide_slot: Sprite = sprite("Sekai Slot Yellow Slider")

    normal_slot_glow: Sprite = sprite("Sekai Slot Glow Cyan")
    slide_slot_glow: Sprite = sprite("Sekai Slot Glow Green")
    flick_slot_glow: Sprite = sprite("Sekai Slot Glow Red")
    critical_slot_glow: Sprite = sprite("Sekai Slot Glow Yellow")
    critical_flick_slot_glow: Sprite = sprite("Sekai Slot Glow Yellow Flick")
    critical_slide_slot_glow: Sprite = sprite("Sekai Slot Glow Yellow Slider Tap")

    normal_slide_connector_slot_glow: Sprite = sprite("Sekai Slot Glow Green Slider Hold")
    critical_slide_connector_slot_glow: Sprite = sprite("Sekai Slot Glow Yellow Slider Hold")

    flick_arrow_up1: Sprite = sprite("Sekai Flick Arrow Red Up 1")
    flick_arrow_up2: Sprite = sprite("Sekai Flick Arrow Red Up 2")
    flick_arrow_up3: Sprite = sprite("Sekai Flick Arrow Red Up 3")
    flick_arrow_up4: Sprite = sprite("Sekai Flick Arrow Red Up 4")
    flick_arrow_up5: Sprite = sprite("Sekai Flick Arrow Red Up 5")
    flick_arrow_up6: Sprite = sprite("Sekai Flick Arrow Red Up 6")
    flick_arrow_up_left1: Sprite = sprite("Sekai Flick Arrow Red Up Left 1")
    flick_arrow_up_left2: Sprite = sprite("Sekai Flick Arrow Red Up Left 2")
    flick_arrow_up_left3: Sprite = sprite("Sekai Flick Arrow Red Up Left 3")
    flick_arrow_up_left4: Sprite = sprite("Sekai Flick Arrow Red Up Left 4")
    flick_arrow_up_left5: Sprite = sprite("Sekai Flick Arrow Red Up Left 5")
    flick_arrow_up_left6: Sprite = sprite("Sekai Flick Arrow Red Up Left 6")
    flick_arrow_down1: Sprite = sprite("Sekai Flick Arrow Red Down 1")
    flick_arrow_down2: Sprite = sprite("Sekai Flick Arrow Red Down 2")
    flick_arrow_down3: Sprite = sprite("Sekai Flick Arrow Red Down 3")
    flick_arrow_down4: Sprite = sprite("Sekai Flick Arrow Red Down 4")
    flick_arrow_down5: Sprite = sprite("Sekai Flick Arrow Red Down 5")
    flick_arrow_down6: Sprite = sprite("Sekai Flick Arrow Red Down 6")
    flick_arrow_down_left1: Sprite = sprite("Sekai Flick Arrow Red Down Left 1")
    flick_arrow_down_left2: Sprite = sprite("Sekai Flick Arrow Red Down Left 2")
    flick_arrow_down_left3: Sprite = sprite("Sekai Flick Arrow Red Down Left 3")
    flick_arrow_down_left4: Sprite = sprite("Sekai Flick Arrow Red Down Left 4")
    flick_arrow_down_left5: Sprite = sprite("Sekai Flick Arrow Red Down Left 5")
    flick_arrow_down_left6: Sprite = sprite("Sekai Flick Arrow Red Down Left 6")
    flick_arrow_fallback: StandardSprite.DIRECTIONAL_MARKER_RED

    critical_arrow_up1: Sprite = sprite("Sekai Flick Arrow Yellow Up 1")
    critical_arrow_up2: Sprite = sprite("Sekai Flick Arrow Yellow Up 2")
    critical_arrow_up3: Sprite = sprite("Sekai Flick Arrow Yellow Up 3")
    critical_arrow_up4: Sprite = sprite("Sekai Flick Arrow Yellow Up 4")
    critical_arrow_up5: Sprite = sprite("Sekai Flick Arrow Yellow Up 5")
    critical_arrow_up6: Sprite = sprite("Sekai Flick Arrow Yellow Up 6")
    critical_arrow_up_left1: Sprite = sprite("Sekai Flick Arrow Yellow Up Left 1")
    critical_arrow_up_left2: Sprite = sprite("Sekai Flick Arrow Yellow Up Left 2")
    critical_arrow_up_left3: Sprite = sprite("Sekai Flick Arrow Yellow Up Left 3")
    critical_arrow_up_left4: Sprite = sprite("Sekai Flick Arrow Yellow Up Left 4")
    critical_arrow_up_left5: Sprite = sprite("Sekai Flick Arrow Yellow Up Left 5")
    critical_arrow_up_left6: Sprite = sprite("Sekai Flick Arrow Yellow Up Left 6")
    critical_arrow_down1: Sprite = sprite("Sekai Flick Arrow Yellow Down 1")
    critical_arrow_down2: Sprite = sprite("Sekai Flick Arrow Yellow Down 2")
    critical_arrow_down3: Sprite = sprite("Sekai Flick Arrow Yellow Down 3")
    critical_arrow_down4: Sprite = sprite("Sekai Flick Arrow Yellow Down 4")
    critical_arrow_down5: Sprite = sprite("Sekai Flick Arrow Yellow Down 5")
    critical_arrow_down6: Sprite = sprite("Sekai Flick Arrow Yellow Down 6")
    critical_arrow_down_left1: Sprite = sprite("Sekai Flick Arrow Yellow Down Left 1")
    critical_arrow_down_left2: Sprite = sprite("Sekai Flick Arrow Yellow Down Left 2")
    critical_arrow_down_left3: Sprite = sprite("Sekai Flick Arrow Yellow Down Left 3")
    critical_arrow_down_left4: Sprite = sprite("Sekai Flick Arrow Yellow Down Left 4")
    critical_arrow_down_left5: Sprite = sprite("Sekai Flick Arrow Yellow Down Left 5")
    critical_arrow_down_left6: Sprite = sprite("Sekai Flick Arrow Yellow Down Left 6")
    critical_arrow_fallback: StandardSprite.DIRECTIONAL_MARKER_YELLOW

    normal_trace_note_left: Sprite = sprite("Sekai Trace Note Green Left")
    normal_trace_note_middle: Sprite = sprite("Sekai Trace Note Green Middle")
    normal_trace_note_right: Sprite = sprite("Sekai Trace Note Green Right")
    normal_trace_note_fallback: StandardSprite.NOTE_HEAD_GREEN
    normal_trace_tick_note: Sprite = sprite("Sekai Trace Diamond Green")
    normal_trace_tick_note_fallback: StandardSprite.NOTE_TICK_GREEN

    critical_trace_note_left: Sprite = sprite("Sekai Trace Note Yellow Left")
    critical_trace_note_middle: Sprite = sprite("Sekai Trace Note Yellow Middle")
    critical_trace_note_right: Sprite = sprite("Sekai Trace Note Yellow Right")
    critical_trace_note_fallback: StandardSprite.NOTE_HEAD_YELLOW
    critical_trace_tick_note: Sprite = sprite("Sekai Trace Diamond Yellow")
    critical_trace_tick_note_fallback: StandardSprite.NOTE_TICK_YELLOW

    trace_flick_note_left: Sprite = sprite("Sekai Trace Note Red Left")
    trace_flick_note_middle: Sprite = sprite("Sekai Trace Note Red Middle")
    trace_flick_note_right: Sprite = sprite("Sekai Trace Note Red Right")
    trace_flick_note_fallback: StandardSprite.NOTE_HEAD_RED
    trace_flick_tick_note: Sprite = sprite("Sekai Trace Diamond Red")
    trace_flick_tick_note_fallback: StandardSprite.NOTE_TICK_RED

    guide_green: Sprite = sprite("Sekai Guide Green")
    guide_green_fallback: StandardSprite.NOTE_CONNECTION_GREEN_SEAMLESS
    guide_yellow: Sprite = sprite("Sekai Guide Yellow")
    guide_yellow_fallback: StandardSprite.NOTE_CONNECTION_YELLOW_SEAMLESS
    guide_red: Sprite = sprite("Sekai Guide Red")
    guide_red_fallback: StandardSprite.NOTE_CONNECTION_RED_SEAMLESS
    guide_purple: Sprite = sprite("Sekai Guide Purple")
    guide_purple_fallback: StandardSprite.NOTE_CONNECTION_PURPLE_SEAMLESS
    guide_cyan: Sprite = sprite("Sekai Guide Cyan")
    guide_cyan_fallback: StandardSprite.NOTE_CONNECTION_CYAN_SEAMLESS
    guide_blue: Sprite = sprite("Sekai Guide Blue")
    guide_blue_fallback: StandardSprite.NOTE_CONNECTION_BLUE_SEAMLESS
    guide_neutral: Sprite = sprite("Sekai Guide Neutral")
    guide_neutral_fallback: StandardSprite.NOTE_CONNECTION_NEUTRAL_SEAMLESS
    guide_black: Sprite = sprite("Sekai Guide Black")
    guide_black_fallback: StandardSprite.NOTE_CONNECTION_NEUTRAL_SEAMLESS

    damage_note_left: Sprite = sprite("Sekai Trace Note Purple Left")
    damage_note_middle: Sprite = sprite("Sekai Trace Note Purple Middle")
    damage_note_right: Sprite = sprite("Sekai Trace Note Purple Right")
    damage_note_fallback: StandardSprite.NOTE_HEAD_PURPLE

    beat_line: StandardSprite.GRID_NEUTRAL
    bpm_change_line: StandardSprite.GRID_PURPLE
    timescale_change_line: StandardSprite.GRID_YELLOW
    special_line: StandardSprite.GRID_RED


class BodySprites(Record):
    left: Sprite
    middle: Sprite
    right: Sprite
    fallback: Sprite

    @property
    def custom_available(self):
        return self.left.is_available


class ArrowSprites(Record):
    up: Array[Sprite, Dim[6]]
    up_left: Array[Sprite, Dim[6]]
    down: Array[Sprite, Dim[6]]
    down_left: Array[Sprite, Dim[6]]
    fallback: Sprite

    def _get_index_from_size(self, size: float) -> int:
        return int(clamp(round(size * 2), 1, 6)) - 1

    def get_sprite(self, size: float, direction: FlickDirection) -> Sprite:
        result = +Sprite
        index = self._get_index_from_size(size)
        match direction:
            case FlickDirection.UP_OMNI:
                result @= self.up[index]
            case FlickDirection.DOWN_OMNI:
                result @= self.down[index]
            case FlickDirection.UP_LEFT | FlickDirection.UP_RIGHT:
                result @= self.up_left[index]
            case FlickDirection.DOWN_LEFT | FlickDirection.DOWN_RIGHT:
                result @= self.down_left[index]
            case _:
                assert_never(direction)
        return result

    @property
    def custom_available(self):
        return self.up_left[0].is_available


class TickSprites(Record):
    normal: Sprite
    fallback: Sprite

    @property
    def custom_available(self):
        return self.normal.is_available


class ActiveConnectorSprites(Record):
    normal: Sprite
    active: Sprite
    fallback: Sprite

    @property
    def custom_available(self):
        return self.normal.is_available


class GuideSprites(Record):
    normal: Sprite
    fallback: Sprite

    @property
    def custom_available(self):
        return self.normal.is_available


normal_note_body_sprites = BodySprites(
    left=Skin.normal_note_left,
    middle=Skin.normal_note_middle,
    right=Skin.normal_note_right,
    fallback=Skin.normal_note_fallback,
)
slide_note_body_sprites = BodySprites(
    left=Skin.slide_note_left,
    middle=Skin.slide_note_middle,
    right=Skin.slide_note_right,
    fallback=Skin.slide_note_fallback,
)
flick_note_body_sprites = BodySprites(
    left=Skin.flick_note_left,
    middle=Skin.flick_note_middle,
    right=Skin.flick_note_right,
    fallback=Skin.flick_note_fallback,
)
critical_note_body_sprites = BodySprites(
    left=Skin.critical_note_left,
    middle=Skin.critical_note_middle,
    right=Skin.critical_note_right,
    fallback=Skin.critical_note_fallback,
)

normal_trace_note_body_sprites = BodySprites(
    left=Skin.normal_trace_note_left,
    middle=Skin.normal_trace_note_middle,
    right=Skin.normal_trace_note_right,
    fallback=Skin.normal_trace_note_fallback,
)
critical_trace_note_body_sprites = BodySprites(
    left=Skin.critical_trace_note_left,
    middle=Skin.critical_trace_note_middle,
    right=Skin.critical_trace_note_right,
    fallback=Skin.critical_trace_note_fallback,
)
trace_flick_note_body_sprites = BodySprites(
    left=Skin.trace_flick_note_left,
    middle=Skin.trace_flick_note_middle,
    right=Skin.trace_flick_note_right,
    fallback=Skin.trace_flick_note_fallback,
)
trace_slide_note_body_sprites = normal_trace_note_body_sprites

damage_note_body_sprites = BodySprites(
    left=Skin.damage_note_left,
    middle=Skin.damage_note_middle,
    right=Skin.damage_note_right,
    fallback=Skin.damage_note_fallback,
)

normal_arrow_sprites = ArrowSprites(
    up=Array(
        Skin.flick_arrow_up1,
        Skin.flick_arrow_up2,
        Skin.flick_arrow_up3,
        Skin.flick_arrow_up4,
        Skin.flick_arrow_up5,
        Skin.flick_arrow_up6,
    ),
    up_left=Array(
        Skin.flick_arrow_up_left1,
        Skin.flick_arrow_up_left2,
        Skin.flick_arrow_up_left3,
        Skin.flick_arrow_up_left4,
        Skin.flick_arrow_up_left5,
        Skin.flick_arrow_up_left6,
    ),
    down=Array(
        Skin.flick_arrow_down1,
        Skin.flick_arrow_down2,
        Skin.flick_arrow_down3,
        Skin.flick_arrow_down4,
        Skin.flick_arrow_down5,
        Skin.flick_arrow_down6,
    ),
    down_left=Array(
        Skin.flick_arrow_down_left1,
        Skin.flick_arrow_down_left2,
        Skin.flick_arrow_down_left3,
        Skin.flick_arrow_down_left4,
        Skin.flick_arrow_down_left5,
        Skin.flick_arrow_down_left6,
    ),
    fallback=Skin.flick_arrow_fallback,
)
critical_arrow_sprites = ArrowSprites(
    up=Array(
        Skin.critical_arrow_up1,
        Skin.critical_arrow_up2,
        Skin.critical_arrow_up3,
        Skin.critical_arrow_up4,
        Skin.critical_arrow_up5,
        Skin.critical_arrow_up6,
    ),
    up_left=Array(
        Skin.critical_arrow_up_left1,
        Skin.critical_arrow_up_left2,
        Skin.critical_arrow_up_left3,
        Skin.critical_arrow_up_left4,
        Skin.critical_arrow_up_left5,
        Skin.critical_arrow_up_left6,
    ),
    down=Array(
        Skin.critical_arrow_down1,
        Skin.critical_arrow_down2,
        Skin.critical_arrow_down3,
        Skin.critical_arrow_down4,
        Skin.critical_arrow_down5,
        Skin.critical_arrow_down6,
    ),
    down_left=Array(
        Skin.critical_arrow_down_left1,
        Skin.critical_arrow_down_left2,
        Skin.critical_arrow_down_left3,
        Skin.critical_arrow_down_left4,
        Skin.critical_arrow_down_left5,
        Skin.critical_arrow_down_left6,
    ),
    fallback=Skin.critical_arrow_fallback,
)

normal_tick_sprites = TickSprites(
    normal=Skin.normal_slide_tick_note,
    fallback=Skin.normal_slide_tick_note_fallback,
)
slide_tick_sprites = normal_tick_sprites
critical_tick_sprites = TickSprites(
    normal=Skin.critical_slide_tick_note,
    fallback=Skin.critical_slide_tick_note_fallback,
)
normal_trace_tick_sprites = TickSprites(
    normal=Skin.normal_trace_tick_note,
    fallback=Skin.normal_trace_tick_note_fallback,
)
critical_trace_tick_sprites = TickSprites(
    normal=Skin.critical_trace_tick_note,
    fallback=Skin.critical_trace_tick_note_fallback,
)
trace_flick_tick_sprites = TickSprites(
    normal=Skin.trace_flick_tick_note,
    fallback=Skin.trace_flick_tick_note_fallback,
)

normal_slide_connector_sprites = ActiveConnectorSprites(
    normal=Skin.normal_slide_connector_normal,
    active=Skin.normal_slide_connector_active,
    fallback=Skin.normal_slide_connector_fallback,
)
critical_slide_connector_sprites = ActiveConnectorSprites(
    normal=Skin.critical_slide_connector_normal,
    active=Skin.critical_slide_connector_active,
    fallback=Skin.critical_slide_connector_fallback,
)

neutral_guide_sprites = GuideSprites(
    normal=Skin.guide_neutral,
    fallback=Skin.guide_neutral_fallback,
)
red_guide_sprites = GuideSprites(
    normal=Skin.guide_red,
    fallback=Skin.guide_red_fallback,
)
green_guide_sprites = GuideSprites(
    normal=Skin.guide_green,
    fallback=Skin.guide_green_fallback,
)
blue_guide_sprites = GuideSprites(
    normal=Skin.guide_blue,
    fallback=Skin.guide_blue_fallback,
)
yellow_guide_sprites = GuideSprites(
    normal=Skin.guide_yellow,
    fallback=Skin.guide_yellow_fallback,
)
purple_guide_sprites = GuideSprites(
    normal=Skin.guide_purple,
    fallback=Skin.guide_purple_fallback,
)
cyan_guide_sprites = GuideSprites(
    normal=Skin.guide_cyan,
    fallback=Skin.guide_cyan_fallback,
)
black_guide_sprites = GuideSprites(
    normal=Skin.guide_black,
    fallback=Skin.guide_black_fallback,
)
