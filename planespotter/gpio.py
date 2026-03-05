import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)

LED_PIN = 17
BUTTON_PIN = 27

try:
    from gpiozero import LED
    from gpiozero import Button as GpioButton

    class StatusLED:
        def __init__(self) -> None:
            self._led = LED(LED_PIN)

        def on(self) -> None:
            self._led.on()

        def off(self) -> None:
            self._led.off()

        def blink(self, on_time: float = 0.5, off_time: float = 0.5) -> None:
            self._led.blink(on_time, off_time)

    class Button:
        def __init__(self, callback: Callable[[], None] | None = None) -> None:
            self._button = GpioButton(BUTTON_PIN, pull_up=True)
            if callback:
                self._button.when_pressed = callback

except (ImportError, Exception):
    logger.warning("GPIO not available, using stubs")

    class StatusLED:
        def on(self) -> None:
            logger.debug("LED on")

        def off(self) -> None:
            logger.debug("LED off")

        def blink(self, on_time: float = 0.5, off_time: float = 0.5) -> None:
            logger.debug("LED blink")

    class Button:
        def __init__(self, callback: Callable[[], None] | None = None) -> None:
            self._callback = callback
