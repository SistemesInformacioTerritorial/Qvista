# import os
# for module in os.listdir(os.path.dirname(__file__)):
#     if module == '__init__.py' or module[-3:] != '.py':
#         continue
#     try:
#         __import__(module[:-3], locals(), globals())
#         print (module)
#     except:
#         print('Fallo'+module)
# del module