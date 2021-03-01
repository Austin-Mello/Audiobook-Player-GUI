################################################################################
# SoundObject.py
# Written by Anthony Hornof - 10-10-2020
# See https://www.pygame.org/docs/
################################################################################

'''

Creates a sound object for use with PagePointerAV.py, by A.Hornof 2020

This section discusses whether to use
pygame.mixer.music.play( ) or
pygame.mixer.Sound.play( )

The program uses pygame.mixer.MUSIC.play( ) because

pygame.mixer.music.play( ) can set the start but not the end.
pygame.mixer.Sound.play( ) can set the end but not the start.
    and because...
If you want to avoid chopping up long sound files into one sound per file,
and instead move through a single soundfile using an index of time-locations,
it seems more important to be able to control the start, rather than the end,
of the sound playback, because there is an obvious alternative for *stopping*
playback (using the event loop), but not an obvious alternative for jumping
into the middle of a sound object.

pygame.mixer.MUSIC.play( ) *might* introduce delays....

pygame.mixer.music.play( ) streams everything from disk, so you cannot load
  different soundfiles and have them all sitting ready to play. It kind of
  requires you to either (a) put everything on the one same tape or (b) rely
  on very fast loads from disk. Regarding (b), you can verify disk loads are
  fast enough by issuing a direct play(), and confirming a fast response.
pygame.mixer.Sound.play( ) permits you to create different objects and have
  them all load in the memory allocated to pygame, and ready to play. But
  you cannot set the start time of playback.

Note that with pygame.mixer.MUSIC, there is no pointer to the soundfile that
  is loaded, because there is always exactly zero or one soundfile loaded.
  You don't need differentiate from among MULTIPLE sound objects.
This also means that you do not need to stop one sound before playing another,
  because pygame.mixer.music itself takes care of this.
'''

################################################################################

import os
import pygame # Currently using 1.9.6

# GLOBAL variables
# Duration of the current sound playing. -1 if no current sound.
TARGET_DURATION = -1

################################################################################
# stop_when_done( ) class function (as opposed to a member function).
# If the sound has been playing for the current sound DURATION, stop playing it.

def stop_when_done():

    global TARGET_DURATION  # Get access to the class variable.

    # If there is a current sound playing...
    if ( TARGET_DURATION != -1 ):
        # If the time spent playing exceeds the target play-time...
            if ( pygame.mixer.music.get_pos() > TARGET_DURATION ):
                # Stop the sound.
                pygame.mixer.music.stop()
                # Indicate that no sound is playing.
                TARGET_DURATION = -1


################################################################################
# SoundObject class.
# Define a class of SoundSegment objects, each of which is prepared to:
#   (a) load a soundfile from disk;
#   (b) start playing it from a specific location; and
#   (c) set a duration after which it should stop playing.
#
# has a pointer to a
#   pygame.mixer.music object, a start time, and a duration. The times are in ms.
# A "segment" is a section of an audio file.
################################################################################

class SoundObject:
    def __init__(self, data_dir_in, filename_in, start_in, duration_in):
        # Pseudo-private member variables.
        # Save all these settings for later playback.
        self._data_dir = data_dir_in
        self._filename = filename_in
        self._start_time = start_in
        self._duration = duration_in


    # Play a sound based on the member variables.
    def play(self):

        global TARGET_DURATION # Get access to the class variable.

        # Load the soundfile from disk. For better or worse, this must be done
        #   every time a sound is played. See long comment at the top of the file.

        # Set up path to subdirectory (from Pete Shinners)
        main_dir = os.path.split(os.path.abspath(__file__))[0]
        data_dir = os.path.join(main_dir, self._data_dir)

        # Join the path and filename, cross-platform.
        filename = os.path.join(data_dir, self._filename)

        # Create the pygame.mixer.Sound object.
        # Try to load the sound file. Exit gracefully if it fails.
        try:
            pygame.mixer.music.load(filename)

        except pygame.error:
            print("Cannot load sound file:", filename)
            raise SystemExit(str(pygame.get_error()))

        # Play the sound from the specified start time. Convert from ms to s.
        pygame.mixer.music.play(0, self._start_time/1000)

        # Save the duration in the global variable, for use by stop_when_done( )
        TARGET_DURATION = self._duration

    def pause(self):
        # Pause the player
        pygame.mixer.music.pause()

        # Save the duration in the global variable, for use when playing again.
        TARGET_DURATION = self._duration
