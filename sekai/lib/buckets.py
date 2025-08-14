from sonolus.script.bucket import Bucket, JudgmentWindow, bucket, bucket_sprite, buckets
from sonolus.script.interval import Interval
from sonolus.script.text import StandardText

from sekai.lib.skin import Skin

WINDOW_SCALE = 1000  # Windows are in ms


@buckets
class Buckets:
    normal_tap_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.normal_note_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            )
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    normal_flick_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.flick_note_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.flick_arrow_fallback,
                x=1,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    normal_slide_start_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.normal_slide_connector_active,
                x=0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.slide_note_fallback,
                x=-2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    normal_slide_end_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.normal_slide_connector_active,
                x=-0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.slide_note_end_fallback,
                x=2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    normal_slide_end_flick_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.normal_slide_connector_active,
                x=-0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.flick_note_fallback,
                x=2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.flick_arrow_fallback,
                x=3,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_tap_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.critical_note_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            )
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_flick_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.critical_note_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_arrow_fallback,
                x=1,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_slide_start_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.critical_slide_connector_active,
                x=0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_note_fallback,
                x=-2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )

    critical_slide_end_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.critical_slide_connector_active,
                x=-0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_note_end_fallback,
                x=2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_slide_end_flick_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.critical_slide_connector_active,
                x=-0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_note_end_fallback,
                x=2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_arrow_fallback,
                x=3,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    normal_trace_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.normal_trace_note_left,
                fallback_sprite=Skin.normal_trace_note_secondary_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.normal_slide_tick_note,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_trace_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.critical_trace_note_left,
                fallback_sprite=Skin.critical_trace_note_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_slide_tick_note,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    normal_trace_flick_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.trace_flick_note_left,
                fallback_sprite=Skin.trace_flick_tick_note_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.trace_flick_tick_note,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.flick_arrow_fallback,
                x=1,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_trace_flick_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.critical_trace_note_left,
                fallback_sprite=Skin.critical_trace_note_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_slide_tick_note,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_arrow_fallback,
                x=1,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    normal_slide_trace_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.normal_slide_connector_active,
                x=0,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.normal_trace_note_left,
                fallback_sprite=Skin.normal_trace_note_secondary_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.normal_slide_tick_note,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_slide_trace_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.critical_slide_connector_active,
                x=0,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_trace_note_left,
                fallback_sprite=Skin.critical_trace_note_fallback,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_slide_tick_note,
                x=0,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    normal_slide_end_trace_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.normal_slide_connector_active,
                x=-0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.normal_trace_note_left,
                fallback_sprite=Skin.normal_trace_note_secondary_fallback,
                x=2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.normal_slide_tick_note,
                x=2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )
    critical_slide_end_trace_note: Bucket = bucket(
        sprites=[
            bucket_sprite(
                sprite=Skin.critical_slide_connector_active,
                x=-0.5,
                y=0,
                w=2,
                h=5,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_trace_note_left,
                fallback_sprite=Skin.critical_trace_note_fallback,
                x=2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
            bucket_sprite(
                sprite=Skin.critical_slide_tick_note,
                x=2,
                y=0,
                w=2,
                h=2,
                rotation=-90,
            ),
        ],
        unit=StandardText.MILLISECOND_UNIT,
    )


def init_buckets():
    Buckets.normal_tap_note @= TAP_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.normal_flick_note @= FLICK_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.normal_slide_start_note @= SLIDE_START_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.normal_slide_end_note @= SLIDE_END_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.normal_slide_end_flick_note @= SLIDE_END_FLICK_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_tap_note @= TAP_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.critical_flick_note @= FLICK_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.critical_slide_start_note @= SLIDE_START_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.critical_slide_end_note @= SLIDE_END_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.critical_slide_end_flick_note @= SLIDE_END_FLICK_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_trace_note @= TRACE_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_trace_note @= TRACE_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_trace_flick_note @= TRACE_FLICK_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_trace_flick_note @= TRACE_FLICK_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_slide_trace_note @= TRACE_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_slide_trace_note @= TRACE_CRITICAL_WINDOW * WINDOW_SCALE
    Buckets.normal_slide_end_trace_note @= TRACE_FLICK_NORMAL_WINDOW * WINDOW_SCALE
    Buckets.critical_slide_end_trace_note @= TRACE_FLICK_CRITICAL_WINDOW * WINDOW_SCALE


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
SLIDE_START_NORMAL_WINDOW = frames_to_window(2.5, 5, 7.5)
SLIDE_START_CRITICAL_WINDOW = frames_to_window(3.3, 4.5, 7.5)
SLIDE_END_NORMAL_WINDOW = frames_to_window((3.5, 4), (3.5, 8), (3.5, 8.5))
SLIDE_END_CRITICAL_WINDOW = frames_to_window((3.5, 4), (3.5, 8), (3.5, 8.5))
SLIDE_END_TRACE_NORMAL_WINDOW = frames_to_window((6, 8.5), (6, 8.5), (6, 8.5))
SLIDE_END_TRACE_CRITICAL_WINDOW = frames_to_window((6, 8.5), (6, 8.5), (6, 8.5))
SLIDE_END_FLICK_NORMAL_WINDOW = frames_to_window((3.5, 4), (3.5, 8), (3.5, 8.5))
SLIDE_END_FLICK_CRITICAL_WINDOW = frames_to_window((3.5, 4), (3.5, 8), (3.5, 8.5))

SLIDE_END_LOCKOUT_DURATION = 0.25
