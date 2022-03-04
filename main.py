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
today_day = date.today().strftime("%d")
today_month_abbr = date.today().strftime("%b")
today_weekday = date.today().strftime("%A")
L_icon_size = 80, 80
M_icon_size = 60, 60
S_icon_size = 27, 27

# set font
font56 = ImageFont.truetype("./font/msjh.ttc", 56)
font28 = ImageFont.truetype("./font/msjh.ttc", 28)
font24 = ImageFont.truetype("./font/msjh.ttc", 24)
font20 = ImageFont.truetype("./font/msjh.ttc", 20)
date32 = ImageFont.truetype("./font/unispace bd.ttf", 32)

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
        draw.line((140, 20, 140, 55), fill=epd.GRAY4, width=3) # date, weekday vertical
        draw.line((335, 0, 335, 80), fill=epd.GRAY4, width=5) # date, main vertical
        draw.rounded_rectangle((10,100,240,270), outline=0, fill=epd.GRAY1, width=2, radius=15) # current wx
        draw.rounded_rectangle((245,100,475,270), outline=0, fill=epd.GRAY1, width=2, radius=15)# forecast
        draw.line((360, 100, 360, 270), fill=epd.GRAY4, width=2) # forecast, vertical
        # date
        draw.text((5,20), today_day+" "+today_month_abbr.upper(), font = date32, fill=epd.GRAY4)
        draw.text((155,20), today_weekday.upper(), font = date32, fill=epd.GRAY4)
        # current weather
        rhrread_logo = Image.open(os.path.join(picdir, str(crrt_wx["icon"])+".bmp"))
        rhrread_logo = rhrread_logo.resize(L_icon_size)
        draw.text((20,105),crrt_wx["district"], font=font24, fill=epd.GRAY4)
        draw.text((30,130),str(crrt_wx["temperature"])+'°', font=font56, fill=epd.GRAY4)
        draw.text((20,200),"濕度: " + str(crrt_wx["humanity"]) + "%", font=font24, fill=epd.GRAY4)
        draw.text((20,230),"雨量: " + str(crrt_wx["rainfall"]) + "mm", font=font24, fill=epd.GRAY4)
        frame.paste(rhrread_logo,(145,145))
        # forecast
        draw.text((265,105),"明天預報", font=font20, fill=epd.GRAY4)
            # weather icon
        fnd_logo = Image.open(os.path.join(picdir, str(forecast_wx[0]["icon"])) + ".bmp")
        fnd_logo = fnd_logo.resize(M_icon_size)
        frame.paste(fnd_logo,(275,135))
            # temp icon
        fnd_logo = Image.open(os.path.join(picdir, "thermometer.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        frame.paste(fnd_logo,(250,200))
        draw.text((280,200),str(forecast_wx[0]["temperatureMin"])+"-"+str(forecast_wx[0]["temperatureMax"])+"°", font=font20, fill=epd.GRAY4)
            # huma icon
        fnd_logo = Image.open(os.path.join(picdir, "rain-drop.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        frame.paste(fnd_logo,(250,235))
        draw.text((280,235),str(forecast_wx[0]["humanityMin"])+"-"+str(forecast_wx[0]["humanityMax"])+"%", font=font20, fill=epd.GRAY4)

        draw.text((375,105),"後天預報", font=font20, fill=epd.GRAY4)
            # weather icon
        fnd_logo = Image.open(os.path.join(picdir, str(forecast_wx[1]["icon"])) + ".bmp")
        fnd_logo = fnd_logo.resize(M_icon_size)
        frame.paste(fnd_logo,(390,135))
            # temp icon
        fnd_logo = Image.open(os.path.join(picdir, "thermometer.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        frame.paste(fnd_logo,(365,200))
        draw.text((395,200),str(forecast_wx[1]["temperatureMin"])+"-"+str(forecast_wx[1]["temperatureMax"])+"°", font=font20, fill=epd.GRAY4)
            # huma icon
        fnd_logo = Image.open(os.path.join(picdir, "rain-drop.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        frame.paste(fnd_logo,(365,235))
        draw.text((395,235),str(forecast_wx[1]["humanityMin"])+"-"+str(forecast_wx[1]["humanityMax"])+"%", font=font20, fill=epd.GRAY4)
        # output
        frame.save(os.path.join(picdir,"output.bmp"))
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