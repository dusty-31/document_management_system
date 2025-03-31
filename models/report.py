from datetime import datetime
from typing import Tuple, Dict, Any, List

from .document import Document
from enums import ReportTypeEnum, ExportFormatEnum


class Report:
    def __init__(
            self,
            report_type: ReportTypeEnum,
            period: Tuple[datetime, datetime],
            parameters: Dict[str, Any] = None,
    ) -> None:
        self.report_type = report_type
        self.period = period
        self.parameters = parameters if parameters else {}
        self.data = None  # Report data after generation

    def generate_report(self, documents: List[Document]) -> str:
        """
        Generate the report based on the report type and period.
        """
        if self.report_type == ReportTypeEnum.DOCUMENT_STATUS:
            return self._generate_document_status_report(documents)
        else:
            return f"Unsupported report type: {self.report_type}"

    def export_report(self, format: ExportFormatEnum = ExportFormatEnum.TEXT):
        """
        Export the generated report in the specified format.
        """
        if format == ExportFormatEnum.TEXT:
            return self._export_to_text()
        elif format == ExportFormatEnum.PDF:
            return self._export_to_pdf()
        else:
            return f"Unsupported export format: {format}"

    def _generate_document_status_report(self, documents: List[Document]) -> str:
        """
        Generate a report on the status of documents.
        """
        report = "Document Status Report\n"
        report += f"Period: {self.period[0]} to {self.period[1]}\n"
        for doc in documents:
            report += f"Document ID: {doc.id}, Status: {doc.status}\n"
        return report

    def _export_to_text(self) -> str:
        """
        Export the report data to a text file.
        """
        if self.data is None:
            return "No data to export."

        return "Report exported to report.txt"

    def _export_to_pdf(self) -> str:
        """
        Export the report data to a PDF file.
        """
        if self.data is None:
            return "No data to export."

        return "Report exported to report.pdf"
