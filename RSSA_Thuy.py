import pandas as pd
import numpy as np
import itertools
import numpy.ma as ma
from datetime import datetime
start=datetime.now()
# the preferential table for day-off of official employees
df = pd.read_excel("PickingNightRule.xlsx", sheet_name=None)
tSchedule = df["Schedule"].set_index("Em")
tOff = df["Off"].set_index("Em")
tRequire = df["Require"].set_index("Day")
print(tOff, tSchedule, tRequire, sep="\n")

#set up the matrix for final schedule
totalEm = len(df["Schedule"].Em)
schedule = np.zeros((totalEm, 7))

#-----------------------------------------#
#start scheduling for official employees
#try to satisfy their desire
#-----------------------------------------#
# 7 scenarios for day-off
assumeDayOff = 1 - np.eye(7, 7)

#function condition to schedule Day-off for official employees
def findDayOffEmTier0(currentSchedule, currentRequire, desiredDayOff):
    # 7 scenarios for day-off that requirement may reduce
    requireAfterDayOff = currentRequire - assumeDayOff
    #standard deviation for each scenario
    stds = requireAfterDayOff.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation
    smallestStds = np.isclose(stds, stds.min())
    # if the desire of the official employeehe has the smallest standard deviation => choose
    # otherwise choose the first scenario of "dayOff" having the smallest standard deviation
    if smallestStds[desiredDayOff.Register - 1]:
        dayOff = assumeDayOff[desiredDayOff.Register - 1]
    else:
        dayOff = assumeDayOff[smallestStds.argmax()]
    #finish scheduling for the official employee
    currentSchedule[0] = dayOff
    currentRequire = currentRequire - dayOff
    return currentSchedule, currentRequire

#-----------------------------------------#
#start scheduling for 2-day-contract temporary employees
#the more consecutive days, the better convenience
#-----------------------------------------#
# print 21 scenarios for 2-day-contract temporary employees
which = np.array(list(itertools.combinations(range(7), 2)))
assumeTwoDays = np.zeros((len(which), 7))
assumeTwoDays[np.arange(len(which))[None].T, which] = 1

#print the specific table for only 2 consecutive days (6 scenarios)
days = ma.make_mask(assumeTwoDays)
results2= []
for index, row in enumerate(days):
    consecutive_days = 0
    for day in row:
        if day:
            consecutive_days += 1
            if consecutive_days == 2:
                results2.append(row)
        else:
            consecutive_days = 0
results2= np.array(results2)
assumeTwoCons = results2*1

#function condition to schedule 2-day-contract employees
def find2ConsEmTier0(currentSchedule, currentRequire, smallestDev2):
    # all scenarios for 2-day-contract that requirement may reduce
    requireAfterTwoDays = currentRequire - assumeTwoDays
    requireAfterTwoCons = currentRequire - assumeTwoCons
    #standard deviation for each scenario (21 scenarios)
    stds2 = requireAfterTwoDays.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation comparing with the full array of 21 scenarios (stds2)
    smallestStds2 = np.isclose(stds2, stds2.min())
    #standard deviation for each 2-consecutive-day scenario only(6 scenarios)
    dev2 = requireAfterTwoCons.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation comparing with the full array of 21 scenarios (stds2)
    smallestDev2 = np.isclose(dev2, stds2.min())
    # if the 2-consecutive-day scenario has the smallest standard deviation => choose
    # otherwise choose the first scenario of "twocons" having the smallest standard deviation
    if smallestDev2.argmax():
        twoWorkDays = assumeTwoCons[smallestDev2.argmax()]
    else:
        twoWorkDays = assumeTwoDays[smallestStds2.argmax()]
    
    currentSchedule[0] = twoWorkDays
    currentRequire = currentRequire - twoWorkDays
    return currentSchedule, currentRequire
#-----------------------------------------#
#start scheduling for 3-day-contract temporary employees
#the more consecutive days, the better convenience
#-----------------------------------------#
# print 35 scenarios for 3-day-contract temporary employees
which = np.array(list(itertools.combinations(range(7), 3)))
assumeThreeDays = np.zeros((len(which), 7))
assumeThreeDays[np.arange(len(which))[None].T, which] = 1

#print the specific table for only 3 consecutive days (5 scenarios)
days = ma.make_mask(assumeThreeDays)
results3 = []
for index, row in enumerate(days):
    consecutive_days = 0
    for day in row:
        if day:
            consecutive_days += 1
            if consecutive_days == 3:
                results3.append(row)
        else:
            consecutive_days = 0
results3 = np.array(results3)
assumeThreeCons = results3*1

#print the specific table for at least 2 consecutive days
days = ma.make_mask(assumeThreeDays)
results3 = []
for index, row in enumerate(days):
    consecutive_days = 0
    for day in row:
        if day:
            consecutive_days += 1
            if consecutive_days == 2:
                results3.append(row)
        else:
            consecutive_days = 0
results3 = np.array(results3)
assumeAtLeastTwoCons = results3*1

#function condition to schedule 3-day-contract employees
def find3ConsEmTier0(currentSchedule, currentRequire, smallestDev3):
    # all scenarios for 3-day-contract that requirement may reduce
    requireAfterThreeDays = currentRequire - assumeThreeDays
    requireAfterThreeCons = currentRequire - assumeThreeCons
    requireAfterAtLeastTwoCons = currentRequire - assumeAtLeastTwoCons
    #standard deviation for each scenario (35 scenarios)
    stds3 = requireAfterThreeDays.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation comparing with the full array of 35 scenarios (stds3)
    smallestStds3 = np.isclose(stds3, stds3.min())
    #standard deviation for each 3-consecutive-day scenario only(5 scenarios)
    dev3 = requireAfterThreeCons.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation comparing with the full array of 35 scenarios (stds3)
    smallestDev3 = np.isclose(dev3, stds3.min())
    #standard deviation for at least 2-consecutive-day scenario
    arr3 = requireAfterAtLeastTwoCons.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation comparing with the full array of 35 scenarios (stds3)
    smallestArr3 = np.isclose(arr3, stds3.min())
    # if the 3-consecutive-day scenario has the smallest standard deviation => choose
    # else if at least 2-consecutive-day scenario has the smallest standard deviation => choose
    # otherwise choose the first scenario of "threecons" having the smallest standard deviation
    if smallestDev3.argmax():
        threeWorkDays = assumeThreeCons[smallestDev3.argmax()]
    elif smallestArr3.argmax():
        threeWorkDays = assumeAtLeastTwoCons[smallestArr3.argmax()]
    else:
        threeWorkDays = assumeThreeDays[smallestStds3.argmax()]
    
    currentSchedule[0] = threeWorkDays
    currentRequire = currentRequire - threeWorkDays
    return currentSchedule, currentRequire
#-----------------------------------------#
#start scheduling for 5-day-contract temporary employees
#the more consecutive days, the better convenience
#-----------------------------------------#
# print 21 scenarios for 5-day-contract temporary employees
which = np.array(list(itertools.combinations(range(7), 5)))
assumeFiveDays = np.zeros((len(which), 7))
assumeFiveDays[np.arange(len(which))[None].T, which] = 1

#print the specific table for only 5 consecutive days (3 scenarios)
days = ma.make_mask(assumeFiveDays)
results5 = []
for index, row in enumerate(days):
    consecutive_days = 0
    for day in row:
        if day:
            consecutive_days += 1
            if consecutive_days == 5:
                results5.append(row)
        else:
            consecutive_days = 0
results5 = np.array(results5)
assumeFiveCons = results5*1

#print the specific table for only 5 consecutive days (3 scenarios)
days = ma.make_mask(assumeFiveDays)
results5 = []
for index, row in enumerate(days):
    consecutive_days = 0
    for day in row:
        if day:
            consecutive_days += 1
            if consecutive_days == 4:
                results5.append(row)
        else:
            consecutive_days = 0
results5 = np.array(results5)
assumeAtLeastFourCons = results5*1

#print the specific table for only 5 consecutive days (3 scenarios)
days = ma.make_mask(assumeFiveDays)
results5 = []
for index, row in enumerate(days):
    consecutive_days = 0
    for day in row:
        if day:
            consecutive_days += 1
            if consecutive_days == 3:
                results5.append(row)
        else:
            consecutive_days = 0
results5 = np.array(results5)
assumeAtLeastThreeCons = results5*1

#function condition to schedule 5-day-contract employees
def find5ConsEmTier0(currentSchedule, currentRequire, smallestDev5):
    # all scenarios for 5-day-contract that requirement may reduce
    requireAfterFiveDays = currentRequire - assumeFiveDays
    requireAfterFiveCons = currentRequire - assumeFiveCons
    requireAfterAtLeastFourCons = currentRequire - assumeAtLeastFourCons
    requireAfterAtLeastThreeCons = currentRequire - assumeAtLeastThreeCons
    #standard deviation for each scenario (21 scenarios)
    stds5 = requireAfterFiveDays.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation comparing with the full array of 21 scenarios (stds5)
    smallestStds5 = np.isclose(stds5, stds5.min())
    #standard deviation for each 5-consecutive-day scenario only(3 scenarios)
    dev5 = requireAfterFiveCons.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation comparing with the full array of 21 scenarios (stds5)
    smallestDev5 = np.isclose(dev5, stds5.min())
    #standard deviation for at least 4-consecutive-day scenario
    alf5 = requireAfterAtLeastFourCons.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation comparing with the full array of 21 scenarios (stds5)
    smallestAlf5 = np.isclose(alf5, stds5.min())
    #standard deviation for at least 3-consecutive-day scenario
    alt5 = requireAfterAtLeastThreeCons.std(axis=1, keepdims=True)
    #check which senario has the smallest standard deviation comparing with the full array of 21 scenarios (stds5)
    smallestAlt5 = np.isclose(alt5, stds5.min())
    # if the 5-consecutive-day scenario has the smallest standard deviation => choose
    # else if at least 4-consecutive-day scenario has the smallest standard deviation => choose
    # else if at least 3-consecutive-day scenario has the smallest standard deviation => choose
    # otherwise choose the first scenario of "fivecons" having the smallest standard deviation
    if smallestDev5.argmax():
        fiveWorkDays = assumeFiveCons[smallestDev5.argmax()]
    elif smallestAlf5.argmax():
        fiveWorkDays = assumeAtLeastFourCons[smallestAlf5.argmax()]
    elif smallestAlt5.argmax():
        fiveWorkDays = assumeAtLeastThreeCons[smallestAlt5.argmax()]
    else:
        fiveWorkDays = assumeFiveDays[smallestStds5.argmax()]
    
    currentSchedule[0] = fiveWorkDays
    currentRequire = currentRequire - fiveWorkDays
    return currentSchedule, currentRequire
#-----------------------------------------#
#The main loop to schedule all employees
#-----------------------------------------#
currentRequire = tRequire.Require.to_numpy()

for index, employee in df["Schedule"].iterrows():
    #if that worker is an offcial employee
    if employee.Type == 0:
        currentSchedule = schedule[index:]
        desireDayOff = tOff.loc[employee.Em]
        currentSchedule, currentRequire = findDayOffEmTier0(
            currentSchedule,
            currentRequire,
            desireDayOff            
        )        
        schedule[index:] = currentSchedule
        
    #else if that worker is 5-day-contract 
    elif employee.Type == 1:
        currentSchedule = schedule[index:]
        desireFiveWorkDays  = assumeFiveCons
        currentSchedule, currentRequire = find5ConsEmTier0(
            currentSchedule,
            currentRequire,
            desireFiveWorkDays           
        )        
        schedule[index:] = currentSchedule
    #else if that worker is 3-day-contract    
    elif employee.Type == 2:
        currentSchedule = schedule[index:]
        desireThreeWorkDays = assumeThreeCons
        currentSchedule, currentRequire = find3ConsEmTier0(
            currentSchedule,
            currentRequire,
            desireThreeWorkDays           
        )        
        schedule[index:] = currentSchedule
    #else that worker is 2-day-contract    
    else:
        currentSchedule = schedule[index:]
        desireTwoWorkDays = assumeTwoCons
        currentSchedule, currentRequire = find2ConsEmTier0(
            currentSchedule,
            currentRequire,
            desireTwoWorkDays               
        )        
        schedule[index:] = currentSchedule
    # #else if that worker is 2-day-contract 
    # elif employee.Type == 1:
    #     currentSchedule = schedule[index:]
    #     desireTwoWorkDays = assumeTwoCons
    #     currentSchedule, currentRequire = find2ConsEmTier0(
    #         currentSchedule,
    #         currentRequire,
    #         desireTwoWorkDays           
    #     )        
    #     schedule[index:] = currentSchedule
    # #else if that worker is 3-day-contract    
    # elif employee.Type == 2:
    #     currentSchedule = schedule[index:]
    #     desireThreeWorkDays = assumeThreeCons
    #     currentSchedule, currentRequire = find3ConsEmTier0(
    #         currentSchedule,
    #         currentRequire,
    #         desireThreeWorkDays           
    #     )        
    #     schedule[index:] = currentSchedule
    # #else that worker is 5-day-contract    
    # else:
    #     currentSchedule = schedule[index:]
    #     desireFiveWorkDays  = assumeFiveCons
    #     currentSchedule, currentRequire = find5ConsEmTier0(
    #         currentSchedule,
    #         currentRequire,
    #         desireFiveWorkDays           
    #     )        
        schedule[index:] = currentSchedule
def excel_like_print(arr):
    print("\n".join(["\t".join(row.astype(int).astype(str)) for row in arr]))
print("The schedule is:")
print(schedule)
print("The current Require is:")
print( currentRequire, sep="\n")
print ("The running time is:",datetime.now()-start)
print("================")
excel_like_print(schedule)
