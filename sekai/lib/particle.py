from sonolus.script.particle import StandardParticle, particles


@particles
class Particles:
    lane: StandardParticle.LANE_LINEAR

    normal_note_circular: StandardParticle.NOTE_CIRCULAR_TAP_CYAN
    normal_note_linear: StandardParticle.NOTE_LINEAR_TAP_CYAN

    slide_note_circular: StandardParticle.NOTE_CIRCULAR_TAP_GREEN
    slide_note_linear: StandardParticle.NOTE_LINEAR_TAP_GREEN

    flick_note_circular: StandardParticle.NOTE_CIRCULAR_TAP_RED
    flick_note_linear: StandardParticle.NOTE_LINEAR_TAP_RED
    flick_note_directional: StandardParticle.NOTE_LINEAR_ALTERNATIVE_RED

    critical_note_circular: StandardParticle.NOTE_CIRCULAR_TAP_YELLOW
    critical_note_linear: StandardParticle.NOTE_LINEAR_TAP_YELLOW
    critical_note_directional: StandardParticle.NOTE_LINEAR_ALTERNATIVE_YELLOW

    normal_slide_tick_note: StandardParticle.NOTE_CIRCULAR_ALTERNATIVE_GREEN

    critical_slide_tick_note: StandardParticle.NOTE_CIRCULAR_ALTERNATIVE_YELLOW

    normal_slide_connector_circular: StandardParticle.NOTE_CIRCULAR_HOLD_GREEN
    normal_slide_connector_linear: StandardParticle.NOTE_LINEAR_HOLD_GREEN

    critical_slide_connector_circular: StandardParticle.NOTE_CIRCULAR_HOLD_YELLOW
    critical_slide_connector_linear: StandardParticle.NOTE_LINEAR_HOLD_YELLOW

    damage_note_circular: StandardParticle.NOTE_CIRCULAR_TAP_PURPLE
    damage_note_linear: StandardParticle.NOTE_LINEAR_TAP_PURPLE
