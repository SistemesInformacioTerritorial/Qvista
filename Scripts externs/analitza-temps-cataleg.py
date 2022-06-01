import os
import plotly.express as px

def mitjana(l):
    return sum(l)/len(l)

llista = []
for x in os.scandir(r"C:\temp\qVista\cronometres"):
    with open(x) as f:
        try:
            temps = float(f.read().split(':')[-1])
            hora = x.name.split('_')[-1].replace('-',':').replace('.txt','')
            llista.append({'hora':hora, 'temps':temps})
        except ValueError:
            # temps no vàlid. L'ignorem
            # això pot passar perquè haguem interromput l'execució quan l'arxiu ja s'havia creat
            pass

temps = [x['temps'] for x in llista]

print('Temps màxim:',max(temps))
print('Temps mitjà:', mitjana(temps))

fig=px.line(llista, x='hora', y='temps', title='Temps (en segons) que ha trigat cada execució')
fig.show()
