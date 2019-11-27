# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 09:30:56 2019

@author: pierre
"""

import matplotlib.pyplot as plt
import csv
import numpy as np
import scipy.stats as stat
import statistics as st
from math import *
time=[]
Q1=[] #Gender
Q2=[] #Student ?
Q3=[]# age range
Q4=[]#previous xp working
Q5=[]#previous xp playing
#autonomous part
Q6=[]#complete autonomous game
Q7=[]#how long autonomous
Q8=[]#enjoyable ?
Q9=[]#engagement
Q10=[]#entertaining
Q11=[]#intelligence
Q12=[]#friendly
Q13=[]#interaction with bob
#cooperative part
Q14=[]#complete cooperative game
Q15=[]#how long cooperative
Q16=[]#enjoyable ?
Q17=[]#engagement
Q18=[]#entertaining
Q19=[]#intelligence
Q20=[]#friendly
Q21=[]#interaction with bob
#Resview
Q22=[]#did you have enough time ?
Q23=[]#Which game prefered
Q24=[]#overall interactions
Q25=[]#future approach on robot






with open('HRI Study - Bob Games_22_11_20.csv') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    for row in csv_reader:
        Q1.append(row["Gender?"])
        Q2.append(row['Highest level of qualification'])
        Q3.append(row['Please select your age range'])
        Q4.append(row['How much previous experience do you have working with robots?'])
        Q5.append(row['How much previous experience do you have playing with robots?'])
        #remaped data
        if row['Did Bob complete the autonomous game? ']=='Yes':
            Q6.append(1)
        elif row['Did Bob complete the autonomous game? ']=='No':
            Q6.append(0)
        else:
            Q6.append(2)
        
        Q7.append(float(row["How long did Bob's autonomous game take to complete? (Time seconds)"]))
        Q8.append(float(row['Was the autonomous game enjoyable?']))
        Q9.append(float(row['Please rate the game engagement']))
        Q10.append(float(row["Was Bob's behaviour entertaining?"]))
        Q11.append(float(row["How would you rate Bob's intelligence in the autonomous game?"]))
        Q12.append(float(row['Was Bob friendly in the autonomous game?']))
        Q13.append(float(row['How would you rate the interaction level of Bob autonomous?']))
        #remaped data
        if row['Were you able to complete the game with Bob?']=='Yes':
            Q14.append(1)
        elif row['Were you able to complete the game with Bob?']=='No':
            Q14.append(0)
        else:
            Q14.append(2)
        Q15.append(float(row['How long did it take to complete the cooperative game? (Time in seconds)']))
        Q16.append(float(row['How enjoyable did you find the cooperative game?']))
        Q17.append(float(row['Please rate the cooperative games engagement']))
        Q18.append(float(row["Was Bob's behaviour entertaining in the cooperative game?"]))
        Q19.append(float(row["How would you rate Bob's intelligence during the cooperative game?"]))
        Q20.append(float(row['Was Bob friendly during the cooperative game']))
        Q21.append(float(row['How would you rate the interaction level of Bob?']))
        Q22.append(row['Did you have enough time to complete the cooperative game?'])
        Q23.append(row['Which game did you prefer?'])
        Q24.append(row['Did you find the overall interactions with Bob a pleasant experience?'])
        Q25.append(row['Having played the games with Bob will this change how you approach future engagement with robots?'])

def ttest(Qx,Qy):
    return abs(t(stat.mode(Qx).mode[0],stat.mode(Qy).mode[0],S(Qx,stat.mode(Qx).mode[0],len(Qx)),S(Qy,stat.mode(Qy).mode[0],len(Qy)),len(Qx),len(Qy)))
def t(Mx,My,Sx,Sy,nx,ny):
    return (Mx-My)/np.sqrt(Sx/nx+Sy/ny)
def S(x,M,n):
    Sum=0
    for i in range(len(x)):
        Sum+=(x[i]-M)
    return Sum**2/(n-1)

#T test
Q715=stat.ttest_ind(Q7,Q15)

#Wilcoxon rank sum
Q816=stat.ranksums(Q8,Q16)
Q917=stat.ranksums(Q9,Q17)
Q1018=stat.ranksums(Q10,Q18)
Q1119=stat.ranksums(Q11,Q19)       
Q1220=stat.ranksums(Q12,Q20)
Q1321=stat.ranksums(Q13,Q21)

print ("Wilcoxon rank sum")

print("pvalues")
print (Q715.pvalue)
print (Q816.pvalue)
print (Q917.pvalue)
print (Q1018.pvalue)
print (Q1119.pvalue)
print (Q1220.pvalue)
print (Q1321.pvalue)  

print("statistic")
print (Q715.statistic)
print (Q816.statistic)
print (Q917.statistic)
print (Q1018.statistic)
print (Q1119.statistic)
print (Q1220.statistic)
print (Q1321.statistic) 


print("-----Results of comparison between autonomous and cooperative-----\n")
print("Wilcoxon rank sum\n")
print("\nDuration ?") 
if Q715.pvalue<0.1:
    print("the two games are different")
else:
    print("the two games are simillar")
    
print("\nEnjoyable ?")
if Q816.pvalue<0.1:
    print("the two games are different")
else:
    print("the two games are simillar")
    
print('\nEngaging ?')
if Q917.pvalue<0.1:
    print("the two games are different")
else:
    print("the two games are simillar")
    
print('\nEntertaining ?')
if Q1018.pvalue<0.1:
    print("the two games are different")
else:
    print("the two games are simillar")
    
print("\nIntelligence ?")
if Q1119.pvalue<0.1:
    print("the two games are different")
else:
    print("the two games are simillar")
    
print("\nFriendly ?")
if Q1220.pvalue<0.1:
    print("the two games are different")
else:
    print("the two games are simillar")
    
print('\nInteraction Level ?')
if Q1321.pvalue<0.1:
    print("the two games are different")
else:
    print("the two games are simillar")


###### Pie Chart#######


plt.figure(1)
labels=[]
sizes=[]
for i in range(14):
    if not(Q8.count(i)==0):
        sizes+=[Q8.count(i)]
        labels += [str(i)]


plt.subplot(2, 2, 1)
plt.title("Likert Scale Responses\n for autonomous game")

plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')


labels=[]
sizes=[]
for i in range(14):
    if not(Q16.count(i)==0):
        sizes+=[Q16.count(i)]
        labels += [str(i)]
plt.ylabel('Enjoyable')
plt.subplot(2,2,2)
plt.title("Likert Scale Responses\n for cooperative game")
plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')

plt.figure(2)
labels=[]
sizes=[]
for i in range(14):
    if not(Q9.count(i)==0):
        sizes+=[Q9.count(i)]
        labels += [str(i)]


plt.subplot(2, 2, 1)
plt.title("Likert Scale Responses\n for autonomous game")

plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')


labels=[]
sizes=[]
for i in range(14):
    if not(Q17.count(i)==0):
        sizes+=[Q17.count(i)]
        labels += [str(i)]
plt.ylabel('Engaging')
plt.subplot(2,2,2)
plt.title("Likert Scale Responses\n for cooperative game")
plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')

plt.figure(3)
labels=[]
sizes=[]
for i in range(14):
    if not(Q10.count(i)==0):
        sizes+=[Q10.count(i)]
        labels += [str(i)]


plt.subplot(2, 2, 1)
plt.title("Likert Scale Responses\n for autonomous game")

plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')


labels=[]
sizes=[]
for i in range(14):
    if not(Q18.count(i)==0):
        sizes+=[Q18.count(i)]
        labels += [str(i)]
plt.ylabel('Entertainment')
plt.subplot(2,2,2)
plt.title("Likert Scale Responses\n for cooperative game")
plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')

plt.figure(4)
labels=[]
sizes=[]
for i in range(14):
    if not(Q11.count(i)==0):
        sizes+=[Q11.count(i)]
        labels += [str(i)]


plt.subplot(2, 2, 1)
plt.title("Likert Scale Responses\n for autonomous game")

plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')


labels=[]
sizes=[]
for i in range(14):
    if not(Q19.count(i)==0):
        sizes+=[Q19.count(i)]
        labels += [str(i)]
plt.ylabel('Intelligence of Cozmo')
plt.subplot(2,2,2)
plt.title("Likert Scale Responses\n for cooperative game")
plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)

plt.axis('equal')

plt.figure(5)
labels=[]
sizes=[]
for i in range(14):
    if not(Q12.count(i)==0):
        sizes+=[Q12.count(i)]
        labels += [str(i)]


plt.subplot(2, 2, 1)
plt.title("Likert Scale Responses\n for autonomous game")

plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')


labels=[]
sizes=[]
for i in range(14):
    if not(Q20.count(i)==0):
        sizes+=[Q20.count(i)]
        labels += [str(i)]
plt.ylabel('Friendliness')
plt.subplot(2,2,2)
plt.title("Likert Scale Responses\n for cooperative game")
plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')

plt.figure(6)
labels=[]
sizes=[]
for i in range(14):
    if not(Q13.count(i)==0):
        sizes+=[Q13.count(i)]
        labels += [str(i)]


plt.subplot(2, 2, 1)
plt.title("Likert Scale Responses\n for autonomous game")

plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')


labels=[]
sizes=[]
for i in range(14):
    if not(Q21.count(i)==0):
        sizes+=[Q21.count(i)]
        labels += [str(i)]
plt.ylabel('Interaction Level')
plt.subplot(2,2,2)
plt.title("Likert Scale Responses\n for cooperative game")
plt.pie(sizes,  labels=labels, 
autopct='%1.1f%%', shadow=True, startangle=0)
plt.axis('equal')

plt.figure(8)
plt.ylabel('duration (s)')
plt.xlabel('autonomous                                      cooperative')
plt.boxplot([Q7,Q15], showfliers=True)

index=[]
for i in range(len(Q7)-1):
    if Q7[i]>60:
        index+=[i]
index.reverse()
for i in index:
    Q7.pop(i)
    Q15.pop(i)

newQ7Q15=stat.ttest_ind(Q7,Q15)
print (newQ7Q15.statistic)
print(newQ7Q15.pvalue)
plt.show()