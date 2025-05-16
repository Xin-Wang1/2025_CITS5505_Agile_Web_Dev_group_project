# 2025_CITS5505_Agile_Web_Dev_group_project [project name]
## 1. Purpose and Design
  This web application is designed to help students select an optimal combination of university courses based on their preferences. Users can upload course details including times, duration, and credit hours, and the system will generate plausible schedules using scheduling algorithms.
### Key Features
- Upload course details via structured forms or CSV
- Automatically generate valid timetable combinations that avoid conflicts
- Display visual weekly schedule of selected course combinations
- Option to share suggested schedules with classmates
## 2. Group Members
| UWA ID   | Name         | GitHub Username |
|----------|--------------|-----------------|
| 24154773 | Ethan He     | *YuaHe0* |
| 24004729 | Manas Rawat  | *ManasR10* |
| 24100783 | Stewie Yang  | *YYHshift1* |
| 24201533 | Xin Wang     | *Xin-Wang1* |

## 3. How to Launch the Application
Creates a virtual environment named venv in the current directory. 
``` 
python -m venv venv
```
Temporarily allows script execution (like activating a virtual environment) in the current PowerShell session. Without this, Windows may block the activation script.
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```
Activates the virtual environment on Windows. After activation, any Python or pip commands will use the virtual environment instead of the system-wide Python.
```
venv\Scripts\activate  
```
Installs all required dependencies listed in the requirements.txt file. This ensures your project has the correct packages to run properly.
```
pip install -r requirements.txt
```
flask run
(You may need to enable script running if using Windows)
```
flask run
```

## 4. How to run test

#### Unit Tests  
Run backend Flask route and logic tests using Python’s built-in `unittest`:

```bash
python -m unittest app/tests/test_routes.py
```
#### Selenium Tests
Start the Flask server in one terminal:
```bash
flask run
```
In another terminal, run the Selenium suite:
```bash
python -m unittest app/tests/test_selenium.py
```
## 5.  Project Structure Overview
```
2025_CITS5505_Agile_Web_Dev_group_project/
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── cleanup.py
│   ├── forms.py
│   ├── insert_sample_data.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── myschedule.py
│   │   ├── schedule.py
│   │   └── unit.py
│   ├── static/
│   │   ├── css/
│   │   │   └── (various .css files)
│   │   ├── js/
│   │   │   └── (various .js files)
│   │   └── image/
│   │       └── avatar.png
│   ├── templates/
│   │   └── (various .html files)
│   └── tests/
│       ├── __init__.py
│       ├── test_routes.py
│       ├── test_selenium.py
│       └── test_unit.py
├── requirements.txt
├── README.md
├── LICENSE
└── units.csv
```
## 6.  Web page instructions

##Upload Unit Details
1. Click choose file and select units.csv
2. Click the upload button

##Select units
1. Click the select button for the unit you want to enrol in
2. Click the Schedule Generate button to direct you to the generation page

##Generated Schedule page
Function 1: You can click the checkboxes to select the lecture, lab, and tutorial.
Function 2: Select a day and enter a time range (10:00-15:00) to add your unavailable time range
Function 3: select one or more preferred days, and the algorithm will auto-generate a schedule for you
(Please note: if two timeslot clash or there is no timeslot for the preferred day you selected, your click or auto select won't work, if you create an unavailable time that clashes with your current timeslot, the unavailable time will overwrite your timeslot)

Click the Generate Schedule button to save the schedule.

##My Schedules

Go to the My Schedule page, where you can view all schedules you generated.


##Share

Go to the Share page, where you can select a user as the recipient, optionally select one of your schedules, and enter message content to send your message.

Inbox: You can see the messages you have received
Sent: You can see the message you have sent








