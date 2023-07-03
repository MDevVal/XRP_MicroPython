from machine import Pin, ADC, Timer

class Board:

    _DEFAULT_BOARD_INSTANCE = None

    @classmethod
    def get_default_board(cls):
        """
        Get the default board instance. This is a singleton, so only one instance of the board will ever exist.
        """
        if cls._DEFAULT_BOARD_INSTANCE is None:
            cls._DEFAULT_BOARD_INSTANCE = cls(28,22)
        return cls._DEFAULT_BOARD_INSTANCE

    def __init__(self, vin_pin:int, button_pin:int):
        self.on_switch = ADC(Pin(vin_pin))
        
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)
        self.button_callback = None

        self.led = Pin("LED", Pin.OUT)
        # A timer ID of -1 is a virtual timer.
        # Leaves the hardware timers for more important uses
        self._virt_timer = Timer(-1)
        self.is_led_blinking = False


    def are_motors_powered(self) -> bool:
        """
        : return: Returns true if the batteries are connected and powering the motors, false otherwise
        : rytpe: bool
        """
        return self.on_switch.read_u16() > 20000

    def set_button_callback(self, trigger, callback):
        """
        Sets an interrupt callback to be triggered on a change in button state, specified by trigger. 
        Follow the link for more information on how to write an Interrupt Service Routine (ISR). 
        https://docs.micropython.org/en/latest/reference/isr_rules.html

        : param trigger: The type of trigger to be used for the interrupt
        : type trigger: Pin.IRQ_RISING | Pin.IRQ_FALLING
        : param callback: The function to be called when the interrupt is triggered
        : type callback: function | None
        """
        self.button_callback = callback
        self.button.irq(trigger=trigger, handler=self.button_callback)

    def is_button_pressed(self) -> bool:
        """
        Returns the state of the button

        : return: True if the button is pressed, False otherwise
        : rtype: bool
        """
        return not self.button.value()
    
    def led_on(self):
        """
        Turns the LED on
        Stops the blinking timer if it is running
        """
        self.is_led_blinking = False
        self.led.on()
        self._virt_timer.deinit()

    def led_off(self):
        """
        Turns the LED off
        Stops the blinking timer if it is running
        """
        self.is_led_blinking = False
        self.led.off()
        self._virt_timer.deinit()

    def led_blink(self, frequency: int):
        """
        Blinks the LED at a given frequency

        : param frequency: The frequency to blink the LED at (in Hz)
        : type frequency: int
        """
        if self.is_led_blinking:
            # disable the old timer so we can reinitialize it
            self._virt_timer.deinit()
        # We set it to twice in input frequency so that
        # the led flashes on and off frequency times per second
        self._virt_timer.init(freq=frequency*2, mode=Timer.PERIODIC,
            callback=lambda t:self.led.toggle())
        self.is_led_blinking = True