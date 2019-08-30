__author__ = 'Dave Spicer'
__version__ = '3.0.22'
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
        version = __version__
        self.SetupMCP23017()
        self.pinAllOff()
        self.GetUser()
        self.Configuration()
        self.CharLCDPlate()
        self.WelcomeMessage(version)
        self.LCD.clear()
        self.PITime()
        self.SystemInformation()
        self.PISleep5()
        self.LCD.clear()
        self.LCD.message('Program Starting\nPlease Wait')
        self.PISleep5()
        self.LCD.clear()
        self.LCD.message('Loading Program\nParameters')
        self.SprinklerParameters()
        self.SprinklerProgram()
        self.LCD.clear()
        self.LCD.message('Checking Weather\nConditions')
        self.Weather()
        self.PISleep5()
        self.LCD.clear()
        self.LCD_Clock()
        self.IP()
        self.ProgramEnableDisable()
    def WelcomeMessage(self, version):
        self.LCD.home()
        self.LCD.setCursor(3,0)
        self.LCD.message('Welcome to\nSprinkler Python')
        self.PISleep2()
        self.LCD.clear()
        self.LCD.setCursor(0, 0)
        self.LCD.message('Version - %s' % (version))
        self.PISleep2()
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
        noTemp = self.CurrentSystemTime + datetime.timedelta(minutes=3)
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
        self.Temp_f = weather[7]
        if self.Temp_f == 'None':
            self.LogEvent = 'No-Temp'
            self.Log()
            while self.CurrentSystemTime <= noTemp:
                self.LCD.message('No Outside Temp')
                self.PISleep60()
                self.PITime()
            self.WeatherDatabaseRead()
        else:
            self.Temp_f = float(weather[7])
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
        self.Rain = (round(self.Rain,2))
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
        self.PISleep2()
        self.clearLCDLeft()
        self.LCD.clear()
        if SSID != "LAN":
            wifistrength = ("iwconfig wlan0 | awk -F'[ =]+' '/Signal level/ {print $7}' | cut -d/ -f1")
            strength = (os.popen(wifistrength).read())
            if strength == '':
                strength = "NO WiFi Signal"
            self.LCD.message('WiFi Signal:\n%s' % (strength))
            self.PISleep2()
        self.clearLCDRight()
        self.LCD.clear()
        self.CheckNetwork()
        self.LCD.message('Internet is:\n%s' % (self.CNET))
        self.PISleep2()
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
        s.connect(("1.1.1.1", 80)) # Change ping address to local network
        self.LCD.setCursor(0, 1)
        self.LCD.message('IP:%s' % (s.getsockname()[0]))
    def ProgramEnableDisable(self):
        round = 1
        self.StartTime = self.Program[2], self.Program[3]
        while self.Program[0] == 'Disabled':
            self.LCD.backlight(self.LCD.VIOLET)
            self.PISleep()
            self.MySQL_Connection_Sprinkler()
            self.SprinklerProgram()
            self.LCD_Clock()
            self.IP()
        while self.Program[0] == 'Enabled':
            self.LCD.backlight(self.LCD.YELLOW)
            self.PISleep()
            self.MySQL_Connection_Sprinkler()
            self.SprinklerProgram()
            self.LCD_Clock()
            self.IP()
            self.WaitForStartTime(round)
    def WaitForStartTime(self, round):
        OrgProgram = self.Program[1]
        delta = self.CurrentSystemTime + datetime.timedelta(minutes=2)
        displayProgramTime = self.CurrentSystemTime + datetime.timedelta(minutes=5)
        self.PITime()
        if round == 1:
            self.LogEvent = 'Wait'
            self.Log()
        self.CheckDayofWeektoRun()
        if self.Go == True:
            RainFound = 1
            while self.StartTime != self.WorkableTime:
                self.FalseWeather()
                LoopTime = self.CurrentSystemTime + datetime.timedelta(minutes=5)
                self.Winterize()
                self.BelowTempCheck()
                self.CheckforRain(RainFound)
                while self.CurrentSystemTime <= LoopTime:
                    if self.CurrentSystemTime >= displayProgramTime:
                        self.displayProgram(displayProgramTime)
                        displayProgramTime = self.CurrentSystemTime + datetime.timedelta(minutes=5)
                        self.LCD.clear()
                    if self.StartTime == self.WorkableTime:
                        self.RunZones(RainFound)
                    if self.CurrentSystemTime >= delta:
                        self.MySQL_Connection_Sprinkler()
                        self.SprinklerProgram()
                        delta = self.CurrentSystemTime + datetime.timedelta(minutes=2)
                    if OrgProgram != self.Program[1]:
                        self.ProgramEnableDisable()
                    self.LCD.backlight(self.LCD.YELLOW)
                    self.LCD_Clock()
                    self.IP()
                    self.PITime()
                    self.PISleep()
                    self.StartTime = self.Program[2], self.Program[3]
                self.Weather()
                self.LCD.clear()
            self.RunZones()
        if self.Go == False:
            self.PITime()
            delta = self.CurrentSystemTime + datetime.timedelta(hours=2)
            NotScheduletoRun = self.CurrentSystemTime + datetime.timedelta(minutes=1)
            while self.CurrentSystemTime <= delta:
                if self.CurrentSystemTime >= NotScheduletoRun:
                    NotScheduletoRun = self.CurrentSystemTime + datetime.timedelta(minutes=1)
                    self.LCD.clear()
                    self.LCD.setCursor(0, 0)
                    self.LCD.backlight(self.LCD.VIOLET)
                    self.LCD.message('Not Schedule to\nrun today')
                    self.PISleep5()
                    self.LCD.backlight(self.LCD.YELLOW)
                self.LCD_Clock()
                self.IP()
                self.PITime()
                self.PISleep1()
        self.SprinklerProgram()
        self.ProgramEnableDisable()
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
            self.LogEvent = 'No Network'
            self.Log()
            os.system("sudo reboot")
    def CountDown(self, RainFound):
        WeatherCheckTime = self.CurrentSystemTime + datetime.timedelta(hours=2)
        self.Log()
        self.PITime()
        self.LCD.clear()
        self.LCD.backlight(self.LCD.WHITE)
        while self.CurrentSystemTime <= self.RainDelay:
            if self.CurrentSystemTime >= WeatherCheckTime:
                WeatherCheckTime = self.CurrentSystemTime + datetime.timedelta(hours=2)
                self.CheckforRain(RainFound)
            TempTime = self.RainDelay - self.CurrentSystemTime
            self.LCD.clear()
            self.LCD.setCursor(3, 0)
            self.LCD.message(('%s Sleep') % (self.LogEvent))
            self.LCD.setCursor(0, 1)
            self.LCD.message('%s' % (TempTime)) #Format Time to HH:MM:SS
            self.PITime()
            self.PISleep1()
        self.LogEvent = 'Resume'
        self.Log()
    def CountDownRunning(self, ZoneRunTime):
        self.LCD.clear()
        round = self.CurrentSystemTime + datetime.timedelta(seconds=15)
        self.LCD.setCursor(0,0)
        self.LCD.message('Remain Run Time')
        while self.CurrentSystemTime <= round:
            #round = self.CurrentSystemTime + datetime.timedelta(seconds=15)
            WaitMin = ZoneRunTime - self.CurrentSystemTime
            self.LCD.setCursor(1, 1)
            self.LCD.message(WaitMin)
            self.PISleep1()
            self.PITime()
        #self.CheckRemainTime = self.CurrentTimeMinute + 3
    def Log(self):
        FormatDate = str(self.CurrentDateIntVersion.year) + '-' + str(self.CurrentDateIntVersion.month) + '-' + str(
            self.CurrentDateIntVersion.day)
        timeformat = '{:02d}:{:02d}'.format(self.CurrentTimeHour, self.CurrentTimeMinute)
        self.MySQL_Connection_Sprinkler()
        self.cur = self.sql.cursor()
        if self.LogEvent == 'Rain':
            Subject = 'Rain Detected at'
            sendEmail = self.SendEmailRain
            self.LogDescription = 'Rain Detected Waiting for countdown timer to expire.'
        if self.LogEvent == 'Wait':
            Subject = 'Waiting to Start the ' + self.Program[1] + ' program at '
            sendEmail = self.SendEmailWait
            self.LogDescription = 'Program is waiting to start the sprinkler System.'
        if self.LogEvent == 'Resume':
            Subject = 'Everything good to resume the ' + self.Program[1] + ' at '
            sendEmail = self.SendEmailResume
            self.LogDescription = 'Resuming normal operation.'
        if self.LogEvent == 'All':
            Subject = 'All Programs Disabled at'
            sendEmail = self.SendEmailAll
            self.LogDescription = 'All programs are disabled - Please enable to continue.'
        if self.LogEvent == 'Temp':
            Subject = 'Temperature Violation Detected at'
            sendEmail = self.SendEmailTemp
            self.LogDescription = 'Temperature is below desired range to run sprinklers.'
        if self.LogEvent == 'Winterize':
            Subject = 'Time to winterize the sprinkler system'
            sendEmail = self.SendEmailWinterize
            self.LogDescription = 'Based on date you provided, It is time to winterize the sprinkler system.'
        if self.LogEvent == 'No-Temp':
            Subject = 'No Temperature Reporting from weather station.'
            sendEmail = self.SendEmailNoTemp
            self.LogDescription = 'No Temperature Reporting from Weather Station.'
        if self.LogEvent == 'Run':
            Subject = 'Sprinkler System has begun running at'
            sendEmail = self.SendEmailRun
            self.LogDescription = 'Sprinkler System has begun to run.'
        if self.LogEvent == 'Done':
            Subject = 'Finished at'
            sendEmail = self.SendEmailDone
            self.LogDescription = 'All Zones have finished running.'
        if self.LogEvent == 'False':
            Subject = 'False Weather. Need to fix the weewx database'
            sendEmail = 'Yes'
            self.LogDescription = 'False weather data. Need to check WeeWX database.'
        if self.LogEvent == 'No-Network':
            Subject = 'No Network - Rebooting.'
            sendEmail = self.SendNoNetwork
            self.LogDescription = 'No Network detected. Rebooting...'
        if self.LogEvent == 'Email-Issue':
            self.LogDescription = 'Something went wrong trying to send the email...'
        #try:
        self.cur.execute(("INSERT INTO `Log` (Date, Time, Event, Program, Description) VALUES ('%s', '%s', '%s', '%s', '%s')"
                              % (FormatDate, timeformat, self.LogEvent, self.Program[1], self.LogDescription)))
        self.sql.commit()
        self.sql.close()
        #except:
            #self.Weather()
        #try:
        if sendEmail == 'Yes':
            self.sendEmail(timeformat, Subject)
        #except:
            #self.LogEvent = 'Something-Happen'
            #self.LogDescription = 'Something went wrong during the check of self.sendEmail statement...'
            #self.log()
            #return
    def sendEmail(self, timeformat, Subject):
            try:
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
                msgbody = header + '\nDate: ' + str(self.CurrentDateIntVersion) + '\nTime: ' + timeformat + '\nEvent: ' + self.LogEvent + ' ' + self.Program[1] + '\nDescription: ' + self.LogDescription + '\nRain Amount: ' + str(self.Rain)
                smtpserver.sendmail(user, sendto, msgbody)
                smtpserver.close()
            except:
                self.LogEvent = 'Email-Issue'
                self.Log()
    def GetUser(self):
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
            user.append(row[14])
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
        self.SendNoNetwork = user[14]
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
    def RunZones(self, RainFound):
        self.CheckforRain(RainFound)
        self.CheckRemainTime = self.CurrentSystemTime + datetime.timedelta(minutes=3)
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
            RTime = self.Program[t]
            ZoneRunTime = self.CurrentSystemTime + datetime.timedelta(minutes=RTime)
            if self.Program[t] == 0:
                self.status = 'Zero Run Time in Database'
                self.UpdateZoneLog(Zone)
                self.PISleep60()
                self.__init__()
            if 0 <= p <= 7:
                Bank = 'A'
            if 8 <= p <= 15:
                Bank = 'B'
                GPIOPin = self.Parameters[p] - 8
            ZRT = RTime - 1
            MinuteRemain = self.CurrentSystemTime + datetime.timedelta(minutes=ZRT)
            while self.CurrentSystemTime <= ZoneRunTime:
                self.BelowTempCheck()
                self.LCD_Clock()
                if self.CurrentSystemTime <= MinuteRemain:
                    if self.CurrentSystemTime >= self.CheckRemainTime:
                        self.CheckRemainTime = self.CurrentSystemTime + datetime.timedelta(minutes=3)
                        self.CountDownRunning(ZoneRunTime)
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
    def CheckforRain(self, RainFound):
        oldRainValue = self.Rain
        self.WeatherDatabaseRead_Rain()
        if self.Rain >= oldRainValue:
            if RainFound > 1:
                if self.Rain > oldRainValue:
                    RainFound = 1
            if self.Rain >= .75:
                Day = 3
                if RainFound == 1:
                    self.RainDelay = self.CurrentSystemTime + datetime.timedelta(Day)
                    RainFound = RainFound + 1
                self.LogEvent = 'Rain'
                self.CountDown(RainFound)
            if self.Rain >= .50:
                Day = 2
                if RainFound == 1:
                    self.RainDelay = self.CurrentSystemTime + datetime.timedelta(Day)
                    RainFound = RainFound + 1
                self.LogEvent = 'Rain'
                self.CountDown(RainFound)
            if self.Rain >= .10 or self.Rain >= .49:
                Day = 1
                if RainFound == 1:
                    self.RainDelay = self.CurrentSystemTime + datetime.timedelta(Day)
                    RainFound = RainFound + 1
                self.LogEvent = 'Rain'
                self.CountDown(RainFound)
            else:
                return
    def FalseWeather(self):
        FalseWeather = datetime.datetime.now() + datetime.timedelta(hours=2)
        FalseWeatherEmail = datetime.datetime.now() + datetime.timedelta(minutes=30)
        if self.Rain > 5:
            while self.CurrentSystemTime < FalseWeather:
                if self.CurrentSystemTime > FalseWeatherEmail:
                    self.LogEvent = 'False'
                    self.Log()
                    FalseWeatherEmail = datetime.datetime.now() + datetime.timedelta(minutes=30)
                self.Rain = 0
                self.PITime()
                self.PISleep1()
                self.LCD_Clock()
                self.IP()
            self.Weather()
    def displayProgram(self, displayProgramTime):
            self.LCD.clear()
            self.LCD.setCursor(1, 0)
            self.LCD.message('Active Program')
            self.LCD.setCursor(0, 1)
            self.LCD.message(self.Program[1])
            self.PISleep5()
            self.PITime()
    def BelowTempCheck(self):
        BelowTempCheckTime = self.CurrentSystemTime + datetime.timedelta(hours=1)
        if self.Temp_f <= 40:
            self.LogEvent = 'Temp'
            self.Log()
            while self.CurrentSystemTime <= BelowTempCheckTime:
                self.LCD.clear()
                self.LCD.backlight(self.LCD.RED)
                self.LCD.setCursor(3,0)
                self.LCD.message('Below Temp')
                self.LCD.setCursor(3,1)
                self.LCD.message('Violation!')
                self.PISleep60()
                self.PITime()
            self.Weather()
            self.WaitForStartTime(round=2)
    def Winterize(self):
        if self.CurrentMonthIntVersion >= 9 and self.CurrentDayIntVersion >= 25:
            self.LogEvent = 'Winterize'
            self.Log()




#=======================================================================================================================
# Things to work on
# - Create a setup.py installer.
# - Add math for runtime for when NULL

run = Sprinklers()

