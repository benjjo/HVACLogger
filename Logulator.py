import pandas as pd
import os
import matplotlib.pyplot as plt
import shutil
import numpy as np
import re


class Logulator:
    """
    Class of tools to construct and plot CSV data for MERAK HVAC logs.
    """
    coach_number = None

    def __init__(self):
        self.all_data = pd.DataFrame()
        self.path = './'
        self.temp_dir = self.path + '.temp/'
        self.version = 'Logulator Lite V5.3'
        self.coach_type = str()
        self.coach_temps_tup = tuple()
        self.base_temperatures = ['External Supply', 'SAT1', 'SAT2']
        self.seated_vars = ('Time date', 'Time date', 'Type', 'Car type', 'External Supply', 'TEMPERATURE_SUPPLY_1',
                            'SAT1', 'TEMPERATURE_SUPPLY_2', 'SAT2', 'TEMPERATURE_RETURN',
                            'Vestibule E2', 'TEMP. VESTIBULE_LEFT', 'Vestibule E1', 'TEMP. STAFF_WC',
                            'Return Air', 'TEMPERATURE_GUARD_GALLEY_WC',
                            'Guards Room', 'TEMP. BERTH_1')
        self.club_vars = ('Time date', 'Time date', 'Type', 'Car type', 'External Supply', 'TEMPERATURE_SUPPLY_1',
                          'SAT1', 'TEMPERATURE_SUPPLY_2', 'SAT2', 'TEMPERATURE_RETURN',
                          'Vestibule E2', 'TEMP. VESTIBULE_LEFT', 'Vestibule E1', 'TEMP. STAFF_WC',
                          'Return Air', 'TEMPERATURE_GUARD_GALLEY_WC',
                          'Crew Room', 'TEMP. GUARD_GALLEY_WC', 'Guards Room', 'TEMP. BERTH_1')
        self.accessible_vars = ('Time date', 'Time date', 'Type', 'Car type', 'External Supply', 'TEMPERATURE_SUPPLY_1',
                                'SAT1', 'TEMPERATURE_SUPPLY_2', 'SAT2', 'TEMPERATURE_RETURN',
                                'Vestibule E2', 'TEMP. VESTIBULE_LEFT', 'Vestibule E1', 'TEMP. STAFF_WC',
                                'Return Air', 'TEMPERATURE_GUARD_GALLEY_WC',
                                'PRM E1', 'TEMP. GUARD_GALLEY_WC', 'PRM E2', 'TEMP. BERTH_1',
                                'Berth 1', 'TEMP. BERTH_7_6', 'Berth 2', 'TEMP. BERTH_6_3',
                                'Berth 3', 'TEMP. BERTH_5_2', 'Berth 4', 'TEMP. BERTH_4',
                                'Berth 5', 'TEMP. BERTH_3_5', 'Berth 6', 'TEMP. BERTH_2_4')
        self.sleeper_vars = ('Time date', 'Time date', 'Type', 'Car type', 'External Supply', 'TEMPERATURE_SUPPLY_1',
                             'SAT1', 'TEMPERATURE_SUPPLY_2', 'SAT2', 'TEMPERATURE_RETURN',
                             'Vestibule E2', 'TEMP. VESTIBULE_LEFT', 'Vestibule E1', 'TEMP. STAFF_WC',
                             'Return Air', 'TEMPERATURE_GUARD_GALLEY_WC',
                             'Galley', 'TEMP. BERTH_1', 'STD WC', 'TEMP. GUARD_GALLEY_WC',
                             'Berth 1', 'NOT_USED_1_10', 'Berth 2', 'TEMPERATURE_BERTH_10',
                             'Berth 3', 'TEMPERATURE_BERTH_9', 'Berth 4', 'TEMPERATURE_BERTH_8',
                             'Berth 5', 'NOT_USED_1_9', 'Berth 6', 'NOT_USED_1_8', 'Berth 7', 'TEMPERATURE_BERTH_5_2',
                             'Berth 8', 'TEMPERATURE_BERTH_4', 'Berth 9', 'TEMPERATURE_BERTH_3_5',
                             'Berth 10', 'TEMPERATURE_BERTH_2_4')

    def get_version(self):
        """
        Returns the current revision of Logulator
        :return:
        """
        return self.version

    def set_coach_type(self, df: pd.DataFrame):
        try:
            self.coach_type = df['Car type'].mode().iloc[0]
        except IndexError:
            print('sǝıʇlnɔıɟɟıd lɐɔınɥɔǝʇ ƃnıʌɐɥ ǝɹɐ ǝʍ')
            input('Your data is probably from 2006 - ABORT! ABORT! ABORT!')

    def set_coach_temps_lists(self):
        """
        Setter method to update the tuple of temperature probes that are used and the list used to calculate the
        average temperature data.
        Updates:
        :return: None
        """
        if self.coach_type == 'SEATED':
            self.coach_temps_tup = self.seated_vars
        elif self.coach_type == 'CLUB':
            self.coach_temps_tup = self.club_vars
        elif self.coach_type == 'ACCESSIBLE':
            self.coach_temps_tup = self.accessible_vars
        elif self.coach_type == 'SLEEPER':
            self.coach_temps_tup = self.sleeper_vars
        else:
            print('sǝıʇlnɔıɟɟıd lɐɔınɥɔǝʇ ƃnıʌɐɥ ǝɹɐ ǝʍ')
            input('Something went terribly wrong - ABORT! ABORT! ABORT!')

    def get_coach_type(self) -> str:
        return self.coach_type

    def make_all_data_df(self):
        """
        Constructs a Pandas Data Frame from a directory of MERAK HVAC CSV files.
        Creates a file all_data.csv from a bunch of HVAC files.
        :return: Pandas Data Frame
        """

        self.make_temporary_text_files('xls')
        self.write_temporary_csv_files()
        self.read_csv_to_allData_df()
        self.write_all_data_to_csv()
        self.all_data.to_csv("all_data.csv", index=False)
        all_data_df = pd.read_csv('all_data.csv')
        self.set_coach_type(all_data_df)

        return all_data_df

    def make_temporary_text_files(self, extension):
        """
        Helper method for makeAllDataDF()
        Creates a temporary directory to store txt versions of the xls files.
        :param extension:
        :return: None
        """
        self.path = os.getcwd()
        files = os.listdir(self.path)
        os.makedirs(self.temp_dir, exist_ok=True)
        counter = 0
        for file in [f for f in files if f[-3:] == extension]:
            with open(file) as fin, open(self.temp_dir + str(counter) + '_New_File.txt', 'w') as fout:
                for line in fin.readlines()[1:]:  # don't look at the first line
                    fout.write(line.replace('\t', ','))
                counter += 1

    def write_temporary_csv_files(self):
        """
        Helper method for makeAllDataDF()
        Creates a bunch of csv files from the txt files created in makeTemporaryTXTFilesForCSV()
        These are processed specifically for the format that is produced by the train.
        :return: None
        """
        temp_files = os.listdir(self.temp_dir)
        counter = 0
        for file in [f for f in temp_files if f[-3:] == 'txt']:
            with open(self.temp_dir + file) as fin, open(self.temp_dir + str(counter) + '_final.csv', 'w') as fout:
                for line in fin:
                    fout.write(line.replace('BERTH_9_FEEDBACK,BERTH_10_FEEDBACK,',
                                            'BERTH_9_FEEDBACK,BERTH_10_FEEDBACK,NothingToSeeHere,'))
                counter += 1

    def create_datalogger_csv(self):
        """
        Creates a CSV file from the Data Logger xlsx file.
        :return:
        """
        logger_df = pd.DataFrame()
        temp_logs = pd.DataFrame()
        path = os.getcwd()
        files = os.listdir(path)
        tempDir = './.tempDL/'
        os.makedirs(tempDir, exist_ok=True)
        counter = 0
        for file in [f for f in files if f[-4:] == 'xlsx']:
            shutil.copy(file, tempDir + str(counter) + '_New_File.xlsx')
            data = pd.read_excel(tempDir + str(counter) + '_New_File.xlsx', engine='openpyxl')
            temp_logs = temp_logs.append(data)
            counter += 1
        logger_df['Time date'] = temp_logs['Time']
        logger_df['Logger Temp. °C'] = temp_logs['Celsius(°C)']
        logger_df = self.sort_by_date_and_reindex(logger_df)
        logger_df.to_csv('loggerData.csv')
        shutil.rmtree(tempDir)

    def write_all_data_to_csv(self):
        """
        Helper method for makeAllDataDF()
        Sorts the all_data DF. Removes the 2019 or less data.
        Removes the tempdir.
        :return: None
        """
        self.sort_by_date_and_reindex(self.all_data).to_csv("all_data.csv", index=False)
        self.all_data = self.all_data[(self.all_data['Time date'].dt.year > 2019)]
        shutil.rmtree(self.temp_dir)

    def read_csv_to_allData_df(self):
        """
        Helper method for makeAllDataDF()
        Reads all the csv files in the ./temp dir into a dataframe
        :return: None
        """
        temp_files = os.listdir(self.temp_dir)
        self.all_data = pd.DataFrame(None)

        for file in [f for f in temp_files if f[-3:] == 'csv']:
            data = pd.read_csv(self.temp_dir + file)
            self.all_data = self.all_data.append(data)

    def df_from_temperature_selection(self):
        count = 0
        df = pd.DataFrame()
        all_data = self.make_all_data_df()
        self.set_coach_temps_lists()
        while count < len(self.coach_temps_tup):
            df[self.coach_temps_tup[count]] = all_data[self.coach_temps_tup[count + 1]]
            count += 2
        df['Average'] = all_data[list(self.coach_temps_tup[11::2])].mean(axis=1)
        return df

    def get_temperature_data_from_allData(self):
        """
        Returns a DataFrame using the temperature sensor data from the HVAC unit.
        Makes/overwrites a temperature_data.csv file.
        :return: temperature_data of type DataFrame
        """

        temperature_data = self.df_from_temperature_selection()
        temperature_data.to_csv("temperature_data.csv", index=False)

        temperature_data = pd.read_csv("temperature_data.csv")
        temperature_data = self.sort_by_date_and_reindex(temperature_data)
        return temperature_data

    def get_data_logger_data_from_csv(self):
        """
        Returns a DataFrame using the Data Logger data.
        If there is no loggerData.csv file available, it will make one with the csv logs.
        :return: logger_df of type DataFrame
        """
        if 'loggerData.csv' not in os.listdir(self.path):
            self.create_datalogger_csv()
        logger_df = pd.read_csv('./loggerData.csv')
        logger_df['Time date'] = pd.to_datetime(logger_df['Time date'])
        logger_df = logger_df.set_index('Time date')
        logger_df = logger_df.dropna(how='any')
        logger_df = logger_df.drop(logger_df.columns[[0]], axis=1)  # Remove superfluous column
        return logger_df

    def get_damper_data_from_csv(self):
        """
        Creates a Data Frame from the MERAK csv files.
        Specifically holds the Damper position data.
        :return: Pandas Data Frame
        """
        if 'damper_data.csv' not in os.listdir(self.path):
            df = self.make_all_data_df()
            damper_data = pd.DataFrame()
            df['Time date'] = pd.to_datetime(df['Time date'])  # new entry
            damper_data['Time date'] = df['Time date']
            damper_data['Fresh Air Damper'] = df['FRESH_DAMPER_FEEDBACK']
            damper_data['Return Air Damper'] = df['RETURN_DAMPER_FEEDBACK']
            damper_data.to_csv("damper_data.csv", index=False)

        damper_data = pd.read_csv("damper_data.csv")
        damper_data = self.sort_by_date_and_reindex(damper_data)
        return damper_data

    @staticmethod
    def sort_by_date_and_reindex(df):
        """
        Helper method that sets up the Data Frame to be indexed by date.
        :param df:
        :return pd.DataFrame():
        """
        df['Time date'] = pd.to_datetime(df['Time date'])
        df = df.sort_values(by='Time date')
        df = df.reset_index(drop=True)  # Reset the index to line up with the sorted data.
        return df

    def spread_index_over_second_increments(self, set_point=22):
        """
        Makes an empty DataFrame with a index using date time incrementing by seconds.
        The date range of the index is set by the info from the data logger as this data
        is more finite than the data from the HVAC unit.
        :return: temp_comparison of type DataFrame
        """
        df = self.get_temperature_data_from_allData()  # Makes a DF using the HVAC sensor data
        logger_data = self.get_data_logger_data_from_csv()  # Makes a DF using the Data Logger data
        start_date = logger_data.index[0]
        end_date = logger_data.index[-1]
        index = pd.date_range(start_date, end=end_date, freq='S')
        columns = ['Set Point']
        temp_comparison = pd.DataFrame(index=index, columns=columns)
        temp_comparison['Set Point'] = temp_comparison['Set Point'].fillna(set_point)
        temperature_data = df[(df['Time date'] >= logger_data.index[0]) &
                              (df['Time date'] <= logger_data.index[-1])].copy().set_index('Time date')
        temp_comparison = logger_data.combine_first(temp_comparison)
        temp_comparison = temperature_data.combine_first(temp_comparison)
        return temp_comparison

    @classmethod
    def get_coach_number(cls):
        return Logulator.coach_number

    @classmethod
    def set_coach_number(cls, number):
        Logulator.coach_number = number


class TempLogger(Logulator):
    def plot_coach_temperatures(self):
        """
        Plots all the temperatures.
        :return:
        """
        temperatureData = Logulator.get_temperature_data_from_allData(self)

        title_suffix = Logulator.get_coach_number()
        if title_suffix == '':
            title_suffix = Logulator.get_coach_type(self)

        df_temp = temperatureData.copy().set_index('Time date')
        ax = df_temp[list(self.coach_temps_tup[2::2])].plot(kind='line')
        df_temp['Average'].plot(kind='line', linestyle=':', ax=ax)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('HVAC Temperatures: ' + title_suffix, color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.legend(title='Sensor')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.get_version(self))
        image_name = (title_suffix + '_' + str(df_temp.index[-1]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(image_name, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()

    def plot_one_temperature_sensor(self, sensor=0):
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
                   6: 'Guards Control Room',
                   7: 'Average'}
        sensors_caf = {1: '71B01', 2: '71B02', 3: '71B03', 4: '71B04', 5: '71B05', 6: '71B06', 7: 'Average'}
        sensor_to_test = sensors[sensor]
        title = sensor_to_test + ' ' + sensors_caf[sensor]
        df = pd.DataFrame()
        df['Time date'] = Logulator.get_temperature_data_from_allData(self)['Time date']
        df[sensors[sensor]] = Logulator.get_temperature_data_from_allData(self)[sensors[sensor]]
        df['Logger Data'] = np.nan

        logger_data = self.get_data_logger_data_from_csv()  # Makes a DF using the Data Logger data
        df_temp = df[(df['Time date'] >= logger_data.index[0]) &
                     (df['Time date'] <= logger_data.index[-1])].copy().set_index('Time date')
        df_temp.plot(kind='line')
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title(title + ' to data logger', color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.legend(title='Sensor')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.get_version(self))
        image_name = (title + str(df_temp.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(image_name, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()


class DampLogger(Logulator):
    def plot_damper_positions(self):
        """
        Plots the MERAK damper position data.
        :return:
        """
        damper_data = Logulator.get_damper_data_from_csv(self)

        df_temp = damper_data.copy().set_index('Time date')
        df_temp.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('HVAC Temperatures', color='C0')
        plt.ylabel('% Percentage Open', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.legend(title='Damper Position %')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.get_version(self))
        imageName = ('Damper Position Data ' + str(df_temp.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(imageName, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()

    def plot_damper_and_temperature_data(self):
        """
        Plots the Damper positions over the top of the temperature data.
        :return:
        """
        df_temp = Logulator.get_temperature_data_from_allData(self).set_index('Time date')
        damper = Logulator.get_damper_data_from_csv(self).set_index('Time date')

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()

        ax1.set_xlabel('Date Time', color='C0')
        ax1.set_ylabel('Temperatures', color='C0')
        ax2.set_ylabel('Damper position %', color='C0')
        ax1.tick_params(axis='x', labelcolor='C0', labelrotation=90)
        ax1.tick_params(axis='y', labelcolor='C0')
        ax2.tick_params(axis='y', labelcolor='C0')

        ax1.plot(df_temp, label='Temperature supply')
        ax2.plot(damper, label='Damper')

        plt.get_current_fig_manager().canvas.set_window_title(Logulator.get_version(self))
        plt.title('Damper position & HVAC Temperatures', color='C0')
        plt.grid('on', linestyle='--')

        plt.show()


class DataLoggerTemperatures(Logulator):
    def plot_data_logger_temperatures(self):
        """
        Plots the Data Logger files.
        :return:
        """
        df_temp = Logulator.get_data_logger_data_from_csv(self).copy()
        df_temp.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('Data Logger Temperatures', color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')

        plt.legend(title='Input Sensor')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.get_version(self))
        image_name = ('Data Logger ' + str(df_temp.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(image_name, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()

    def plot_data_logger_against_HVAC(self, sensor=0):
        """
        Plots the data logger file over the top of the MERAK data for the same time period.
        :param sensor:
        :return:
        """
        sensor = int(sensor)
        sensors = {1: 'Dining Floor Return', 2: 'External Grill Supply', 3: 'Vestibule E1',
                   4: 'Vestibule E2', 5: 'Guards Rest Room', 6: 'Guards Control Room'}
        sensors_CAF = {1: '71B01', 2: '71B02', 3: '71B03', 4: '71B04', 5: '71B05', 6: '71B06'}
        sensor_to_test = sensors[sensor]
        title = sensor_to_test + ' ' + sensors_CAF[sensor]

        df_temps = pd.DataFrame()
        temp_comparison = Logulator.spread_index_over_second_increments(self)

        df_temps['Logger Temps. °C'] = temp_comparison['Logger Temp. °C'].ffill()
        df_temps['HVAC Temps. °C'] = temp_comparison[sensor_to_test].ffill()
        df_temps['Set Point'] = temp_comparison['Set Point']
        df_temps.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time date', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title(title, color='C0')
        plt.ylabel('Temperature', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.legend(title='Input Sensor')
        plt.get_current_fig_manager().canvas.set_window_title(Logulator.get_version(self))
        image_name = (title + ' ' + str(df_temps.index[0]) + '.png').replace(' ', '_').replace(':', '')
        plt.savefig(image_name, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()


def print_sensor_choices():
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
    path = os.getcwd()
    try:
        coach = re.findall("15...", path)[0]
    except IndexError:
        coach = 'Caledonian'
    choice = input("Type the Coach number or just ENTER for [" + coach + "]") or coach
    os.system('cls')
    Logulator.set_coach_number(choice)
    temp.plot_coach_temperatures()


if __name__ == "__main__":
    main()
