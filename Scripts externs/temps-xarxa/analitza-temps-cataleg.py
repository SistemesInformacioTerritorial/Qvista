import os
import plotly.express as px

def mitjana(l):
    return sum(l)/len(l)

funcions={}
for x in os.scandir(r"d:/cronometres2"):
    if x.name.endswith('txt'):
        with open(x) as f:
            hora = x.name.split('_')[-1].replace('-',':').replace('.txt','')
            for line in f.readlines():
                print(line)
                func, temps = line.split(':')
                if func not in funcions:
                    funcions[func]=[]
                try:
                    # funcions[func][hora]=float(temps)
                    funcions[func].append({'hora':hora, 'temps':float(temps)})
                except ValueError:
                    # temps no vàlid. L'ignorem
                    # això pot passar perquè haguem interromput l'execució quan l'arxiu ja s'havia creat
                    pass

for func in funcions.keys():
    fig = px.line(funcions[func], x='hora', y='temps', title=f'Temps (en segons) que ha trigat la funció {func}')
    fig.show()
