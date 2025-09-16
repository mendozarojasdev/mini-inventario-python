import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QFormLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QDoubleSpinBox, QSpinBox, QHeaderView, QTableWidgetItem, QMessageBox, QFileDialog
from PySide6.QtCore import QSize, QRegularExpression, QUrl, QLocale
from PySide6.QtGui import QIcon, QRegularExpressionValidator
# MariaDB connection
from lib.mariadb_connection import conn, cursor
# Fecha actual
from lib.fecha_actual import fecha_formateada, fecha_ddMaaaa
# Reportlab
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
# Para poder colocar pagina x de Y
from PyPDF2 import PdfReader
# Visualizar y guardar PDF
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
import os

# Ruta base desde donde se ejecuta el EXE
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Cargar recursos desde carpeta 'img'
LOGO_PATH = os.path.join(BASE_DIR, "img", "dairy-products.png")
REPORT_LOGO_PATH = os.path.join(BASE_DIR, "img", "report.png")
# Ruta del archivo_temp.pdf
RUTA_PDF_TEMP = os.path.join(BASE_DIR, "temp", "archivo_temp.pdf")
RUTA_TEMP_DIR = os.path.join(BASE_DIR, "temp")

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		# Coloca locale para utilizar . en lugar de , en QDoubleSpinBox en Ubuntu pero puede no funcionar, es mejor con set-locale-languaje.txt colocando LANG=es_MX.UTF-8
		QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
		self.report_viewer_window = None
		self.setWindowTitle("Mini Inventario 2")
		self.setFixedSize(QSize(800, 500))
		self.setWindowIcon(QIcon(LOGO_PATH))
		
		# Crear etiquetas (variables locales)
		lbl_codigo_barras = QLabel("Código de barras:")
		lbl_producto = QLabel("Producto:")
		lbl_precio = QLabel("Precio:")
		lbl_existencias = QLabel("Existencias:")

		# Crear cuadros de texto y spin (variables de instancia)
		#QSpinBox utiliza un int de 32 bits por defecto, lo que significa que su valor máximo es 2,147,483,647
		self.txt_codigo_barras = QLineEdit()
		self.txt_codigo_barras.setMaxLength(13) # Limita el campo a 15 caracteres
		# Utiliza una expresión regular para aceptar solo números, en la db el campo debe ser varchar(13) ya que python solo cuenta con int y float y no bigint
		regex = QRegularExpression(r"^\d{0,13}$")
		validator = QRegularExpressionValidator(regex)
		self.txt_codigo_barras.setValidator(validator)

		self.txt_producto = QLineEdit()

		self.spin_precio = QDoubleSpinBox()
		self.spin_precio.setDecimals(2) # Asigna 2 decimales
		self.spin_precio.setMaximum(9999.99)
		self.spin_precio.setMinimum(0.00)
		self.spin_precio.setSingleStep(1) # Incrementa/decrementa en 1 desde las flechas

		self.spin_existencias = QSpinBox()
		self.spin_existencias.setMaximum(9999) # Por defecto 99
		self.spin_existencias.setMinimum(0)
		self.spin_existencias.setSingleStep(1)

		self.spin_producto_id = QSpinBox()
		self.spin_producto_id.setMaximum(9999)
		self.spin_producto_id.setMinimum(0)
		self.spin_producto_id.setVisible(False)

		# Crear botones
		self.btn_guardar = QPushButton("Guardar")
		self.btn_guardar.clicked.connect(self.guardar_producto)
		
		self.btn_actualizar = QPushButton("Actualizar")
		self.btn_actualizar.setEnabled(False)
		self.btn_actualizar.clicked.connect(self.actualizar_producto)
		
		self.btn_eliminar = QPushButton("Eliminar")
		self.btn_eliminar.setEnabled(False)
		self.btn_eliminar.clicked.connect(self.eliminar_producto)

		btn_generar_reporte = QPushButton("Generar Reporte")
		btn_generar_reporte.clicked.connect(self.report_viewer_open)
		
		btn_limpiar = QPushButton("Limpiar")
		btn_limpiar.clicked.connect(self.limpiar)

		# Crear tabla para visualizar los datos
		self.table = QTableWidget()
		self.table.setColumnCount(5)
		self.table.setHorizontalHeaderLabels(["ID", "Código de Barras", "Producto", "Precio", "Existencias"])
		# Adapta el ancho de la última columna para abarcar todo el ancho de la tabla
		#self.table.horizontalHeader().setStretchLastSection(True)
		# Ajustar ancho del ID al contenido
		self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
		# Ajusta las demás columnas estrechamente
		self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
		self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
		# Ajustar ancho al contenido
		self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
		self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
		# Coloca los datos en los campos de texto al seleccionar un registro
		self.table.cellClicked.connect(self.get_selected_row)
		# Oculta la numeración de filas
		self.table.verticalHeader().setVisible(False)

		# Contenedor botones (horizontal)
		container_btn_ga = QHBoxLayout()
		container_btn_ga.addWidget(self.btn_guardar)
		container_btn_ga.addWidget(self.btn_actualizar)
		container_btn_ga.addWidget(self.btn_eliminar)

		container_btn_el = QHBoxLayout()
		container_btn_el.addWidget(btn_limpiar)
		container_btn_el.addWidget(btn_generar_reporte)

		# Contenedor formulario (etiqueta - campo)
		container_form = QFormLayout()
		container_form.addRow(lbl_codigo_barras, self.txt_codigo_barras)
		container_form.addRow(lbl_producto, self.txt_producto)
		container_form.addRow(lbl_precio, self.spin_precio)
		container_form.addRow(lbl_existencias, self.spin_existencias)
		container_form.addRow(self.spin_producto_id)

		# Contenedor formulario botones (vertical)
		container_form_btn = QVBoxLayout()
		container_form_btn.addLayout(container_form)
		container_form_btn.addLayout(container_btn_ga)
		container_form_btn.addLayout(container_btn_el)

		# Contenedor formulario botones tabla (horizontal)
		container_form_btn_table = QHBoxLayout()
		container_form_btn_table.addWidget(self.table)
		container_form_btn_table.addLayout(container_form_btn)

		layout = QVBoxLayout() # Vertical porque container_form_btn_table es un solo contenedor con todos los demás contenedores para que se pueda adaptar al tamaño de toda la ventana
		layout.addLayout(container_form_btn_table)

		widget = QWidget()

		widget.setLayout(layout)
		self.setCentralWidget(widget)
		self.cargar_tabla()

	def eliminar_producto(self):
		producto_id = self.spin_producto_id.value()
		
		confirmacion = QMessageBox.question(self, "Confirmación", "¿Estás seguro de eliminar este producto?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

		if confirmacion == QMessageBox.Yes:
			try:
				# debe contener una coma cuando solo hay un parámetro (producto_id,)
				cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
				conn.commit()

				# Mostrar mensaje de éxito
				QMessageBox.information(self, "Éxito!", "El producto han sido eliminado de la base de datos correctamente!")

				# Limpiar campos
				self.limpiar()

				# Recargar datos en la tabla
				self.cargar_tabla()

				self.btn_guardar.setEnabled(True)
				self.btn_actualizar.setEnabled(False)
				self.btn_eliminar.setEnabled(False)
			except Exception as e:
				# Mostrar mensaje de error
				QMessageBox.critical(self, "Error...", f"Ocurrió un problema al eliminar el producto: {e}")
				print(f"Ocurrió un problema al eliminar el producto: {e}")

	def actualizar_producto(self):
		codigo_barras = self.txt_codigo_barras.text()
		producto = self.txt_producto.text()
		precio = self.spin_precio.value()
		existencias = self.spin_existencias.value()
		producto_id = self.spin_producto_id.value()

		# Inserta en la base de datos
		try:
			cursor.execute("UPDATE productos SET codigo_barras = ?, producto = ?, precio = ?, existencias = ? WHERE id = ?", (codigo_barras, producto, precio, existencias, producto_id))
			conn.commit()

			# Mostrar mensaje de éxito
			QMessageBox.information(self, "Éxito!", "Los datos han sido actualizados en la base de datos correctamente!")

			# Recargar datos en la tabla
			self.cargar_tabla()

		except Exception as e:
			# Mostrar mensaje de error
			QMessageBox.critical(self, "Error...", f"Ocurrió un problema al actualizar los datos: {e}")
			print(f"Ocurrió un problema al actualizar los datos: ", e)

	def guardar_producto(self):
		# Muestra por consola
		codigo_barras = self.txt_codigo_barras.text()
		producto = self.txt_producto.text()
		precio = self.spin_precio.value() # no es necesario convertir con float(spin_precio.value()) porque .value() ya trae el formato del dato
		existencias = self.spin_existencias.value()

		# Inserta en la base de datos
		try:
			cursor.execute("INSERT INTO productos (codigo_barras, producto, precio, existencias) VALUES (?, ?, ?, ?)", (codigo_barras, producto, precio, existencias))
			conn.commit()

			# Mostrar mensaje de éxito
			QMessageBox.information(self, "Éxito!", "Los datos han sido almacenados en la base de datos correctamente!")

			# Limpiar campos
			self.limpiar()

			# Recargar datos en la tabla
			self.cargar_tabla()

		except Exception as e:
			# Mostrar mensaje de error
			QMessageBox.critical(self, "Error...", f"Ocurrió un problema al insertar los datos: {e}")
			print(f"Ocurrió un problema al insertar los datos: ", e)
	
	def cargar_tabla(self):
		""" Incluye un verticalScroll de forma automática cuando se requiere """
		try:
			cursor.execute("SELECT * FROM productos")
			registros = cursor.fetchall()
			# Coloca la cantidad de filas dependiendo de la cantidad de registros
			self.table.setRowCount(len(registros))
			# Rellena la tabla con los registros
			for i, (producto_id, codigo_barras, producto, precio, existencias) in enumerate(registros):
				self.table.setItem(i, 0, QTableWidgetItem(str(producto_id)))
				self.table.setItem(i, 1, QTableWidgetItem(str(codigo_barras)))
				self.table.setItem(i, 2, QTableWidgetItem(producto))
				self.table.setItem(i, 3, QTableWidgetItem(str(precio)))
				self.table.setItem(i, 4, QTableWidgetItem(str(existencias)))
		except Exception as e:
			print(f"Error al cargar los datos de la tabla:", e)
	
	def get_selected_row(self, row, column):
		""" Obtiene los campos de la fila y los coloca en los campos de texto """
		producto_id = self.table.item(row, 0).text()
		codigo_barras = self.table.item(row, 1).text()
		producto = self.table.item(row, 2).text()
		precio = self.table.item(row, 3).text()
		existencias = self.table.item(row, 4).text()

		self.spin_producto_id.setValue(int(producto_id)) # es necesario convertir porque table no tiene .value() solo .text()
		self.txt_codigo_barras.setText(codigo_barras)
		self.txt_producto.setText(producto)
		self.spin_precio.setValue(float(precio))
		self.spin_existencias.setValue(int(existencias))

		self.btn_guardar.setEnabled(False)
		self.btn_actualizar.setEnabled(True)
		self.btn_eliminar.setEnabled(True)
		
	def limpiar(self):
		# Limpiar campos
		self.spin_producto_id.clear()
		self.txt_codigo_barras.clear()
		self.txt_producto.clear()
		self.spin_precio.clear()
		self.spin_existencias.clear()

		self.btn_guardar.setEnabled(True)
		self.btn_actualizar.setEnabled(False)
		self.btn_eliminar.setEnabled(False)
	
	# ReportViewer
	def generar_pdf_reportlab(self, bandera):
		title_page = "Reporte de Productos"
		logo_size = Image(REPORT_LOGO_PATH, width=50, height=50)
		
		documento = BaseDocTemplate(RUTA_PDF_TEMP, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30, title=title_page)

		# Crear marco de contenido
		frame = Frame(documento.leftMargin, documento.bottomMargin, documento.width, documento.height, id='contenido')

		# Agregar plantilla de página
		if bandera:
			# Sin pie de página
			plantilla = PageTemplate(id='plantilla_base', frames=[frame])
			documento.addPageTemplates([plantilla])
		else:
			# Con pie de página
			plantilla = PageTemplate(id='plantilla_base', frames=[frame], onPage=pie_de_pagina)
			documento.addPageTemplates([plantilla])
		# Estilos
		estilos = getSampleStyleSheet()
		contenido = []

		# Título
		encabezado = [
			[logo_size, title_page]
		]
		encabezado_style = TableStyle([
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
			('FONTSIZE', (-1, -1), (-1, -1), 16)
		])
		table_encabezado = Table(encabezado, colWidths=[150, 350], rowHeights=[50])
		table_encabezado.setStyle(encabezado_style)
		contenido.append(table_encabezado)

		# Subtítulo
		page_header = [
			[fecha_formateada]
		]
		page_header_style = TableStyle([
			('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
			('FONTSIZE', (0, 0), (-1, -1), 12)
		])
		table_page_header = Table(page_header, colWidths=[500])
		table_page_header.setStyle(page_header_style)
		
		contenido.append(table_page_header)
		contenido.append(Spacer(1, 12))

		try:
			cursor.execute("SELECT * FROM productos")
			productos = cursor.fetchall()
			#conn.close()

			for producto in productos:
				print(producto[0], producto[1], producto[2], producto[3], producto[4])
			
			datos = [["ID", "Código de Barras", "Producto", "Precio", "Existencias"]]
			# Datos de ejemplo
			# Paragraph Normal sirve para colocar salto de linea cuando el texto sobrepasa la celda

			for i, row in enumerate(productos):
				datos.append([
					row[0],
					row[1],
					Paragraph(row[2], estilos["Normal"]),
					row[3],
					row[4]
				])

			# Crear tabla
			# repatRows=1 permite colocar el encabeza si hay más de una página
			tabla = Table(datos, colWidths=[50, 125, 200, 50, 75], repeatRows=1)

			# Estilo de la tabla
			estilo_tabla = TableStyle([
				('BACKGROUND', (0, 0), (-1, 0), colors.midnightblue),
				('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
				('ALIGN', (0, 0), (-1, -1), 'CENTER'),
				('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
				('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
				('FONTSIZE', (0, 0), (-1, 0), 12),
				('BOTTOMPADDING', (0, 0), (-1, 0), 10),
				('BACKGROUND', (0, 1), (-1, -1), colors.beige),
				('GRID', (0, 0), (-1, -1), 1, colors.black),
			])

			tabla.setStyle(estilo_tabla)
			contenido.append(tabla)
		except Exception as e:
			print("Error al rellenar tabla del reporte:", e)

		# Construir el documento
		documento.build(contenido)

		print(f"Reporte generado con éxito: {RUTA_PDF_TEMP}")

	def report_viewer_open(self):
		asegurar_carpeta_temp() # Crea temp/
		# Primero crea el reporte.pdf en temp/
		#ruta = "temp/archivo_temp.pdf"
		# Es necesario crear el archivo dos veces, la primera para poder obtener el total de páginas y el segundo para colocárselos
		self.generar_pdf_reportlab(True)
		self.generar_pdf_reportlab(False)

		# Abre la ventana con la ruta del archivo en la carpeta temp/
		self.report_viewer_window = ReportViewer()
		self.report_viewer_window.show()

# Función para dibujar el pie de página con número de página
def pie_de_pagina(canvas, doc):
	canvas.saveState()
	page_number = doc.page

	# Obtiene el total de paginas (una vez creado el archivo)
	pdf_reader = PdfReader(RUTA_PDF_TEMP)
	total_pages = len(pdf_reader.pages)

	pagina = f"Página {page_number} de {total_pages}"
	canvas.setFont("Helvetica", 9)
	canvas.drawString(265, 30, pagina)
	canvas.restoreState()

	# De esta forma también es posible colocar el Título si hay varias hojas

def asegurar_carpeta_temp():
	""" Crea la carpeta temp/ ya que pyinstaller no incluye carpetas vacías, la carpeta temp/ es necesaria para crear el archivo pdf temporal """
	if not os.path.exists(RUTA_TEMP_DIR):
		os.makedirs(RUTA_TEMP_DIR)
		print(f"Carpeta creada: {RUTA_TEMP_DIR}")
	else:
		print(f"Carpeta ya existe: {RUTA_TEMP_DIR}")

class ReportViewer(QWidget):
	def __init__(self):
		super().__init__()
		#self.ruta_archivo_temp = ruta # para eliminarlo de temp/
		self.setWindowTitle("Report Viewer")
		self.setFixedSize(QSize(1200, 600))
		self.setWindowIcon(QIcon(LOGO_PATH))

		web_view = QWebEngineView()

		settings = web_view.settings()
		settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
		# Habilitar visualización para archivos PDF
		settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
		
		# Habilitar manejo de descargas
		profile = web_view.page().profile()
		profile.downloadRequested.connect(self.on_download_requested)

		#url_pdf = QUrl.fromLocalFile(os.path.abspath(ruta))
		url_pdf = QUrl.fromLocalFile(RUTA_PDF_TEMP)
		web_view.load(QUrl(url_pdf))

		layout = QVBoxLayout()
		layout.addWidget(web_view)

		self.setLayout(layout)
	
	def on_download_requested(self, download):
		file_name = f"reporte-productos-{fecha_ddMaaaa}"

		# Mostrar diálogo para elegir carpeta de guardado
		save_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo como", file_name, "PDF Files (*.pdf)")
		# _ obtiene el filtro de archivo seleccionado, pero no lo necesitamos, así que lo descartamos. "Si no vas a usar una variable, llama a esa variable _." alternativa ruta = resultado[0]

		if save_path:
			# Establecer nombre de archivo y ruta de descarga
			directory = os.path.dirname(save_path)
			filename = os.path.basename(save_path)

			download.setDownloadDirectory(directory)
			download.setDownloadFileName(filename)
			download.accept()

	# Override
	# Elimina el archivo.pdf temporal al cerar la ventana ReportViewer
	def closeEvent(self, event):
		if os.path.exists(RUTA_PDF_TEMP):
			try:
				os.remove(RUTA_PDF_TEMP)
				print(f"Archivo '{RUTA_PDF_TEMP}' eliminado.")
			except Exception as e:
				print("No se pudo eliminar el archivo:", e)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()