import pytest
from datetime import datetime, timedelta

from enums import ReportTypeEnum, ExportFormatEnum
from models.report import Report


class TestReport:
    @pytest.fixture
    def report_period(self):
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        return start_date, end_date

    @pytest.fixture
    def document_status_report(self, report_period):
        return Report(
            report_type=ReportTypeEnum.DOCUMENT_STATUS,
            period=report_period
        )

    def test_create_object(self, report_period):
        report = Report(
            report_type=ReportTypeEnum.DOCUMENT_STATUS,
            period=report_period
        )
        assert report.report_type == ReportTypeEnum.DOCUMENT_STATUS
        assert report.period == report_period
        assert report.parameters == {}
        assert report.data is None

    def test_generate_document_status_report(self, document_status_report, document):
        documents = [document]
        result = document_status_report._generate_document_status_report(documents)

        assert "Document Status Report" in result
        assert f"Document ID: {document.id}" in result
        assert f"Status: {document.status}" in result

    def test_generate_report(self, document_status_report, document):
        documents = [document]
        result = document_status_report.generate_report(documents=documents)

        assert "Document Status Report" in result
        assert f"Document ID: {document.id}" in result
        assert f"Status: {document.status}" in result

    def test_generate_unsupported_report_type(self, report_period, document):
        report = Report(
            report_type="unsupported_type",
            period=report_period
        )
        documents = [document]
        result = report.generate_report(documents=documents)

        assert "Unsupported report type" in result

    def test_export_to_text(self, document_status_report):
        document_status_report.data = "Some report data"
        result = document_status_report._export_to_text()

        assert "exported to report.txt" in result

    def test_export_to_pdf(self, document_status_report):
        document_status_report.data = "Some report data"
        result = document_status_report._export_to_pdf()

        assert "exported to report.pdf" in result

    def test_export_no_data(self, document_status_report):
        result = document_status_report._export_to_text()

        assert "No data to export" in result

    def test_export_report_text_format(self, document_status_report):
        document_status_report.data = "Some report data"
        result = document_status_report.export_report(format=ExportFormatEnum.TEXT)

        assert "exported to report.txt" in result

    def test_export_report_pdf_format(self, document_status_report):
        document_status_report.data = "Some report data"
        result = document_status_report.export_report(format=ExportFormatEnum.PDF)

        assert "exported to report.pdf" in result

    def test_export_report_unsupported_format(self, document_status_report):
        document_status_report.data = "Some report data"
        unsupported_format = "UNSUPPORTED"
        result = document_status_report.export_report(format=unsupported_format)

        assert f"Unsupported export format: {unsupported_format}" in result