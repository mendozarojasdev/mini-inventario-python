from datetime import datetime

# Obtener la fecha y hora actual
fecha_hora_actual = datetime.now()

# Formatear la fecha y hora
fecha_formateada = fecha_hora_actual.strftime("%d/%B/%Y %I:%M %p")
fecha_ddMaaaa = fecha_hora_actual.strftime("%d-%B-%Y")

# Reemplazar el nombre del mes en inglés por español
meses = {
	"January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
	"May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
	"September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

for eng, esp in meses.items():
	fecha_formateada = fecha_formateada.replace(eng, esp)
	fecha_ddMaaaa = fecha_ddMaaaa.replace(eng, esp)

#print(fecha_formateada)