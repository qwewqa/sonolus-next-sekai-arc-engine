from math import pi

from sonolus.script.globals import level_data
from sonolus.script.interval import clamp, lerp, remap, unlerp
from sonolus.script.quad import Quad, QuadLike, Rect
from sonolus.script.runtime import aspect_ratio, is_tutorial, screen, time
from sonolus.script.transform import Transform2d
from sonolus.script.vec import Vec2

from sekai.lib.ease import EaseType, ease
from sekai.lib.options import Options

LANE_T = 47 / 850
LANE_B = 1176 / 850

LANE_HITBOX_L = -6
LANE_HITBOX_R = 6
LANE_HITBOX_T = (803 / 850) * 0.6
LANE_HITBOX_B = 1.5

NOTE_H = 75 / 850 / 2
NOTE_EDGE_W = 0.25
NOTE_SLIM_EDGE_W = 0.125

TARGET_ASPECT_RATIO = 16 / 9

# Value between 0 and 1 where smaller values mean a 'harsher' approach with more acceleration.
APPROACH_START = 1.06**-45

# Value above 1 where we cut off drawing sprites. Doesn't really matter as long as it's high enough,
# such that something like a flick arrow below the judge line isn't obviously suddenly cut off.
APPROACH_CUTOFF = 2

CONNECTOR_QUALITY_MULTIPLIER = 2


@level_data
class Layout:
    transform: Transform2d
    w_scale: float
    h_scale: float
    scaled_note_h: float


def init_layout():
    if Options.lock_stage_aspect_ratio:
        if aspect_ratio() > TARGET_ASPECT_RATIO:
            field_w = screen().h * TARGET_ASPECT_RATIO
            field_h = screen().h
        else:
            field_w = screen().w
            field_h = screen().w / TARGET_ASPECT_RATIO
    else:
        field_w = screen().w
        field_h = screen().h

    t = field_h * (0.5 + 1.15875 * (47 / 1176))
    b = field_h * (0.5 - 1.15875 * (803 / 1176))
    w = field_w * ((1.15875 * (1420 / 1176)) / TARGET_ASPECT_RATIO / 12)

    Layout.w_scale = w
    Layout.h_scale = b - t
    Layout.scaled_note_h = NOTE_H * Layout.h_scale
    Layout.transform = Transform2d.new().scale(Vec2(Layout.w_scale, Layout.h_scale)).translate(Vec2(0, t))


def approach(from_time: float, to_time: float, now: float) -> float:
    return APPROACH_START ** remap(from_time, to_time, 1, 0, now)


def approach_to(to_time: float, now: float) -> float:
    return approach(to_time - preempt_time(), to_time, now)


def preempt_time() -> float:
    return lerp(0.35, 4, unlerp(12, 1, Options.note_speed) ** 1.31)


def get_alpha(target_time: float, now: float | None = None) -> float:
    if is_tutorial():
        return 1.0
    if Options.hidden > 0:
        # Fade based on real time.
        # We don't want to use scaled time because it doesn't interact well with gimmicks like
        # negative timescale.
        if now is None:
            now = time()
        change_point = approach(0, 1, 1 - Options.hidden)
        progress = approach_to(target_time, now)
        return remap(change_point - 0.05, change_point + 0.05, 1, 0, progress)
    return 1.0


def transform_vec(v: Vec2) -> Vec2:
    return Layout.transform.transform_vec(v)


def transform_quad(q: QuadLike) -> Quad:
    return Layout.transform.transform_quad(q)


def vec_at(lane: float, progress: float) -> Vec2:
    return transform_vec(Vec2(lane * progress, progress))


def touch_x_to_lane(x: float) -> float:
    return x / Layout.w_scale


def perspective_vec(x: float, y: float, progress: float = 1.0) -> Vec2:
    return transform_vec(Vec2(x * y * progress, y * progress))


def perspective_rect(l: float, r: float, t: float, b: float, progress: float = 1.0) -> Quad:
    return transform_quad(
        Quad(
            bl=Vec2(l * b * progress, b * progress),
            br=Vec2(r * b * progress, b * progress),
            tl=Vec2(l * t * progress, t * progress),
            tr=Vec2(r * t * progress, t * progress),
        )
    )


def layout_sekai_stage() -> Quad:
    w = (2048 / 1420) * 12 / 2
    h = 1176 / 850
    rect = Rect(l=-w, r=w, t=LANE_T, b=LANE_T + h)
    return Layout.transform.transform_quad(rect)


def layout_lane_by_edges(l: float, r: float) -> Quad:
    return perspective_rect(l=l, r=r, t=LANE_T, b=LANE_B)


def layout_lane(lane: float, size: float) -> Quad:
    return layout_lane_by_edges(lane - size, lane + size)


def layout_stage_cover() -> Rect:
    return Rect(
        l=screen().l,
        r=screen().r,
        t=screen().t,
        b=lerp(transform_vec(Vec2(0, LANE_T)).y, screen().b, Options.stage_cover),
    )


def layout_background_dim() -> Rect:
    return screen()


def layout_fallback_judge_line() -> Quad:
    return perspective_rect(l=-6, r=6, t=1 - NOTE_H, b=1 + NOTE_H)


def layout_note_body_by_edges(l: float, r: float, h: float, progress: float):
    return perspective_rect(l=l, r=r, t=1 - h, b=1 + h, progress=progress)


def layout_note_body_slices_by_edges(
    l: float, r: float, h: float, edge_w: float, progress: float
) -> tuple[Quad, Quad, Quad]:
    m = (l + r) / 2
    if r < l:
        # Make the note 0 width; shouldn't normally happen, but in case, we want to handle it gracefully
        l = r = m
    ml = min(l + edge_w, m)
    mr = max(r - edge_w, m)
    return (
        layout_note_body_by_edges(l=l, r=ml, h=h, progress=progress),
        layout_note_body_by_edges(l=ml, r=mr, h=h, progress=progress),
        layout_note_body_by_edges(l=mr, r=r, h=h, progress=progress),
    )


def layout_regular_note_body(lane: float, size: float, progress: float) -> tuple[Quad, Quad, Quad]:
    return layout_note_body_slices_by_edges(
        l=lane - size + Options.note_margin,
        r=lane + size - Options.note_margin,
        h=NOTE_H,
        edge_w=NOTE_EDGE_W,
        progress=progress,
    )


def layout_regular_note_body_fallback(lane: float, size: float, progress: float) -> Quad:
    return layout_note_body_by_edges(
        l=lane - size + Options.note_margin,
        r=lane + size - Options.note_margin,
        h=NOTE_H,
        progress=progress,
    )


def layout_slim_note_body(lane: float, size: float, progress: float) -> tuple[Quad, Quad, Quad]:
    return layout_note_body_slices_by_edges(
        l=lane - size + Options.note_margin,
        r=lane + size - Options.note_margin,
        h=NOTE_H,  # Height is handled by the sprite rather than being changed here
        edge_w=NOTE_SLIM_EDGE_W,
        progress=progress,
    )


def layout_slim_note_body_fallback(lane: float, size: float, progress: float) -> Quad:
    return layout_note_body_by_edges(
        l=lane - size + Options.note_margin,
        r=lane + size - Options.note_margin,
        h=NOTE_H / 2,  # For fallback, we need to halve the height manually engine-side
        progress=progress,
    )


def layout_tick(lane: float, progress: float) -> Rect:
    center = transform_vec(Vec2(lane, 1) * progress)
    return Rect.from_center(center, Vec2(Layout.scaled_note_h, Layout.scaled_note_h) * -2 * progress)


def layout_flick_arrow(lane: float, size: float, direction: int, progress: float, animation_progress: float):
    w = clamp(size, 0, 3) * (1 if -direction >= 0 else -1) / 2
    base_bl = transform_vec(Vec2(lane - w, 1) * progress)
    base_br = transform_vec(Vec2(lane + w, 1) * progress)
    up = (base_br - base_bl).rotate(pi / 2 if -direction >= 0 else -pi / 2)
    base_tl = base_bl + up
    base_tr = base_br + up
    offset = Vec2(direction * Layout.w_scale, 2 * Layout.w_scale) * animation_progress * progress
    return Quad(
        bl=base_bl,
        br=base_br,
        tl=base_tl,
        tr=base_tr,
    ).translate(offset)


def layout_flick_arrow_fallback(lane: float, size: float, direction: int, progress: float, animation_progress: float):
    w = clamp(size / 2, 1, 2)
    offset = Vec2(direction * Layout.w_scale, 2 * Layout.w_scale) * animation_progress * progress
    return (
        Rect(l=-1, r=1, t=1, b=-1)
        .as_quad()
        .rotate(-pi / 6 * direction)
        .scale(Vec2(w, w) * Layout.w_scale * progress)
        .translate(transform_vec(Vec2(lane, 1) * progress))
        .translate(offset)
    )


def layout_slot_effect(lane: float):
    return perspective_rect(
        l=lane - 0.5,
        r=lane + 0.5,
        b=1 + NOTE_H,
        t=1 - NOTE_H,
    )


def layout_slot_glow_effect(lane: float, size: float, animation_progress: float):
    s = 1 + 0.25 * Options.slot_effect_size
    h = 4 * Layout.w_scale * Options.slot_effect_size
    l_min = transform_vec(Vec2(lane - size * s, 1))
    r_min = transform_vec(Vec2(lane + size * s, 1))
    l_max = (l_min + Vec2(0, h)) * Vec2(s, 1)
    r_max = (r_min + Vec2(0, h)) * Vec2(s, 1)
    return Quad(
        bl=l_min,
        br=r_min,
        tl=lerp(l_min, l_max, animation_progress),
        tr=lerp(r_min, r_max, animation_progress),
    )


def layout_linear_effect(lane: float, shear: float):
    w = Options.note_effect_size
    bl = transform_vec(Vec2(lane - w, 1))
    br = transform_vec(Vec2(lane + w, 1))
    up = (br - bl).rotate(pi / 2) + (shear + 0.125 * lane) * (br - bl) / 2
    return Quad(
        bl=bl,
        br=br,
        tl=bl + up,
        tr=br + up,
    )


def layout_circular_effect(lane: float, w: float, h: float):
    w *= Options.note_effect_size
    h *= Options.note_effect_size * Layout.w_scale / Layout.h_scale
    b = 1 + h
    t = 1 - h
    return transform_quad(
        Quad(
            bl=Vec2(lane * b - w, b),
            br=Vec2(lane * b + w, b),
            tl=Vec2(lane * t - w, t),
            tr=Vec2(lane * t + w, t),
        )
    )


def layout_slide_connector_segment(
    start_lane: float,
    start_size: float,
    start_progress: float,
    end_lane: float,
    end_size: float,
    end_progress: float,
) -> Quad:
    if start_progress < end_progress:
        start_lane, end_lane = end_lane, start_lane
        start_size, end_size = end_size, start_size
        start_progress, end_progress = end_progress, start_progress
    return transform_quad(
        Quad(
            bl=vec_at(start_lane - start_size, start_progress),
            br=vec_at(start_lane + start_size, start_progress),
            tl=vec_at(end_lane - end_size, end_progress),
            tr=vec_at(end_lane + end_size, end_progress),
        )
    )


def slide_interpolate(
    start_lane: float,
    start_size: float,
    start_progress: float,
    end_lane: float,
    end_size: float,
    end_progress: float,
    ease_type: EaseType,
    progress: float,
) -> tuple[float, float, float]:
    eased = ease(ease_type, unlerp(start_progress, end_progress, progress))
    return lerp(start_lane, end_lane, eased), lerp(start_size, end_size, eased), progress


def layout_sim_line(
    l_lane: float,
    l_progress: float,
    r_lane: float,
    r_progress: float,
) -> Quad:
    if l_lane > r_lane:
        l_lane, r_lane = r_lane, l_lane
        l_progress, r_progress = r_progress, l_progress
    if l_progress < APPROACH_START:
        l_lane = remap(l_progress, r_progress, l_lane, r_lane, APPROACH_START)
        l_progress = APPROACH_START
    elif l_progress > APPROACH_CUTOFF:
        l_lane = remap(l_progress, r_progress, l_lane, r_lane, APPROACH_CUTOFF)
        l_progress = APPROACH_CUTOFF
    if r_progress < APPROACH_START:
        r_lane = remap(r_progress, l_progress, r_lane, l_lane, APPROACH_START)
        r_progress = APPROACH_START
    elif r_progress > APPROACH_CUTOFF:
        r_lane = remap(r_progress, l_progress, r_lane, l_lane, APPROACH_CUTOFF)
        r_progress = APPROACH_CUTOFF
    return Quad(
        bl=perspective_vec(l_lane, l_progress - NOTE_H, l_progress),
        br=perspective_vec(r_lane, r_progress - NOTE_H, r_progress),
        tl=perspective_vec(l_lane, l_progress + NOTE_H, l_progress),
        tr=perspective_vec(r_lane, r_progress + NOTE_H, r_progress),
    )


def layout_hitbox(
    lane: float,
    size: float,
    leniency: float,
) -> Quad:
    return layout_lane(lane, size + leniency)
