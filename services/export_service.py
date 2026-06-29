import json
import xml.etree.ElementTree as ET
from pathlib import Path


class ExportService:
    def export(self, data: dict, output_format: str, output_path: str) -> None:
        if output_format == "json":
            self._export_json(data, output_path)
        elif output_format == "xml":
            self._export_xml(data, output_path)
        else:
            raise ValueError("Output format must be 'json' or 'xml'.")

    def _export_json(self, data: dict, output_path: str) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def _export_xml(self, data: dict, output_path: str) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        root = ET.Element("results")

        for query_name, rows in data.items():
            query_element = ET.SubElement(root, query_name)

            for row in rows:
                row_element = ET.SubElement(query_element, "row")

                for key, value in row.items():
                    field = ET.SubElement(row_element, key)
                    field.text = str(value)

        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)
