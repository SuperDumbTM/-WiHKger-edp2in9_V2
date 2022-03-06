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
tmpdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp')
conf = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'conf')
if (os.path.exists(libdir)):
    sys.path.append(libdir)
if not (os.path.exists(tmpdir)):
    os.makedirs(tmpdir)
    
# user input
DIST = ""
RAINFALL_DIST = ""
VERBOSE_FLAG = False
ROTATE_FLAG = False
ROTATE_DEGREE = 0
IMAGEOUT_FLAG = False
DRYRUN_FLAG = False
MUTE_WXINFO_FLAG = False
# translation
month = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
# setting
today_day = date.today().strftime("%d")
today_month_abbr = date.today().strftime("%b")
today_weekday = date.today().strftime("%A")
L_icon_size = 80, 80
M_icon_size = 60, 60
S_icon_size = 27, 27
W_icon_size = 46,46
# set font
font56 = ImageFont.truetype("./font/msjh.ttc", 56)
font28 = ImageFont.truetype("./font/msjh.ttc", 28)
font24 = ImageFont.truetype("./font/msjh.ttc", 24)
font20 = ImageFont.truetype("./font/msjh.ttc", 20)
date32 = ImageFont.truetype("./font/unispace bd.ttf", 32)
# text drawing functions
signs_draw_info={
    "WMSGNL":{"color":"B","piority":2}, # 季候風
    "WL":{"color":"B","piority":3}, # 山泥傾瀉
    "WTMW":{"color":"R","piority":0}, # 海嘯
    "WTS":{"color":"B","piority":2}, # 雷暴
    # Temps
    "WHOT":{"color":"R","piority":1},
    "WCOLD":{"color":"B","piority":1},
    "WFROST":{"color":"R","piority":1}, # 霜凍
    # Dry
    "WFIREY":{"color":"B","piority":2},
    "WFIRER":{"color":"R","piority":2},
    # Rain storm
    "WRAINA":{"color":"B","piority":0},
    "WRAINR":{"color":"R","piority":0},
    "WRAINB":{"color":"B","piority":0},
    "WFNTSA":{"color":"B","piority":3}, # 北部水浸
    # TC
    "WTCPRE8":{"color":"R","piority":1},
    "TC1":{"color":"B","piority":0},
    "TC3":{"color":"B","piority":0},
    "TC8NE":{"color":"R","piority":0},
    "TC8SE":{"color":"R","piority":0},
    "TC8SW":{"color":"R","piority":0},
    "TC8NW":{"color":"R","piority":0},
    "TC9":{"color":"R","piority":0},
    "TC10":{"color":"R","piority":0},
}
warn_sign_coords = ((340,17),(386,17),(432,17))
def draw_warning_sign(warning_name,idx,img_Black):
    warnsum_logo = Image.open(os.path.join(picdir, str(warning_name)+".bmp"))
    warnsum_logo = warnsum_logo.resize(W_icon_size)
    img_Black.paste(warnsum_logo,warn_sign_coords[idx])

def main(argv):
    global DIST, RAINFALL_DIST, VERBOSE_FLAG, ROTATE_FLAG, IMAGEOUT_FLAG, ROTATE_DEGREE, DRYRUN_FLAG, MUTE_WXINFO_FLAG

    opts, args = getopt.getopt(argv[1:],'d:r:vhiR:',
        ["district=","rainfall-district=","verbose","image-save","help","rotate-display=","dry-run","mute-weather-info"])
    for opt,arg in opts:
        if opt in ['-d', '--district']:
            DIST = arg
        elif opt in ['-r', '--rainfall-district']:
            RAINFALL_DIST = arg
        elif opt in ['-v', '--verbose']:
            VERBOSE_FLAG = True
        elif opt in ['-R', '--rotate-display']:
            ROTATE_FLAG = True
            ROTATE_DEGREE = int(arg)
        elif opt in ['-i', '--image-save']:
            IMAGEOUT_FLAG = True
        elif opt in ['--dry-run']:
            IMAGEOUT_FLAG = True
            VERBOSE_FLAG = True
            DRYRUN_FLAG = True
        elif opt in ('--mute-weather-info'):
            MUTE_WXINFO_FLAG = True
        elif opt in ['-h', '--help']:
            with open(os.path.join(conf,"help.txt"),'r') as h:
                print(h.read())
            exit()
    if (VERBOSE_FLAG): print("[DEBUG]","DIST: ",DIST,"RAINFALL_DIST: ",RAINFALL_DIST,"ROTATE_FLAG: ",ROTATE_FLAG,"\nROTATE_DEGREE: ",
            ROTATE_DEGREE,"IMAGEOUT_FLAG: ",IMAGEOUT_FLAG, "DRYRUN_FLAG: ",DRYRUN_FLAG)

    if(DIST==""): 
        DIST="香港天文台"
        if (VERBOSE_FLAG): print("[WARN] district is not set, fallback to '香港天文台'")
    if(RAINFALL_DIST==""):
        RAINFALL_DIST="油尖旺"
        if (VERBOSE_FLAG): print("[WARN] rainfall district is not set, fallback to '油尖旺'")
    
    epd = epd3in7.EPD()
    wx = weather_info.WeatherInfo(dist=DIST,rainfall_dist=RAINFALL_DIST)
    crrt_wx=wx.rhrread_process(VERBOSE_FLAG and not MUTE_WXINFO_FLAG)
    forecast_wx=wx.fnd_process(VERBOSE_FLAG and not MUTE_WXINFO_FLAG)
    warnings=wx.warnsum_process(VERBOSE_FLAG and not MUTE_WXINFO_FLAG)

    try:
        # init
        if not (DRYRUN_FLAG):
            if (VERBOSE_FLAG): print("[INFO] Initializating...")
            epd.init(0)
            epd.Clear(0xFF, 0)
        img_4Gray = Image.new('L', (epd.height, epd.width), 0xFF)  # 0xFF: clear the frame, draw white
        draw = ImageDraw.Draw(img_4Gray)

        if (VERBOSE_FLAG): print("[INFO] Drawing frame...")
        draw.line((0, 80, epd.height, 80), fill=epd.GRAY4, width=5) # date
        draw.line((140, 20, 140, 55), fill=epd.GRAY4, width=3) # date, weekday vertical
        draw.line((335, 0, 335, 80), fill=epd.GRAY4, width=5) # date, main vertical
        draw.rounded_rectangle((10,100,240,270), outline=0, fill=epd.GRAY1, width=2, radius=15) # current wx
        draw.rounded_rectangle((245,100,475,270), outline=0, fill=epd.GRAY1, width=2, radius=15)# forecast
        draw.line((360, 100, 360, 270), fill=epd.GRAY4, width=2) # forecast, vertical
        
        # date
        if (VERBOSE_FLAG): print("[INFO] Drawing date information...")
        draw.text((5,20), today_day+" "+today_month_abbr.upper(), font = date32, fill=epd.GRAY4)
        draw.text((155,20), today_weekday.upper(), font = date32, fill=epd.GRAY4)
        
        # warning sign
        if (VERBOSE_FLAG): print("[INFO] Drawing warning sign information...")
        
        position_count = 0
        for warning_name in warnings:
            if (position_count==3): break
            draw_warning_sign(warning_name,position_count,img_4Gray)
            position_count+=1
        

        # current weather
        if (VERBOSE_FLAG): print("[INFO] Drawing current weather information...")
        rhrread_logo = Image.open(os.path.join(picdir, str(crrt_wx["icon"])+".bmp"))
        rhrread_logo = rhrread_logo.resize(L_icon_size)
        draw.text((20,105),crrt_wx["district"], font=font24, fill=epd.GRAY4)
        draw.text((30,130),str(crrt_wx["temperature"])+'°', font=font56, fill=epd.GRAY4)
        draw.text((20,200),"濕度: " + str(crrt_wx["humanity"]) + "%", font=font24, fill=epd.GRAY4)
        draw.text((20,230),"雨量: " + str(crrt_wx["rainfall"]) + "mm", font=font24, fill=epd.GRAY4)
        img_4Gray.paste(rhrread_logo,(145,145))
        
        # forecast
        if (VERBOSE_FLAG): print("[INFO] Drawing forecast information...")
        draw.text((265,105),"明天預報", font=font20, fill=epd.GRAY4)
            # weather icon
        fnd_logo = Image.open(os.path.join(picdir, str(forecast_wx["0"]["icon"])) + ".bmp")
        fnd_logo = fnd_logo.resize(M_icon_size)
        img_4Gray.paste(fnd_logo,(275,135))
            # temp
        fnd_logo = Image.open(os.path.join(picdir, "thermometer.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        img_4Gray.paste(fnd_logo,(250,200))
        draw.text((280,200),str(forecast_wx["0"]["temperatureMin"])+"-"+str(forecast_wx["0"]["temperatureMax"])+"°", font=font20, fill=epd.GRAY4)
            # huma
        fnd_logo = Image.open(os.path.join(picdir, "rain-drop.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        img_4Gray.paste(fnd_logo,(250,235))
        draw.text((280,235),str(forecast_wx["0"]["humanityMin"])+"-"+str(forecast_wx["0"]["humanityMax"])+"%", font=font20, fill=epd.GRAY4)

        draw.text((375,105),"後天預報", font=font20, fill=epd.GRAY4)
            # weather icon
        fnd_logo = Image.open(os.path.join(picdir, str(forecast_wx["1"]["icon"])) + ".bmp")
        fnd_logo = fnd_logo.resize(M_icon_size)
        img_4Gray.paste(fnd_logo,(390,135))
            # temp
        fnd_logo = Image.open(os.path.join(picdir, "thermometer.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        img_4Gray.paste(fnd_logo,(365,200))
        draw.text((395,200),str(forecast_wx["1"]["temperatureMin"])+"-"+str(forecast_wx["1"]["temperatureMax"])+"°", font=font20, fill=epd.GRAY4)
            # huma
        fnd_logo = Image.open(os.path.join(picdir, "rain-drop.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        img_4Gray.paste(fnd_logo,(365,235))
        draw.text((395,235),str(forecast_wx["1"]["humanityMin"])+"-"+str(forecast_wx["1"]["humanityMax"])+"%", font=font20, fill=epd.GRAY4)
        
        # output
        if (IMAGEOUT_FLAG): 
            if (VERBOSE_FLAG): print("[INFO] Saving the e-paper display output to temp/...")
            img_4Gray.save(os.path.join(tmpdir,"output.bmp"))
        if (ROTATE_FLAG): 
            if (VERBOSE_FLAG): print("[INFO] Rotating the e-paper display output by {0}".format(str(ROTATE_DEGREE)+"°"))
            img_4Gray = img_4Gray.rotate(ROTATE_DEGREE)
        
        if (VERBOSE_FLAG): print("[INFO] Drawing to the e-paper display...")
        if not (DRYRUN_FLAG): epd.display_4Gray(epd.getbuffer_4Gray(img_4Gray))    
        if (VERBOSE_FLAG): print("Done.")

    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd3in7.epdconfig.module_exit()
        exit()


if __name__=="__main__":
    main(sys.argv)