from math import ceil
from typing import assert_never

from sonolus.script.archetype import EntityRef, PreviewArchetype, callback, entity_data, imported
from sonolus.script.interval import clamp, lerp, remap_clamped
from sonolus.script.sprite import Sprite

from sekai.lib import archetype_names
from sekai.lib.connector import (
    ConnectorKind,
    apply_guide_alpha_curve,
    get_active_connector_sprites,
    get_connector_alpha_option,
    get_connector_quality_option,
    get_connector_z,
    get_guide_connector_sprites,
    map_connector_kind,
)
from sekai.lib.ease import EaseType, ease
from sekai.lib.layout import get_alpha
from sekai.lib.options import Options, SlideMod
from sekai.preview import note
from sekai.preview.layout import (
    PREVIEW_COLUMN_SECS,
    layout_preview_slide_connector_segment,
    time_to_preview_col,
    time_to_preview_y,
)


class PreviewConnector(PreviewArchetype):
    name = archetype_names.CONNECTOR

    head_ref: EntityRef[note.PreviewBaseNote] = imported(name="head")
    tail_ref: EntityRef[note.PreviewBaseNote] = imported(name="tail")
    segment_head_ref: EntityRef[note.PreviewBaseNote] = imported(name="segmentHead")
    segment_tail_ref: EntityRef[note.PreviewBaseNote] = imported(name="segmentTail")

    kind: ConnectorKind = entity_data()
    ease_type: EaseType = entity_data()

    @callback(order=-1)
    def preprocess(self):
        head = self.head
        tail = self.tail
        head.init_data()
        tail.init_data()
        self.kind = map_connector_kind(self.segment_head.segment_kind)
        covered_note_ref = head.ref()
        while covered_note_ref.index != self.tail_ref.index:
            covered_note: note.PreviewBaseNote = covered_note_ref.get()
            covered_note.segment_kind = self.kind
            covered_note_ref @= covered_note.next_ref
        self.ease_type = head.connector_ease

    def render(self):
        draw_connector(
            kind=self.kind,
            ease_type=self.ease_type,
            head_lane=self.head.lane,
            head_size=self.head.size,
            head_target_time=self.head.target_time,
            tail_lane=self.tail.lane,
            tail_size=self.tail.size,
            tail_target_time=self.tail.target_time,
            segment_head_target_time=self.segment_head.target_time,
            segment_head_lane=self.segment_head.lane,
            segment_head_alpha=self.segment_head.segment_alpha,
            segment_tail_target_time=self.segment_tail.target_time,
            segment_tail_alpha=self.segment_tail.segment_alpha,
        )

    @property
    def head(self) -> note.PreviewBaseNote:
        return self.head_ref.get()

    @property
    def tail(self) -> note.PreviewBaseNote:
        return self.tail_ref.get()

    @property
    def segment_head(self) -> note.PreviewBaseNote:
        return self.segment_head_ref.get()

    @property
    def segment_tail(self) -> note.PreviewBaseNote:
        return self.segment_tail_ref.get()


def draw_connector(
    kind: ConnectorKind,
    ease_type: EaseType,
    head_lane: float,
    head_size: float,
    head_target_time: float,
    tail_lane: float,
    tail_size: float,
    tail_target_time: float,
    segment_head_target_time: float,
    segment_head_lane: float,
    segment_head_alpha: float,
    segment_tail_target_time: float,
    segment_tail_alpha: float,
):
    if head_target_time == tail_target_time:
        return

    match Options.slide_mod:
        case SlideMod.NONE:
            pass
        case SlideMod.MONORAIL:
            match kind:
                case (
                    ConnectorKind.ACTIVE_NORMAL
                    | ConnectorKind.ACTIVE_CRITICAL
                    | ConnectorKind.ACTIVE_FAKE_NORMAL
                    | ConnectorKind.ACTIVE_FAKE_CRITICAL
                ):
                    head_size = 0.4
                    tail_size = 0.4
                case _:
                    pass
        case _:
            assert_never(Options.slide_mod)

    normal_sprite = Sprite(-1)
    match kind:
        case (
            ConnectorKind.ACTIVE_NORMAL
            | ConnectorKind.ACTIVE_CRITICAL
            | ConnectorKind.ACTIVE_FAKE_NORMAL
            | ConnectorKind.ACTIVE_FAKE_CRITICAL
        ):
            sprites = get_active_connector_sprites(kind)
            if sprites.custom_available:
                normal_sprite @= sprites.normal
            else:
                normal_sprite @= sprites.fallback
        case (
            ConnectorKind.GUIDE_NEUTRAL
            | ConnectorKind.GUIDE_RED
            | ConnectorKind.GUIDE_GREEN
            | ConnectorKind.GUIDE_BLUE
            | ConnectorKind.GUIDE_YELLOW
            | ConnectorKind.GUIDE_PURPLE
            | ConnectorKind.GUIDE_CYAN
            | ConnectorKind.GUIDE_BLACK
        ):
            sprites = get_guide_connector_sprites(kind)
            if sprites.custom_available:
                normal_sprite @= sprites.normal
            else:
                normal_sprite @= sprites.fallback
        case ConnectorKind.NONE:
            return
        case _:
            assert_never(kind)

    match kind:
        case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_CRITICAL:
            segment_head_alpha = 1.0
            segment_tail_alpha = 1.0
        case ConnectorKind.ACTIVE_FAKE_NORMAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
            segment_head_alpha = 1.0
            segment_tail_alpha = 1.0
        case (
            ConnectorKind.GUIDE_NEUTRAL
            | ConnectorKind.GUIDE_RED
            | ConnectorKind.GUIDE_GREEN
            | ConnectorKind.GUIDE_BLUE
            | ConnectorKind.GUIDE_YELLOW
            | ConnectorKind.GUIDE_PURPLE
            | ConnectorKind.GUIDE_CYAN
            | ConnectorKind.GUIDE_BLACK
        ):
            pass
        case _:
            assert_never(kind)

    head_alpha = remap_clamped(
        segment_head_target_time, segment_tail_target_time, segment_head_alpha, segment_tail_alpha, head_target_time
    )
    tail_alpha = remap_clamped(
        segment_head_target_time, segment_tail_target_time, segment_head_alpha, segment_tail_alpha, tail_target_time
    )

    match ease_type:
        case EaseType.NONE | EaseType.LINEAR if head_alpha == tail_alpha:
            quality_dist_scale = 0
        case _:
            quality_dist_scale = 100 / PREVIEW_COLUMN_SECS * (tail_target_time - head_target_time)
    quality_alpha_scale = 30 * abs(head_alpha - tail_alpha)
    segment_count = max(1, ceil(get_connector_quality_option(kind) * max(quality_dist_scale, quality_alpha_scale)))

    z = get_connector_z(kind, segment_head_target_time, segment_head_lane)

    last_lane = head_lane
    last_size = head_size
    last_alpha = head_alpha
    last_target_time = head_target_time
    last_col = time_to_preview_col(head_target_time)

    for i in range(1, segment_count + 1):
        next_frac = i / segment_count
        next_lane = lerp(head_lane, tail_lane, ease(ease_type, next_frac))
        next_size = max(1e-3, lerp(head_size, tail_size, ease(ease_type, next_frac)))
        next_alpha = lerp(head_alpha, tail_alpha, next_frac)
        next_target_time = lerp(head_target_time, tail_target_time, next_frac)
        next_col = time_to_preview_col(next_target_time)

        a = clamp(
            get_alpha((last_target_time + next_target_time) / 2)
            * apply_guide_alpha_curve((last_alpha + next_alpha) / 2)
            * get_connector_alpha_option(kind),
            0,
            1,
        )

        for col in range(last_col, next_col + 1):
            start_y = time_to_preview_y(last_target_time, col)
            end_y = time_to_preview_y(next_target_time, col)
            for layout in layout_preview_slide_connector_segment(
                start_lane=last_lane,
                start_size=last_size,
                start_y=start_y,
                end_lane=next_lane,
                end_size=next_size,
                end_y=end_y,
                col=col,
            ):
                normal_sprite.draw(layout, z=z, a=a)

        last_lane = next_lane
        last_size = next_size
        last_alpha = next_alpha
        last_target_time = next_target_time
        last_col = next_col
