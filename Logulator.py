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

    def readDataLoggerCSV(self):
        if 'loggerData.csv' not in os.listdir(self.path):
            self.createDataLoggerCSV()
        return pd.read_csv('loggerData.csv')

    def makeDataLoggerDataFrame(self):
        df = self.readDataLoggerCSV()
        dataLogger = pd.DataFrame()
        dataLogger['Time date'] = df['Time']
        dataLogger['Temperature °C'] = df['Celsius(°C)']
        dataLogger.to_csv("dataLogger.csv", index=False)
        dataLogger = pd.read_csv("dataLogger.csv")
        dataLogger = self.dateSortAndReIndex(dataLogger)
        dataLogger = dataLogger.set_index('Time date')
        return dataLogger

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
        if 'temperatureData.csv' not in os.listdir(self.path):
            df = self.getAllData()
            temperatureData = pd.DataFrame()
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
        else:
            temperatureData = pd.read_csv("temperatureData.csv")

        temperatureData = self.dateSortAndReIndex(temperatureData)
        temperatureData = temperatureData.set_index('Time date')
        return temperatureData

    def getDamperData(self):
        if './damperData.csv' not in os.listdir(self.path):
            df = self.getAllData()
            damperData = pd.DataFrame()
            damperData['Time date'] = df['Time date']
            damperData['Fresh Air Damper'] = df['FRESH_DAMPER_FEEDBACK']
            damperData['Return Air Damper'] = df['RETURN_DAMPER_FEEDBACK']
            damperData.to_csv("damperData.csv", index=False)
        else:
            damperData = pd.read_csv("damperData.csv")

        damperData = self.dateSortAndReIndex(damperData)
        damperData = damperData.set_index('Time date')
        return damperData

    def dateSortAndReIndex(self, df):
        df['Time date'] = pd.to_datetime(df['Time date'])
        df = df.sort_values(by='Time date')
        df = df.reset_index(drop=True)  # Reset the index to line up with the sorted data.
        return df


class TempLogger(Logulator):
    def plotTemperatures(self):
        temperatureData = Logulator.getTempData(self)

        dfTemp = temperatureData.copy()
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

        dfTemp = damperData.copy()
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


class DataLoggerTemperatures(Logulator):
    def plotDataLoggerTemps(self):
        dfTemp = Logulator.makeDataLoggerDataFrame(self).copy()
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
        sensors = {1: 'Dining Floor Return', 2: 'External Grill Supply', 3: 'Vestibule E1',
                   4: 'Vestibule E2', 5: 'Guards Rest Room', 6: 'Guards Control Room'}
        sensorsCAF = {1: '71B01', 2: '71B02', 3: '71B03', 4: '71B04', 5: '71B05', 6: '71B06'}
        sensorToTest = sensors[int(sensor)]

        loggerData = Logulator.readDataLoggerCSV(self)
        loggerData = loggerData.set_index('Time date')
        loggerData = loggerData.dropna(how='any')

        df = pd.read_csv("temperatureData.csv")
        # temperatureData = df.set_index('Time date')
        temperatureData = df[
            (df['Time date'] >= loggerData.index[0]) & (df['Time date'] <= loggerData.index[-1])].copy().set_index(
            'Time date')
        loggerData = loggerData.iloc[10:-5]  # Drop rows
        dl = loggerData['Temperature °C']
        y1 = temperatureData[sensorToTest]
        x = temperatureData.index
        fig, ax1 = plt.subplots()
        ax2 = ax1.twiny()  # instantiate a second axes that shares the same x-axis
        ax1.set_xlabel('Date Time', color='C0')
        ax1.set_ylabel('Temperatures', color='C0')
        ax1.tick_params(axis='x', labelcolor='C0', labelrotation=90)
        ax1.tick_params(axis='y', labelcolor='C0')
        ax2.tick_params(axis='x', labelcolor='C0')
        ax2.tick_params(axis='y', labelcolor='C0')

        curveDL = ax2.plot(dl, label='Data Logger', color='tab:green')
        label = sensors[int(sensor)] + ' ' + sensorsCAF[int(sensor)]
        curve1 = ax1.plot(x, y1, label=label, color='tab:blue')

        plt.tight_layout(pad=2)

        plt.title(label, color='C0')
        lgd = plt.legend(title='Legend', bbox_to_anchor=(1.1, 1), loc='upper left')
        plt.grid('on', linestyle='--')

        ax2.set_xticks([])  # Hide the xticks on the top axis.
        ax1.set_xticks(range(0, len(x), 20))

        plt.grid('on', linestyle='--')

        plt.savefig('myfig100.png', dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, bbox_extra_artists=(lgd,), bbox_inches='tight',
                    transparent=False, pad_inches=0.1)

        plt.show()


def main():
    print("""
    1. Plot HVAC temperatures
    2. Plot Damper data
    3. Plot DataLogger file
    4. Plot DataLogger file on top of HVAC sensor
        1. 71B01    Return floor sensor
        2. 71B02    External Grill supply
        3. 71B03    E1 Vestibule
        4. 71B04    E2 Vestibule
        5. 71B05    Guard's rest room
        6. 71B06    Guard's control room
    """)
    input("Enter choice: ")

    # temp = TempLogger()
    # damp = DampLogger()
    dataLog = DataLoggerTemperatures()

    # temp.plotTemperatures()
    # damp.plotDamperPositions()
    # dataLog.plotDataLoggerTemps()
    dataLog.plotDataLoggerOverHVAC(input("Sensor: "))


if __name__ == "__main__":
    main()
