#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, sys, getopt
from datetime import date
import time

from lib import epd4in2b_V2, weather_info, hk_holiday
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
FORECAST_TEXT = "generalSituation"
MUTE_WXINFO_FLAG = False
# translation
month = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
# setting
today_day = date.today().strftime("%d")
today_month_abbr = date.today().strftime("%b")
today_week = date.today().strftime("%A")
L_icon_size = 75, 75
M_icon_size = 60, 60
S_icon_size = 27, 27
W_icon_size = 32,32
# set font
font56 = ImageFont.truetype("./font/msjh.ttc", 56)
font28 = ImageFont.truetype("./font/msjh.ttc", 28)
font24 = ImageFont.truetype("./font/msjh.ttc", 24)
bfont24 = ImageFont.truetype("./font/msjhbd.ttc", 24)
font22 = ImageFont.truetype("./font/msjh.ttc", 22)
font18 = ImageFont.truetype("./font/msjh.ttc", 18)
font14 = ImageFont.truetype("./font/msjh.ttc", 14)
font11 = ImageFont.truetype("./font/msjh.ttc", 11)
date26 = ImageFont.truetype("./font/unispace bd.ttf", 26)
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
warn_sign_coords = ((270,0),(316,0),(362,0),(270,33),(316,33),(362,33))
def draw_warning_sign(warning_name,idx,img_Black,img_RedYellow):
    if (signs_draw_info[warning_name]['color']=='B'):
        warnsum_logo = Image.open(os.path.join(picdir, str(warning_name)+".bmp"))
        warnsum_logo = warnsum_logo.resize(W_icon_size)
        img_Black.paste(warnsum_logo,warn_sign_coords[idx])
    elif (signs_draw_info[warning_name]['color']=='R'):
        warnsum_logo = Image.open(os.path.join(picdir, str(warning_name)+".bmp"))
        warnsum_logo = warnsum_logo.resize(W_icon_size)
        img_RedYellow.paste(warnsum_logo,warn_sign_coords[idx])
def draw_temperature(temp,drawB,drawRY):
    if (temp<10):
            drawB.rectangle((15,105,80,170), fill=0)
            drawB.text((15,100),'8°', font=font56, fill=255)
    elif (temp<=12):
        drawB.rectangle((15,105,100,170), fill=0)
        drawB.text((15,100),str(temp)+'°', font=font56, fill=255)
    elif (temp>32):
        drawRY.rectangle((15,105,100,170), fill=0)
        drawRY.text((15,100),str(temp)+'°', font=font56, fill=255)
    else:
        drawB.text((15,100),str(temp)+'°', font=font56, fill=0)
def draw_weather_descript(text,drawB,drawRY):
    num_words = 0
    if (len(text)<=34):
        num_words = 17
        for i in range(len(text)//num_words):
            text=text[:(i+1)*num_words]+"\n"+text[(i+1)*num_words:]
        drawB.text((0,235),text, font=font22, fill=0)
    elif (len(text)<=44):
        num_words = 22
        for i in range(len(text)//num_words):
            text=text[:(i+1)*num_words]+"\n"+text[(i+1)*num_words:]
        drawB.text((0,240),text, font=font18, fill=0)
    elif (len(text)<=84):
        num_words = 28
        for i in range(len(text)//num_words):
            text=text[:(i+1)*num_words]+"\n"+text[(i+1)*num_words:]
        drawB.text((0,240),text, font=font14, fill=0)
    else: # text may overflow
        num_words = 36
        for i in range(len(text)//num_words):
            text=text[:(i+1)*num_words]+"\n"+text[(i+1)*num_words:]
        drawB.text((0,240),text, font=font11, fill=0)
def draw_day(date,drawB,drawRY):
    if (hk_holiday.isHoliday(date)):
        drawB.text((4,1), hk_holiday.get_holiday_name(), font = font14, fill=0)
        drawRY.text((4,20), today_day+" "+today_month_abbr.upper(), font = date26, fill=0)
    else:
        drawB.text((4,20), today_day+" "+today_month_abbr.upper(), font = date26, fill=0)
def draw_week(week,drawB,drawRY):
    if (week=="Saturday" or today_week=="Sunday"):
        drawRY.text((120,20), week.upper(), font = date26, fill=0)
    else:
        drawB.text((120,20), week.upper(), font = date26, fill=0)

def main(argv):
    global DIST, RAINFALL_DIST, VERBOSE_FLAG, ROTATE_FLAG, IMAGEOUT_FLAG, ROTATE_DEGREE, DRYRUN_FLAG, FORECAST_TEXT,MUTE_WXINFO_FLAG

    opts, args = getopt.getopt(argv[1:],'d:r:vhiR:f:',
        ["district=","rainfall-district=","verbose","image-save","help","rotate-display=","dry-run","forecast-text-type=", "mute-weather-info"])
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
        elif opt in ['-f', '--forecast-text-type']:
            if (str(arg) not in ["generalSituation","forecastDesc","outlook"]):
                print("[ERROR] Input for flag -f/--forecast-text-type shoud be \"generalSituation\"/\"forecastDesc\"/\"outlook\".  \nAbord...")
                exit(-1)
            FORECAST_TEXT = arg
        elif opt in ('mute-weather-info'):
            MUTE_WXINFO_FLAG = True
        elif opt in ['-h', '--help']:
            with open(os.path.join(conf,"help.txt"),'r') as h:
                print(h.read())
            exit()
    
    if(DIST==""): 
        DIST="香港天文台"
        if (VERBOSE_FLAG): print("[WARN] district is not set, fallback to '香港天文台'")
    if(RAINFALL_DIST==""):
        RAINFALL_DIST="油尖旺"
        if (VERBOSE_FLAG): print("[WARN] rainfall district is not set, fallback to '油尖旺'")
    
    epd = epd4in2b_V2.EPD()
    wx = weather_info.WeatherInfo(dist=DIST,rainfall_dist=RAINFALL_DIST)
    crrt_wx=wx.rhrread_process(VERBOSE_FLAG and not MUTE_WXINFO_FLAG)
    forecast_wx=wx.fnd_process(VERBOSE_FLAG and not MUTE_WXINFO_FLAG)
    forecast_desc=wx.flw_process(VERBOSE_FLAG and not MUTE_WXINFO_FLAG)
    warnings=wx.warnsum_process(VERBOSE_FLAG and not MUTE_WXINFO_FLAG)

    try:
        # init
        if not (DRYRUN_FLAG):
            if (VERBOSE_FLAG): print("[INFO] Initializating...")
            epd.init()
            epd.Clear()
        img_Black = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the imgB, draw white
        img_RedYellow = Image.new('1', (epd.width, epd.height), 255)
        drawB = ImageDraw.Draw(img_Black)
        drawRY = ImageDraw.Draw(img_RedYellow)

        if (VERBOSE_FLAG): print("[INFO] Drawing frame...")
        drawB.line((0, 66, epd.width, 66), fill=0, width=3) # date
        drawB.line((110, 15, 110, 50), fill=0, width=3) # date, weekday vertical
        drawB.line((260, 0, 260, 66), fill=0, width=3) # date, main vertical
        drawB.line((260,32,epd.width,32), fill=0) # warn horizontal
        drawB.line((306,0,306,66), fill=0) # warn vertical
        drawB.line((352,0,352,66), fill=0) # warn vertical
        drawB.rounded_rectangle((1,70,196,235), outline=0, fill=255, width=2, radius=15) # current wx
        drawB.rounded_rectangle((203,70,398,235), outline=0, fill=255, width=2, radius=15) # forecast
        drawB.line((300, 70, 300, 235), fill=0, width=2) # forecast, vertical
        
        # date
        if (VERBOSE_FLAG): print("[INFO] Drawing date information...")
        draw_day(str(date.today().strftime("%Y%m%d")),drawB,drawRY)
        draw_week(today_week,drawB,drawRY)
        
        # warning sign
        if (VERBOSE_FLAG): print("[INFO] Drawing warning sign information...")
        
        position_count = 0
        for warning_name in warnings:
            if (position_count==6): break
            draw_warning_sign(warning_name,position_count,img_Black,img_RedYellow)
            position_count+=1


        # current weather
        if (VERBOSE_FLAG): print("[INFO] Drawing current weather information...")
        rhrread_logo = Image.open(os.path.join(picdir, str(crrt_wx["icon"])+".bmp"))
        rhrread_logo = rhrread_logo.resize(L_icon_size)
        img_Black.paste(rhrread_logo,(115,110))
        drawB.text((10,75),crrt_wx["district"], font=bfont24, fill=0)
        draw_temperature(crrt_wx["temperature"],drawB,drawRY)
        drawB.text((10,170),"濕度: " + str(crrt_wx["humanity"]) + "%", font=font24, fill=0)
        drawB.text((10,200),"雨量: " + str(crrt_wx["rainfall"]) + "mm", font=font24, fill=0)
        
        # forecast
        if (VERBOSE_FLAG): print("[INFO] Drawing forecast information...")
        drawB.text((217,75),"明天預報", font=font18, fill=0)
            # weather icon
        fnd_logo = Image.open(os.path.join(picdir, str(forecast_wx["0"]["icon"])) + ".bmp")
        fnd_logo = fnd_logo.resize(M_icon_size)
        img_Black.paste(fnd_logo,(220,105))
            # temp
        fnd_logo = Image.open(os.path.join(picdir, "thermometer.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        img_Black.paste(fnd_logo,(205,170))
        drawB.text((232,170),str(forecast_wx["0"]["temperatureMin"])+"-"+str(forecast_wx["0"]["temperatureMax"])+"°", font=font18, fill=0)
            # huma
        fnd_logo = Image.open(os.path.join(picdir, "rain-drop.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        img_Black.paste(fnd_logo,(205,200))
        drawB.text((232,200),str(forecast_wx["0"]["humanityMin"])+"-"+str(forecast_wx["0"]["humanityMax"])+"%", font=font18, fill=0)

        drawB.text((314,75),"後天預報", font=font18, fill=0)
            # weather icon
        fnd_logo = Image.open(os.path.join(picdir, str(forecast_wx["1"]["icon"])) + ".bmp")
        fnd_logo = fnd_logo.resize(M_icon_size)
        img_Black.paste(fnd_logo,(317,105))
            # temp
        fnd_logo = Image.open(os.path.join(picdir, "thermometer.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        img_Black.paste(fnd_logo,(302,170))
        drawB.text((329,170),str(forecast_wx["1"]["temperatureMin"])+"-"+str(forecast_wx["1"]["temperatureMax"])+"°", font=font18, fill=0)
            # huma
        fnd_logo = Image.open(os.path.join(picdir, "rain-drop.bmp"))
        fnd_logo = fnd_logo.resize(S_icon_size)
        img_Black.paste(fnd_logo,(302,200))
        drawB.text((329,200),str(forecast_wx["1"]["humanityMin"])+"-"+str(forecast_wx["1"]["humanityMax"])+"%", font=font18, fill=0)
        
        # forecast Description
        if (VERBOSE_FLAG): print("[INFO] Drawing forecast description...")
        draw_weather_descript(forecast_desc[FORECAST_TEXT],drawB,drawRY)
        
        # output
        if (IMAGEOUT_FLAG): 
            if (VERBOSE_FLAG): print("[INFO] Saving the e-paper display output to temp/...")
            img_Black.save(os.path.join(tmpdir,"black.bmp"))
            img_RedYellow.save(os.path.join(tmpdir,"red.bmp"))
        if (ROTATE_FLAG):
            if (VERBOSE_FLAG): print("[INFO] Rotating the e-paper display output by {0}",ROTATE_DEGREE)
            img_Black = img_Black.rotate(ROTATE_DEGREE)
            img_RedYellow = img_RedYellow.rotate(ROTATE_DEGREE)

        if (VERBOSE_FLAG): print("[INFO] Drawing to the e-paper display...")
        if not (DRYRUN_FLAG): epd.display(epd.getbuffer(img_Black), epd.getbuffer(img_RedYellow))     
        if (VERBOSE_FLAG): print("Done.")

    except IOError as e:
        logging.info(e)

    except getopt.GetoptError:
        pass
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd4in2b_V2.epdconfig.module_exit()
        exit()


if __name__=="__main__":
    main(sys.argv)