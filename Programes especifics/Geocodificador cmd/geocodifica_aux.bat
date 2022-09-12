pushd "../../"
call python_env.bat
"%PYTHONHOME%\python" "%CD%\Programes especifics\Geocodificador cmd\geocodifica.py" %*
popd