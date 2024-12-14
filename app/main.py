import gradio as gr
import redis
import pandas as pd

# Conectar a Redis
r = redis.Redis(host='redis', port=6379, db=0)

# Funciones auxiliares
def obtener_documentos_dict():
    keys = r.keys()
    documentos = [eval(r.get(key)) for key in keys]
    return documentos

def filtrar_documentos(documentos, texto_busqueda):
    if not texto_busqueda:
        return documentos
    texto_busqueda = texto_busqueda.lower()
    return [
        doc for doc in documentos
        if any(
            texto_busqueda in str(value).lower() for value in doc.values()
        )
    ]

# Funciones del negocio
def insertar_documento(codigo, nombre, descripcion, estado, fecha_creacion, codigo_proyecto, codigo_empleado, codigo_tarea):
    documento = {
        "CODIGO": codigo,
        "NOMBRE": nombre,
        "DESCRIPCION": descripcion,
        "ESTADO": estado,
        "FECHA_CREACION": fecha_creacion,
        "CODIGO_PROYECTO": codigo_proyecto,
        "CODIGO_EMPLEADO": codigo_empleado,
        "CODIGO_TAREA": codigo_tarea,
    }
    r.set(codigo, str(documento))
    return f"Documento con código {codigo} agregado.", actualizar_tabla(''), gr.update(choices=obtener_codigos_documentos())

def eliminar_documento(codigo):
    if codigo and r.exists(codigo):
        r.delete(codigo)
        return f"Documento con código {codigo} eliminado.", actualizar_tabla(''), gr.update(choices=obtener_codigos_documentos(), value=None)
    return f"Documento con código {codigo} no existe.", actualizar_tabla(''), gr.update(choices=obtener_codigos_documentos())

def cargar_datos_documento(codigo):
    if codigo and r.exists(codigo):
        documento = eval(r.get(codigo))
        return (
            documento["CODIGO"],
            documento["NOMBRE"],
            documento["DESCRIPCION"],
            documento["ESTADO"],
            documento["FECHA_CREACION"],
            documento["CODIGO_PROYECTO"],
            documento["CODIGO_EMPLEADO"],
            documento["CODIGO_TAREA"],
            f"Documento con código {codigo} cargado para editar."
        )
    else:
        return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), f"Documento con código {codigo} no existe."

def actualizar_documento(original_codigo, codigo, nombre, descripcion, estado, fecha_creacion, codigo_proyecto, codigo_empleado, codigo_tarea):
    if original_codigo != codigo and r.exists(codigo):
        return "El código nuevo ya existe. Elija otro código.", actualizar_tabla(''), gr.update(choices=obtener_codigos_documentos())
    if original_codigo != codigo:
        r.delete(original_codigo)
    documento = {
        "CODIGO": codigo,
        "NOMBRE": nombre,
        "DESCRIPCION": descripcion,
        "ESTADO": estado,
        "FECHA_CREACION": fecha_creacion,
        "CODIGO_PROYECTO": codigo_proyecto,
        "CODIGO_EMPLEADO": codigo_empleado,
        "CODIGO_TAREA": codigo_tarea,
    }
    r.set(codigo, str(documento))
    return f"Documento con código {codigo} actualizado.", actualizar_tabla(''), gr.update(choices=obtener_codigos_documentos())

def obtener_codigos_documentos():
    return [key.decode('utf-8') for key in r.keys()]

# Función para actualizar la tabla basada en búsqueda
def actualizar_tabla(texto_busqueda):
    documentos = obtener_documentos_dict()
    documentos_filtrados = filtrar_documentos(documentos, texto_busqueda)
    if documentos_filtrados:
        df = pd.DataFrame(documentos_filtrados)
    else:
        df = pd.DataFrame(columns=["CODIGO", "NOMBRE", "DESCRIPCION", "ESTADO", "FECHA_CREACION",
                                   "CODIGO_PROYECTO", "CODIGO_EMPLEADO", "CODIGO_TAREA"])
    return df

with gr.Blocks() as demo:
    gr.Markdown("# Gestor de Documentos")

    # Sección de documentos
    with gr.Column():
        gr.Markdown("## Documentos")
        
        buscador = gr.Textbox(label="Buscar en Documentos", placeholder="Ingrese texto para buscar...")
        
        tabla_documentos = gr.DataFrame(
            headers=["CODIGO", "NOMBRE", "DESCRIPCION", "ESTADO", "FECHA_CREACION",
                     "CODIGO_PROYECTO", "CODIGO_EMPLEADO", "CODIGO_TAREA"],
            interactive=False
        )

    # Sección para crear y gestionar documentos
    with gr.Column():
        gr.Markdown("## Crear Documento")

        with gr.Row():
            codigo_input = gr.Textbox(label="Código del Documento")
            nombre_input = gr.Textbox(label="Nombre del Documento")
            descripcion_input = gr.Textbox(label="Descripción del Documento")
            estado_input = gr.Textbox(label="Estado del Documento")

        with gr.Row():
            fecha_creacion_input = gr.Textbox(label="Fecha de Creación (YYYY-MM-DD)")
            codigo_proyecto_input = gr.Textbox(label="Código del Proyecto")
            codigo_empleado_input = gr.Textbox(label="Código del Empleado")
            codigo_tarea_input = gr.Textbox(label="Código de la Tarea")

        with gr.Row():
            insertar_button = gr.Button("Insertar Documento")
            actualizar_button = gr.Button("Actualizar Documento")
            limpiar_button = gr.Button("Limpiar Formulario")

        output_text = gr.Textbox(label="Resultado", interactive=False)

        with gr.Row():
            codigo_seleccionar_dropdown = gr.Dropdown(label="Seleccione el Código del Documento", choices=[], interactive=True)
            cargar_datos_button = gr.Button("Cargar Datos para Editar")
            eliminar_button = gr.Button("Eliminar Documento")

        original_codigo = gr.State()

        def limpiar_formulario():
            return gr.update(value=''), gr.update(value=''), gr.update(value=''), gr.update(value=''), gr.update(value=''), gr.update(value=''), gr.update(value=''), gr.update(value='')

        def inicializar():
            return actualizar_tabla(''), gr.update(choices=obtener_codigos_documentos())

        demo.load(fn=inicializar, outputs=[tabla_documentos, codigo_seleccionar_dropdown])

        buscador.change(fn=actualizar_tabla, inputs=buscador, outputs=tabla_documentos)

        limpiar_button.click(fn=limpiar_formulario, outputs=[
            codigo_input, nombre_input, descripcion_input, 
            estado_input, fecha_creacion_input, codigo_proyecto_input, 
            codigo_empleado_input, codigo_tarea_input
        ])

        insertar_button.click(
            insertar_documento,
            inputs=[
                codigo_input, nombre_input, descripcion_input, estado_input, fecha_creacion_input,
                codigo_proyecto_input, codigo_empleado_input, codigo_tarea_input
            ],
            outputs=[output_text, tabla_documentos, codigo_seleccionar_dropdown]
        )

        cargar_datos_button.click(
            cargar_datos_documento,
            inputs=[codigo_seleccionar_dropdown],
            outputs=[
                codigo_input, nombre_input, descripcion_input, estado_input, fecha_creacion_input,
                codigo_proyecto_input, codigo_empleado_input, codigo_tarea_input, output_text
            ]
        ).then(
            lambda x: x,
            inputs=[codigo_input],
            outputs=original_codigo
        )

        actualizar_button.click(
            actualizar_documento,
            inputs=[
                original_codigo, codigo_input, nombre_input, descripcion_input, estado_input, fecha_creacion_input,
                codigo_proyecto_input, codigo_empleado_input, codigo_tarea_input
            ],
            outputs=[output_text, tabla_documentos, codigo_seleccionar_dropdown]
        )

        eliminar_button.click(
            eliminar_documento,
            inputs=[codigo_seleccionar_dropdown],
            outputs=[output_text, tabla_documentos, codigo_seleccionar_dropdown]
        )

demo.launch(server_name="0.0.0.0", server_port=7860)