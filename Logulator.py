import pandas as pd
import os
import matplotlib.pyplot as plt
import shutil


class Logulator:
    def __init__(self):
        self.all_data = pd.DataFrame()
        self.path = './'
        self.tempDir = self.path + '.temp/'

    def getAllData(self):
        if 'all_data.csv' not in os.listdir(self.path):
            self.setupCSVFiles('xls')
            self.writeTempCSVFiles()
            self.csvToDataFrame()
            self.writeAllDataCSV()
            self.all_data.to_csv("all_data.csv", index=False)

        return pd.read_csv('all_data.csv')

    def setupCSVFiles(self, extension):
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
        tempLogs = pd.DataFrame()
        self.path = os.getcwd()
        files = os.listdir(self.path)
        os.makedirs(self.tempDir, exist_ok=True)
        files_xlsx = [f for f in files if f[-4:] == 'xlsx']
        counter = 0
        for file in files_xlsx:
            os.rename(file, self.tempDir + str(counter) + '_New_File.xlsx')
            data = pd.read_excel(self.tempDir + str(counter) + '_New_File.xlsx', engine='openpyxl')
            tempLogs = tempLogs.append(data)
            counter += 1
        tempLogs.to_csv('loggerData.csv')

    def writeAllDataCSV(self):
        self.all_data.to_csv("all_data.csv", index=False)
        shutil.rmtree(self.tempDir)

    def csvToDataFrame(self):
        tempFiles = os.listdir(self.tempDir)
        self.all_data = pd.DataFrame(None)
        files_csv = [f for f in tempFiles if f[-3:] == 'csv']

        for file in files_csv:
            data = pd.read_csv(self.tempDir + file)
            self.all_data = self.all_data.append(data)

    def getTempData(self):
        """
        Returns a DataFrame using the temperature sensor data from the HVAC unit.
        If there is no temperatureData.csv file available, it will make one with the
        HVAC csv logs.
        :return: temperatureData of type DataFrame
        """
        temperatureData = pd.DataFrame()

        if 'temperatureData.csv' not in os.listdir(self.path):
            df = self.getAllData()
            temperatureData['Time date'] = df['Time date']
            temperatureData['External Grill Supply'] = df['TEMPERATURE_SUPPLY_1']
            temperatureData['SAT1'] = df['TEMPERATURE_SUPPLY_2']
            temperatureData['SAT2'] = df['TEMPERATURE_RETURN']
            temperatureData['Vestibule E2'] = df['TEMP. VESTIBULE_LEFT']
            temperatureData['Vestibule E1'] = df['TEMP. STAFF_WC']
            temperatureData['Dining Floor Return'] = df['TEMPERATURE_GUARD_GALLEY_WC']
            temperatureData['Guards Rest Room'] = df['TEMP. GUARD_GALLEY_WC']
            temperatureData['Guards Control Room'] = df['TEMP. BERTH_1']
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
        loggerDF = pd.DataFrame()
        if 'loggerData.csv' not in os.listdir(self.path):
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
            loggerDF['Time date'] = pd.to_datetime(loggerDF['Time date'])
            loggerDF = self.sortByDateAndReIndex(loggerDF)
            loggerDF.to_csv('loggerData.csv')
            shutil.rmtree(tempDir)

        loggerDF = pd.read_csv('./loggerData.csv')
        loggerDF = loggerDF.set_index('Time date')
        loggerDF = loggerDF.dropna(how='any')
        loggerDF = loggerDF.drop(loggerDF.columns[[0]], axis=1)  # Remove superfluous column
        return loggerDF

    def getDamperData(self):
        if 'damperData.csv' not in os.listdir(self.path):
            df = self.getAllData()
            damperData = pd.DataFrame()
            damperData['Time date'] = df['Time date']
            damperData['Fresh Air Damper'] = df['FRESH_DAMPER_FEEDBACK']
            damperData['Return Air Damper'] = df['RETURN_DAMPER_FEEDBACK']
            damperData.to_csv("damperData.csv", index=False)

        damperData = pd.read_csv("damperData.csv")
        damperData = self.sortByDateAndReIndex(damperData)
        # damperData = damperData.set_index('Time date')
        return damperData

    def sortByDateAndReIndex(self, df):
        df['Time date'] = pd.to_datetime(df['Time date'])
        df = df.sort_values(by='Time date')
        df = df.reset_index(drop=True)  # Reset the index to line up with the sorted data.
        return df

    def makeTempComparisonDF(self, upper=25, lower=16):
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
        columns = ['Upper comfort level', 'Lower comfort level']
        tempComparison = pd.DataFrame(index=index, columns=columns)
        tempComparison['Upper comfort level'] = tempComparison['Upper comfort level'].fillna(upper)
        tempComparison['Lower comfort level'] = tempComparison['Lower comfort level'].fillna(lower)
        temperatureData = df[(df['Time date'] >= loggerData.index[0]) &
                             (df['Time date'] <= loggerData.index[-1])].copy().set_index('Time date')
        tempComparison = loggerData.combine_first(tempComparison)
        tempComparison = temperatureData.combine_first(tempComparison)
        return tempComparison


class TempLogger(Logulator):
    def plotTemperatures(self):
        temperatureData = Logulator.getTempData(self)
        dfTemp = temperatureData.copy().set_index('Time date')
        dfTemp.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('HVAC Temperatures', color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        lgd = plt.legend(title='Channel', bbox_to_anchor=(1.05, 1))

        plt.savefig('myfig100.png', dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, bbox_extra_artists=(lgd,), bbox_inches='tight',
                    transparent=False, pad_inches=0.1)
        plt.show()


class DampLogger(Logulator):
    def plotDamperPositions(self):
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
        lgd = plt.legend(title='Damper Position %', bbox_to_anchor=(1.05, 1))
        imageName = ('Damper Position Data ' + str(dfTemp.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(imageName, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, bbox_extra_artists=(lgd,), bbox_inches='tight',
                    transparent=False, pad_inches=0.1)
        plt.show()


class DataLoggerTemperatures(Logulator):
    def plotDataLoggerTemps(self):
        dfTemp = Logulator.getLoggerData(self).copy()
        dfTemp.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('Data Logger Temperatures', color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        lgd = plt.legend(title='Channel', bbox_to_anchor=(1.05, 1))

        plt.savefig('myfig001.png', dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, bbox_extra_artists=(lgd,), bbox_inches='tight',
                    transparent=False, pad_inches=0.1)
        plt.show()

    def plotDataLoggerOverHVAC(self, sensor):
        sensor = int(sensor)
        sensors = {1: 'Dining Floor Return', 2: 'External Grill Supply', 3: 'Vestibule E1',
                   4: 'Vestibule E2', 5: 'Guards Rest Room', 6: 'Guards Control Room'}
        sensorsCAF = {1: '71B01', 2: '71B02', 3: '71B03', 4: '71B04', 5: '71B05', 6: '71B06'}
        sensorToTest = sensors[sensor]
        title = sensorToTest + ' ' + sensorsCAF[sensor]

        dfTemps = pd.DataFrame()
        tempComparison = Logulator.makeTempComparisonDF(self)

        # ffill will fill in the NaN gaps with previous data
        dfTemps['Logger Temps. °C'] = tempComparison['Logger Temp. °C'].ffill()
        dfTemps['HVAC Temps. °C'] = tempComparison[sensorToTest].ffill()
        dfTemps['Upper comfort level'] = tempComparison['Upper comfort level']
        dfTemps['Lower comfort level'] = tempComparison['Lower comfort level']
        dfTemps.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title(title, color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        lgd = plt.legend(title='Input Sensor', bbox_to_anchor=(1.05, 1))

        imageName = (title + ' ' + str(dfTemps.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(imageName, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, bbox_extra_artists=(lgd,), bbox_inches='tight',
                    transparent=False, pad_inches=0.1)
        plt.show()


def main():
    choice = 0
    temp = TempLogger()
    damp = DampLogger()
    dataLog = DataLoggerTemperatures()

    print("""
    Choose operation:
        1. Plot HVAC temperatures
        2. Plot Damper data
        3. Plot DataLogger file
        4. Plot DataLogger file on top of HVAC sensor
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
        print("""
    Choose sensor to map:
        1. 71B01    Return floor sensor
        2. 71B02    External Grill supply
        3. 71B03    E1 Vestibule
        4. 71B04    E2 Vestibule
        5. 71B05    Guard's rest room
        6. 71B06    Guard's control room
        """)
        dataLog.plotDataLoggerOverHVAC(input("Sensor: "))


if __name__ == "__main__":
    main()
