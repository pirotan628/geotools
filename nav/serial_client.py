import socket
import serial
import pyproj
import micropyGPS
import threading
import time

grs80 = pyproj.Geod(ellps='GRS80')  # GRS80楕円体
gps = micropyGPS.MicropyGPS(9, 'dd') # JST

# UDP (forward to)
HOST = ''
PORT = 50001
ADDRESS = "127.0.0.1"
skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Serial (source)
dev = '/dev/tty.usbserial'  # MacOS
#dev = '/dev/ttyUSB0'        # Linux
brate = 4800                # borate for BU-353S4 Module


def get_param():
    try:
       reffile = 'param.txt'
       f = open(reffile)
       lines = f.read()
       f.close()

       line = lines.split('\n')
       coord = line[0].split(',')
       #lon_ref, lat_ref = 135.292489, 34.717932  # 深江
       lon, lat = float(coord[0]), float(coord[1])

       #declination = -7.5
       dec = float(line[1])
    except:
       lon,lat,dec = 0, 0, 0
    return lon, lat, dec

def put_info(line):
#    try:
       inffile = 'info.txt'
       f = open(inffile, mode='w')
       for i in range(len(line)):
          f.write(line[i])
          f.write('\n')
       f.close
#    except:
#        return 1
       return 0

def rungps(): # GPSモジュールを読み、GPSオブジェクトを更新する
    ser = serial.Serial(dev, brate, timeout=10)    
    ser.readline() # 最初の1行は中途半端なデーターが読めることがあるので、捨てる
    while True:
        response = ser.readline()
        skt.sendto(response, (ADDRESS, PORT))
        sentence = response.decode('utf-8')
        print(sentence.strip())   

        if sentence[0] != '$': # 先頭が'$'でなければ捨てる
            continue
        for x in sentence: # 読んだ文字列を解析してGPSオブジェクトにデーターを追加、更新する
            gps.update(x)

gpsthread = threading.Thread(target=rungps, args=()) # 上の関数を実行するスレッドを生成
gpsthread.daemon = True
gpsthread.start() # スレッドを起動


while True:
    lon_ref, lat_ref, declination = get_param()
    if gps.clean_sentences > 20: # Wait for enough data
        h = gps.timestamp[0] if gps.timestamp[0] < 24 else gps.timestamp[0] - 24
        year, month, day = gps.date[2], gps.date[1], gps.date[0]
        hour, minute, seconds = h, gps.timestamp[1], gps.timestamp[2]
        lon_now, lat_now = gps.longitude[0], gps.latitude[0]

        azimuth, bkw_azimuth, distance = grs80.inv(lon_now, lat_now, lon_ref, lat_ref)
        azm_mag, bkw_azm_mag = azimuth - declination, bkw_azimuth + declination
        nauticalmile = distance / 1852

#        print('\033[31m',end="")        
        print('* 20%02d/%02d/%02d %2d:%02d:%04.1f' % (year, month, day, hour, minute, seconds))
        print('* %2.8f, %2.8f' % (lat_now, lon_now))
        print('* %03.2f, %03.2f, %.2f, %.2f' % (azimuth, bkw_azimuth, distance, nauticalmile))
        print('* %03.2f, %03.2f' % (azm_mag, bkw_azm_mag), end="")
#        print('\033[0m')
        
        line=[]
        line.append("20{0:02d}/{1:02d}/{2:02d} {3:02d}:{4:02d}:{5:04.1f}".format(year, month, day, hour, minute, seconds))
        line.append("{0:2.8f}, {1:2.8f}".format(lat_now, lon_now))
        line.append("{0:03.2f}, {1:03.2f}, {2:.2f}, {3:.2f}".format(azimuth, bkw_azimuth, distance, nauticalmile))
        line.append("{0:03.2f}, {1:03.2f}".format(azm_mag, bkw_azm_mag))
        dummy = put_info(line)

    #time.sleep(1.0)
