import pandas as pd
import os
import matplotlib.pyplot as plt
import shutil


class Logulator:
    """
    Takes a bunch of text files with an xls extension and tab separated data and turns them into usable csv files.
    """
    def __init__(self):
        self.all_data = pd.DataFrame()
        self.path = os.getcwd()
        self.files = os.listdir(self.path)
        self.tempDir = self.path + '/.temp/'

    def makeTempFolder(self, path):
        os.makedirs(path + './.temp/', exist_ok=True)
        return path + './.temp/'

    def deleteTempFolder(self, folder):
        shutil.rmtree(folder)

    def getFiles(self, path, suffix):
        files = [f for f in os.listdir(path) if f[-3:] == suffix]
        return files

    def xlsProcessor(self, path):
        files_xls = self.getFiles(path, 'xls')
        tempFolder = self.makeTempFolder(path)
        txtPrefixCounter = 0
        for file in files_xls:
            with open(file) as fin, open(tempFolder + str(txtPrefixCounter) + '_New_File.txt', 'w') as fout:
                for line in fin.readlines()[1:]:  # don't look at the first line
                    fout.write(line.replace('\t', ','))
                txtPrefixCounter += 1

    def txtProcessor(self, path):
        files_txt = self.getFiles(path, 'txt')
        txtPrefixCounter = 0
        for file in files_txt:
            with open(path + file) as fin, open(path + str(txtPrefixCounter) + '_final.csv', 'w') as fout:
                for line in fin:
                    fout.write(line.replace('BERTH_9_FEEDBACK,BERTH_10_FEEDBACK,',
                                            'BERTH_9_FEEDBACK,BERTH_10_FEEDBACK,NothinToSeeHere,'))
                txtPrefixCounter += 1

    def writeCSVDataToFile(self, path):
        files_csv = self.getFiles(path, 'csv')
        all_data = pd.DataFrame()

        for file in files_csv:
            data = pd.read_csv(path + file)
            all_data = all_data.append(data)

        all_data.to_csv("all_data.csv", index=False)
        shutil.rmtree(path)

    def csvProcessor(self):
        df = pd.read_csv('all_data.csv')
        df['Time date'] = pd.to_datetime(df['Time date'])
        df = df.sort_values(by='Time date')
        df = df[(df['Time date'].dt.year > 2006)]
        return df

    def temperaturDataHelper(self, df):
        """
        Creates a data frame with specific temperature data entries.
        :return:
        """
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

        if not 'temperatureData.csv' in os.listdir('./'):
            temperatureData.to_csv("temperatureData.csv", index=False)
        return temperatureData

    def temperatureData(self):
        return self.temperaturDataHelper[(self.temperaturDataHelper['Time date'].dt.year > 2006)].copy().set_index('Time date')

    def showPlot(self, df):
        df.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('HVAC Temperatures', color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        lgd = plt.legend(title='Channel', bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.savefig('myfig100.png', dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, bbox_extra_artists=(lgd,), bbox_inches='tight',
                    transparent=False, pad_inches=0.1)

        plt.show()

