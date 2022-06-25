import mido

__all__ = (
    "Note",
)


class Note:
    """
    Note with absolute start and end time in frames.
    Also supports linked-list like behavior within track.
    """
    note: int
    velocity: int
    start: float
    end: float

    def __init__(self, note, velocity, start, end, midi: "Midi", index: int):
        """
        :param midi: Midi object this note belongs to.
        :param index: Index of this note in the track. Allows for linked-list.
        """
        self.note = note
        self.velocity = velocity
        self.start = start
        self.end = end

        self.midi = midi
        self.index = index

    def __repr__(self):
        return (f"animpiano.Note(note={self.note}, velocity={self.velocity}, "
                f"start={self.start}, end={self.end})")

    def diff(self, other: "Note") -> float:
        """
        Calculate difference in frames between this note and another's start.
        Positive if this note starts after other.
        """
        return self.start - other.start

    @property
    def next(self) -> "Note":
        """
        Get next note in midi.
        """
        ind = self.index + 1
        if ind >= len(self.midi.notes):
            return None
        return self.midi.notes[ind]

    @property
    def prev(self) -> "Note":
        """
        Get previous note in midi.
        """
        ind = self.index - 1
        if ind < 0:
            return None
        return self.midi.notes[ind]


class Midi:
    """
    Parse a midi file, combining all tracks.
    """

    def __init__(self, path: str, fps: float, offset: float = None) -> None:
        """
        Parse a midi file.

        :param path: Path to midi file.
        :param fps: Frames per second.
        :param offset: Offset in frames to add to all notes.
        """
        self.notes = []

        starts = [0] * 1000
        vels = [0] * 1000
    
        frame = 0
        started = False
        for msg in midi:
            if started:
                frame += msg.time * fps
    
            if msg.type.startswith("note_"):
                started = True
                note = msg.note
                vel = msg.velocity if msg.type == "note_on" else 0
                if vel == 0:
                    n = Note(note, vels[note], starts[note]+offset, frame+offset, self, len(self.notes))
                    self.notes.append(n)
                else:
                    starts[note] = frame
                    vels[note] = vel

    @property
    def length(self) -> float:
        """
        Duration, in frames, between first note's start and last note's end.
        Does not regard offset.
        """
        return self.notes[-1].end - self.notes[0].start
    
    def notes_used(self) -> int:
        """
        Returns set of all notes used.
        """
        return set(n.note for n in self.notes)
