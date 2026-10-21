import itertools
from io import BytesIO
import xlsxwriter
import pandas as pd

from .fields_serializer import FieldsSerializer
from .. import constants, data_models


MAX_ROW = 1048575
MAX_COL = 16383


class XlsxGenerator:

    @staticmethod
    def clean_csv_str(data: str) -> str:
        # Comma is the inline list's own delimiter with no escape mechanism
        # in this format, so it genuinely can't be preserved without
        # switching to a cell-range source instead of a literal list - it's
        # stripped rather than corrupting the list.
        data = data.replace(',', '')

        # xlsxwriter's data_validation() wraps the whole joined list in a
        # single pair of double quotes with no escaping of its own (see
        # _write_formula_1 in xlsxwriter's worksheet.py), so an embedded `"`
        # would otherwise prematurely terminate that wrapping string as far
        # as Excel's formula parser is concerned, corrupting everything
        # after it. Doubling it instead follows Excel's own string-literal
        # escape convention, so the true value round-trips correctly.
        data = data.replace('"', '""')

        # A leading `'` is separately consumed by Excel's own text-qualifier
        # autoformat the moment the value lands in a cell - whether typed or
        # selected from this very dropdown - stripping exactly one leading
        # apostrophe from the stored value. Prefixing with an extra `'`
        # compensates: that one gets consumed as the qualifier, leaving the
        # real leading apostrophe intact in what's actually stored.
        if data.startswith("'"):
            data = "'" + data

        return data

    @staticmethod
    def _write_df_sheet(sheet, df, bold_format, na_format):
        headers = [header.capitalize() for header in df.columns]
        sheet.write_row(0, 0, headers)
        for row_num, row_data in enumerate(df.values.tolist(), start=1):
            for col_num, cell_data in enumerate(row_data):
                sheet.write(
                    row_num,
                    col_num,
                    "" if pd.isnull(cell_data) else cell_data,
                    na_format if pd.isnull(cell_data) else None,
                )
        sheet.set_row(0, None, bold_format)
        sheet.freeze_panes(1, 0)
        sheet.autofit()

    @staticmethod
    def generate_field_def(
        fields: list[data_models.Field],
    ) -> BytesIO:
        output_bytes = BytesIO()
        with xlsxwriter.Workbook(output_bytes, {'nan_inf_to_errors': True}) as xlsx:
            bold_format = xlsx.add_format()
            bold_format.set_bold()
            na_format = xlsx.add_format()
            na_format.set_bg_color("#D9D9D9")
            
            fields_sheet = xlsx.add_worksheet("FieldDefinitions")
            fields_df = FieldsSerializer.serialize_fields_to_df(fields)
            XlsxGenerator._write_df_sheet(fields_sheet, fields_df, bold_format, na_format)
        
        return output_bytes

    @staticmethod
    def generate_workbook(
        workbook: data_models.Template,
        date_format: str,
        df: pd.DataFrame | None = None,
        include_constant_category: bool = False,
        standardisation_log_df: pd.DataFrame | None = None,
    ) -> BytesIO:
        output_bytes = BytesIO()
        _fields = workbook.get_fields_dict()
        with xlsxwriter.Workbook(output_bytes, {'nan_inf_to_errors': True}) as xlsx:
            all_dropdown_selections = workbook.get_all_dropdown_selections_dict()
            field_selections = workbook.get_field_selection_dict()

            bold_format = xlsx.add_format()
            bold_format.set_bold()
            na_format = xlsx.add_format()
            na_format.set_bg_color("#D9D9D9")
            date_cell_format = xlsx.add_format({
                'num_format': constants.DATE_FORMAT_XLSX_NUM_FORMAT[date_format],
            })

            metadata_sheet = xlsx.add_worksheet("Metadata")
            
            data = [
                'ID',
                'Template',
                'Project Title',
                'Project Code',
                'Project Lead',
                'Data Steward',
                'Project Start Date',
                'Project End Date',
            ]
            metadata_sheet.write_column(0, 0, data)
            metadata_sheet.set_column(0, 0, 20, bold_format)
            metadata_sheet.write('B1', str(workbook.id))
            metadata_sheet.write('B2', workbook.template_name)

            fields_sheet = xlsx.add_worksheet("FieldDefinitions")
            fields_df = FieldsSerializer.serialize_fields_to_df(workbook.get_selected_fields())
            XlsxGenerator._write_df_sheet(fields_sheet, fields_df, bold_format, na_format)

            constant_sheet = xlsx.add_worksheet("ConstantCategoryFields")
            constant_fields = set()
            index = 0
            for field_id in workbook.field_order:
                if not field_selections[field_id]:
                    continue
                if field_id not in all_dropdown_selections:
                    continue

                source = [XlsxGenerator.clean_csv_str(header) for header, value in all_dropdown_selections[field_id].items() if value]
                if len(source) != 1:
                    continue

                constant_fields.add(field_id)
                constant_sheet.write(0, index, _fields[field_id].header)
                constant_sheet.write(1, index, source[0])
                index += 1
            
            constant_sheet.set_row(0, None, bold_format)
            constant_sheet.freeze_panes(1, 0)
            constant_sheet.autofit()

            raw_sheet = xlsx.add_worksheet("RawData")
            index = 0
            for field_id in workbook.field_order:
                if not field_selections[field_id]:
                    continue
                if not include_constant_category:
                    if field_id in constant_fields:
                        continue

                raw_sheet.write(0, index, _fields[field_id].header)
                if field_id in all_dropdown_selections:
                    source = [XlsxGenerator.clean_csv_str(header) for header, value in all_dropdown_selections[field_id].items() if value]
                    raw_sheet.data_validation(1, index, MAX_ROW, index, {
                        'validate': 'list',
                        'source': source,
                    })
                if isinstance(_fields[field_id], data_models.Date):
                    raw_sheet.set_column(index, index, None, date_cell_format)
                index += 1
            
            if df is not None:
                df_filtered = df
                if not include_constant_category:
                    constant_field_headers = [_fields[field_id].header for field_id in constant_fields]
                    df_filtered = df.drop(columns=constant_field_headers)
                
                for row_num, row_data in enumerate(df_filtered.values.tolist(), start=1):
                    raw_sheet.write_row(row_num, 0, row_data)
            
            raw_sheet.set_row(0, None, bold_format)
            raw_sheet.freeze_panes(1, 0)
            raw_sheet.autofit()

            if standardisation_log_df is not None and not standardisation_log_df.empty:
                log_sheet = xlsx.add_worksheet("StandardisationLog")
                XlsxGenerator._write_df_sheet(log_sheet, standardisation_log_df, bold_format, na_format)

        return output_bytes

    @staticmethod
    def generate_qr(
        workbook: data_models.Template,
    ) -> BytesIO:
        output_bytes = BytesIO()
        _fields = workbook.get_fields_dict()
        with xlsxwriter.Workbook(output_bytes) as xlsx:
            all_dropdown_selections = workbook.get_all_dropdown_selections_dict()
            field_selections = workbook.get_field_selection_dict()

            bold_format = xlsx.add_format()
            bold_format.set_bold()

            qr_sheet = xlsx.add_worksheet("QRCode")
            values_list = []
            index = 0
            for field_id in workbook.field_order:
                if not field_selections[field_id]:
                    continue
                if field_id not in all_dropdown_selections:
                    continue

                source = [XlsxGenerator.clean_csv_str(header) for header, value in all_dropdown_selections[field_id].items() if value]
                if len(source) > 1:
                    qr_sheet.write(0, index, _fields[field_id].header)
                    values_list.append(source)
                    index += 1
            
            if values_list:
                data = list(itertools.product(*values_list))
                qr_sheet.add_table(1, 0, len(data), len(values_list)-1, {
                    'data': data,
                    'header_row': False,
                    'style': None,
                })

            qr_sheet.set_row(0, None, bold_format)
            qr_sheet.freeze_panes(1, 0)
            qr_sheet.autofit()

        return output_bytes
