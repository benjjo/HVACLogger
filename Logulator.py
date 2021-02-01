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

    def writeTempLoggerFiles(self):
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

    def getDataLoggerDF(self):
        if 'loggerData.csv' not in os.listdir(self.path):
            self.writeTempLoggerFiles()
        return pd.read_csv('loggerData.csv')

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

    def getDataLogger(self):
        df = self.getDataLoggerDF()
        df.head()
        dataLogger = pd.DataFrame()
        dataLogger['Time date'] = df['Time']
        dataLogger['Temperature °C'] = df['Celsius(°C)']
        dataLogger.to_csv("dataLogger.csv", index=False)
        dataLogger = pd.read_csv("dataLogger.csv")
        dataLogger = self.dateSortAndReIndex(dataLogger)
        dataLogger = dataLogger.set_index('Time date')
        return dataLogger

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

        dfTemp = Logulator.getDataLogger(self).copy()
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


def main():
    temp = TempLogger()
    damp = DampLogger()
    dataLog = DataLoggerTemperatures()

    # temp.plotTemperatures()
    # damp.plotDamperPositions()
    dataLog.plotDataLoggerTemps()


if __name__ == "__main__":
    main()
