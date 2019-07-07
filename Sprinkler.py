__author__ = 'Dave Spicer'
import Adafruit_CharLCDPlate as LCD
import datetime
import time
import mysql.connector
import os
import socket
import smtplib
import smbus

class Sprinklers:
    def __init__(self):
        self.SetupMCP23017()
        self.pinAllOff()
        self.GetUser()
        self.Configuration()
        self.CharLCDPlate()
        self.LCD.clear()
        self.PITime()
        self.LCD.clear()
        self.SystemInformation()
        self.PISleep5()
        self.LCD.clear()
        self.LCD.message('Program Starting\nPlease Wait')
        self.PISleep5()
        self.LCD.clear()
        self.LCD.message('Checking Weather\nConditions')
        self.Weather()
        self.LCD.clear()
        self.LCD.message('Loading Program\nParameters')
        self.SprinklerParameters()
        self.SprinklerProgram()
        self.PISleep5()
        self.LCD.clear()
        self.LCD_Clock()
        self.IP()
        self.ProgramEnableDisable()
    def CharLCDPlate(self):
        self.LCD = LCD.Adafruit_CharLCDPlate()
        self.LCD.begin(16, 2)
    def LCD_Clock(self):
        self.LCD.home()
        self.LCD.message(datetime.datetime.now().strftime('%b %d %H:%M:%S'))
    def PITime(self):
        self.CurrentDateIntVersion = datetime.date.today()
        self.CurrentSystemTime = datetime.datetime.now()
        self.CurrentTimeHour = self.CurrentSystemTime.hour
        self.CurrentTimeMinute = self.CurrentSystemTime.minute
        self.CurrentTimeSecond = self.CurrentSystemTime.second
        self.CurrentSystemDate = self.CurrentSystemTime.date()
        self.CurrentMonth = self.CurrentSystemTime.strftime('%m')
        self.CurrentMonthIntVersion = self.CurrentDateIntVersion.month
        self.CurrentDay = self.CurrentSystemTime.strftime('%d')
        self.CurrentDayIntVersion = self.CurrentDateIntVersion.day
        self.CurrentYear = self.CurrentSystemTime.strftime('%y')
        self.CurrentYearIntVersion = self.CurrentDateIntVersion.year
        self.WorkableTime = self.CurrentTimeHour, self.CurrentTimeMinute
        Day = self.CurrentSystemTime.today().weekday()
        if Day == 0:
            self.Day = 'Monday'
        if Day == 1:
            self.Day = 'Tuesday'
        if Day == 2:
            self.Day = 'Wednesday'
        if Day == 3:
            self.Day = 'Thursday'
        if Day == 4:
            self.Day = 'Friday'
        if Day == 5:
            self.Day = 'Saturday'
        if Day == 6:
            self.Day = 'Sunday'
    def Weather(self):
        self.LCD.backlight(self.LCD.TEAL)
        self.LCD.clear()
        self.WeatherDatabaseRead_Rain()
        self.WeatherDatabaseRead()
        self.WeatherDisplay()
    def WeatherDisplay(self):
        self.LCD.message('Current Weather\nConditions')
        self.PISleep5()
        self.LCD.clear()
        ReadableTime = datetime.datetime.fromtimestamp(self.Epoch).strftime('%m-%d-%Y %H:%M:%S')
        self.LCD.message('Last Observation\n%s' % (ReadableTime))
        self.PISleep5()
        self.LCD.clear()
        self.LCD.message('Current Temp:\n%s' % (self.Temp_f))
        self.PISleep5()
        self.LCD.clear()
        self.LCD.message('Recorded Rain:\n%s inches' % (self.Rain))
        self.PISleep5()
        self.LCD.clear()
    def WeatherDatabaseRead(self):
        self.MySQL_Connection_Weather()
        weather = []
        self.cur = self.sql.cursor()
        self.cur.execute("Select * FROM archive ORDER BY dateTime DESC LIMIT 1")
        results = str(self.cur.fetchone())
        test = results.split(',')
        for row in test:
            row = row.lstrip()
            if row[0] == '(':
                weather.append(row[1::])
            else:
                weather.append(row)
        lastOld = weather[51]
        weather[51] = lastOld[:-1]
        self.cur.close()
        self.Epoch = int(weather[0])
        self.Temp_f = float(weather[7])
        if self.Temp_f == 'None':
            self.LogEvent = 'No Temp'
            self.Log()
    def WeatherDatabaseRead_Rain(self):
        self.MySQL_Connection_Weather()
        RainDB = []
        self.cur = self.sql.cursor()
        self.cur.execute("Select * FROM archive_day_rain ORDER BY dateTime DESC LIMIT 1")
        results1 = str(self.cur.fetchone())
        test1 = results1.split(',')
        for row in test1:
            row = row.lstrip('(')
            if row[0] == '(':
                RainDB.append(row[1::])
            else:
                RainDB.append(row)
        Rain = RainDB[5]
        self.Rain = float(Rain[1:6])
        self.RainTime = int(RainDB[0])
    def MySQL_Connection_Sprinkler(self):
        self.CheckNetwork()
        self.sql = mysql.connector.connect(host='mysql.spicertech.info', user='sprinkler',
                              password='sprinkler', database='Sprinkler_V3')
        return
    def MySQL_Connection_Weather(self):
        self.CheckNetwork()
        self.sql = mysql.connector.connect(host='mysql.spicertech.info', user='weewx',
                               password='weewx', database='weewx')
        return
    def SprinklerParameters(self):
        round = 1
        self.MySQL_Connection_Sprinkler()
        self.Parameters = []
        self.cur = self.sql.cursor()
        self.cur.execute("Select * FROM Parameters")
        results = self.cur.fetchall()
        self.cur.close()
        for row in results:
            self.Parameters.append(row[0])
            self.Parameters.append(row[1])
            self.Parameters.append(row[2])
            self.Parameters.append(row[3])
            self.Parameters.append(row[4])
            self.Parameters.append(row[5])
            self.Parameters.append(row[6])
            self.Parameters.append(row[7])
            self.Parameters.append(row[8])
            self.Parameters.append(row[9])
            self.Parameters.append(row[10])
            self.Parameters.append(row[11])
            self.Parameters.append(row[12])
            self.Parameters.append(row[13])
            self.Parameters.append(row[14])
            self.Parameters.append(row[15])
            self.Parameters.append(row[16])
            self.Parameters.append(row[17])
            self.Parameters.append(row[18])
            self.Parameters.append(row[19])
            self.Parameters.append(row[20])
            self.Parameters.append(row[21])
            self.Parameters.append(row[22])
            self.Parameters.append(row[23])
            self.Parameters.append(row[24])
            self.Parameters.append(row[25])
            self.Parameters.append(row[26])
            self.Parameters.append(row[27])
            self.Parameters.append(row[28])
            self.Parameters.append(row[29])
            self.Parameters.append(row[30])
            self.Parameters.append(row[31])
    def SprinklerProgram(self): # Fix the list
        round = 1
        self.MySQL_Connection_Sprinkler()
        self.Program = []
        self.cur = self.sql.cursor()
        self.cur.execute("Select * FROM Program ORDER BY Enabled DESC LIMIT 1")
        results = self.cur.fetchall()
        self.cur.close()
        for row in results:
            self.Program.append(row[0])
            self.Program.append(row[1])
            self.Program.append(row[2])
            self.Program.append(row[3])
            self.Program.append(row[4])
            self.Program.append(row[5])
            self.Program.append(row[6])
            self.Program.append(row[7])
            self.Program.append(row[8])
            self.Program.append(row[9])
            self.Program.append(row[10])
            self.Program.append(row[11])
            self.Program.append(row[12])
            self.Program.append(row[13])
            self.Program.append(row[14])
            self.Program.append(row[15])
            self.Program.append(row[16])
            self.Program.append(row[17])
            self.Program.append(row[18])
            self.Program.append(row[19])
            self.Program.append(row[20])
            self.Program.append(row[21])
            self.Program.append(row[22])
            self.Program.append(row[23])
            self.Program.append(row[24])
            self.Program.append(row[25])
            self.Program.append(row[26])
            self.Program.append(row[27])
        if self.Program == []:
            self.LogEvent = 'All'
            self.Log()
            self.Enabled = 'Disabled'
            self.StartTimeHR = 0
            self.StartTimeMin = 0
            while round <= 240:
                round += 1
                self.LCD.backlight(self.LCD.VIOLET)
                self.LCD_Clock()
                self.IP()
                self.PISleep1()
            self.PITime()
            self.Weather()
            self.ProgramEnableDisable()
            self.PISleep5()
            self.LCD.clear()
    def SystemInformation(self):
        self.LCD.clear()
        wifisSSID = ("iwconfig wlan0 | grep 'ESSID:' | awk '{print $4}' | sed 's/ESSID://g'")
        SSID = (os.popen(wifisSSID).read())
        if SSID == '':
            SSID = "LAN"
        self.LCD.message('Connected to:\n%s' % (SSID))
        self.PISleep5()
        self.clearLCDLeft()
        self.LCD.clear()
        if SSID != "LAN":
            wifistrength = ("iwconfig wlan0 | awk -F'[ =]+' '/Signal level/ {print $7}' | cut -d/ -f1")
            strength = (os.popen(wifistrength).read())
            if strength == '':
                strength = "NO WiFi Signal"
            self.LCD.message('WiFi Signal:\n%s' % (strength))
            self.PISleep5()
        self.clearLCDRight()
        self.LCD.clear()
        self.CheckNetwork()
        self.LCD.message('Internet is:\n%s' % (self.CNET))
        self.PISleep5()
        if self.CNET == "ERROR\n":
            self.LCD.clear()
            self.LCD.message('System is\nRebooting')
            self.PISleep5()
            self.LCD.clear()
            os.system("sudo reboot")
    def clearLCDRight(self):
        j=0
        while (j < 16):
            self.LCD.scrollDisplayRight()
            time.sleep(.03)
            j += 1
    def clearLCDLeft(self):
        j=0
        while (j < 16):
            self.LCD.scrollDisplayLeft()
            time.sleep(.03)
            j += 1
    def IP(self):
        self.CheckNetwork()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        self.LCD.setCursor(0, 1)
        self.LCD.message('IP:%s' % (s.getsockname()[0]))
    def ProgramEnableDisable(self):
        self.StartTime = self.Program[2], self.Program[3]
        round = 1
        while self.Program[0] == 'Disabled':
            self.LCD.backlight(self.LCD.VIOLET)
            if round == 1:
                round += 1
            self.PISleep()
            self.MySQL_Connection_Sprinkler()
            self.SprinklerProgram()
            self.LCD_Clock()
            self.IP()
        round = 1
        while self.Program[0] == 'Enabled':
            self.LCD.backlight(self.LCD.YELLOW)
            if round == 1:
                round += 1
            self.PISleep()
            self.MySQL_Connection_Sprinkler()
            self.SprinklerProgram()
            self.LCD_Clock()
            self.IP()
            self.WaitForStartTime()
    def WaitForStartTime(self):
        self.PITime()
        round = 1
        if round == 1:
            self.LogEvent = 'Wait'
            self.Log()
        self.CheckDayofWeektoRun()
        if self.Go == True:
            while self.StartTime != self.WorkableTime:
                LoopTime = self.CurrentTimeMinute + 3
                if LoopTime >= 60:
                    LoopTime = self.CurrentTimeMinute + 4
                if self.CurrentMonthIntVersion >= 9 and self.CurrentDayIntVersion >= 25:
                    self.LogEvent = 'Winterize'
                    self.Log()
                if self.Temp_f <= 40:
                    self.LogEvent = 'Temp'
                    self.Log()
                    self.CountDown()
                if self.Rain >= 0.10:
                    self.LogEvent = 'Rain'
                    self.CountDown()
                while self.CurrentTimeMinute != LoopTime:
                    if self.StartTime == self.WorkableTime:
                        self.RunZones()
                    self.LCD.backlight(self.LCD.YELLOW)
                    round += 1
                    self.PITime()
                    self.MySQL_Connection_Sprinkler()
                    self.SprinklerProgram()
                    self.LCD_Clock()
                    self.IP()
                    self.PITime()
                    self.PISleep()
                    self.StartTime = self.Program[2], self.Program[3]
                round = 1
                self.Weather()
                self.LCD.clear()
            self.RunZones()
        if self.Go == False:
            self.PISleep60()
            self.__init__()
    def UpdateZoneLog(self, Zone):
        FormatDate = str(self.CurrentDateIntVersion.year) + '-' + str(self.CurrentDateIntVersion.month) + '-' + str(self.CurrentDateIntVersion.day)
        #FormatDate = str(self.CurrentYear) + '-' + str(self.CurrentMonth) + '-' + str(self.CurrentDay)
        FormatTime = str(self.CurrentTimeHour) + ':' + str(self.CurrentTimeMinute) + ':' + str(self.CurrentTimeSecond)
        self.MySQL_Connection_Sprinkler()
        ZoneLog = []
        self.cur = self.sql.cursor()
        ZoneLog.append(Zone)
        ZoneLog.append(self.status)
        ZoneLog.append(FormatDate)
        ZoneLog.append(FormatTime)
        Zone = ZoneLog[0]
        Status = ZoneLog[1]
        SDate = ZoneLog[2]
        STime = ZoneLog[3]
        self.cur.execute(("INSERT INTO `Sprinkler_log` (`Zone`, `Status`,`Date`,`Time`) "
                          "VALUES ('%s', '%s', '%s', '%s')" % (Zone, Status, SDate, STime)))
        self.sql.commit()
        self.cur.close()
    def CheckNetwork(self):
        checknet = ("ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && echo OK || echo ERROR")
        self.CNET = (os.popen(checknet).read())
        if self.CNET == "ERROR\n":
            self.LCD.clear()
            self.LCD.message('System is\nRebooting')
            self.PISleep5()
            self.LCD.clear()
            os.system("sudo reboot")
    def CountDown(self):
        self.Log()
        self.PITime()
        self.LCD.clear()
        self.LCD.backlight(self.LCD.WHITE)
        if self.Rain >= .50:
            WaitHR = 48 - self.CurrentTimeHour
            WaitMin = 59 - self.CurrentTimeMinute
        else:
            WaitHR = 23 - self.CurrentTimeHour
            WaitMin = 59 - self.CurrentTimeMinute
        while self.CurrentTimeHour != WaitHR:
            while self.CurrentTimeMinute != WaitMin:
                round = 1
                if self.Rain >= .50:
                    WaitHR = 48 - self.CurrentTimeHour
                    WaitMin = 59 - self.CurrentTimeMinute
                else:
                    WaitHR = 23 - self.CurrentTimeHour
                    WaitMin = 59 - self.CurrentTimeMinute
                timeformat = '{:02d}:{:02d}'.format(WaitHR, WaitMin)
                self.LCD.clear()
                self.LCD.setCursor(3, 0)
                self.LCD.message(('%s Sleep') % (self.LogEvent))
                self.LCD.setCursor(5, 1)
                self.LCD.message('%s' % (timeformat))
                self.PISleep1()
                self.PITime()
                while round <= 350:
                    round += 1
                    self.LCD.setCursor(5, 1)
                    self.LCD.message('%s' % (timeformat))
                    self.PITime()
                    self.PISleep()
                self.Weather()
            self.PISleep60()
            self.PITime()
        self.LogEvent = 'Resume'
        self.Log()
    def CountDownRunningLessthanHR(self, ZoneRunTime):
        self.LCD.clear()
        round = 1
        self.LCD.setCursor(0,0)
        self.LCD.message('Remain Run Time')
        while round <= 15:
            round += 1
            WaitMin = ZoneRunTime - self.CurrentTimeMinute
            timeformat = '{:02d}'.format(WaitMin)
            self.LCD.setCursor(5, 1)
            self.LCD.message((':%s min') % (timeformat))
            self.PISleep1()
            self.PITime()
        self.CheckRemainTime = self.CurrentTimeMinute + 3
    def CountDownRunningGreaterthanHR(self, RunTime): # Check this method runs correctly
        self.LCD.clear()
        round = 1
        self.LCD.setCursor(0,0)
        self.LCD.message('Remain Run Time')
        while round <= 15:
            round += 1
            WaitMin = RunTime - self.CurrentTimeMinute
            timeformat = '{:02d}'.format(WaitMin)
            self.LCD.setCursor(5, 1)
            self.LCD.message((':%s min') % (timeformat))
            self.PISleep1()
            self.PITime()
        self.CheckRemainTime = self.CurrentTimeMinute + 3
    def Log(self):
        timeformat = '{:02d}:{:02d}'.format(self.CurrentTimeHour, self.CurrentTimeMinute)
        self.MySQL_Connection_Sprinkler()
        self.cur = self.sql.cursor()
        if self.LogEvent == 'Rain':
            Subject = 'Rain Detected at'
            sendEmail = self.SendEmailRain
            self.LogDescription = 'Rain Detected. Waiting for New Day to Start'
        if self.LogEvent == 'Wait':
            Subject = 'Waiting to Start at'
            sendEmail = self.SendEmailWait
            self.LogDescription = 'Program is waiting to start the sprinkler System'
        if self.LogEvent == 'Resume':
            Subject = 'Everything good at'
            sendEmail = self.SendEmailResume
            self.LogDescription = 'Resuming normal operation'
        if self.LogEvent == 'All':
            Subject = 'Program Disbaled at'
            sendEmail = self.SendEmailAll
            self.LogDescription = 'All programs are disabled. Please enable to continue'
        if self.LogEvent == 'Temp':
            Subject = 'Temperature Vioaltion Detected at'
            sendEmail = self.SendEmailTemp
            self.LogDescription = 'Temperature is below desired range to run sprinklers'
        if self.LogEvent == 'Winterize':
            Subject = 'Time to winterized'
            sendEmail = self.SendEmailWinterize
            self.LogDescription = 'Based on date you provided, It is time to winterize the sprinkler system'
        if self.LogEvent == 'No Temp':
            Subject = 'No Temperature Reporting'
            sendEmail = self.SendEmailNoTemp
            self.LogDescription = 'No Temperature Reporting from Weather Station'
        if self.LogEvent == 'Run':
            Subject = 'Sprinkler System has begun at'
            sendEmail = self.SendEmailRun
            self.LogDescription = 'Sprinkler System has begun to run the Zones'
        if self.LogEvent == 'Done':
            Subject = 'Finished at'
            sendEmail = self.SendEmailDone
            self.LogDescription = 'All Zones have finished running.'
        if self.LogEvent == 'Check':
            Subject = 'Program needs checked'
            sendEmail == 'Yes'
            self.LogDescription = 'Program match the criteria and needs to be check.'
        self.cur.execute(("INSERT INTO `Log` (Date, Time, Event, Description) VALUES ('%s', '%s', '%s', '%s')"
                          % (self.CurrentDateIntVersion, timeformat, self.LogEvent, self.LogDescription)))
        self.sql.commit()
        self.sql.close()
        if sendEmail == 'Yes':
            self.sendEmail(timeformat, Subject)
    def sendEmail(self, timeformat, Subject):
            sendto = self.EmailAddy
            user = self.SMTP_User
            password = self.SMTP_Password
            smtpsrv = self.SMTP_Server
            smtpserver = smtplib.SMTP(smtpsrv, self.SMTP_Port)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo()
            smtpserver.login(user, password)
            header = 'To:' + sendto + '\n' + 'From: ' + user + '\n' + 'Subject:' + Subject + ' ' + timeformat + '\n'
            msgbody = header + '\nDate: ' + str(self.CurrentDateIntVersion) + '\nTime: ' + timeformat + '\nEvent: ' + self.LogEvent + '\nDescription: ' + self.LogDescription
            smtpserver.sendmail(user, sendto, msgbody)
            smtpserver.close()
    def GetUser(self):  ##Good to Go
        self.MySQL_Connection_Sprinkler()
        user = []
        self.cur = self.sql.cursor()
        self.cur.execute("Select * FROM User_Database")
        results = self.cur.fetchall()
        self.cur.close()
        for row in results:
            user.append(row[0])
            user.append(row[1])
            user.append(row[2])
            user.append(row[3])
            user.append(row[4])
            user.append(row[5])
            user.append(row[6])
            user.append(row[7])
            user.append(row[8])
            user.append(row[9])
            user.append(row[10])
            user.append(row[11])
            user.append(row[12])
            user.append(row[13])
        self.username = user[0]
        self.FirstName = user[1]
        self.LastName = user[2]
        self.Password = user[3]
        self.EmailAddy = user[4]
        self.SendEmailRain = user[5]
        self.SendEmailWait = user[6]
        self.SendEmailResume = user[7]
        self.SendEmailAll = user[8]
        self.SendEmailTemp = user[9]
        self.SendEmailWinterize = user[10]
        self.SendEmailNoTemp = user[11]
        self.SendEmailRun = user[12]
        self.SendEmailDone = user[13]
    def Configuration(self):
        self.MySQL_Connection_Sprinkler()
        Config = []
        self.cur = self.sql.cursor()
        self.cur.execute("Select * FROM Configuration")
        results = self.cur.fetchall()
        self.cur.close()
        for row in results:
            Config.append(row[0])
            Config.append(row[1])
            Config.append(row[2])
            Config.append(row[3])
        self.SMTP_Server = Config[0]
        self.SMTP_Port = Config[1]
        self.SMTP_User = Config[2]
        self.SMTP_Password = Config[3]
    def PISleep(self):
        time.sleep(100.0 / 1000.0)
    def PISleep1(self):
        time.sleep(1)
    def PISleep2(self):
        time.sleep(2)
    def PISleep5(self):
        time.sleep(5)
    def PISleep60(self):
        time.sleep(60)
    def SetupMCP23017(self):
        global valueA
        global valueB
        valueA = 0xff
        valueB = 0xff
        self.ADDR = 0x21
        IODIRA = 0x00
        IODIRB = 0x01
        GPIOA = 0x12
        GPIOB = 0x13
        self.OLATA = 0x14
        self.OLATB = 0x15
        self.bus = smbus.SMBus(1)
        self.bus.write_byte_data(self.ADDR, self.OLATA, valueA)
        self.bus.write_byte_data(self.ADDR, self.OLATB, valueA)
        self.bus.write_byte_data(self.ADDR, IODIRA, 0x00)
        self.bus.write_byte_data(self.ADDR, IODIRB, 0x00)
    def pinOn(self, bank, pin, Zone):
        global valueA
        global valueB
        bit = pin - 1
        if bank == 'A':
            valueA = valueA & (0xff - (1 << bit))
            self.bus.write_byte_data(self.ADDR, self.OLATA, valueA)
        if bank == 'B':
            valueB = valueB & (0xff - (1 << bit))
            self.bus.write_byte_data(self.ADDR, self.OLATB, valueB)
        if bank == 'A' or bank == 'B':
            self.LCD.clear()
            self.LCD.backlight(self.LCD.GREEN)
            self.LCD_Clock()
            self.LCD.setCursor(0, 1)
            self.LCD.message('Zone %s Running.' % (Zone))
            self.status = 'Running...'
            self.UpdateZoneLog(Zone)
            self.PISleep5()
    def pinOff(self, bank, pin, Zone):
        global valueA
        global valueB
        bit = pin - 1
        if bank == 'A':
            valueA = valueA | (1 << bit)
            self.bus.write_byte_data(self.ADDR, self.OLATA, valueA)
        if bank == 'B':
            valueB = valueB | (1 << bit)
            self.bus.write_byte_data(self.ADDR, self.OLATB, valueB)
        if bank == 'A' or bank == 'B':
            self.LCD.clear()
            self.LCD.backlight(self.LCD.RED)
            self.LCD_Clock()
            self.LCD.setCursor(0,1)
            self.LCD.message('Zone %s Shutdown.' % (Zone))
            self.status = 'Shutdown...'
            self.UpdateZoneLog(Zone)
            self.PISleep5()
            self.RestBetweenZones(Zone)
    def pinStatus(self, bank, pin, Zone):
        global valueA
        global valueB
        bit = pin - 1
        if bank == 'A' or bank == 'a':
            state = ((valueA & (1 << bit)) != 1)
        else:
            state = ((valueB & (1 << bit)) != 1)
        self.CheckZoneisRunning(state, bank, pin, Zone)
        return state
    def pinAllOff(self):
        global valueA
        global valueB
        valueA = 0xff
        self.bus.write_byte_data(self.ADDR, self.OLATA, valueA)
        valueB = 0xff
        self.bus.write_byte_data(self.ADDR, self.OLATB, valueB)
    def RunZones(self):
        self.CheckRemainTime = self.CurrentTimeMinute + 3
        self.LogEvent = 'Run'
        self.Log()
        Zone = 1; round = 1; t = 12; p = 0
        for p in range(16):
            GPIOPin = self.Parameters[p]
            if self.Program[t] is None:
                self.status = 'Run Time set to Null in Database. Restarting Program'
                self.UpdateZoneLog(Zone)
                self.PISleep60()
                self.__init__()
            ZoneRunTime = self.CurrentTimeMinute + self.Program[t]
            if self.Program[t] == 0:
                self.status = 'Zero Run Time in Database'
                self.UpdateZoneLog(Zone)
                self.PISleep60()
                self.__init__()
            if ZoneRunTime < 60:
                if 0 <= p <= 7:
                    Bank = 'A'
                if 8 <= p <= 15:
                    Bank = 'B'
                    GPIOPin = self.Parameters[p] - 8
                while self.CurrentTimeMinute < ZoneRunTime:
                    self.LCD_Clock()
                    if self.CheckRemainTime == self.CurrentTimeMinute:
                        self.CountDownRunningLessthanHR(ZoneRunTime)
                        self.LCD.clear()
                        self.LCD_Clock()
                        self.LCD.setCursor(0, 1)
                        self.LCD.message('Zone %s Running.' % (Zone))
                    if round == 1:
                        self.pinOn(Bank, GPIOPin, Zone)
                        self.pinStatus(Bank, GPIOPin, Zone)
                        round += 1
                    self.PITime()
                    self.PISleep()
            if ZoneRunTime >= 60:
                RunTime = ZoneRunTime - 60
                ZoneEndTime = self.CurrentTimeHour + 1, RunTime
                if self.CurrentTimeHour + 1 >= 24:
                    ZoneEndTime = 0, RunTime
                    #print(ZoneEndTime)
                if 0 <= p <= 7:
                    Bank = 'A'
                if 8 <= p <= 15:
                    Bank = 'B'
                    GPIOPin = self.Parameters[p] - 8
                while self.WorkableTime < ZoneEndTime:
                    self.LCD_Clock()
                    if self.CheckRemainTime == self.CurrentTimeMinute: # Check to make sure that this works
                        self.CountDownRunningLessthanHR(RunTime)
                        self.LCD.clear()
                        self.LCD_Clock()
                        self.LCD.setCursor(0, 1)
                        self.LCD.message('Zone %s Running.' % (Zone))
                    if round == 1:
                        self.pinOn(Bank, GPIOPin, Zone)
                        self.pinStatus(Bank,GPIOPin,Zone)
                        round += 1
                    self.PITime()
                    self.PISleep()
            self.pinOff(Bank, GPIOPin, Zone)
            Zone += 1; round = 1; t += 1; p += 1
        self.LCD.clear()
        self.status = 'Finished...'
        self.UpdateZoneLog(Zone)
        self.LogEvent = 'Done'
        self.Log()
        self.LogEvent = 'Wait'
        self.Log()
    def CheckZoneisRunning(self, state, bank, pin, Zone):
        if state == False:
            self.pinOn(self,bank, pin, Zone)
    def RestBetweenZones(self, Zone):
        round = 1
        rest = self.CurrentTimeMinute + self.Program[4]
        RestEndTime = self.CurrentTimeHour, rest
        self.LCD.clear()
        self.LCD.backlight(self.LCD.VIOLET)
        self.LCD_Clock()
        self.LCD.setCursor(0,1)
        self.LCD.message('Zone %s Sleeping.' % Zone)
        self.status = 'Sleeping...'
        self.UpdateZoneLog(Zone)
        while self.WorkableTime < RestEndTime:
            if rest == 60:
                rest = 0
                RestEndTime = self.CurrentTimeHour + 1, rest
            if self.CurrentTimeHour == 24:
                self.CurrentTimeHour = 0
                self.PISleep60()
            self.PITime()
            self.LCD_Clock()
            self.PISleep()
    def CheckDayofWeektoRun(self):
        if self.Day == 'Monday' and self.Program[6] == 'Yes':
            self.Go = True
            return
        elif self.Day == 'Tuesday' and self.Program[7] == 'Yes':
            self.Go = True
            return
        elif self.Day == 'Wednesday' and self.Program[8] == 'Yes':
            self.Go = True
            return
        elif self.Day == 'Thursday' and self.Program[9] == 'Yes':
            self.Go = True
            return
        elif self.Day == 'Friday' and self.Program[10] == 'Yes':
            self.Go = True
            return
        elif self.Day == 'Saturday' and self.Program[11] == 'Yes':
            self.Go = True
            return
        elif self.Day == 'Sunday' and self.Program[5] == 'Yes':
            self.Go = True
            return
        else:
            self.Go = False

#=======================================================================================================================
# Things to work on
# - Create a method to have a countdown remaining when the zone is running. Show that every 3 minutes
# - ReActivate the commented out section of the program that were disabled for testing
# - Need to add check for Rain when the zone is running.
# - Create a setup.py installer.
# - in ChecktheNetwork, when it fails add to log stating it is rebooting
# - Add math for runtime for when NULL

run = Sprinklers()

