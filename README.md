# 2025_CITS5505_Agile_Web_Dev_group_project
## Application Overview
The **Smart Course Selection Tool** is a web application designed to help university students optimize and share their course schedules efficiently. It allows users to:

- Register and log into a secure account
- Upload unit/course information via CSV
- Visually select and customize preferred class times
- Automatically generate conflict-free weekly schedules
- Share their schedules with classmates through an in-app messaging system
- View and manage their personalized schedule history

The application prioritizes usability and responsiveness, providing a Bootstrap-based interface enhanced with AJAX and JavaScript for dynamic interaction.
## 2. Group Members
| UWA ID   | Name         | GitHub Username |
|----------|--------------|-----------------|
| 24154773 | Ethan He     | *YuaHe0* |
| 24004729 | Manas Rawat  | *ManasR10* |
| 24100783 | Stewie Yang  | *YYHshift1* |
| 24201533 | Xin Wang     | *Xin-Wang1* |

## 3. How to Launch the Application
1. Clone the private repository
```
 git clone [https://github.com/your-private-repo.git](https://github.com/Xin-Wang1/2025_CITS5505_Agile_Web_Dev_group_project.git)
   cd ./2025_CITS5505_Agile_Web_Dev_group_project
```
2. Request the `.env` file from your project administrator.
This file contains environment-specific settings such as secret keys and database configuration.
Once received, place it into the root directory of the project.
3. Create virtual environment and install dependencies:
``` 
python -m venv venv
```
Temporarily allows script execution (like activating a virtual environment) in the current PowerShell session. Without this, Windows may block the activation script.
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```
Activates the virtual environment on Windows. After activation, any Python or pip commands will use the virtual environment instead of the system-wide Python.
```
venv\Scripts\activate  # on Mac: source venv/bin/activate
```
Installs all required dependencies listed in the requirements.txt file. This ensures your project has the correct packages to run properly.
```
pip install -r requirements.txt
```
4. Initialize the database
```
python init_db.py
```
5. Run the application
```bash
flask run
```
Then visit http://127.0.0.1:5000 in your browser.

## 4. How to run test

#### Unit Tests  
To run unit tests for registration, login, upload, and scheduling:
```bash
python -m unittest tests.test_unit
```
#### Selenium Tests
Make sure you have Google Chrome and ChromeDriver installed. Then run:
```bash
python tests/test_selenium.py
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
│       ├── config_test.py
│       ├── test_selenium.py
│       ├── test_units.csv
│       └── test_unit.py
├── requirements.txt
├── README.md
├── run.py
├── run_testserve.py
├── init_db.py
└── units.csv
```
## 6.  Web page instructions

#### Upload Unit Details
1. Click choose file and select units.csv
2. Click the upload button

#### Select units
1. Click the select button for the unit you want to enrol in
2. Click the Schedule Generate button to direct you to the generation page

#### Generated Schedule page
Function 1: You can click the checkboxes to select the lecture, lab, and tutorial.
Function 2: Select a day and enter a time range (10:00-15:00) to add your unavailable time range
Function 3: select one or more preferred days, and the algorithm will auto-generate a schedule for you
(Please note: if two timeslot clash or there is no timeslot for the preferred day you selected, your click or auto select won't work, if you create an unavailable time that clashes with your current timeslot, the unavailable time will overwrite your timeslot)

Click the Generate Schedule button to save the schedule.

#### My Schedules

Go to the My Schedule page, where you can view all schedules you generated.


#### Share

Go to the Share page, where you can select a user as the recipient, optionally select one of your schedules, and enter message content to send your message.

Inbox: You can see the messages you have received
Sent: You can see the message you have sent








