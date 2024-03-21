@echo off
setlocal enabledelayedexpansion

REM Define the path to your Python script
set PYTHON_SCRIPT="get_sk.py"

REM Define the name of your conda environment
set CONDA_ENV="ids"

REM Define the range of files each process should handle
set RANGE=2500

REM Define the total number of files
set TOTAL_FILES=10000

REM Create the log directory if it does not exist
if not exist log mkdir log

REM Start the processes
for /L %%i in (0, %RANGE%, %TOTAL_FILES%) do (
    set /a start=%%i
    set /a end=!start!+%RANGE%-1
    echo Starting process for files !start! to !end!
    call conda activate %CONDA_ENV% && start /B python %PYTHON_SCRIPT% --start !start! --end !end! > log\output_!start!_!end!.txt 2> log\error_!start!_!end!.txt
)

echo All processes started.