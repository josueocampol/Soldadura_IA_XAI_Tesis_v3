# ==========================
# ANEXO C: Integración Slicer + MONAI Label
# Anexo C: Integración con 3D Slicer y MONAI Label

# Este script se utilizó dentro del entorno Python Interactor de 3D Slicer para 
# conectar el servidor MONAI Label, ejecutar inferencias en línea y visualizar resultados 
# segmentados en el entorno gráfico.
# ==========================

monai_module = slicer.modules.monailabel.widgetRepresentation().self()

# Configurar conexión al servidor local
server_url = "http://192.168.100.8:8000"
monai_module.logic.setServer(server_url)
monai_module.serverUrl = server_url

# Ejecutar inferencia sobre un volumen cargado en el entorno Slicer
volume_node = slicer.util.getNode('CT_Weld_Volume')
params = {"model": "DeepEditWeld", "user": "operator01"}
result = monai_module.logic.infer("segment", volume_node, params)

print("✅ Segmentación completada con MONAI Label:", result)

# Permite la ejecución remota de inferencia sin necesidad de exportar manualmente archivos.
# El modelo "DeepEditWeld" responde a una arquitectura basada en edición interactiva de regiones defectuosas en cordones de soldadura.
# Los resultados se visualizan directamente en 3D Slicer, combinando las vistas axial, sagital y coronal.