from fifo import Fifo
from piotimer import Piotimer
from machine import ADC, Pin
import micropython

micropython.alloc_emergency_exception_buf(200)


class Adc:
    def __init__(self, adc_pin):
        self.adc = ADC(Pin(adc_pin, Pin.IN))
        self.adc_fifo = Fifo(size=50, typecode='i')
        self.tmr = Piotimer(freq=10, callback=self.adc_callback)

    def adc_callback(self, tmr):
        self.adc_fifo.put(self.adc.read_u16())


def adc_main(pin):
    dmm = Adc(pin)

    while True:
        while dmm.adc_fifo.has_data():
            adc_count = dmm.adc_fifo.get()
            print('ADC COUNT: {:-5} = VOLTAGE: {:1.3}V'.format(adc_count, adc_count / ((1 << 16) - 1) * 3.3))


# Press the green button in the gutter <to run the script.
if __name__ == '__main__':
    adc_main(26)