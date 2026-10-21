import numpy as np
import pandas as pd
import uniserde
from uniserde import ObjectId

from .. import constants, data_models

SERDE = uniserde.JsonSerde()


class FieldsSerializer:

    @staticmethod
    def serialize_fields_to_df(fields: list[data_models.Field]) -> pd.DataFrame:
        if not fields:
            return pd.DataFrame()
    
        base_meta = ["header", "group", "type", "desc", "ref"]
        measurement_meta = ["trait", "unit", "method"]
        processed_dfs = []
        for field in fields:
            doc = SERDE.as_json(field)
            del doc["_id"]
            del doc["owner_id"]
            del doc["scope"]

            meta_data = {k: doc.get(k, "") for k in base_meta}
            if isinstance(field, data_models.Measurement):
                for k in measurement_meta:
                    meta_data[k] = doc.get(k, "")
            
            meta_df = pd.DataFrame([meta_data])

            # Create the Item Rows (starting from a fresh row)
            record_key = next((k for k in ['params', 'values'] if k in doc), None)
            if record_key and len(doc[record_key]) > 0:
                item_df = pd.DataFrame(doc[record_key]).add_prefix('item_')
                # Combine: Meta row first, then Item rows below it
                doc_df = pd.concat([meta_df, item_df], ignore_index=True)
            else:
                doc_df = meta_df

            processed_dfs.append(doc_df)

        df = pd.concat(processed_dfs, ignore_index=True)
        
        # Organize columns: root columns first, then item columns
        base_cols = [c for c in base_meta if c in df.columns]
        measurement_cols = [c for c in measurement_meta if c in df.columns]
        item_cols = [c for c in df.columns if c.startswith("item_")]
        return df[base_cols + measurement_cols + item_cols]

    @staticmethod
    def deserialize_fields_from_df(df: pd.DataFrame) -> tuple[list[data_models.Field], list[str]]:
        if df.empty:
            return [], []

        df = df.fillna("")
        df.columns = df.columns.str.lower()

        valid_cols = ["header", "group", "type", "desc", "ref", "trait", "unit", "method", "item_header", "item_desc", "item_param", "item_value"]
        if not (set(df.columns) <= set(valid_cols)):
            return [], []

        # Grouping based on the 'header' column
        doc_identifier = (df['header'] != "").cumsum()
        output_json = []

        for _, group in df.groupby(doc_identifier, sort=False):
            first_row = group.iloc[0]
            doc = {}
            
            # Identify column types
            item_cols = [c for c in df.columns if c.startswith('item_')]
            meta_cols = [c for c in df.columns if c not in item_cols]

            # Extract Metadata from the first row
            for col in meta_cols:
                val = first_row[col]
                # Skip empty strings for now; we will enforce mandatory fields later
                if val != "":
                    doc[col] = val

            # Type-Specific Enforcement
            doc_type = doc.get('type', '')
            
            # Mandatory for ALL docs
            for field in ['desc', 'ref', 'group']:
                if field not in doc:
                    doc[field] = ""
            
            # Mandatory ONLY for Measurement
            if doc_type == "Measurement":
                for field in ['trait', 'unit', 'method']:
                    if field not in doc:
                        # Look at the dataframe column; if it exists, take value, else ""
                        doc[field] = first_row.get(field, "")

            doc_type = doc.get('type', '')
            list_key = None
            if doc_type == "Measurement":
                list_key = 'params'
            elif doc_type == "Category":
                list_key = 'values'
            
            if list_key:
                items = []
                if len(group) > 1:
                    item_rows = group.iloc[1:]
                    active_item_cols = [c for c in item_rows.columns if c.startswith('item_') and (item_rows[c] != "").any()]
                    for _, row in item_rows.iterrows():
                        item = {c.replace('item_', ''): row[c] for c in active_item_cols if row[c] != ""}
                        if item:
                            if doc_type == "Category" and 'desc' not in item:
                                item['desc'] = ""
                            items.append(item)

                doc[list_key] = items

            output_json.append(doc)

        output_headers = [doc["header"] for doc in output_json if "header" in doc]
        output_fields = []
        for doc in output_json:
            doc["_id"] = str(ObjectId())
            doc["owner_id"] = str(ObjectId())
            doc["scope"] = data_models.Scope.USER.name

            try:
                field = SERDE.from_json(constants.FIELD_TYPE_DICT[doc["type"]], doc)
            except Exception as e:
                print(f"An error occurred parsing the following field: {doc}")
                print(e)
                continue

            output_fields.append(field)

        return output_fields, output_headers
