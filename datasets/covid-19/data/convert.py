#!/usr/bin/python3
import csv

files = [
         # "mod_time_series_covid19_recovered_global.csv",
         # "mod_time_series_covid19_deaths_US.csv",
         # "mod_time_series_covid19_deaths_global.csv",
         # "mod_time_series_covid19_confirmed_US.csv",
         "mod_time_series_covid19_confirmed_global.csv"
         ]

def diffs():
    for f in files:
        with open(f, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',')
            previous = next(datareader)
            diff = []
            for row in datareader:
                temp = []
                for i in range(len(row)):
                    temp.append(int(row[i]) - int(previous[i]))

                diff.append(temp)
                previous = row

        with open('diff_{}'.format(f), 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=',')
            datawriter.writerows(diff)

def aggregatedDiffs():
    aggregate = 7
    for f in files:
        with open(f, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',')
            previous = next(datareader)
            diff = []
            count = 0
            temp = []
            for row in datareader:
                if not temp:
                    temp = [0 for i in range(len(row))]

                for i in range(len(row)):
                    temp[i] += int(row[i]) - int(previous[i])

                previous = row
                count += 1

                if count % aggregate == 0:
                    diff.append(temp)
                    temp = []

        with open('week_diff_{}'.format(f), 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=',')
            datawriter.writerows(diff)

def mergedDiffs():
    aggregate = 7
    for f in files:
        with open(f, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',')
            previous = next(datareader)
            diff = []
            temp = []
            count = 0
            for row in datareader:
                for i in range(len(row)):
                    temp.append(int(row[i]) - int(previous[i]))

                previous = row
                count += 1

                if count % aggregate == 0:
                    diff.append(temp)
                    temp = []

        with open('weekMerged_diff_{}'.format(f), 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=',')
            datawriter.writerows(diff)

def concatenateWeek():
    aggregate = 7
    for f in files:
        with open(f, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',')
            temp = []
            data =[]
            count = 0
            for row in datareader:
                for i in range(len(row)):
                    temp.append(int(row[i]))

                count += 1

                if count % aggregate == 0:
                    data.append(temp)
                    temp = []

        with open('weekConcatenate_{}'.format(f), 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=',')
            datawriter.writerows(data)

#diffs()
#aggregatedDiffs()
mergedDiffs()
#concatenateWeek()
