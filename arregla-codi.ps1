# flags interessants:
# --in-place
# --remove-unused-variables
# remove-all-unused-imports
# remove-duplicate-keys
ls -Path moduls -Name | Select-String \.py | Select-String Qv* | Foreach-Object {
    if(-Not($_ -like "QvImports.py")){
        echo $_
        # python c:\Users\P625615\AppData\Roaming\python\Python37\Scripts\dewildcard.py moduls\$_ --single-line -w
        python -m autoflake --in-place --remove-unused-variables moduls\$_
    }
}

# python c:\Users\P625615\AppData\Roaming\python\Python37\Scripts\dewildcard.py qVista.py --single-line -w
python -m autoflake --in-place --remove-unused-variables qVista.py