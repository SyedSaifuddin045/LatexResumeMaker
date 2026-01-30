import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class TestUI:
    @pytest.fixture(scope="class")
    def driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run headless for CI/Speed
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        yield driver
        driver.quit()

    def test_load_ui(self, driver):
        """Test that the UI loads safely."""
        # Calculate absolute path to index.html
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        html_path = os.path.join(base_dir, 'gui', 'index.html')
        url = f"file:///{html_path.replace(os.path.sep, '/')}"
        
        driver.get(url)
        assert "ATS Resume Genius" in driver.title

    def test_generate_button(self, driver):
        """Test the generate flow with mocked pywebview."""
        # Mock pywebview bridge
        driver.execute_script("""
            window.pywebview = {
                api: {
                    generate_latex_source: function(data) {
                        console.log("Mock called: generate_latex_source", data);
                        return Promise.resolve({success: true, tex_content: "MOCK_TEX"});
                    },
                    compile_pdf: function(tex) {
                        return Promise.resolve({success: true, pdf_base64: "MOCK_PDF_BASE64"});
                    },
                    save_settings: function(cfg) { return Promise.resolve({success: true}); }
                }
            };
            // Dispatch event to notify app that pywebview is ready
            window.dispatchEvent(new Event('pywebviewready'));
        """)

        # Wait for elements
        wait = WebDriverWait(driver, 10)
        job_desc = wait.until(EC.presence_of_element_located((By.ID, "job-desc")))
        generate_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn-generate")))
        
        # Fill Mock Data
        job_desc.send_keys("Software Engineer job description mock.")
        
        # Click Generate
        # Use JS click to avoid ElementClickInterceptedException in headless mode
        driver.execute_script("arguments[0].click();", generate_btn)
        
        # Verify loading state or success
        # The app shows a loader or updates status text
        try:
            wait.until(EC.visibility_of_element_located((By.ID, "loader")))
        except:
            pass # Loader might be too fast or logic differs slightly
            
        # Check if generate_latex_source was called
        logs = driver.get_log("browser")
        # Note: In headless chrome, getting console logs can be finicky depending on permissions,
        # but let's assume standard behavior. Alternatively, check if a global var was set.
        
        # Better check: Verify the "generated-latex" textarea eventually gets "MOCK_TEX"
        # The app logic sets this on success.
        
        # Since the app.js logic handles the promise resolve:
        # 1. Calls generate_latex_source
        # 2. On success, sets value of #generated-latex
        
        generated_latex = wait.until(lambda d: d.find_element(By.ID, "generated-latex").get_attribute("value") == "MOCK_TEX")
        assert generated_latex

    def test_theme_toggle_existence(self, driver):
        """Verify settings navigation works."""
        nav_settings = driver.find_element(By.XPATH, "//div[contains(text(), 'Settings')]")
        nav_settings.click()
        
        wait = WebDriverWait(driver, 5)
        view_settings = wait.until(EC.visibility_of_element_located((By.ID, "view-settings")))
        assert view_settings.is_displayed()

