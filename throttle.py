from machine import Pin
import utime

#  GP25 = on-board LED, set as a output
led_onboard = Pin(25, Pin.OUT)

# GP14 - set as a input
speed_sensor = Pin(14, Pin.IN, Pin.PULL_DOWN)

last_sensor_high_ms = utime.ticks_ms()
last_sensor_low_ms = utime.ticks_ms()


KM_PER_REVOLUTION = 2.18 / 1000 # ( 2.18 meters : circumference of a 27.5" x 2.25" wheel )
MS_IN_AN_HOUR = 3600000
MAX_SPEED_KMH = 20
MAX_SPEED_DURATION = int(MS_IN_AN_HOUR / (MAX_SPEED_KMH / KM_PER_REVOLUTION)) # ( 20 km/h)

print ("MAX_SPEED_KMH=", MAX_SPEED_KMH, " MAX_SPEED_DURATION=", MAX_SPEED_DURATION)

def sensor_handler(pin):
    global last_sensor_high_ms
    global last_sensor_low_ms
    # debounce (only trigger once in a 100mS period)
    irq_trigger_time = utime.ticks_ms()
    last_low_to_trigger_ms = utime.ticks_diff (irq_trigger_time, last_sensor_low_ms)
    last_high_to_trigger_ms = utime.ticks_diff (irq_trigger_time, last_sensor_high_ms)

    if (pin.value() == 1):
        
        if (last_high_to_trigger_ms >= last_low_to_trigger_ms ):
            # Got a high edge, ignore all high edges for the next 80mS
            if (last_high_to_trigger_ms >80):
                if (last_high_to_trigger_ms <MAX_SPEED_DURATION): # last high <350mS ago, need to throttle
                    throttle = True
                    # artifical sleep (will cause future interupts to queue, and should be rejected as debounce)
                    throttle_by_ms = MAX_SPEED_DURATION - last_high_to_trigger_ms
                    utime.sleep_ms(throttle_by_ms)
                    last_high_to_trigger_ms = last_high_to_trigger_ms + throttle_by_ms
                else:
                    throttle = False

                revolutions_per_hour = MS_IN_AN_HOUR/last_high_to_trigger_ms
                print ("Speed=", KM_PER_REVOLUTION * revolutions_per_hour ,"kph (throttle=",throttle,") (last_high_to_trigger_ms=",last_high_to_trigger_ms,")" ) 
            
            #else:
            #    print ("*bounce ON diff=", last_high_to_trigger_ms)
            #    last_sensor_high_ms = irq_trigger_time
            led_onboard.value(1)
            last_sensor_high_ms = utime.ticks_ms()          
        #else:
        #   print ("Already ON")

    else:

        # Got a high edge, ignore all high edges for the next 80mS
        if (last_low_to_trigger_ms >= last_high_to_trigger_ms):
            if (last_low_to_trigger_ms >80):
                
                # ensure on for at least 10ms when throttled
                if (last_high_to_trigger_ms < 10):
                    utime.sleep_ms(10 - last_high_to_trigger_ms)
                
                #print ("OFF (on for ",last_high_to_trigger_ms ," or 10mS, whever higher) (last_low_to_trigger_ms=", last_low_to_trigger_ms, ")")
                led_onboard.value(0)
                last_sensor_low_ms = utime.ticks_ms()
            #else:
            #    print ("*bounce OFF diff=", last_low_to_trigger_ms, " (last_low_to_trigger_ms=", last_low_to_trigger_ms, ")")
        #else:
        #   print ("Already OFF")

speed_sensor.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=sensor_handler)

