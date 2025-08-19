from sonolus.script.particle import Particle, StandardParticle, particles
from sonolus.script.record import Record

EMPTY_PARTICLE = Particle(-1)


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


class NoteParticleSet(Record):
    circular: Particle
    linear: Particle
    directional: Particle
    tick: Particle
    lane: Particle


normal_note_particles = NoteParticleSet(
    circular=Particles.normal_note_circular,
    linear=Particles.normal_note_linear,
    directional=EMPTY_PARTICLE,
    tick=EMPTY_PARTICLE,
    lane=Particles.lane,
)
slide_note_particles = NoteParticleSet(
    circular=Particles.slide_note_circular,
    linear=Particles.slide_note_linear,
    directional=EMPTY_PARTICLE,
    tick=EMPTY_PARTICLE,
    lane=Particles.lane,
)
flick_note_particles = NoteParticleSet(
    circular=Particles.flick_note_circular,
    linear=Particles.flick_note_linear,
    directional=Particles.flick_note_directional,
    tick=EMPTY_PARTICLE,
    lane=Particles.lane,
)
critical_note_particles = NoteParticleSet(
    circular=Particles.critical_note_circular,
    linear=Particles.critical_note_linear,
    directional=EMPTY_PARTICLE,
    tick=EMPTY_PARTICLE,
    lane=Particles.lane,
)
critical_flick_note_particles = NoteParticleSet(
    circular=Particles.critical_note_circular,
    linear=Particles.critical_note_linear,
    directional=Particles.critical_note_directional,
    tick=EMPTY_PARTICLE,
    lane=Particles.lane,
)
damage_note_particles = NoteParticleSet(
    circular=Particles.damage_note_circular,
    linear=Particles.damage_note_linear,
    directional=EMPTY_PARTICLE,
    tick=EMPTY_PARTICLE,
    lane=Particles.lane,
)
normal_tick_particles = NoteParticleSet(
    circular=EMPTY_PARTICLE,
    linear=EMPTY_PARTICLE,
    directional=EMPTY_PARTICLE,
    tick=Particles.normal_slide_tick_note,
    lane=EMPTY_PARTICLE,
)
critical_tick_particles = NoteParticleSet(
    circular=EMPTY_PARTICLE,
    linear=EMPTY_PARTICLE,
    directional=EMPTY_PARTICLE,
    tick=Particles.critical_slide_tick_note,
    lane=EMPTY_PARTICLE,
)
empty_note_particles = NoteParticleSet(
    circular=EMPTY_PARTICLE,
    linear=EMPTY_PARTICLE,
    directional=EMPTY_PARTICLE,
    tick=EMPTY_PARTICLE,
    lane=EMPTY_PARTICLE,
)
