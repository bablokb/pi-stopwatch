#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Stopwatch implementation
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-stopwatch
#
# ----------------------------------------------------------------------------

FONT_NAME = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'
FONT_SIZE = 40

import smbus, threading, signal, sys, time

from lib_oled96 import ssd1306
from PIL        import ImageFont

import RPi.GPIO as GPIO

# --- pin-configuration   ----------------------------------------------------

PIN_START    =  5
PIN_RESET    =  6
PIN_END      = 19
PIN_ENABLE   = 13
PIN_BUZZER   = 24

# --- initialize oled-display   ----------------------------------------------

def init_oled():
  """ initialize oled-disply """

  global oled, font

  i2cbus = smbus.SMBus(1)
  oled   = ssd1306(i2cbus)
  font   = ImageFont.truetype(FONT_NAME,FONT_SIZE)
  oled.cls()

# --- application-class   ----------------------------------------------------

class Stopwatch(object):

  _STATE_READY   = 0
  _STATE_RUNNING = 1
  
  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    self._end_event  = threading.Event()

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(PIN_START,    GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_RESET,    GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_END,      GPIO.IN,  pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_BUZZER,   GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(PIN_ENABLE,   GPIO.OUT, initial=GPIO.LOW)

    GPIO.add_event_detect(PIN_START, GPIO.FALLING, self.on_start,200)
    GPIO.add_event_detect(PIN_RESET, GPIO.FALLING, self.on_reset,200)
    GPIO.add_event_detect(PIN_END,   GPIO.FALLING, self.on_end,200)

    self._state    = Stopwatch._STATE_READY
    self._duration = 0.0
    self._display_time(0.0)

  # --- process start   ------------------------------------------------------

  def on_start(self,pin):
    """ start stopwatch and enable power """

    if self._state == Stopwatch._STATE_READY:
      self._state = Stopwatch._STATE_RUNNING
      self._end_event.clear()
      self._update_thread = threading.Thread(target=self._update_oled)
      self._update_thread.start()
      self._stime = time.monotonic()
      GPIO.output(PIN_ENABLE, GPIO.HIGH)
    else:
      self._buzz(1)

  # --- process reset   ------------------------------------------------------

  def on_reset(self,pin):
    """ reset stopwatch """

    if self._state == Stopwatch._STATE_RUNNING:
      self._end_event.set()
      self._state = Stopwatch._STATE_READY
      self._update_thread.join()

    GPIO.output(PIN_ENABLE, GPIO.LOW)
    self._display_time(0.0)
    self._buzz(1)

  # --- process end    ------------------------------------------------------

  def on_end(self,pin):
    """ stop stopwatch """

    if self._state == Stopwatch._STATE_RUNNING:
      self._duration = time.monotonic() - self._stime
      self._state    = Stopwatch._STATE_READY
      self._end_event.set()
      self._buzz(3)

  # --- update oled-display   ------------------------------------------------

  def _update_oled(self):
    start = time.monotonic()
    while True:
      now = time.monotonic()
      self._display_time(now-start)

      # wait (up to) one second
      delay = max(0.0,1.0-(time.monotonic()-now))
      if self._end_event.wait(delay):
        break

    # display final duration
    self._display_time(self._duration)

  # --- display data on   ----------------------------------------------------

  def _display_time(self,value):
    global oled, font
    oled.canvas.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    y_off = 0
    oled.canvas.text((0,y_off),"{0:5.1f}".format(value),font=font,fill=1)
    oled.display()

  # --- sound buzzer   -------------------------------------------------------

  def _buzz(self,count):
    for i in range(count):
      GPIO.output(PIN_BUZZER, GPIO.LOW)     # buzzer on
      time.sleep(0.25)
      GPIO.output(PIN_BUZZER, GPIO.HIGH)    # buzzer off
      time.sleep(0.25)

  # --- process exit   -------------------------------------------------------

  def on_exit(self):
    self._end_event.set()

# --------------------------------------------------------------------------

def signal_handler(_signo, _stack_frame):
  """ Signal-handler to cleanup threads """

  global swatch
  swatch.on_exit()
  sys.exit(0)

# --------------------------------------------------------------------------

if __name__ == "__main__":

  # create objects and run
  init_oled()
  swatch = Stopwatch()

  # setup signal handlers
  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGINT, signal_handler)

  # --- main loop   ---------------------------------------------------------

  signal.pause()
