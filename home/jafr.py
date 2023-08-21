import os
import sys
import json
import datetime
import re

def main():
    todaysTask = []
    threeDaysTask = []
    todaysMeeting = []
    oneWeeksMeeting = []
    today = datetime.datetime.today().date()
    threeDaysLater = today + datetime.timedelta(days=3)
    oneWeekLater = today + datetime.timedelta(days=7)

    with open("tasks.md", "r") as taskFile:
        taskLines = taskFile.readlines()
        taskFile.close()

    for line in taskLines:
        if "Due:" and "not complete" in line:
            task = line.split("-")[1].split("Due:")[0].strip()
            due = line.split("Due:")[1].split("not complete")[0].strip()
            dueDate = datetime.datetime.strptime(due, "%d/%m/%y").date()
            if dueDate == today:
                todaysTask.append(task)
            elif today < dueDate <= threeDaysLater:
                threeDaysTask.append(task + " by " + due)

    print("Just a friendly reminder! You have these tasks to finish today.")
    for task in todaysTask:
        print("- "+task)

    print("These tasks need to be finished in the next three days!")
    for task in threeDaysTask:
        print("- "+task)

    with open("meetings.md", "r") as meetingFile:
        meetingLines = meetingFile.readlines()
        meetingFile.close()

    for line in meetingLines:
        if "Scheduled:" in line:
            meeting = line.split("-")[1].split("Scheduled:")[0].strip()
            time, date = line.split("Scheduled:")[1].strip().split()
            meeting_date = datetime.datetime.strptime(date, "%d/%m/%y").date()
            if today == meeting_date:
                todaysMeeting.append(f"{meeting} at {time}")
            if today < meeting_date <= oneWeekLater:
                oneWeeksMeeting.append(f"{meeting} on {date} at {time}")

    print("You have the following meetings today!")
    for meeting in todaysMeeting:
        print("- "+meeting)

    print("You have the following meetings scheduled over the next week!")
    for meeting in oneWeeksMeeting:
        print("- "+meeting)

    with open("passwd") as passwdFile:
        passwdLines = passwdFile.readlines()
        passwdFile.close()

    userIDtoNameDic = {}
    userIDtoHomeDic = {}
    for userPasswd in passwdLines:
        userID = userPasswd.split(":")[2]
        userHome = userPasswd.split(":")[5]
        userName = userPasswd.split(":")[0]
        userIDtoNameDic[userID] = userName
        userIDtoHomeDic[userID] = userHome

    idx = 0
    while idx != 6:
        print("What would you like to do?\n"
          "1. Complete tasks\n"
          "2. Add a new meeting.\n"
          "3. Share a task.\n"
          "4. Share a meeting.\n"
          "5. Change Jafr's master directory.\n"
          "6. Exit")
        idx = int(input())

        if idx == 5:
            print("Which directory would you like Jafr to use?")
            absPath = input()

            with open(".jafr/user-settings.json", "r") as js:
                data = json.load(js)
            data['master'] = absPath
            with open(".jafr/user-settings.json", "w") as js:
                json.dump(data, js, indent=4)

            print("Master directory changed to "+absPath)

        if idx == 1:
            uncompletedTasks = {}
            taskCounter = 1
            print("Which task(s) would you like to mark as completed?")
            for n, line in enumerate(taskLines):
                if "not complete" in line:
                    task = line.split("-")[1].split("Due:")[0].strip()
                    due = line.split("Due:")[1].split("not complete")[0].strip()
                    print(str(taskCounter) + ". " + task + " by " + due)
                    uncompletedTasks[taskCounter] = n
                    taskCounter += 1
            toBeCompletedIndices = list(map(int, input().split()))

            for taskNum in toBeCompletedIndices:
                if taskNum in uncompletedTasks:
                    originalIndex = uncompletedTasks[taskNum]  # 从任务计数器获取原始索引
                    taskLines[originalIndex] = taskLines[originalIndex].replace("not complete", "complete")

            with open("tasks.md", "w") as file:
                file.writelines(taskLines)
            print("Marked as complete.")

        if idx == 2:
            print("Please enter a meeting description:")
            meetingDescription = input()
            print("Please enter a date:")
            meetingDate = input()
            print("Please enter a time:")
            meetingTime = input()

            if "##### added by you" in meetingLines:
                meetingLines.extend(["- "+meetingDescription+" Scheduled: "+meetingTime+" "+meetingDate])
            else:
                meetingLines.extend(["\n", "\n", "##### added by you", "\n", "\n", "- "+meetingDescription+" Scheduled: "+meetingTime+" "+meetingDate])
            with open("meetings.md", "w") as file:
                file.writelines(meetingLines)
            print("Ok, I have added "+meetingDescription+" on "+meetingDate+" at "+meetingTime+".")

            shareOrNot = input("Would you like to share this meeting? [y/n]:")
            if shareOrNot == "y":
                print("Who would you like to share with?")

        if idx == 3:
            print("Which task would you like to share?")
            n=0
            taskList = []
            for line in taskLines:
                if "Due:" in line:
                    n+=1
                    task = line.split("-")[1].split("Due:")[0].strip()
                    due = line.split("Due:")[1].split("not complete")[0].strip()
                    print(str(n)+". "+task+" by "+due)
                    taskList.append(line)
            whichTaskToShare = int(input())

            print("Who would you like to share with?")
            for userID, userName in userIDtoNameDic:
                print(userID+" "+userName)
            sharedUserIDs = input().split()
            for sharedUserID in sharedUserIDs:
                sharedUserName = userIDtoNameDic[sharedUserID]
                sharedUserHome = userIDtoHomeDic[sharedUserID]
                with open(sharedUserHome+".jafr/user-settings.json", "r") as settingFile:
                    userSettings = json.load(settingFile)
                    settingFile.close()
                sharedUserSetting = userSettings[sharedUserName]
                sharedUserPath = os.join(sharedUserHome, sharedUserSetting)
                with open(sharedUserPath+"/tasks.md", "a") as f:
                    f.write("")
                    f.write("##### shared by "+os.environ['USER'])
                    f.write(taskList[whichTaskToShare-1])

            print("Task shared.")

if __name__ == '__main__':
    main()
