from datetime import datetime

#Plantilla final para el envío de correos. Esta es la versión correcta. Falta eliminar únicamente los emojis y colores. 
class ReporteManager:
    def __init__(self, incidencias_df):
        self.incidencias_df = incidencias_df

    def _generar_tabla_incidencias_html(self, rut_empleado):
        """Genera la tabla HTML de incidencias para un RUT específico con estilo mejorado."""
        
        # Filtrar el DataFrame de incidencias por el RUT del empleado
        incidencias_empleado = self.incidencias_df[self.incidencias_df['rut_empleado'] == rut_empleado]

        if incidencias_empleado.empty:
            # Mensaje sobrio y claro cuando no hay incidencias
            return "<p style='margin-left: 20px; color: #6c757d; font-style: italic; font-size: 13px;'>✅ Este colaborador/a no registra ausencias, permisos o licencias activas.</p>"

        # Generar el HTML de la tabla de incidencias
        tabla_html = """
        <div style='margin-left: 20px; margin-top: 10px; margin-bottom: 20px;'>
            <h4 style='color: #2c3e50; border-left: 4px solid #f39c12; padding-left: 10px; font-size: 14px; margin-bottom: 10px;'>
                📂 Permisos y Licencias Encontradas:
            </h4>
            
            <table style='width: 95%; border-collapse: collapse; margin-top: 5px; font-size: 12px; border: 1px solid #e0e0e0;'>
                <thead>
                    <tr style='background-color: #34495e;'>
                        <th style='padding: 8px 12px; border: none; color: white; text-align: left;'>Tipo de Permiso</th>
                        <th style='padding: 8px 12px; border: none; color: white; text-align: left;'>Fecha Inicio</th>
                        <th style='padding: 8px 12px; border: none; color: white; text-align: left;'>Fecha Fin</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, row in incidencias_empleado.iterrows():
            # Aplicar un fondo sutil a las filas pares para mejorar la lectura (zebra stripe)
            row_style = "background-color: #f9f9f9;" if i % 2 == 0 else "background-color: white;"
            
            # Asumo que ya tienes las columnas formateadas:
            # 'Tipo_Permiso_Formateado', 'fecha_inicio_formato', 'fecha_fin_formato'
            
            tabla_html += f"""
                    <tr style='{row_style}'>
                        <td style='padding: 8px 12px; border-right: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0;'>{row['Tipo_Permiso_Formateado']}</td>
                        <td style='padding: 8px 12px; border-right: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0;'>{row['fecha_inicio_formato']}</td>
                        <td style='padding: 8px 12px; border-bottom: 1px solid #e0e0e0;'>{row['fecha_fin_formato']}</td>
                    </tr>
            """
            
        tabla_html += """
                </tbody>
            </table>
        </div>
        """
        return tabla_html

    def _generar_html_reporte_por_jefe(self, nombre_jefe, empleados_data):
        """
        Genera HTML consolidado para un jefe específico, creando una tabla separada 
        para cada motivo de alerta, utilizando agrupación manual (sin itertools).
        """
        
        # 1. AGRUPAR LOS EMPLEADOS POR MOTIVO DE FORMA MANUAL
        empleados_por_motivo = {}
        for emp in empleados_data:
            motivo = emp['motivo']
            
            # Si el motivo no existe en el diccionario, inicializa una lista vacía
            if motivo not in empleados_por_motivo:
                empleados_por_motivo[motivo] = []
                
            # Agrega el empleado a la lista de su motivo
            empleados_por_motivo[motivo].append(emp)

        # 2. INICIO DEL HTML Y ESTILOS (Se mantiene la sección de estilos y encabezado general)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Alertas de Contratos</title>
            <style>
                /* ... (Tus estilos CSS) ... */
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                /* Se añade un estilo para el título de la tabla de grupo */
                .group-title {{
                    border-bottom: 2px solid #adb5bd; /* Separador sutil */
                    color: #1565c0; 
                    margin-top: 30px;
                    padding-bottom: 5px;
                }}

                /* ESTILOS DE TABLA */
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px; 
                    margin-bottom: 30px; 
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #007bff;
                    color: white;
                    font-weight: bold;
                }}
                /* Alternancia de filas */
                tr:nth-child(odd) {{
                    background-color: #ffffff;
                }}
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                
                /* Colores de Alerta Actualizados */
                .urgente {{
                    background-color: #f7f7f7 !important; /* Gris muy claro para fila Indefinido */
                }}
                .tipo-alerta {{
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .segundo-plazo {{
                    background: #fff3cd;
                    color: #856404;
                }}
                .indefinido {{
                    background: #dee2e6; /* Gris claro para el tag Indefinido */
                    color: #495057; 
                }}
                
                /* Estilo para filas de incidencia */
                .incidencia-row td {{
                    padding: 0;
                    border: none;
                    background-color: #f8f9fa; 
                }}
                
                /* Estilos generales */
                .header {{ text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
                .header h1 {{ color: #007bff; margin: 0; font-size: 28px; }}
                .jefe-info {{ background: #e3f2fd; padding: 15px; border-radius: 6px; margin-bottom: 25px; }}
                .jefe-info h2 {{ margin: 0; color: #1565c0; }}
                .summary {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 6px; margin-bottom: 25px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #dee2e6; text-align: center; color: #6c757d; font-size: 14px; }}

            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Alertas de Contratos</h1>
                    <p>Empleados que requieren atención inmediata</p>
                </div>
                
                <div class="jefe-info">
                    <h2>👤 {nombre_jefe}</h2>
                    <p>Los siguientes empleados bajo su supervisión requieren atención:</p>
                </div>
                
                <div class="summary">
                    <strong>📊 Resumen:</strong> {len(empleados_data)} empleado(s) requieren revisión de contrato
                </div>
                
        """
        
        # 3. GENERACIÓN DE TABLAS SEPARADAS
        # Usamos sorted() para asegurar un orden consistente en las tablas (ej: alfabético por motivo)
        for motivo in sorted(empleados_por_motivo.keys()):
            grupo_empleados = empleados_por_motivo[motivo]
            
            # 3.1. Encabezado del grupo (Tabla)
            html += f"""
                <h3 class="group-title">Motivo: {motivo} ({len(grupo_empleados)} Empleado(s))</h3>
                
                <table>
                    <thead>
                        <tr>
                            <th>👤 Empleado</th>
                            <th>💼 Cargo</th>
                            <th>📅 Fecha Inicio</th>
                            <th>📝 Tipo Alerta</th>
                            </tr>
                    </thead>
                    <tbody>
            """
            
            # 3.2. Iterar sobre los empleados del grupo para llenar la tabla
            # Se puede ordenar por otro campo aquí si se desea (ej: 'fecha_inicio')
            for emp in grupo_empleados:
                rut_empleado = emp.get('rut') 
                
                # Estilos de fila y etiqueta
                clase_fila = "urgente" if emp['tipo_alerta'] == 'INDEFINIDO' else ""
                clase_tipo = "indefinido" if emp['tipo_alerta'] == 'INDEFINIDO' else "segundo-plazo"
                
                html += f"""
                    <tr class="{clase_fila}">
                        <td><strong>{emp['empleado']}</strong></td>
                        <td>{emp['cargo']}</td>
                        <td>{emp['fecha_inicio']}</td>
                        <td><span class="tipo-alerta {clase_tipo}">{emp['tipo_alerta']}</span></td>
                    </tr>
                """
                
                # 3.3. Fila de Subtabla de Incidencias
                tabla_incidencias_html = self._generar_tabla_incidencias_html(rut_empleado)
                
                # El colspan es 4
                html += f"""
                    <tr class="incidencia-row">
                        <td colspan="4" style="padding: 0; border: none;"> 
                            {tabla_incidencias_html}
                        </td>
                    </tr>
                """
            
            # 3.4. Cerrar la tabla actual
            html += """
                    </tbody>
                </table>
            """
            
        # 4. CIERRE DEL HTML (Footer)
        html += """
                <div class="footer">
                    <p><strong>⏰ Acción requerida:</strong> Por favor revise y tome las acciones necesarias para estos contratos.</p>
                    <p>📧 Este es un correo automático generado por el Sistema de Alertas de Contratos</p>
                    <hr>
                    <small>Para consultas, contacte al área de Recursos Humanos</small>
                </div>
            </div>
        </body>
        </html>
        """
        return html