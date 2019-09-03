import what3words

geocoder = what3words.Geocoder("HTD7LNB9")

palabras = geocoder.convert_to_3wa(what3words.Coordinates(51.000027, 0.100009), language='fr')

coordenadas = geocoder.convert_to_coordinates('agudo.lista.caja')

# print (palabras)
print(coordenadas['words'])