"""
Export service for generating CSV, Excel, and PDF files from loan data.

This module provides a unified interface for exporting loan calculations and
amortization schedules in multiple formats.
"""

from __future__ import annotations

import io
from typing import Protocol, Dict, Any, Optional
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


class ExportStrategy(Protocol):
    """Interface for export strategies."""
    
    def export(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> bytes:
        """
        Export data to specific format.
        
        Args:
            data: DataFrame containing the data to export
            metadata: Dictionary containing additional information like title, parameters, etc.
            
        Returns:
            Bytes of the exported file
        """
        ...


class CSVExporter:
    """Export to CSV format with UTF-8 BOM encoding."""
    
    def export(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> bytes:
        """
        Export DataFrame to CSV with UTF-8 BOM encoding.
        
        Args:
            data: DataFrame to export
            metadata: Not used for CSV export, but kept for interface consistency
            
        Returns:
            CSV file as bytes with UTF-8 BOM encoding
        """
        # Use utf-8-sig encoding which adds BOM for Excel compatibility
        csv_string = data.to_csv(index=False)
        return csv_string.encode('utf-8-sig')


class ExcelExporter:
    """Export to Excel with multiple sheets."""
    
    def export(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> bytes:
        """
        Export DataFrame to Excel with multiple sheets.
        
        Args:
            data: Primary DataFrame to export
            metadata: Dictionary that can contain:
                - 'additional_sheets': List of tuples (sheet_name, dataframe)
                - 'primary_sheet_name': Name for the primary data sheet (default: 'Data')
                
        Returns:
            Excel file as bytes
        """
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Write primary data sheet
            primary_sheet_name = metadata.get('primary_sheet_name', 'Data')
            data.to_excel(writer, sheet_name=primary_sheet_name, index=False)
            
            # Write additional sheets if provided
            additional_sheets = metadata.get('additional_sheets', [])
            for sheet_name, df in additional_sheets:
                if isinstance(df, pd.DataFrame):
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        buffer.seek(0)
        return buffer.getvalue()


class PDFExporter:
    """Export to PDF with formatting."""
    
    def export(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> bytes:
        """
        Export DataFrame to PDF with title, parameters, and formatted table.
        
        Migrated from functions.py generar_pdf_tabla().
        
        Args:
            data: DataFrame to export
            metadata: Dictionary containing:
                - 'title': Title for the PDF document
                - 'parameters': Dictionary of parameter key-value pairs to display
                
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        
        # Use landscape A4 for better table display
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=24,
            rightMargin=24,
            topMargin=24,
            bottomMargin=24
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Add title
        title = metadata.get('title', 'Report')
        elements.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
        elements.append(Spacer(1, 10))
        
        # Add parameters section
        parameters = metadata.get('parameters', {})
        if parameters:
            for key, value in parameters.items():
                elements.append(Paragraph(f"<b>{key}:</b> {value}", styles["Normal"]))
            elements.append(Spacer(1, 12))
        
        # Convert DataFrame to table data (all strings for stability)
        table_data = [list(map(str, data.columns.tolist()))]
        table_data.extend([list(map(str, row)) for row in data.values.tolist()])
        
        # Create table with header row repetition
        table = Table(table_data, repeatRows=1, hAlign="LEFT")
        
        # Apply table styling
        table.setStyle(TableStyle([
            # Header styling
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            
            # Alignment
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),  # First column centered
            
            # Grid and padding
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        buffer.seek(0)
        return buffer.getvalue()


class ExportService:
    """
    Orchestrates export operations for different file formats.
    
    This service provides a unified interface for exporting loan data
    in CSV, Excel, and PDF formats.
    """
    
    def __init__(self):
        """Initialize export service with available exporters."""
        self.exporters: Dict[str, ExportStrategy] = {
            'csv': CSVExporter(),
            'excel': ExcelExporter(),
            'pdf': PDFExporter()
        }
    
    def export(
        self,
        format: str,
        data: pd.DataFrame,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Export data in the specified format.
        
        Args:
            format: Export format ('csv', 'excel', or 'pdf')
            data: DataFrame containing the data to export
            metadata: Optional dictionary with format-specific metadata
            
        Returns:
            Exported file as bytes
            
        Raises:
            ValueError: If format is not supported
        """
        if metadata is None:
            metadata = {}
            
        format_lower = format.lower()
        
        if format_lower not in self.exporters:
            supported = ', '.join(self.exporters.keys())
            raise ValueError(
                f"Unsupported export format: '{format}'. "
                f"Supported formats: {supported}"
            )
        
        exporter = self.exporters[format_lower]
        return exporter.export(data, metadata)
    
    def generate_filename(
        self,
        report_type: str,
        extension: str,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate a standardized filename for exports.
        
        Format: {report_type}_{timestamp}.{extension}
        
        Args:
            report_type: Type of report (e.g., 'amortization', 'sensitivity')
            extension: File extension (e.g., 'csv', 'xlsx', 'pdf')
            timestamp: Optional timestamp (defaults to current time)
            
        Returns:
            Formatted filename string
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Format timestamp as ISO format (YYYY-MM-DD_HH-MM-SS)
        timestamp_str = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
        
        return f"{report_type}_{timestamp_str}.{extension}"
