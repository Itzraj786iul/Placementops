from __future__ import annotations

import csv
import io
from typing import Iterable

from openpyxl import Workbook

from app.modules.exports.enums import COLUMN_LABELS, ExportColumn


def build_csv(columns: list[ExportColumn], rows: Iterable[dict[str, str]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[column.value for column in columns],
        extrasaction="ignore",
    )
    writer.writerow({column.value: COLUMN_LABELS[column] for column in columns})
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8-sig")


def build_xlsx(columns: list[ExportColumn], rows: Iterable[dict[str, str]]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Applications"

    headers = [COLUMN_LABELS[column] for column in columns]
    sheet.append(headers)

    keys = [column.value for column in columns]
    for row in rows:
        sheet.append([row.get(key, "") for key in keys])

    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()
