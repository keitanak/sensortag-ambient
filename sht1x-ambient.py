# -*- coding: utf-8 -*-
# while True:
#     SHT1xから
#     温度、湿度を取得し、Ambientに送信
#
import bluepy
import time
import sys
import argparse
import ambient
import argparse
import RPi.GPIO as GPIO
from pi_sht1x import SHT1x

import logging

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

class Choices(list):
    def __contains__(self, item):
        return super(Choices, self).__contains__(item.upper())
        
def main():
    channelId = チャネルID
    writeKey = 'ライトキー'

    vdd_choices = Choices(['5V', '4V', '3.5V', '3V', '2.5V'])
    resolution_choices = Choices(['HIGH', 'LOW'])

    parser = argparse.ArgumentParser(description='Reads the temperature and relative humidity from the SHT1x series '
                                                 'of sensors using the pi_sht1x library.')
    parser.add_argument('data_pin', type=int, metavar='data-pin', help='Data pin used to connect to the sensor.')
    parser.add_argument('sck_pin', type=int, metavar='sck-pin', help='SCK pin used to connect to the sensor.')
    parser.add_argument('-g', '--gpio-mode', choices=['BCM', 'BOARD'], default='BCM',
                        help='RPi.GPIO mode used, either GPIO.BOARD or GPIO.BCM. Defaults to GPIO.BCM.')
    parser.add_argument('-v', '--vdd', choices=vdd_choices, default='3.5V',
                        help='Voltage used to power the sensor. Defaults to 3.5V.')
    parser.add_argument('-r', '--resolution', choices=resolution_choices, default='HIGH',
                        help='Resolution used by the sensor, 14/12-bit or 12-8-bit. Defaults to High.')
    parser.add_argument('-e', '--heater', action='store_true',
                        help='Used to turn the internal heater on (used for calibration).')
    parser.add_argument('-o', '--otp-no-reload', action='store_true',
                        help='Used to enable OTP no reload, will save about 10ms per measurement.')
    parser.add_argument('-c', '--no-crc-check', action='store_false', help='Performs CRC checking.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging.')
    parser.add_argument('-i',action='store',type=float, default=300.0, help='scan interval')

    args = parser.parse_args()

    am = ambient.Ambient(channelId, writeKey)
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    mode = GPIO.BCM if args.gpio_mode.upper() == 'BCM' else GPIO.BOARD
    with SHT1x(args.data_pin, args.sck_pin, gpio_mode=mode, vdd=args.vdd, resolution=args.resolution,
           heater=args.heater, otp_no_reload=args.otp_no_reload, crc_check=args.no_crc_check,
           logger=logger) as sensor:
            
        while True:
            temp = sensor.read_temperature()
            humidity = sensor.read_humidity(temp)
            
            data = {}
            data['d1'] = float(temp)  # set ambient temperature to d1
            data['d2'] = float(humidity)  # set humidity to d2
            
            print(data)
            if am:
                try:
                    r = am.send(data)
                    print(r.status_code)
                except:
                    print('Could not sent')
                finally:
                    sys.stdout.flush()

            time.sleep(args.i)
        # tag.waitForNotifications(arg.t)

if __name__ == "__main__":
    main()
