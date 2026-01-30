import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Ensure we can import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import Bridge

class TestBridge:
    @pytest.fixture
    def bridge(self):
        with patch('api.SettingsManager') as MockSettings, \
             patch('api.AIEngine') as MockAI, \
             patch('api.LatexEngine') as MockLatex:
            
            # Setup default mocks
            MockSettings.return_value.get.return_value = "default_value"
            
            bridge = Bridge()
            return bridge

    def test_save_pdf_no_pdf(self, bridge):
        """Test save_pdf when no PDF has been generated yet."""
        bridge.last_pdf_path = None
        result = bridge.save_pdf()
        assert result['success'] is False
        assert "No PDF generated yet" in result['error']

    def test_save_pdf_no_window(self, bridge):
        """Test save_pdf when window is not initialized."""
        bridge.last_pdf_path = "/tmp/fake.pdf"
        with patch('os.path.exists', return_value=True):
            bridge.window = None
            result = bridge.save_pdf()
            assert result['success'] is False
            assert "Window not initialized" in result['error']

    def test_save_pdf_success(self, bridge):
        """Test successful PDF save."""
        bridge.last_pdf_path = "/tmp/source.pdf"
        bridge.window = MagicMock()
        bridge.window.create_file_dialog.return_value = "/tmp/dest.pdf"
        
        with patch('os.path.exists', return_value=True), \
             patch('shutil.copy') as mock_copy:
            
            result = bridge.save_pdf()
            
            assert result['success'] is True
            assert result['path'] == "/tmp/dest.pdf"
            mock_copy.assert_called_once_with("/tmp/source.pdf", "/tmp/dest.pdf")

    def test_save_pdf_cancel(self, bridge):
        """Test save_pdf when user cancels dialog."""
        bridge.last_pdf_path = "/tmp/source.pdf"
        bridge.window = MagicMock()
        bridge.window.create_file_dialog.return_value = None
        
        with patch('os.path.exists', return_value=True):
            result = bridge.save_pdf()
            assert result['success'] is False
            assert "Cancelled" in result['error']

    def test_generate_latex_source_success(self, bridge):
        """Test generating latex source from AI."""
        payload = {
            "job_description": "Software Engineer",
            "template_name": "modern",
            "user_data": '{"name": "John"}'
        }
        
        # Mock AI response
        bridge.ai.generate_resume_content.return_value = {"key": "value"}
        bridge.latex.render_template.return_value = "LATEX CONTENT"
        
        result = bridge.generate_latex_source(payload)
        
        assert result['success'] is True
        assert result['tex_content'] == "LATEX CONTENT"
        bridge.ai.generate_resume_content.assert_called_once()
        bridge.latex.render_template.assert_called_once_with("modern", {"key": "value"})

    def test_generate_latex_source_invalid_json(self, bridge):
        """Test generation with invalid user data JSON."""
        payload = {
            "user_data": "{invalid_json}"
        }
        result = bridge.generate_latex_source(payload)
        assert result['success'] is False
        assert "Invalid User Data JSON" in result['error']

    def test_compile_pdf_success(self, bridge):
        """Test PDF compilation."""
        tex_content = "some latex"
        bridge.latex.compile_pdf.return_value = ("/tmp/out.pdf", "log content")
        
        with patch('builtins.open', mock_open(read_data=b"PDF_DATA")), \
             patch('base64.b64encode', return_value=b"BASE64_PDF"):
             
            result = bridge.compile_pdf(tex_content)
            
            assert result['success'] is True
            assert result['pdf_base64'] == "BASE64_PDF"
            assert bridge.last_pdf_path == "/tmp/out.pdf"

    def test_compile_pdf_fail(self, bridge):
        """Test PDF compilation failure."""
        bridge.latex.compile_pdf.side_effect = Exception("Compilation failed")
        
        result = bridge.compile_pdf("bad latex")
        
        assert result['success'] is False
        assert "Compilation failed" in result['error']
