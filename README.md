# WiHKger-edp3in7-epd4in2b
### 透過 e-paper 屏幕顯示即時天氣資訊、未來天氣預測
- 適用於 Waveshare 3.7inch e-Paper HAT 及 Waveshare 4.2inch e-Paper Module (B)<br>
- A fork of https://github.com/JamesXtest/WiHKger-edp2in9_V2 

#### 3.7" e papaer display 預覽
![output](https://user-images.githubusercontent.com/71750702/156729070-ffcb76b7-8e9e-4fca-8dd1-915b5f5f45ae.jpg)

#### 4.2" e papaer display 預覽
![4 2_largefont](https://user-images.githubusercontent.com/71750702/156893165-f51af7d0-cd81-4ee8-b78b-67711ab1c5ce.jpg)
![4 2_midfont](https://user-images.githubusercontent.com/71750702/156893166-83ac87b7-dbca-45ad-a798-35cb30cd4578.jpg)
![4 2_smallfont](https://user-images.githubusercontent.com/71750702/156893167-d9533ca3-b9b5-432a-9b5f-eb6d9e0c779c.jpg)
![4 2_tempcolor](https://user-images.githubusercontent.com/71750702/156893168-fed5748d-bdc9-4730-acc8-3ba083b0e50e.jpg)

### 修改項目
- 天氣預測由顯示未來一天新增至兩天
- 新增顯示當天日期
- 支援從command line修改天氣資料地區，詳見 Usage
- 分離 HKO API return parsing 至獨立 module
- [！] 右上空位重未諗到放咩好

### 4.2" 三色 display 版本獨有功能
- 週未（六, 日）時，星期顯示為紅色（或黃色）
- 即時溫度
  - <13°：黑底白字
  - 13°<溫度<28°：黑字
  - <32°：紅/黃字
  - \>32°：紅/黃底白字
- 顯示天氣概況/天氣預測內容/天氣展望

# Usage
### Hardware Requirements
- 可以連接網絡及有GPIO插頭 raspberry pi
  - Arduino理論上都可以，但未測試過。另外亦須使用其他library，或須自行修改source code
- Waveshare 3.7" e papaer
### Dependency & Library
- Python (≥3.7)
- Pillow (pip)

(Required by Waveshare e-paper for RPi)<br>
- BCM2835 libraries,  wiringPi libraries, Python libraries 請參考 <br>
[3.7inch e-Paper HAT - Waveshare Wiki](https://www.waveshare.com/wiki/3.7inch_e-Paper_HAT)<br>
[4.2inch e-Paper Module (B) - Waveshare Wiki](https://www.waveshare.com/wiki/4.2inch_e-Paper_Module_(B))

注：WiringPi 官方已停止更新，須使用第三方開發嘅 [WiringPi fork](https://github.com/WiringPi/WiringPi)
```
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
tar zxvf bcm2835-1.60.tar.gz 
cd bcm2835-1.60/
sudo ./configure
sudo make
sudo make check
sudo make install
```
```
sudo apt-get install wiringpi
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
```
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
sudo pip3 install Pillow
python3 -m pip install pillow --upgrade
```
### 執行/使用
#### 下載
```wget -c https://github.com/SuperDumbTM/WiHKger-edp3in7-epd4in2b/archive/refs/tags/latest.tar.gz -O - | sudo tar -xz```<br>
或<br>
```wget -c https://github.com/SuperDumbTM/WiHKger-edp3in7-epd4in2b/archive/refs/tags/<specific version>.tar.gz -O - | sudo tar -xz```<br>

#### 執行
測試 e-paper : ```python3 epd_3in7_test.py```<br>
主程式 : ```python3 main.py [-flags]```<br>

如未能成功執行，請嘗試安裝 libopenjp2-7 library
```sudo apt-get install libopenjp2-7```

#### 排程執行
- crontab
1. 修改 ```epd3in7_refresh / epd4in2b_V2_refresh``` 內嘅 ```dist="<天氣資料地區>", rain="<雨量資料地區>"```
3. 修改程式檔案位置至 ```cd <path to program directory>```
4. 按需要增減flag至 ```python3 main.py -d $dist -r $rain <flags>```
5. 新增crontab：在terminal執行 ```crontab -e```
> <b>Example</b><br>
> 每半小時更新一次 ```*/30 * * * *  <path to epd3in7_refresh directory>/epd3in7_refresh```<br>
> 每一小時更新一次 ```0 */1 * * *  <path to epd3in7_refresh directory>/epd3in7_refresh```

#### Flags
  1. 設定天氣資料地區（預設：香港天文台）<br>
      ```-d/--district <地區>```
  2. 設定雨量資料地區（預設：觀塘）<br>
      ```-r/--rainfall-district <地區>```
  3. 反轉屏幕輸出<br>
      ```-R/--rotate-display <角度>```
  4. 詳細模式（輸出運行資料至 terminal）<br>
      ```-v/--verbose```
  5. 儲存屏幕輸出至/temp資料夾<br>
      ```-i/--image-save```
  6. 只執行程式，唔更新 e-paper display<br>
      呢個 flag 會自動設定埋```-v -i```<br>
      ```--dry-run```
  7. 設定天氣預報文字類型 (只適用於 4.2")<br>
      generalSituation（天氣概況，預設）,forecastDesc（天氣預測內容）,outlook（天氣展望）<br>
      ```-f/--forecast-text-type```
