#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, sys, getopt
from datetime import date, timedelta
import time
from lib import epd3in7, weather_info
from PIL import Image,ImageDraw,ImageFont
import traceback, logging

# path
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
# user input
DIST = ""
RAINFALL_DIST = ""
VERBOSE_FLAG = False
ROTATE_FLAG = False
# translation
month = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
# settinh
today = (date.today().strftime("%d"),date.today().strftime("%m"),date.today().strftime("%Y"),
    date.today().strftime("%A"),date.today().strftime("%b"))
str_date = today[0] + "," + today[4].upper() + " | " + today[3].upper()
L_icon_size = 80, 80
S_icon_size = 60, 60
# set font
font48 = ImageFont.truetype("./font/msjh.ttc", 48)
font28 = ImageFont.truetype("./font/msjh.ttc", 28)
font24 = ImageFont.truetype("./font/msjh.ttc", 24)
font18 = ImageFont.truetype("./font/msjh.ttc", 18)
date30 = ImageFont.truetype("./font/unispace bd.ttf", 30)

def main(argv):
    global DIST, RAINFALL_DIST, VERBOSE_FLAG, ROTATE_FLAG

    opts, args = getopt.getopt(argv[1:],'d:r:vhR',["district=","rainfall-district=","verbose","help","rotate-display"])
    for opt,arg in opts:
        if opt in ['-d', '--district']:
            DIST = arg
        elif opt in ['-r', '--rainfall-district']:
            RAINFALL_DIST = arg
        elif opt in ['-v', '--verbose']:
            VERBOSE_FLAG = True
        elif opt in ['-R', '--rotate-display']:
            ROTATE_FLAG = True
        elif opt in ['-h', '--help']:
            pass #TODO
    if(DIST=="" and VERBOSE_FLAG): print("[WARN] district is missing, fallback to '香港天文台'")
    if(RAINFALL_DIST=="" and VERBOSE_FLAG): print("[WARN] rainfall district is missing, fallback to '觀塘'")
    
    epd = epd3in7.EPD()
    wx = weather_info.WeatherInfo(dist=DIST,rainfall_dist=RAINFALL_DIST)
    crrt_wx=wx.rhrread_process(VERBOSE_FLAG)
    forecast_wx=wx.fnd_process(VERBOSE_FLAG)

    try:
        # init
        epd.init(0)
        epd.Clear(0xFF, 0)
        frame = Image.new('L', (epd.height, epd.width), 0xFF)  # 0xFF: clear the frame, draw white
        draw = ImageDraw.Draw(frame)

        draw.line((0, 80, epd.height, 80), fill=epd.GRAY4, width=5) # date
        draw.line((335, 0, 335, 80), fill=epd.GRAY4, width=5) # date, vertical
        draw.rounded_rectangle((10,100,240,270), outline=0, fill=epd.GRAY1, width=2, radius=15) # current wx
        draw.rounded_rectangle((245,100,475,270), outline=0, fill=epd.GRAY1, width=2, radius=15)# forecast
        draw.line((360, 100, 360, 270), fill=epd.GRAY4, width=2) # forecast, vertical
        # date
        draw.text((10,20), str_date, font = date30, fill=epd.GRAY4)
        # current weather
        rhrread_logo = Image.open(os.path.join(picdir, str(crrt_wx["icon"])+".bmp"))
        rhrread_logo = rhrread_logo.resize(L_icon_size)

        draw.text((20,105),crrt_wx["district"], font=font24, fill=epd.GRAY4)
        draw.text((30,130),str(crrt_wx["temperature"])+'°', font=font48, fill=epd.GRAY4)
        draw.text((20,190),"濕度: " + str(crrt_wx["humanity"]) + "%", font=font24, fill=epd.GRAY4)
        draw.text((20,220),"雨量: " + str(crrt_wx["rainfall"]) + "mm", font=font24, fill=epd.GRAY4)
        frame.paste(rhrread_logo,(145,145))
        # forecast
        draw.text((270,105),"明天預報", font=font18, fill=epd.GRAY4)
        fnd_logo = Image.open(os.path.join(picdir, str(forecast_wx[0]["icon"])) + ".bmp")
        fnd_logo = fnd_logo.resize(S_icon_size)
        frame.paste(fnd_logo,(275,130))
        draw.text((250,200),"温度: "+str(forecast_wx[0]["temperatureMin"])+"-"+str(forecast_wx[0]["temperatureMax"])+"°", font=font18, fill=epd.GRAY4)
        draw.text((250,220),"濕度: "+str(forecast_wx[0]["humanityMin"])+"-"+str(forecast_wx[0]["humanityMax"])+"%", font=font18, fill=epd.GRAY4)

        draw.text((380,105),"後天預報", font=font18, fill=epd.GRAY4)
        fnd_logo = Image.open(os.path.join(picdir, str(forecast_wx[1]["icon"])) + ".bmp")
        fnd_logo = fnd_logo.resize(S_icon_size)
        frame.paste(fnd_logo,(385,130))
        draw.text((365,200),"温度: "+str(forecast_wx[1]["temperatureMin"])+"-"+str(forecast_wx[0]["temperatureMax"])+"°", font=font18, fill=epd.GRAY4)
        draw.text((365,220),"濕度: "+str(forecast_wx[1]["humanityMin"])+"-"+str(forecast_wx[0]["humanityMax"])+"%", font=font18, fill=epd.GRAY4)
        
        # output
        if (ROTATE_FLAG): frame = frame.rotate(180)
        epd.display_4Gray(epd.getbuffer_4Gray(frame))     

    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd3in7.epdconfig.module_exit()
        exit()


if __name__=="__main__":
    main(sys.argv)