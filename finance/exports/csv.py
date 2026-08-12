import csv

from django.http import HttpResponse


def create_csv_response(
    *,
    filename: str,
    headers: list[str],
    rows,
) -> HttpResponse:
    """
    Create a UTF-8 CSV HTTP response.

    UTF-8 BOM is intentionally added so applications such as
    Microsoft Excel correctly detect Persian/Unicode text.
    """

    response = HttpResponse(
        content_type="text/csv; charset=utf-8-sig",
    )

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    writer.writerow(headers)

    for row in rows:
        writer.writerow(row)

    return response
