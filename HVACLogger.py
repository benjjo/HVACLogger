import pandas as pd
import os
import matplotlib.pyplot as plt
import shutil

"""
Takes a bunch of text files with an xls extension and tab separated data and turns them into usable csv files.
"""
all_data = pd.DataFrame()

path = os.getcwd()
files = os.listdir(path)
os.makedirs(path + './.temp/', exist_ok=True)
tempDir = path + '/.temp/'
files_xls = [f for f in files if f[-3:] == 'xls']

counter = 0
for file in files_xls:
    with open(file) as fin, open('./.temp/' + str(counter) + '_New_File.txt', 'w') as fout:
        for line in fin.readlines()[1:]:  # don't look at the first line
            fout.write(line.replace('\t', ','))
        counter += 1

tempDir = path + '/.temp/'
tempFiles = os.listdir(tempDir)

files_txt = [f for f in tempFiles if f[-3:] == 'txt']

counter = 0
for file in files_txt:
    with open(tempDir + file) as fin, open('./.temp/' + str(counter) + '_final.csv', 'w') as fout:
        for line in fin:
            fout.write(line.replace('BERTH_9_FEEDBACK,BERTH_10_FEEDBACK,',
                                    'BERTH_9_FEEDBACK,BERTH_10_FEEDBACK,NothinToSeeHere,'))
        counter += 1

tempFiles = os.listdir(tempDir)
files_csv = [f for f in tempFiles if f[-3:] == 'csv']

for file in files_csv:
    data = pd.read_csv(tempDir + file)
    all_data = all_data.append(data)

all_data.to_csv("all_data.csv", index=False)
shutil.rmtree(tempDir)

df = pd.read_csv('all_data.csv')

df['Time date'] = pd.to_datetime(df['Time date'])
df = df.sort_values(by='Time date')
df = df[(df['Time date'].dt.year > 2006)]

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

df = temperatureData[(temperatureData['Time date'].dt.year > 2006)].copy().set_index('Time date')
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