A Pi Systemd-Service to measure Times
=====================================

Overview
--------

This is a special stopwatch to measure time from a "start-event"
to an "end-event".

Using a normal button, the user activates the stopwatch and sets a given
"start" GPIO to high. It then monitors an "end" GPIO for an interrupt and
stops the watch as soon as the GPIO changes to low.

The main rationale for this project was to measure boot-times of a second Pi
from power on up to the timepoint when an application program starts. In
this scenario, the "start" GPIO is connected to an enable-pin
of the power-supply of the second Pi. This could be a bucket-converter
or maybe a wide-input shim from Pimoroni giving power to the Pi. Once started,
the application provides the end-event by pulling a GPIO to low.


Hardware
--------

The setup uses the following hardware-components:

  - Pi-Zero
  - one normal button for "Start"
  - one normal button for "Reset"
  - one mini-oled display
  - one buzzer
  - some jumper-wires

![](image.png)


Software
--------

Run

    git clone https://github.com/bablokb/pi-stopwatch.git
    cd pi-stopwatch
    sudo tools/install

to install the software and some prerequisite packages. This will also enable
a systemd-service so that the service starts at boot-time.
