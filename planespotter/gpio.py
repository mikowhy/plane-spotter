import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

LED_PIN = 17
BUTTON_PIN = 27

_led_class: Any = None
_button_class: Any = None

try:
    from gpiozero import LED
    from gpiozero import Button as GpioButton

    _led_class = LED
    _button_class = GpioButton
except (ImportError, Exception):
    logger.warning("GPIO not available, using stubs")


class StatusLED:
    def __init__(self) -> None:
        self._led: Any = _led_class(LED_PIN) if _led_class else None

    def on(self) -> None:
        if self._led:
            self._led.on()
        else:
            logger.debug("LED on")

    def off(self) -> None:
        if self._led:
            self._led.off()
        else:
            logger.debug("LED off")

    def blink(self, on_time: float = 0.5, off_time: float = 0.5) -> None:
        if self._led:
            self._led.blink(
                on_time=on_time,
                off_time=off_time,
            )
        else:
            logger.debug("LED blink")


class Button:
    def __init__(self, callback: Callable[[], None] | None = None) -> None:
        self._callback = callback
        if _button_class:
            self._button: Any = _button_class(
                BUTTON_PIN,
                pull_up=True,
            )
            if callback:
                self._button.when_pressed = callback
