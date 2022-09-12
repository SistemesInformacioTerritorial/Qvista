@echo off
pushd "../../"
call python_env.bat
"%PYTHONHOME%\python" "%CD%/Programes especifics/MaBIM/qMaBIM.py" %*
popd