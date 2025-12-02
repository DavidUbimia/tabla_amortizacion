"""
Tests for the export service module.
"""

import io
from datetime import datetime

import pandas as pd
import pytest

from services.export_service import (
    CSVExporter,
    ExcelExporter,
    PDFExporter,
    ExportService
)


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'Mes': [0, 1, 2, 3],
        'Pago': [0.0, 1000.0, 1000.0, 1000.0],
        'Interés': [0.0, 100.0, 90.0, 80.0],
        'Abono a capital': [0.0, 900.0, 910.0, 920.0],
        'Saldo restante': [10000.0, 9100.0, 8190.0, 7270.0]
    })


@pytest.fixture
def sample_metadata():
    """Create sample metadata for testing."""
    return {
        'title': 'Test Amortization Table',
        'parameters': {
            'Monto': '$10,000.00',
            'Tasa anual': '12.0%',
            'Plazo': '12 meses'
        }
    }


class TestCSVExporter:
    """Tests for CSVExporter."""
    
    def test_export_returns_bytes(self, sample_dataframe):
        """Test that CSV export returns bytes."""
        exporter = CSVExporter()
        result = exporter.export(sample_dataframe, {})
        assert isinstance(result, bytes)
    
    def test_export_includes_headers(self, sample_dataframe):
        """Test that CSV includes column headers."""
        exporter = CSVExporter()
        result = exporter.export(sample_dataframe, {})
        csv_string = result.decode('utf-8-sig')
        assert 'Mes' in csv_string
        assert 'Pago' in csv_string
        assert 'Interés' in csv_string
    
    def test_export_includes_data(self, sample_dataframe):
        """Test that CSV includes data rows."""
        exporter = CSVExporter()
        result = exporter.export(sample_dataframe, {})
        csv_string = result.decode('utf-8-sig')
        assert '1000.0' in csv_string
        assert '10000.0' in csv_string
    
    def test_export_uses_utf8_bom(self, sample_dataframe):
        """Test that CSV uses UTF-8 BOM encoding."""
        exporter = CSVExporter()
        result = exporter.export(sample_dataframe, {})
        # UTF-8 BOM is EF BB BF
        assert result[:3] == b'\xef\xbb\xbf'


class TestExcelExporter:
    """Tests for ExcelExporter."""
    
    def test_export_returns_bytes(self, sample_dataframe):
        """Test that Excel export returns bytes."""
        exporter = ExcelExporter()
        result = exporter.export(sample_dataframe, {})
        assert isinstance(result, bytes)
    
    def test_export_creates_valid_excel(self, sample_dataframe):
        """Test that Excel export creates a valid Excel file."""
        exporter = ExcelExporter()
        result = exporter.export(sample_dataframe, {})
        
        # Try to read it back with pandas
        buffer = io.BytesIO(result)
        df_read = pd.read_excel(buffer, sheet_name='Data')
        
        # Check that data matches
        assert len(df_read) == len(sample_dataframe)
        assert list(df_read.columns) == list(sample_dataframe.columns)
    
    def test_export_with_custom_sheet_name(self, sample_dataframe):
        """Test Excel export with custom primary sheet name."""
        exporter = ExcelExporter()
        metadata = {'primary_sheet_name': 'Amortization'}
        result = exporter.export(sample_dataframe, metadata)
        
        buffer = io.BytesIO(result)
        df_read = pd.read_excel(buffer, sheet_name='Amortization')
        assert len(df_read) == len(sample_dataframe)
    
    def test_export_with_additional_sheets(self, sample_dataframe):
        """Test Excel export with multiple sheets."""
        exporter = ExcelExporter()
        
        summary_df = pd.DataFrame({
            'Metric': ['Total Paid', 'Total Interest'],
            'Value': [3000.0, 270.0]
        })
        
        metadata = {
            'primary_sheet_name': 'Schedule',
            'additional_sheets': [
                ('Summary', summary_df)
            ]
        }
        
        result = exporter.export(sample_dataframe, metadata)
        
        buffer = io.BytesIO(result)
        
        # Check both sheets exist
        df_schedule = pd.read_excel(buffer, sheet_name='Schedule')
        df_summary = pd.read_excel(buffer, sheet_name='Summary')
        
        assert len(df_schedule) == len(sample_dataframe)
        assert len(df_summary) == 2


class TestPDFExporter:
    """Tests for PDFExporter."""
    
    def test_export_returns_bytes(self, sample_dataframe, sample_metadata):
        """Test that PDF export returns bytes."""
        exporter = PDFExporter()
        result = exporter.export(sample_dataframe, sample_metadata)
        assert isinstance(result, bytes)
    
    def test_export_creates_valid_pdf(self, sample_dataframe, sample_metadata):
        """Test that PDF export creates a valid PDF file."""
        exporter = PDFExporter()
        result = exporter.export(sample_dataframe, sample_metadata)
        
        # Check PDF magic number (starts with %PDF)
        assert result[:4] == b'%PDF'
    
    def test_export_without_metadata(self, sample_dataframe):
        """Test PDF export with minimal metadata."""
        exporter = PDFExporter()
        result = exporter.export(sample_dataframe, {})
        assert isinstance(result, bytes)
        assert result[:4] == b'%PDF'


class TestExportService:
    """Tests for ExportService orchestrator."""
    
    def test_service_has_all_exporters(self):
        """Test that service initializes with all exporters."""
        service = ExportService()
        assert 'csv' in service.exporters
        assert 'excel' in service.exporters
        assert 'pdf' in service.exporters
    
    def test_export_csv(self, sample_dataframe):
        """Test exporting via service with CSV format."""
        service = ExportService()
        result = service.export('csv', sample_dataframe)
        assert isinstance(result, bytes)
        assert result[:3] == b'\xef\xbb\xbf'  # UTF-8 BOM
    
    def test_export_excel(self, sample_dataframe):
        """Test exporting via service with Excel format."""
        service = ExportService()
        result = service.export('excel', sample_dataframe)
        assert isinstance(result, bytes)
    
    def test_export_pdf(self, sample_dataframe, sample_metadata):
        """Test exporting via service with PDF format."""
        service = ExportService()
        result = service.export('pdf', sample_dataframe, sample_metadata)
        assert isinstance(result, bytes)
        assert result[:4] == b'%PDF'
    
    def test_export_case_insensitive(self, sample_dataframe):
        """Test that format parameter is case-insensitive."""
        service = ExportService()
        result_lower = service.export('csv', sample_dataframe)
        result_upper = service.export('CSV', sample_dataframe)
        assert result_lower == result_upper
    
    def test_export_invalid_format_raises_error(self, sample_dataframe):
        """Test that invalid format raises ValueError."""
        service = ExportService()
        with pytest.raises(ValueError, match="Unsupported export format"):
            service.export('invalid', sample_dataframe)
    
    def test_generate_filename_default_timestamp(self):
        """Test filename generation with default timestamp."""
        service = ExportService()
        filename = service.generate_filename('amortization', 'csv')
        
        assert filename.startswith('amortization_')
        assert filename.endswith('.csv')
        assert len(filename.split('_')) >= 2  # Has timestamp
    
    def test_generate_filename_custom_timestamp(self):
        """Test filename generation with custom timestamp."""
        service = ExportService()
        timestamp = datetime(2024, 1, 15, 14, 30, 45)
        filename = service.generate_filename('sensitivity', 'xlsx', timestamp)
        
        assert filename == 'sensitivity_2024-01-15_14-30-45.xlsx'
    
    def test_generate_filename_format(self):
        """Test that filename follows the required format."""
        service = ExportService()
        timestamp = datetime(2024, 12, 1, 10, 0, 0)
        filename = service.generate_filename('test_report', 'pdf', timestamp)
        
        # Format should be: {report_type}_{timestamp}.{extension}
        assert filename == 'test_report_2024-12-01_10-00-00.pdf'
        assert filename.startswith('test_report_')
        assert filename.endswith('.pdf')
        # Timestamp should be in ISO format
        assert '2024-12-01' in filename
