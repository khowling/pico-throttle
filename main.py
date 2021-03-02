from machine import Pin
import utime
import screen

#  GP25 = on-board LED, set as a output
led_onboard = Pin(25, Pin.OUT)
led_onboard.value(0)

# GP14 - set as a input
speed_sensor = Pin(14, Pin.IN, Pin.PULL_UP)
motor = Pin(17, Pin.OUT)
motor.value(0)


# ( 2.195 meters : circumference of a 27.5" x 2.25" wheel )
KM_PER_REVOLUTION = 2.195 / 1000
MS_IN_AN_HOUR = 3600000
MAX_SPEED_KMH = 20
MAX_SPEED_DURATION = int(
    MS_IN_AN_HOUR / (MAX_SPEED_KMH / KM_PER_REVOLUTION))  # ( 20 km/h)
print("MAX_SPEED_KMH=", MAX_SPEED_KMH,
      " MAX_SPEED_DURATION=", MAX_SPEED_DURATION)

irq_last_rotation_time = 0
#irq_last_speed_calc = 0


def sensor_handler(sensor):
    global irq_last_rotation_time
    #global irq_last_speed_calc

    irq_trigger_time = utime.ticks_ms()
    irq_last_rotation_time_diff = utime.ticks_diff(irq_trigger_time, irq_last_rotation_time)

    # Got a falling edge, ignore all falling edges for the next 80mS (need to be doing 100kph!)
    if (irq_last_rotation_time_diff > 80):
        #irq_last_speed_calc = KM_PER_REVOLUTION * (MS_IN_AN_HOUR/irq_last_rotation_time_diff)
        #print ("IRQ irq_last_speed_calc=",irq_last_speed_calc, " (irq_last_rotation_time_diff=",irq_last_rotation_time_diff,")")
        irq_last_rotation_time = irq_trigger_time



speed_sensor.irq(trigger=Pin.IRQ_FALLING, handler=sensor_handler)

last_loop_pulce_started = 0 
last_loop_pulce_finished = 0
irq_time = 0
irq_speed = 0

oled = screen.SCREEN()
oled.test()

while True:
    loop_time = utime.ticks_ms()
    last_processed_diff = utime.ticks_diff(irq_last_rotation_time, last_loop_pulce_finished)
    new_rotation_since_last_pulce_finished = last_processed_diff > 0

    irq_time = irq_last_rotation_time
    #irq_speed = irq_last_speed_calc

    # We have a new irq rotation since the last pulce we sent!
    if (new_rotation_since_last_pulce_finished):

        duration_since_last_pulce = utime.ticks_diff(loop_time, last_loop_pulce_started)
        delay = 0

        if (duration_since_last_pulce < MAX_SPEED_DURATION):
            # Too fast! Delay before sending the pulce
            delay = MAX_SPEED_DURATION - duration_since_last_pulce
            utime.sleep_ms(delay)

        # send pulce length depending on the speed (max .5seconds)
        on_for = min(500, int((duration_since_last_pulce+delay) * 0.05))
        speed = KM_PER_REVOLUTION * (MS_IN_AN_HOUR / (duration_since_last_pulce+delay))
        #print("irq_speed=", "{:.1f}".format(irq_speed), " speed=", "{:.1f}".format(speed), " on_for=", on_for," diff1=", utime.ticks_diff(irq_time, irq_last_rotation_time), " last_loop_pulce_finished=", last_loop_pulce_finished)
        oled.display(speed)
        last_loop_pulce_started = loop_time + delay
        led_onboard.value(1)
        motor.value(1)

        utime.sleep_ms(on_for)
    else:
        utime.sleep_ms(10)

    if (new_rotation_since_last_pulce_finished):
        last_loop_pulce_finished = utime.ticks_ms()
        led_onboard.value(0)
        motor.value(0)
