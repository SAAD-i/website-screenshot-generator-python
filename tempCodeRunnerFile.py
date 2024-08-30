from flask import Flask, render_template, request, send_file, url_for, flash, redirect
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import validators

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Set up the path to the WebDriver
CHROME_DRIVER_PATH = r'C:\Users\Shaban\Desktop\Flask-Applicatioin\Website-ScreenShot-Generation\chromedriver-win64\chromedriver.exe'

# Function to take a screenshot of a website
def take_screenshot(url, device, full_page):
    print(f"Taking screenshot of {url} on {device} with full_page={full_page}")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    if device == 'mobile':
        mobile_emulation = {
            "deviceName": "Nexus 5"
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        driver.execute_script("document.body.style.overflow='hidden';")

        if full_page:
            total_width = driver.execute_script("return document.body.scrollWidth")
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(total_width, total_height)
        else:
            viewport_width = driver.execute_script("return window.innerWidth")
            viewport_height = driver.execute_script("return window.innerHeight")
            driver.set_window_size(viewport_width, viewport_height)

        screenshot_path = os.path.join('static', 'screenshot.png')
        driver.save_screenshot(screenshot_path)
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        flash(f"Error taking screenshot: {e}", 'error')
        screenshot_path = None
    finally:
        driver.quit()

    print(f"Screenshot path: {screenshot_path}")
    return screenshot_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if not validators.url(url):
            flash('Invalid URL. Please enter a valid URL starting with http:// or https://', 'error')
            return redirect(url_for('index'))
        
        device = request.form['device']
        full_page = request.form['full_page'] == 'full_page'
        screenshot_path = take_screenshot(url, device, full_page)
        if screenshot_path:
            screenshot_url = url_for('static', filename='screenshot.png')
            return render_template('result.html', screenshot_url=screenshot_url)
        else:
            flash('Failed to take screenshot. Please try again.', 'error')
            return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/download')
def download():
    screenshot_path = os.path.join('static', 'screenshot.png')
    return send_file(screenshot_path, mimetype='image/png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
