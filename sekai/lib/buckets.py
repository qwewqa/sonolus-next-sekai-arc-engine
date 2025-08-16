from sonolus.script.bucket import Bucket, JudgmentWindow, bucket, bucket_sprite, buckets
from sonolus.script.interval import Interval
from sonolus.script.sprite import Sprite
from sonolus.script.text import StandardText

from sekai.lib.skin import Skin

WINDOW_SCALE = 1000  # Windows are in ms


def create_bucket_sprites(
    body: Sprite | None = None,
    body_fallback: Sprite | None = None,
    arrow: Sprite | None = None,
    tick: Sprite | None = None,
    connector_left: Sprite | None = None,
    connector_mid: Sprite | None = None,
    connector_right: Sprite | None = None,
    body_x: float = 0,
):
    sprites = []

    if connector_left is not None:
        sprites.append(
            bucket_sprite(
                sprite=connector_left,
                x=0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            )
        )

    if connector_mid is not None:
        sprites.append(
            bucket_sprite(
                sprite=connector_mid,
                x=0,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            )
        )

    if connector_right is not None:
        sprites.append(
            bucket_sprite(
                sprite=connector_right,
                x=-0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            )
        )

    if body is not None:
        sprite_args = {
            "sprite": body,
            "x": body_x,
            "y": 0,
            "w": 2,
            "h": 2,
            "rotation": -90,
        }
        if body_fallback is not None:
            sprite_args["fallback_sprite"] = body_fallback
        sprites.append(bucket_sprite(**sprite_args))

    if arrow is not None:
        sprites.append(
            bucket_sprite(
                sprite=arrow,
                x=body_x + 1,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            )
        )

    if tick is not None:
        sprites.append(
            bucket_sprite(
                sprite=tick,
                x=body_x,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            )
        )

    return sprites


# Desired buckets
# - normal_tap
# - normal_flick
# - normal_trace
# - normal_trace_flick
# - [skip] normal_release
# - normal_head_tap
# - normal_head_flick
# - normal_head_trace
# - normal_head_trace_flick
# - [skip] normal_head_release
# - [skip] normal_tail_tap
# - normal_tail_flick
# - normal_tail_trace
# - normal_tail_trace_flick
# - normal_tail_release
# Critical versions of each directly under the normal versions (alternate)


@buckets
class Buckets:
    # Normal buckets
    normal_tap: Bucket = bucket(
        sprites=create_bucket_sprites(body=Skin.normal_note_fallback),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_tap: Bucket = bucket(
        sprites=create_bucket_sprites(body=Skin.critical_note_fallback),
        unit=StandardText.MILLISECOND_UNIT,
    )

    normal_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            body=Skin.flick_note_fallback,
            arrow=Skin.flick_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            body=Skin.critical_note_fallback,
            arrow=Skin.critical_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    normal_trace: Bucket = bucket(
        sprites=create_bucket_sprites(
            body=Skin.normal_trace_note_left,
            body_fallback=Skin.normal_trace_note_secondary_fallback,
            tick=Skin.normal_slide_tick_note,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_trace: Bucket = bucket(
        sprites=create_bucket_sprites(
            body=Skin.critical_trace_note_left,
            body_fallback=Skin.critical_trace_note_fallback,
            tick=Skin.critical_slide_tick_note,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    normal_trace_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            body=Skin.trace_flick_note_left,
            body_fallback=Skin.trace_flick_tick_note_fallback,
            tick=Skin.trace_flick_tick_note,
            arrow=Skin.flick_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_trace_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            body=Skin.critical_trace_note_left,
            body_fallback=Skin.critical_trace_note_fallback,
            tick=Skin.critical_slide_tick_note,
            arrow=Skin.critical_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    # Head buckets
    normal_head_tap: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_left=Skin.normal_slide_connector_active,
            body=Skin.slide_note_fallback,
            body_x=-2,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_head_tap: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_left=Skin.critical_slide_connector_active,
            body=Skin.critical_note_fallback,
            body_x=-2,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    normal_head_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_left=Skin.normal_slide_connector_active,
            body=Skin.flick_note_fallback,
            body_x=-2,
            arrow=Skin.flick_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_head_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_left=Skin.critical_slide_connector_active,
            body=Skin.critical_note_fallback,
            body_x=-2,
            arrow=Skin.critical_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    normal_head_trace: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_mid=Skin.normal_slide_connector_active,
            body=Skin.normal_trace_note_left,
            body_fallback=Skin.normal_trace_note_secondary_fallback,
            tick=Skin.normal_slide_tick_note,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_head_trace: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_mid=Skin.critical_slide_connector_active,
            body=Skin.critical_trace_note_left,
            body_fallback=Skin.critical_trace_note_fallback,
            tick=Skin.critical_slide_tick_note,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    normal_head_trace_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_mid=Skin.normal_slide_connector_active,
            body=Skin.trace_flick_note_left,
            body_fallback=Skin.trace_flick_tick_note_fallback,
            tick=Skin.trace_flick_tick_note,
            arrow=Skin.flick_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_head_trace_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_mid=Skin.critical_slide_connector_active,
            body=Skin.critical_trace_note_left,
            body_fallback=Skin.critical_trace_note_fallback,
            tick=Skin.critical_slide_tick_note,
            arrow=Skin.critical_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    # Tail buckets
    normal_tail_release: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_right=Skin.normal_slide_connector_active,
            body=Skin.slide_note_end_fallback,
            body_x=2,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_tail_release: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_right=Skin.critical_slide_connector_active,
            body=Skin.critical_note_end_fallback,
            body_x=2,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    normal_tail_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_right=Skin.normal_slide_connector_active,
            body=Skin.flick_note_fallback,
            body_x=2,
            arrow=Skin.flick_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_tail_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_right=Skin.critical_slide_connector_active,
            body=Skin.critical_note_end_fallback,
            body_x=2,
            arrow=Skin.critical_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    normal_tail_trace: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_right=Skin.normal_slide_connector_active,
            body=Skin.normal_trace_note_left,
            body_fallback=Skin.normal_trace_note_secondary_fallback,
            body_x=2,
            tick=Skin.normal_slide_tick_note,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_tail_trace: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_right=Skin.critical_slide_connector_active,
            body=Skin.critical_trace_note_left,
            body_fallback=Skin.critical_trace_note_fallback,
            body_x=2,
            tick=Skin.critical_slide_tick_note,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )

    normal_tail_trace_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_right=Skin.normal_slide_connector_active,
            body=Skin.trace_flick_note_left,
            body_fallback=Skin.trace_flick_tick_note_fallback,
            body_x=2,
            tick=Skin.trace_flick_tick_note,
            arrow=Skin.flick_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_tail_trace_flick: Bucket = bucket(
        sprites=create_bucket_sprites(
            connector_right=Skin.critical_slide_connector_active,
            body=Skin.critical_trace_note_left,
            body_fallback=Skin.critical_trace_note_fallback,
            body_x=2,
            tick=Skin.critical_slide_tick_note,
            arrow=Skin.critical_arrow_fallback,
        ),
        unit=StandardText.MILLISECOND_UNIT,
    )


def init_buckets():
    Buckets.normal_tap @= TAP_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_tap @= TAP_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_flick @= FLICK_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_flick @= FLICK_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_trace @= TRACE_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_trace @= TRACE_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_trace_flick @= TRACE_FLICK_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_trace_flick @= TRACE_FLICK_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_head_tap @= TAP_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_head_tap @= TAP_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_head_flick @= FLICK_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_head_flick @= FLICK_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_head_trace @= TRACE_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_head_trace @= TRACE_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_head_trace_flick @= TRACE_FLICK_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_head_trace_flick @= TRACE_FLICK_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_tail_flick @= SLIDE_END_FLICK_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_tail_flick @= SLIDE_END_FLICK_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_tail_trace @= SLIDE_END_TRACE_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_tail_trace @= SLIDE_END_TRACE_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_tail_trace_flick @= SLIDE_END_TRACE_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_tail_trace_flick @= SLIDE_END_TRACE_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_tail_release @= SLIDE_END_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_tail_release @= SLIDE_END_CRITICAL_WINDOW * WINDOW_SCALE


def frames_to_window(
    perfect: float | tuple[float, float],
    great: float | tuple[float, float],
    good: float | tuple[float, float],
) -> JudgmentWindow:
    perfect = perfect if isinstance(perfect, tuple) else (perfect, perfect)
    great = great if isinstance(great, tuple) else (great, great)
    good = good if isinstance(good, tuple) else (good, good)
    return JudgmentWindow(
        perfect=Interval(-perfect[0] / 60, perfect[1] / 60),
        great=Interval(-great[0] / 60, great[1] / 60),
        good=Interval(-good[0] / 60, good[1] / 60),
    )


TAP_NORMAL_WINDOW = frames_to_window(2.5, 5, 7.5)
TAP_CRITICAL_WINDOW = frames_to_window(3.3, 4.5, 7.5)

FLICK_NORMAL_WINDOW = frames_to_window(2.5, (6.5, 7.5), (7.5, 8.5))
FLICK_CRITICAL_WINDOW = frames_to_window(3.5, (6.5, 7.5), (7.5, 8.5))

TRACE_NORMAL_WINDOW = frames_to_window(3.5, 3.5, 3.5)
TRACE_CRITICAL_WINDOW = frames_to_window(3.5, 3.5, 3.5)

TRACE_FLICK_NORMAL_WINDOW = frames_to_window((6.5, 7.5), (6.5, 7.5), (6.5, 7.5))
TRACE_FLICK_CRITICAL_WINDOW = frames_to_window((6.5, 7.5), (6.5, 7.5), (6.5, 7.5))

SLIDE_END_NORMAL_WINDOW = frames_to_window((3.5, 4), (3.5, 8), (3.5, 8.5))
SLIDE_END_CRITICAL_WINDOW = frames_to_window((3.5, 4), (3.5, 8), (3.5, 8.5))

SLIDE_END_TRACE_NORMAL_WINDOW = frames_to_window((6, 8.5), (6, 8.5), (6, 8.5))
SLIDE_END_TRACE_CRITICAL_WINDOW = frames_to_window((6, 8.5), (6, 8.5), (6, 8.5))

SLIDE_END_FLICK_NORMAL_WINDOW = frames_to_window((3.5, 4), (3.5, 8), (3.5, 8.5))
SLIDE_END_FLICK_CRITICAL_WINDOW = frames_to_window((3.5, 4), (3.5, 8), (3.5, 8.5))

SLIDE_END_LOCKOUT_DURATION = 0.25
