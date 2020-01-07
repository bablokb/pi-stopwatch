Tests
=====

  * program-start
    - PIN_ENABLE is low                (ok)
    - display: 0.0                     (ok)
  * start-button
    - PIN_ENABLE is high               (ok)
    - display is counting time         (ok)
  * pull PIN_END to GND
    - PIN_ENABLE is high               (ok)
    - display shows final time         (ok)
    - buzzer sounds
  * reset-button during ready
    - PIN_ENABLE is low                (ok)
    - display: 0.0                     (ok)
  * reset-button during run
    - PIN_ENABLE is low                (ok)
    - display stops and changes to 0.0 (ok)
