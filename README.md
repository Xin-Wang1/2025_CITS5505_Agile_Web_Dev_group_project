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

## 4. How to Run Tests

We use both unit tests and end-to-end tests to verify application correctness.

### 4.1 Unit Tests (Flask Routes)

Run the following command to execute unit tests that verify the core Flask routes:

```bash
python3 -m unittest app/tests/test_routes.py
```
