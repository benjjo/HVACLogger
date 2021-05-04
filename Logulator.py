import pandas as pd
import os
import matplotlib.pyplot as plt
import shutil
import numpy as np


class Logulator:
    """
    Class of tools to construct and plot CSV data for MERAK HVAC logs.
    """
    def __init__(self):
        self.all_data = pd.DataFrame()
        self.path = './'
        self.tempDir = self.path + '.temp/'
        self.version = 'Logulator V4.1'
        self.coachType = str()
        self.seatVars = ('Time date', 'Time date', 'Type', 'Car type', 'External Supply', 'TEMPERATURE_SUPPLY_1',
                         'SAT1', 'TEMPERATURE_SUPPLY_2', 'SAT2', 'TEMPERATURE_RETURN',
                         'Vestibule E2', 'TEMP. VESTIBULE_LEFT', 'Vestibule E1', 'TEMP. STAFF_WC',
                         'Return Air', 'TEMPERATURE_GUARD_GALLEY_WC',
                         'Guards Room', 'TEMP. BERTH_1')
        self.clubVars = ('Time date', 'Time date', 'Type', 'Car type', 'External Supply', 'TEMPERATURE_SUPPLY_1',
                         'SAT1', 'TEMPERATURE_SUPPLY_2', 'SAT2', 'TEMPERATURE_RETURN',
                         'Vestibule E2', 'TEMP. VESTIBULE_LEFT', 'Vestibule E1', 'TEMP. STAFF_WC',
                         'Return Air', 'TEMPERATURE_GUARD_GALLEY_WC',
                         'Crew Room', 'TEMP. GUARD_GALLEY_WC', 'Guards Room', 'TEMP. BERTH_1')
        self.accVars = ('Time date', 'Time date', 'Type', 'Car type', 'External Supply', 'TEMPERATURE_SUPPLY_1',
                        'SAT1', 'TEMPERATURE_SUPPLY_2', 'SAT2', 'TEMPERATURE_RETURN',
                        'Vestibule E2', 'TEMP. VESTIBULE_LEFT', 'Vestibule E1', 'TEMP. STAFF_WC',
                        'Return Air', 'TEMPERATURE_GUARD_GALLEY_WC',
                        'PRM E1', 'TEMP. GUARD_GALLEY_WC', 'PRM E2', 'TEMP. BERTH_1',
                        'Berth 1', 'TEMP. BERTH_7_6', 'Berth 2', 'TEMP. BERTH_6_3',
                        'Berth 3', 'TEMP. BERTH_5_2', 'Berth 4', 'TEMP. BERTH_4',
                        'Berth 5', 'TEMP. BERTH_3_5', 'Berth 6', 'TEMP. BERTH_2_4')
        self.sleeperVars = ('Time date', 'Time date', 'Type', 'Car type', 'External Supply', 'TEMPERATURE_SUPPLY_1',
                            'SAT1', 'TEMPERATURE_SUPPLY_2', 'SAT2', 'TEMPERATURE_RETURN',
                            'Vestibule E2', 'TEMP. VESTIBULE_LEFT', 'Vestibule E1', 'TEMP. STAFF_WC',
                            'Return Air', 'TEMPERATURE_GUARD_GALLEY_WC',
                            'Galley', 'TEMP. BERTH_1', 'STD WC', 'TEMP. GUARD_GALLEY_WC',
                            'Berth 1', 'NOT_USED_1_10', 'Berth 2', 'TEMPERATURE_BERTH_10',
                            'Berth 3', 'TEMPERATURE_BERTH_9', 'Berth 4', 'TEMPERATURE_BERTH_8',
                            'Berth 5', 'NOT_USED_1_9', 'Berth 6', 'NOT_USED_1_8', 'Berth 7', 'TEMPERATURE_BERTH_5_2',
                            'Berth 8', 'TEMPERATURE_BERTH_4', 'Berth 9', 'TEMPERATURE_BERTH_3_5',
                            'Berth 10', 'TEMPERATURE_BERTH_2_4')
        self.seated_temp_vars = ('Vestibule E2', 'Vestibule E1', 'Return Air', 'Guards Room')
        self.club_temp_vars = ('Vestibule E2', 'Vestibule E1', 'Return Air', 'Crew Room', 'Guards Room')
        self.acc_temp_vars = ('Vestibule E2', 'Vestibule E1', 'Return Air', 'PRM E1', 'PRM E2',
                              'Berth 1', 'Berth 2', 'Berth 3', 'Berth 4', 'Berth 5', 'Berth 6')
        self.sleeper_temp_vars = ('Vestibule E2', 'Vestibule E1', 'Return Air', 'PRM E1', 'PRM E2',
                                  'Berth 1', 'Berth 2', 'Berth 3', 'Berth 4', 'Berth 5',
                                  'Berth 6', 'Berth 7', 'Berth 8', 'Berth 9', 'Berth 10')

    def getVersion(self):
        """
        Returns the current revision of Logulator
        :return:
        """
        return self.version

    def setCoachType(self, df: pd.DataFrame):
        try:
            self.coachType = df['Car type'].mode().iloc[0]
        except IndexError:
            print('ʍǝ ɐɹǝ ɥɐʌınƃ ʇǝɔɥnıɔɐl dıɟɟıɔnlʇıǝs')
            input('Your data is probably from 2006 - ABORT! ABORT! ABORT!')

    def getCoachType(self) -> str:
        return self.coachType

    def makeAllDataDF(self):
        """
        Constructs a Pandas Data Frame from a directory of MERAK HVAC CSV files.
        Creates a file all_data.csv from a bunch of HVAC files if it hasn't already
        been created.
        :return: Pandas Data Frame
        """
        if 'all_data.csv' not in os.listdir(self.path):
            self.makeTemporaryTXTFilesForCSV('xls')
            self.writeTempCSVFiles()
            self.csvToDataFrame()
            self.writeAllDataCSV()
            self.all_data.to_csv("all_data.csv", index=False)
        allDataDF = pd.read_csv('all_data.csv')
        self.setCoachType(allDataDF)

        return allDataDF

    def makeTemporaryTXTFilesForCSV(self, extension):
        """
        Helper method for makeAllDataDF()
        Creates a temporary directory to store txt versions of the xls files.
        :param extension:
        :return: None
        """
        self.path = os.getcwd()
        files = os.listdir(self.path)
        os.makedirs(self.tempDir, exist_ok=True)
        files_xls = [f for f in files if f[-3:] == extension]
        counter = 0
        for file in files_xls:
            with open(file) as fin, open(self.tempDir + str(counter) + '_New_File.txt', 'w') as fout:
                for line in fin.readlines()[1:]:  # don't look at the first line
                    fout.write(line.replace('\t', ','))
                counter += 1

    def writeTempCSVFiles(self):
        """
        Helper method for makeAllDataDF()
        Creates a bunch of csv files from the txt files created in makeTemporaryTXTFilesForCSV()
        These are processed specifically for the format that is produced by the train.
        :return: None
        """
        tempFiles = os.listdir(self.tempDir)
        files_txt = [f for f in tempFiles if f[-3:] == 'txt']
        counter = 0
        for file in files_txt:
            with open(self.tempDir + file) as fin, open(self.tempDir + str(counter) + '_final.csv', 'w') as fout:
                for line in fin:
                    fout.write(line.replace('BERTH_9_FEEDBACK,BERTH_10_FEEDBACK,',
                                            'BERTH_9_FEEDBACK,BERTH_10_FEEDBACK,NothinToSeeHere,'))
                counter += 1

    def createDataLoggerCSV(self):
        """
        Creates a CSV file from the Data Logger xlsx file.
        :return:
        """
        loggerDF = pd.DataFrame()
        tempLogs = pd.DataFrame()
        path = os.getcwd()
        files = os.listdir(path)
        tempDir = './.tempDL/'
        os.makedirs(tempDir, exist_ok=True)
        files_xlsx = [f for f in files if f[-4:] == 'xlsx']
        counter = 0
        for file in files_xlsx:
            shutil.copy(file, tempDir + str(counter) + '_New_File.xlsx')
            data = pd.read_excel(tempDir + str(counter) + '_New_File.xlsx', engine='openpyxl')
            tempLogs = tempLogs.append(data)
            counter += 1
        loggerDF['Time date'] = tempLogs['Time']
        loggerDF['Logger Temp. °C'] = tempLogs['Celsius(°C)']
        loggerDF = self.sortByDateAndReIndex(loggerDF)
        loggerDF.to_csv('loggerData.csv')
        shutil.rmtree(tempDir)

    def writeAllDataCSV(self):
        """
        Helper method for makeAllDataDF()
        Sorts the all_data DF. Removes the 2019 or less data.
        Removes the tempdir.
        :return: None
        """
        self.sortByDateAndReIndex(self.all_data).to_csv("all_data.csv", index=False)
        self.all_data = self.all_data[(self.all_data['Time date'].dt.year > 2019)]
        shutil.rmtree(self.tempDir)

    def csvToDataFrame(self):
        """
        Helper method for makeAllDataDF()
        Reads all the csv files in the ./temp dir into a dataframe
        :return: None
        """
        tempFiles = os.listdir(self.tempDir)
        self.all_data = pd.DataFrame(None)
        files_csv = [f for f in tempFiles if f[-3:] == 'csv']

        for file in files_csv:
            data = pd.read_csv(self.tempDir + file)
            self.all_data = self.all_data.append(data)

    def makeTempdataCSV(self):
        count = 0
        var_tuple = tuple()
        df = pd.DataFrame()
        allData = self.makeAllDataDF()

        if self.coachType == 'SEATED':
            var_tuple = self.seatVars
        elif self.coachType == 'CLUB':
            var_tuple = self.clubVars
        elif self.coachType == 'ACCESSIBLE':
            var_tuple = self.accVars
        elif self.coachType == 'SLEEPER':
            var_tuple = self.sleeperVars
        else:
            print('ʍǝ ɐɹǝ ɥɐʌınƃ ʇǝɔɥnıɔɐl dıɟɟıɔnlʇıǝs')
            input('Something went terribly wrong - ABORT! ABORT! ABORT!')

        var_num = len(var_tuple)
        while count < var_num:
            df[var_tuple[count]] = allData[var_tuple[count + 1]]
            count += 2
        return df

    def getTempData(self):
        """
        Returns a DataFrame using the temperature sensor data from the HVAC unit.
        If there is no temperatureData.csv file available, it will make one with the
        HVAC csv logs.
        :return: temperatureData of type DataFrame
        """
        # temperatureData = pd.DataFrame()

        if 'temperatureData.csv' not in os.listdir(self.path):
            temperatureData = self.makeTempdataCSV()
            temperatureData.to_csv("temperatureData.csv", index=False)

        temperatureData = pd.read_csv("temperatureData.csv")
        temperatureData = self.sortByDateAndReIndex(temperatureData)
        return temperatureData

    def getLoggerData(self):
        """
        Returns a DataFrame using the Data Logger data.
        If there is no loggerData.csv file available, it will make one with the csv logs.
        :return: loggerDF of type DataFrame
        """
        if 'loggerData.csv' not in os.listdir(self.path):
            self.createDataLoggerCSV()
        loggerDF = pd.read_csv('./loggerData.csv')
        loggerDF['Time date'] = pd.to_datetime(loggerDF['Time date'])
        loggerDF = loggerDF.set_index('Time date')
        loggerDF = loggerDF.dropna(how='any')
        loggerDF = loggerDF.drop(loggerDF.columns[[0]], axis=1)  # Remove superfluous column
        return loggerDF

    def getDamperData(self):
        """
        Creates a Data Frame from the MERAK csv files.
        Specifically holds the Damper position data.
        :return: Pandas Data Frame
        """
        if 'damperData.csv' not in os.listdir(self.path):
            df = self.makeAllDataDF()
            damperData = pd.DataFrame()
            df['Time date'] = pd.to_datetime(df['Time date'])  # new entry
            damperData['Time date'] = df['Time date']
            damperData['Fresh Air Damper'] = df['FRESH_DAMPER_FEEDBACK']
            damperData['Return Air Damper'] = df['RETURN_DAMPER_FEEDBACK']
            damperData.to_csv("damperData.csv", index=False)

        damperData = pd.read_csv("damperData.csv")
        damperData = self.sortByDateAndReIndex(damperData)
        return damperData

    def sortByDateAndReIndex(self, df):
        """
        Helper method that sets up the Data Frame to be indexed by date.
        :param df:
        :return:
        """
        df['Time date'] = pd.to_datetime(df['Time date'])
        df = df.sort_values(by='Time date')
        df = df.reset_index(drop=True)  # Reset the index to line up with the sorted data.
        return df

    def makeTempComparisonDF(self, set_point=22):
        """
        Makes an empty DataFrame with a index using date time incrementing by seconds.
        The date range of the index is set by the info from the data logger as this data
        is more finite than the data from the HVAC unit.
        :return: tempComparison of type DataFrame
        """
        df = self.getTempData()  # Makes a DF using the HVAC sensor data
        loggerData = self.getLoggerData()  # Makes a DF using the Data Logger data
        start_date = loggerData.index[0]
        end_date = loggerData.index[-1]
        index = pd.date_range(start_date, end=end_date, freq='S')
        columns = ['Set Point']
        tempComparison = pd.DataFrame(index=index, columns=columns)
        tempComparison['Set Point'] = tempComparison['Set Point'].fillna(set_point)
        temperatureData = df[(df['Time date'] >= loggerData.index[0]) &
                             (df['Time date'] <= loggerData.index[-1])].copy().set_index('Time date')
        tempComparison = loggerData.combine_first(tempComparison)
        tempComparison = temperatureData.combine_first(tempComparison)
        return tempComparison


class TempLogger(Logulator):
    def plotTemperatures(self):
        """
        Plots all the temperatures.
        :return:
        """
        temperatureData = Logulator.getTempData(self)
        dfTemp = temperatureData.copy().set_index('Time date')
        dfTemp.plot(kind='line')
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('HVAC Temperatures: ' + Logulator.getCoachType(self), color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.legend(title='Sensor')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.getVersion(self))
        imageName = ('HVAC Temperature Sensors ' + str(dfTemp.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(imageName, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()

    def plotTemperaturesOneSensor(self, sensor=0):
        """
        Plots the temperatures from the MERAK unit for one selected sensor.
        :param sensor:
        :return:
        """
        sensors = {1: 'Dining Floor Return',
                   2: 'External Grill Supply',
                   3: 'Vestibule E1',
                   4: 'Vestibule E2',
                   5: 'Guards Rest Room',
                   6: 'Guards Control Room'}
        sensorsCAF = {1: '71B01', 2: '71B02', 3: '71B03', 4: '71B04', 5: '71B05', 6: '71B06'}
        sensorToTest = sensors[sensor]
        title = sensorToTest + ' ' + sensorsCAF[sensor]
        df = pd.DataFrame()
        df['Time date'] = Logulator.getTempData(self)['Time date']
        df[sensors[sensor]] = Logulator.getTempData(self)[sensors[sensor]]
        df['Logger Data'] = np.nan

        loggerData = self.getLoggerData()  # Makes a DF using the Data Logger data
        dfTemp = df[(df['Time date'] >= loggerData.index[0]) &
                    (df['Time date'] <= loggerData.index[-1])].copy().set_index('Time date')
        dfTemp.plot(kind='line')
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title(title + ' to data logger', color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.legend(title='Sensor')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.getVersion(self))
        imageName = (title + str(dfTemp.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(imageName, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()


class DampLogger(Logulator):
    def plotDamperPositions(self):
        """
        Plots the MERAK damper position data.
        :return:
        """
        damperData = Logulator.getDamperData(self)

        dfTemp = damperData.copy().set_index('Time date')
        dfTemp.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('HVAC Temperatures', color='C0')
        plt.ylabel('% Percentage Open', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.legend(title='Damper Position %')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.getVersion(self))
        imageName = ('Damper Position Data ' + str(dfTemp.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(imageName, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()

    def plotDamperOverTemps(self):
        """
        Plots the Damper positions over the top of the temperature data.
        :return:
        """
        dfTemp = Logulator.getTempData(self).set_index('Time date')
        damper = Logulator.getDamperData(self).set_index('Time date')

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()

        ax1.set_xlabel('Date Time', color='C0')
        ax1.set_ylabel('Temperatures', color='C0')
        ax2.set_ylabel('Damper position %', color='C0')
        ax1.tick_params(axis='x', labelcolor='C0', labelrotation=90)
        ax1.tick_params(axis='y', labelcolor='C0')
        ax2.tick_params(axis='y', labelcolor='C0')

        ax1.plot(dfTemp, label='Temperature supply')
        ax2.plot(damper, label='Damper')

        plt.get_current_fig_manager().canvas.set_window_title(Logulator.getVersion(self))
        plt.title('Damper position & HVAC Temperatures', color='C0')
        plt.grid('on', linestyle='--')

        plt.show()


class DataLoggerTemperatures(Logulator):
    def plotDataLoggerTemps(self):
        """
        Plots the Data Logger files.
        :return:
        """
        dfTemp = Logulator.getLoggerData(self).copy()
        dfTemp.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('Data Logger Temperatures', color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')

        plt.legend(title='Input Sensor')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.getVersion(self))
        imageName = ('Data Logger ' + str(dfTemp.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(imageName, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()

    def plotDataLoggerOverHVAC(self, sensor=0):
        """
        Plots the data logger file over the top of the MERAK data for the same time period.
        :param sensor:
        :return:
        """
        sensor = int(sensor)
        sensors = {1: 'Dining Floor Return',
                   2: 'External Grill Supply',
                   3: 'Vestibule E1',
                   4: 'Vestibule E2',
                   5: 'Guards Rest Room',
                   6: 'Guards Control Room'
                   }
        sensorsCAF = {1: '71B01', 2: '71B02', 3: '71B03', 4: '71B04', 5: '71B05', 6: '71B06'}
        sensorToTest = sensors[sensor]
        title = sensorToTest + ' ' + sensorsCAF[sensor]

        dfTemps = pd.DataFrame()
        tempComparison = Logulator.makeTempComparisonDF(self)

        # ffill will fill in the NaN gaps with previous data
        dfTemps['Logger Temps. °C'] = tempComparison['Logger Temp. °C'].ffill()
        dfTemps['HVAC Temps. °C'] = tempComparison[sensorToTest].ffill()
        dfTemps['Set Point'] = tempComparison['Set Point']
        dfTemps.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title(title, color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.legend(title='Input Sensor')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.getVersion(self))
        imageName = (title + ' ' + str(dfTemps.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(imageName, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()


def printSensorList():
    print("""
    Choose sensor to map:
        1. 71B01    Return floor sensor
        2. 71B02    Fresh air supply
        3. 71B03    E1 Vestibule
        4. 71B04    E2 Vestibule
        5. 71B05    Crew room
        6. 71B06    Guard's room
        """)


def main():
    temp = TempLogger()
    damp = DampLogger()
    dataLog = DataLoggerTemperatures()

    print("""
    Choose operation:
        1. Plot HVAC temperatures
        2. Plot Damper data
        3. Plot DataLogger file
        4. Plot DataLogger file on top of HVAC sensor
        5. Plot Dampers against temperatures
        6. Plot one temperature sensor
    """)
    choice = int(input("Enter choice: "))
    os.system('cls')

    if choice == 1:
        temp.plotTemperatures()
    elif choice == 2:
        damp.plotDamperPositions()
    elif choice == 3:
        dataLog.plotDataLoggerTemps()
    elif choice == 4:
        printSensorList()
        dataLog.plotDataLoggerOverHVAC(int(input("Sensor: ")))
    elif choice == 5:
        damp.plotDamperOverTemps()
    elif choice == 6:
        printSensorList()
        temp.plotTemperaturesOneSensor(int(input("Sensor: ")))
    else:
        print("Your choice was invalid.")


if __name__ == "__main__":
    main()