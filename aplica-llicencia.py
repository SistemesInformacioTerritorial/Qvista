import os


llicencia='''# Copyright (C) 2020  Jordi Cebrián, Aleix Dalmau, Xavier Llinares, Oriol Martí, Javier Nieva, Carlos Pretel
# Sistemes d'Informació Territorial, Institut Municipal d'Informàtica, Ajuntament de Barcelona
# Nexus Geographics
# 
# This file is part of qVista.
# qVista is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qVista is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with qVista.  If not, see <https://www.gnu.org/licenses/>.

'''

for root, subdirs, files in os.walk('.'):
    for x in files:
        if not x.endswith('.py') or not 'qv' in x.lower(): continue
        path=os.path.join(root,x)
        print(path)
        with open(path,'r', encoding='utf-8') as f:
            cont=f.read()
        if not 'GNU General Public License' in cont:
            with open(path,'w', encoding='utf-8') as f: 
                f.write(llicencia+cont)
        input()