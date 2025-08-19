from services.sensor_data_storage.sensor_data_storage import SensorDataStorage
from services.report_generator.report_generator_commands import ReportGeneratorCommands
from support.logger import Logger
from middleware.client_middleware import ClientMiddleware
from ..service_interface import ServiceInterface
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.chart import LineChart, Reference
from datetime import datetime
import os
from typing import Dict, Any
import json
from openpyxl.utils import get_column_letter


class ReportGenerator(ServiceInterface):
    _sensor_data_storage: SensorDataStorage

    def __init__(self, middleware: ClientMiddleware, sensor_data_storage: SensorDataStorage):
        self._logger = Logger()
        self._middleware = middleware
        self._sensor_data_storage = sensor_data_storage

        self.initialize_commands()

        self._logger .info("Report Generator initialized")

    def initialize_commands(self):
        commands = {
            ReportGeneratorCommands.GENERATE_REPORT: self.generate_report_command,
            ReportGeneratorCommands.GENERATE_CHART_REPORT: self.generate_chart_report_command
        }
        self._middleware.add_commands(commands)

    def generate_report_command(self, command):
        """
        Command to generate a report based on the provided data.
        """
        self._logger.info(
            f"Generating report with command: {command}")

        # Call read_sensor_info with a callback to handle the response
        self._sensor_data_storage.read_sensor_info(
            command, self._handle_sensor_data_for_excel)

    def generate_chart_report_command(self, command):
        """
        Command to generate a chart report based on the provided data.
        """
        self._logger.info(
            f"Generating chart report with command: {command}")

        # Call read_sensor_info with a callback to handle the response
        self._sensor_data_storage.read_sensor_info(
            command, self._handle_sensor_data_for_chart)

    def _handle_sensor_data_for_chart(self, result, data_out):
        """
        Callback to handle sensor data and create Excel chart report.
        """
        if result and data_out and 'info' in data_out:
            try:
                excel_file_path = self._create_excel_chart_report(
                    data_out['info'])
                self._logger.info(
                    f"Excel chart report created successfully: {excel_file_path}")
                self._middleware.send_command_answear(
                    True,
                    {"status": "success", "file_path": excel_file_path,
                        "report": data_out['info']},
                    data_out.get('requestId', '')
                )
            except Exception as e:
                self._logger.error(f"Failed to create Excel chart report: {e}")
                self._middleware.send_command_answear(
                    False,
                    {"status": "error",
                        "message": f"Failed to create Excel chart report: {e}"},
                    data_out.get('requestId', '')
                )
        else:
            self._logger.error(
                "Failed to generate chart report - no data received")
            self._middleware.send_command_answear(
                False,
                {"status": "error",
                    "message": "Failed to generate chart report - no data received"},
                data_out.get('requestId', '')
            )

    def _handle_sensor_data_for_excel(self, result, data_out):
        """
        Callback to handle sensor data and create Excel report.
        """
        if result and data_out and 'info' in data_out:
            try:
                excel_file_path = self._create_excel_report(data_out['info'])
                self._logger.info(
                    f"Excel report created successfully: {excel_file_path}")
                self._middleware.send_command_answear(
                    True,
                    {"status": "success", "file_path": excel_file_path,
                        "report": data_out['info']},
                    data_out["commandId"]
                )
            except Exception as e:
                self._logger.error(f"Failed to create Excel report: {e}")
                self._middleware.send_command_answear(
                    False,
                    {"status": "error", "message": f"Failed to create Excel report: {e}"},
                    data_out["commandId"]
                )
        else:
            self._logger.error("Failed to generate report - no data received")
            self._middleware.send_command_answear(
                False,
                {"status": "error",
                    "message": "Failed to generate report - no data received"},
                data_out["commandId"]
            )

    def _create_excel_report(self, sensor_data: Dict[str, Any]) -> str:
        """
        Create an Excel report from sensor data, following the format of the provided image.
        Linha 2 do Excel são os nomes amigáveis dos sensores.
        """

        if (len(sensor_data) == 0):
            self._logger.error(
                "Sem dados para gerar relatório")
            return ""

        # 1. Carregar o mapeamento de nomes amigáveis dos sensores
        config_path = os.path.join(os.path.dirname(
            __file__), '../../config/ui_config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            ui_config = json.load(f)

        # 2. Criar um dicionário para mapear sensor_full_topic para nome amigável e tipo
        topic_to_name = {}
        topic_to_type = {}
        for group in ui_config.values():
            for sensor in group:
                # O nome do tópico completo é gateway-topic-indicator
                full_topic = f"{sensor['gateway']}-{sensor['topic']}-{sensor['indicator']}"
                topic_to_name[full_topic] = sensor['name']
                topic_to_type[full_topic] = sensor['sensorType']

        # 3. Definir a ordem das colunas dinamicamente conforme os sensores presentes
        # Pega os nomes amigáveis dos sensores presentes em sensor_data, na ordem do ui_config.json
        present_names = []
        for group in ui_config.values():
            for sensor in group:
                full_topic = f"{sensor['gateway']}-{sensor['topic']}-{sensor['indicator']}"
                if full_topic in sensor_data:
                    present_names.append(sensor['name'])
        col_names = present_names
        topics_in_order = [
            k for k, v in topic_to_name.items() if v in col_names]

        # 4. Coletar todos os timestamps únicos e ordenar
        all_timestamps = set()
        for topic in topics_in_order:
            for entry in sensor_data.get(topic, []):
                all_timestamps.add(entry['timestamp'])
        sorted_timestamps = sorted(all_timestamps)

        # 5. Montar um dicionário auxiliar para acesso rápido com interpolação
        # {topic: {timestamp: value}}
        topic_time_value = {}
        for topic in topics_in_order:
            topic_time_value[topic] = {}
            last_known_value = None

            # Ordenar as entradas por timestamp para garantir ordem cronológica
            sorted_entries = sorted(sensor_data.get(
                topic, []), key=lambda x: x['timestamp'])

            for entry in sorted_entries:
                topic_time_value[topic][entry['timestamp']] = entry['value']
                last_known_value = entry['value']

            # Agora preencher todos os timestamps com interpolação
            for ts in sorted_timestamps:
                if ts not in topic_time_value[topic]:
                    topic_time_value[topic][ts] = last_known_value

        # 6. Criar o arquivo Excel
        wb = Workbook()
        ws = wb.active
        if (ws == None):
            self._logger.error(
                "Failed to create Excel report - no worksheet found")
            return ""

        ws.title = "Relatório"

        # Linha 1: cabeçalho superior
        ws.append(["Instrumento:", "Câmara 2 s/ trad externo", "", "", ""])
        # Linha 2: cabeçalho dos sensores
        header = ["Data"] + col_names
        ws.append(header)

        # 7. Preencher os dados
        for ts in sorted_timestamps:
            # Converter timestamp ISO para formato brasileiro
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                formatted_timestamp = dt.strftime("%d/%m/%Y %H:%M:%S")
            except:
                formatted_timestamp = ts  # fallback se não conseguir converter

            row = [formatted_timestamp]
            for topic in topics_in_order:
                # Agora sempre tem valor devido à interpolação
                value = topic_time_value[topic][ts]
                row.append(value)
            ws.append(row)

        # 8. Ajustar estilos (cores de fundo e bordas)
        bold_font = Font(bold=True)

        # Definir cores de fundo
        color_row1 = PatternFill(start_color="b7e1cd",
                                 end_color="b7e1cd", fill_type="solid")
        color_row2 = PatternFill(start_color="cecece",
                                 end_color="cecece", fill_type="solid")

        # Definir borda
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Aplicar cor de fundo e estilo para linha 1
        for cell in ws[1]:
            cell.fill = color_row1
            cell.font = bold_font
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="left")

        # Aplicar cor de fundo e estilo para linha 2
        for cell in ws[2]:
            cell.fill = color_row2
            cell.font = bold_font
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center")

        # Aplicar bordas para todas as linhas de dados
        for row_num in range(3, len(sorted_timestamps) + 3):
            for cell in ws[row_num]:
                cell.border = thin_border

        # 9. Ajustar largura das colunas
        for i, col in enumerate(header, 1):
            ws.column_dimensions[get_column_letter(
                i)].width = 22 if i == 1 else 18

        # 10. Criar nova aba para sensores elétricos (power, current, tension, powerFactor)
        self._create_electrical_sensors_tab(
            wb, sensor_data, topic_to_name, topic_to_type, sorted_timestamps)

        # 11. Salvar o arquivo
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.abspath(f"report_{now_str}.xlsx")
        wb.save(file_path)
        return file_path

    def _create_electrical_sensors_tab(self, wb, sensor_data: Dict[str, Any], topic_to_name: Dict[str, str],
                                       topic_to_type: Dict[str, str], sorted_timestamps: list) -> None:
        """
        Create a new tab for electrical sensors (power, current, tension, powerFactor) with additional header information.
        """
        # 1. Identificar sensores elétricos
        electrical_sensor_types = [
            "Power", "Current", "Tension", "PowerFactor"]
        electrical_topics = []
        electrical_names = []

        for topic, sensor_type in topic_to_type.items():
            if sensor_type in electrical_sensor_types and topic in sensor_data:
                electrical_topics.append(topic)
                electrical_names.append(topic_to_name[topic])

        # Se não há sensores elétricos, não criar a aba
        if not electrical_topics:
            return

        # 2. Criar nova aba
        ws_electrical = wb.create_sheet("Sensores Elétricos")

        # 3. Calcular estatísticas para o cabeçalho
        total_power_consumption = 0
        power_factor_values = []
        current_values = []
        has_power = False
        has_power_factor = False
        has_current = False

        # Coletar todos os valores para cálculos
        for topic in electrical_topics:
            for entry in sensor_data.get(topic, []):
                try:
                    value = float(entry['value'])
                    sensor_type = topic_to_type[topic]

                    if sensor_type == "Power":
                        total_power_consumption += value
                        has_power = True
                    elif sensor_type == "PowerFactor":
                        power_factor_values.append(value)
                        has_power_factor = True
                    elif sensor_type == "Current":
                        current_values.append(value)
                        has_current = True
                except (ValueError, TypeError):
                    # Skip invalid values
                    continue

        # Calcular médias e máximos
        avg_power_factor = sum(power_factor_values) / \
            len(power_factor_values) if power_factor_values else 0
        max_current = max(current_values) if current_values else 0

        # 4. Criar cabeçalho com informações adicionais
        ws_electrical.append(
            ["Instrumento:", "Câmara 2 s/ trad externo", "", "", ""])

        # Adicionar linhas de cabeçalho apenas se os sensores correspondentes existirem
        header_row_count = 1  # Começa com 1 (linha do instrumento)

        if has_power:
            ws_electrical.append(
                ["Consumo Total de Energia: ", f"{total_power_consumption:.2f} W", "", "", ""])
            header_row_count += 1

        if has_power_factor:
            ws_electrical.append(
                ["Fator de Potência Médio: ", f"{avg_power_factor:.3f}", "", "", ""])
            header_row_count += 1

        if has_current:
            ws_electrical.append(
                ["Corrente Máxima: ", f"{max_current:.2f} A", "", "", ""])
            header_row_count += 1

        # 5. Cabeçalho dos sensores
        header = ["Data"] + electrical_names
        ws_electrical.append(header)

        # 6. Montar dados com interpolação para sensores elétricos
        topic_time_value = {}
        for topic in electrical_topics:
            topic_time_value[topic] = {}
            last_known_value = None

            sorted_entries = sorted(sensor_data.get(
                topic, []), key=lambda x: x['timestamp'])

            for entry in sorted_entries:
                try:
                    value = float(entry['value'])
                    topic_time_value[topic][entry['timestamp']] = value
                    last_known_value = value
                except (ValueError, TypeError):
                    # Use 0 as fallback for invalid values
                    topic_time_value[topic][entry['timestamp']] = 0
                    if last_known_value is None:
                        last_known_value = 0

            for ts in sorted_timestamps:
                if ts not in topic_time_value[topic]:
                    topic_time_value[topic][ts] = last_known_value

        # 7. Preencher os dados
        for ts in sorted_timestamps:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                formatted_timestamp = dt.strftime("%d/%m/%Y %H:%M:%S")
            except:
                formatted_timestamp = ts

            row = [formatted_timestamp]
            for topic in electrical_topics:
                value = topic_time_value[topic][ts]
                row.append(value)
            ws_electrical.append(row)

        # 8. Aplicar estilos
        bold_font = Font(bold=True)

        # Definir cores de fundo
        color_row1 = PatternFill(start_color="b7e1cd",
                                 end_color="b7e1cd", fill_type="solid")
        color_row2 = PatternFill(start_color="cecece",
                                 end_color="cecece", fill_type="solid")
        color_row3 = PatternFill(start_color="e6f3ff",
                                 end_color="e6f3ff", fill_type="solid")

        # Definir borda
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Aplicar cor de fundo e estilo para todas as linhas de cabeçalho (linha 1 até header_row_count)
        for row_num in range(1, header_row_count + 1):
            for cell in ws_electrical[row_num]:
                cell.fill = color_row1
                cell.font = bold_font
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="left")

        # Aplicar cor de fundo e estilo para linha do cabeçalho dos sensores
        sensor_header_row = header_row_count + 1
        for cell in ws_electrical[sensor_header_row]:
            cell.fill = color_row3
            cell.font = bold_font
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center")

        # Aplicar bordas para todas as linhas de dados
        data_start_row = sensor_header_row + 1
        for row_num in range(data_start_row, len(sorted_timestamps) + data_start_row):
            for cell in ws_electrical[row_num]:
                cell.border = thin_border

        # 9. Ajustar largura das colunas
        for i, col in enumerate(header, 1):
            ws_electrical.column_dimensions[get_column_letter(
                i)].width = 22 if i == 1 else 18

    def _create_excel_chart_report(self, sensor_data: Dict[str, Any]) -> str:
        """
        Create an Excel report with charts from sensor data.
        Gera gráficos de linha para cada sensor.
        """
        # 1. Carregar o mapeamento de nomes amigáveis dos sensores
        config_path = os.path.join(os.path.dirname(
            __file__), '../../config/ui_config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            ui_config = json.load(f)

        # 2. Criar um dicionário para mapear sensor_full_topic para nome amigável
        topic_to_name = {}
        for group in ui_config.values():
            for sensor in group:
                full_topic = f"{sensor['gateway']}-{sensor['topic']}-{sensor['indicator']}"
                topic_to_name[full_topic] = sensor['name']

        # 3. Definir a ordem das colunas dinamicamente
        present_names = []
        for group in ui_config.values():
            for sensor in group:
                full_topic = f"{sensor['gateway']}-{sensor['topic']}-{sensor['indicator']}"
                if full_topic in sensor_data:
                    present_names.append(sensor['name'])
        col_names = present_names
        topics_in_order = [
            k for k, v in topic_to_name.items() if v in col_names]

        # 4. Coletar todos os timestamps únicos e ordenar
        all_timestamps = set()
        for topic in topics_in_order:
            for entry in sensor_data.get(topic, []):
                all_timestamps.add(entry['timestamp'])
        sorted_timestamps = sorted(all_timestamps)

        # 5. Montar dados com interpolação
        topic_time_value = {}
        for topic in topics_in_order:
            topic_time_value[topic] = {}
            last_known_value = None

            sorted_entries = sorted(sensor_data.get(
                topic, []), key=lambda x: x['timestamp'])

            for entry in sorted_entries:
                topic_time_value[topic][entry['timestamp']] = entry['value']
                last_known_value = entry['value']

            for ts in sorted_timestamps:
                if ts not in topic_time_value[topic]:
                    topic_time_value[topic][ts] = last_known_value

        # 6. Criar o arquivo Excel
        wb = Workbook()
        ws = wb.active
        if (ws == None):
            self._logger.error(
                "Failed to create Excel report - no worksheet found")
            return ""
        ws.title = "Dados dos Sensores"

        # 7. Adicionar cabeçalho
        header = ["Timestamp"] + col_names
        ws.append(header)

        # 8. Preencher dados
        for ts in sorted_timestamps:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                formatted_timestamp = dt.strftime("%d/%m/%Y %H:%M:%S")
            except:
                formatted_timestamp = ts

            row = [formatted_timestamp]
            for topic in topics_in_order:
                value = topic_time_value[topic][ts]
                row.append(value)
            ws.append(row)

        # 9. Criar gráfico de linha
        chart = LineChart()
        chart.title = "Leituras dos Sensores"
        chart.style = 13
        chart.x_axis.title = "Tempo"
        chart.y_axis.title = "Valor"

        # Definir dados para o gráfico
        # Categorias (eixo X) - timestamps
        categories = Reference(ws, min_col=1, min_row=2,
                               max_row=len(sorted_timestamps) + 1)

        # Dados (eixo Y) - valores dos sensores
        data = Reference(ws, min_col=2, max_col=len(col_names) + 1,
                         min_row=1, max_row=len(sorted_timestamps) + 1)

        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)

        # 10. Adicionar gráfico à planilha
        ws.add_chart(chart, ("A" + str(len(sorted_timestamps) + 5)))

        # 11. Ajustar largura das colunas
        for i, col in enumerate(header, 1):
            ws.column_dimensions[get_column_letter(i)].width = 20

        # 12. Salvar o arquivo
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.abspath(f"chart_report_{now_str}.xlsx")
        wb.save(file_path)
        return file_path
