# WiHKger-edp3in7 

A fork of https://github.com/JamesXtest/WiHKger-edp2in9_V2 （適用於 Waveshare 3.7" e papaer）

透過 e-paper 屏幕顯示即時天氣資訊、未來天氣預測

![output](https://user-images.githubusercontent.com/71750702/156729070-ffcb76b7-8e9e-4fca-8dd1-915b5f5f45ae.jpg)

### 修改項目
- 天氣預測由顯示未來一天新增至兩天
- 新增顯示當天日期
- 支援從command line修改天氣資料地區，詳見 Usage
- 分離 HKO API return parsing 至獨立 module
- [！] 左上空位重未諗到放咩好

# Usage
### Dependency & Library required
- Python (≥3.7)
- Pillow (pip)

(Required by Waveshare e-paper for RPi - [3.7inch e-Paper HAT - Waveshare Wiki](https://www.waveshare.com/wiki/3.7inch_e-Paper_HAT))<br>
- python3-pil
- python3-numpy
- RPi.GPIO (pip)
- spidev (pip)
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
sudo pip3 install Pillow
```
### 執行/使用
測試 e-paper: ```python3 epd_3in7_test.py```<br>

主程式: ```python3 main.py [-flags]```<br>

#### 排程執行
- crontab
1. 修改 ```epd3in7_refresh``` 內嘅 ```dist="<天氣資料地區>", rain="<雨量資料地區>"```
3. 修改程式檔案位置至 ```cd <path to program directory>```
4. 按需要增減flag至 ```python3 main.py -d $dist -r $rain <flags>```
5. 新增crontab：在terminal執行 ```crontab -e```
> <b>Example</b><br>
> 每半小時更新一次 ```*/30 * * * *  <path to epd3in7_refresh directory>/epd3in7_refresh```<br>
> 每一小時更新一次 ```0 */1 * * *  <path to epd3in7_refresh directory>/epd3in7_refresh```

#### Flags
  1. 設定天氣資料地區（預設：香港天文台）<br>
      ```-d/--district <地區>```
  3. 設定雨量資料地區（預設：觀塘）<br>
      ```-r/--rainfall-district <地區>```
  5. 反轉屏幕輸出（180度）<br>
      ```-R/--rotate-display```
  7. 詳細模式（輸出運行資料至 terminal）<br>
      ```-v/--verbose```
  9. 儲存屏幕輸出至/temp資料夾<br>
      ```-i/--image-save```
