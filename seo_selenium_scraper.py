import time  # For sleep/delay to mimic human actions
import random  # For randomizing sleep intervals
import json  # For saving results in JSON format
import csv  # For reading/writing CSV files
import re  # For regular expressions (domain extraction)
from collections import Counter, defaultdict  # For counting and grouping domains
# Selenium: for browser automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# BeautifulSoup: for HTML parsing
from bs4 import BeautifulSoup
from wordcloud import WordCloud  # For generating word clouds
import matplotlib.pyplot as plt  # For plotting word clouds
import pygsheets  # For Google Sheets integration

# --- Anti-bot setup ---
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

# Function to load keywords from a CSV file
# Expects a column named '關鍵字' (Keyword)
def load_keywords_from_csv(csv_path):
    keywords = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header_found = False
        col_idx = None
        for row in reader:
            # Skip empty rows
            if not any(cell.strip() for cell in row):
                continue
            if not header_found:
                # Find the column index for '關鍵字'
                for idx, cell in enumerate(row):
                    if cell.strip() == '關鍵字':
                        col_idx = idx
                        header_found = True
                        break
                continue
            if header_found and col_idx is not None:
                # Extract keyword from the correct column
                if len(row) > col_idx and row[col_idx].strip():
                    keywords.append(row[col_idx].strip())
    print(f"[INFO] Loaded {len(keywords)} keywords from CSV: {keywords}")
    return keywords

# Load keywords at the start of the script
KEYWORDS = load_keywords_from_csv('keywords.csv')

# --- Selenium options ---
chrome_options = Options()
chrome_options.add_argument(f"user-agent={USER_AGENT}")  # Set custom user-agent
# chrome_options.add_argument("--headless")  # Uncomment for headless mode
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Sleep for a random interval to mimic human browsing
def random_sleep(a=2, b=4):
    time.sleep(random.uniform(a, b))

# Scroll the page down several times to load more content
def scroll_page(driver, scroll_pause=1, scroll_count=3):
    for _ in range(scroll_count):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")  # Scroll down
        time.sleep(scroll_pause)

# Try to click the 'Show More' button if it exists
def click_show_more(driver):
    try:
        show_more = driver.find_element(By.XPATH, '//button[contains(text(), "Show more") or contains(text(), "顯示更多")]')
        show_more.click()
        print("[INFO] Clicked 'Show More' button.")
        time.sleep(2)
    except Exception:
        pass  # Ignore if not found

# Try to click the link icon to reveal sources
def click_link_icon(driver):
    try:
        icon = driver.find_element(By.CLASS_NAME, 'niO4u')
        icon.click()
        print("[INFO] Clicked the link icon to reveal sources.")
        time.sleep(2)
    except Exception as e:
        print(f"[DEBUG] Could not click link icon: {e}")

# Extract AIO content and source links from the page
def get_aio_content(driver):
    # Use Selenium to scroll and click buttons
    scroll_page(driver, scroll_pause=1, scroll_count=5)
    click_show_more(driver)
    click_link_icon(driver)  
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all AIO content sections
    aio_sections = soup.find_all('div', class_='WaaZC')
    aio_texts = []
    for section in aio_sections:
        text = section.get_text(separator='\n', strip=True)
        if text:
            aio_texts.append(text)
    # Find all AIO source links
    aio_source_links = []
    for a_tag in soup.find_all('a', class_='KEVENd', href=True):
        label = a_tag.get('aria-label', '').strip()
        href = a_tag['href']
        aio_source_links.append({'text': label, 'href': href})
    print(f"[DEBUG] Found {len(aio_source_links)} AIO source links (KEVENd):")
    for link in aio_source_links:
        print(f"- {link['text']}: {link['href']}")
    
    if aio_texts:
        return {'text': '\n'.join(aio_texts), 'links': aio_source_links}
    return None

# Save the results to a CSV file
def save_results_csv(results, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['關鍵字', 'AIO內容', '來源連結'])  # Write header
        for keyword, data in results.items():
            text = data['text'] if data['text'] else ''
            links = '\n'.join([l['href'] for l in data['links']]) if data['links'] else ''
            writer.writerow([keyword, text, links])
    print(f"[INFO] Results saved to {csv_path}")

# Save domain analysis to a CSV file
def save_domain_analysis_csv(results, csv_path):
    domain_counts_per_keyword = defaultdict(Counter)
    for keyword, data in results.items():
        for link in data['links']:
            domain = extract_domain(link['href'])
            domain_counts_per_keyword[keyword][domain] += 1
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['關鍵字', '網域', '次數'])  # Write header
        for keyword, counter in domain_counts_per_keyword.items():
            for domain, count in counter.most_common():
                writer.writerow([keyword, domain, count])
    print(f"[INFO] Domain analysis saved to {csv_path}")

# Export results directly to Google Sheets
def export_to_google_sheets(results, credentials_file='credentials.json', spreadsheet_name='SEO Scraper Results'):
    """
    Export results directly to Google Sheets using pygsheets.
    
    Args:
        results: Dictionary containing the scraping results
        credentials_file: Path to Google Sheets API credentials JSON file
        spreadsheet_name: Name of the Google Sheets spreadsheet to create/use
    """
    try:
        # Authorize with Google Sheets API
        gc = pygsheets.authorize(service_file=credentials_file)
        
        # Try to open existing spreadsheet first
        try:
            spreadsheet = gc.open(spreadsheet_name)
            print(f"[INFO] Opened existing spreadsheet: {spreadsheet_name}")
        except pygsheets.SpreadsheetNotFound:
            # If no existing spreadsheet, try to create one
            try:
                spreadsheet = gc.create(spreadsheet_name)
                print(f"[INFO] Created new spreadsheet: {spreadsheet_name}")
            except Exception as create_error:
                print(f"[WARNING] Could not create spreadsheet: {create_error}")
                print("[INFO] Trying to use a shared spreadsheet instead...")
                
                # Try to open any available spreadsheet
                try:
                    all_spreadsheets = gc.open_all()
                    if all_spreadsheets:
                        spreadsheet = all_spreadsheets[0]  # Use the first available
                        print(f"[INFO] Using existing spreadsheet: {spreadsheet.title}")
                    else:
                        print("[ERROR] No spreadsheets available and cannot create new ones")
                        print("[INFO] Please manually create a Google Sheets file and share it with the service account")
                        return None
                except Exception as list_error:
                    print(f"[ERROR] Cannot list spreadsheets: {list_error}")
                    return None
        
        # Create worksheet for main results
        try:
            worksheet = spreadsheet.worksheet_by_title('AIO Results')
        except pygsheets.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title='AIO Results', rows=1000, cols=10)
        
        # Prepare data for Google Sheets
        sheet_data = [['關鍵字', 'AIO內容', '來源連結']]  # Header
        for keyword, data in results.items():
            text = data['text'] if data['text'] else ''
            links = '\n'.join([l['href'] for l in data['links']]) if data['links'] else ''
            sheet_data.append([keyword, text, links])
        
        # Update worksheet with data
        worksheet.update_values('A1', sheet_data)
        print(f"[INFO] Exported {len(results)} results to Google Sheets")
        
        # Create worksheet for domain analysis
        try:
            domain_worksheet = spreadsheet.worksheet_by_title('Domain Analysis')
        except pygsheets.WorksheetNotFound:
            domain_worksheet = spreadsheet.add_worksheet(title='Domain Analysis', rows=1000, cols=5)
        
        # Prepare domain analysis data
        domain_counts_per_keyword = defaultdict(Counter)
        for keyword, data in results.items():
            for link in data['links']:
                domain = extract_domain(link['href'])
                domain_counts_per_keyword[keyword][domain] += 1
        
        domain_sheet_data = [['關鍵字', '網域', '次數']]  # Header
        for keyword, counter in domain_counts_per_keyword.items():
            for domain, count in counter.most_common():
                domain_sheet_data.append([keyword, domain, count])
        
        # Update domain analysis worksheet
        domain_worksheet.update_values('A1', domain_sheet_data)
        print(f"[INFO] Exported domain analysis to Google Sheets")
        
        # Get the spreadsheet URL
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
        print(f"[INFO] Google Sheets URL: {spreadsheet_url}")
        
        return spreadsheet_url
        
    except Exception as e:
        print(f"[ERROR] Failed to export to Google Sheets: {e}")
        print("[INFO] Make sure you have:")
        print("1. Created a Google Cloud Project")
        print("2. Enabled Google Sheets API")
        print("3. Created a service account and downloaded credentials.json")
        print("4. Shared your Google Sheets with the service account email")
        print("5. OR manually create a Google Sheets file and share it with the service account")
        return None

# Generate a word cloud from all AIO text
def generate_wordcloud(all_text):
    if not all_text.strip():
        print("[INFO] No AIO text to generate word cloud.")
        return
    font_path = 'NotoSansMonoCJKtc-VF.otf'  # Font for Chinese/Japanese
    wc = WordCloud(font_path=font_path, width=800, height=400, background_color='white', collocations=False).generate(all_text)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('AIO內容 Word Cloud')
    plt.savefig('aio_wordcloud.png', bbox_inches='tight')  # Save to file
    plt.show()

# Extract domain from a URL using regex
def extract_domain(url):
    match = re.search(r'https?://([^/]+)/?', url)
    return match.group(1) if match else url

# Print domain analysis to terminal
def domain_analysis(results):
    domain_counts_overall = Counter()
    domain_counts_per_keyword = defaultdict(Counter)
    for keyword, data in results.items():
        for link in data['links']:
            domain = extract_domain(link['href'])
            domain_counts_overall[domain] += 1
            domain_counts_per_keyword[keyword][domain] += 1
    print("\n[INFO] Most cited domains OVERALL:")
    for domain, count in domain_counts_overall.most_common(10):
        print(f"{domain}: {count}")
    print("\n[INFO] Most cited domains PER KEYWORD:")
    for keyword, counter in domain_counts_per_keyword.items():
        print(f"- {keyword}")
        for domain, count in counter.most_common(5):
            print(f"    {domain}: {count}")

# --- Main script entry point ---
def main():
    # Start Selenium WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1200, 900)  # Set browser window size
    results = {}  # Store results for all keywords
    for keyword in KEYWORDS:
        print(f"Searching: {keyword}")
        driver.get("https://www.google.com/")  # Open Google homepage
        random_sleep(2, 4)  # Wait to mimic human
        try:
            search_box = driver.find_element(By.NAME, "q")  # Find search box
            search_box.clear()  # Clear any pre-filled text
            search_box.send_keys(keyword)  # Enter keyword
            random_sleep(1, 2)
            search_box.send_keys(Keys.RETURN)  # Submit search
            random_sleep(3, 5)
            # Save the full HTML for manual inspection
            with open('full_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("[INFO] Saved full page HTML to full_page.html. Please open this file and search for your AIO content.")
            # Extract AIO content and links
            aio_content = get_aio_content(driver)
            if aio_content:
                print(f"AIO content for '{keyword}':\n{aio_content['text']}\nLinks:")
                for link in aio_content['links']:
                    print(f"- {link['text']}: {link['href']}")
                print('-'*40)
                results[keyword] = aio_content
            else:
                print(f"No AIO content found for '{keyword}'.\n{'-'*40}")
                results[keyword] = {'text': 'NO_AIO_FOUND', 'links': []}
        except Exception as e:
            print(f"Error searching '{keyword}': {e}")
            results[keyword] = {'text': 'NO_AIO_FOUND', 'links': []}
        random_sleep(2, 4)
    driver.quit()  # Close browser
    # Save results to JSON for review
    with open('aio_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nResults saved to aio_results.json")
    # Save results to CSV
    save_results_csv(results, 'aio_results.csv')
    # Save domain analysis to CSV
    save_domain_analysis_csv(results, 'aio_domain_analysis.csv')
    # Export results to Google Sheets
    sheets_url = export_to_google_sheets(results)
    if sheets_url:
        print(f"[SUCCESS] Results exported to Google Sheets: {sheets_url}")
    # Generate word cloud from all AIO texts (excluding NO_AIO_FOUND)
    all_text = '\n'.join([v['text'] for v in results.values() if v['text'] and v['text'] != 'NO_AIO_FOUND'])
    generate_wordcloud(all_text)
    # Print domain analysis to terminal
    domain_analysis(results)
    print("\nSummary of results:")
    for k, v in results.items():
        print(f"{k}: {v['text'][:100]}{'...' if v['text'] and len(v['text']) > 100 else ''}")
        if v['links']:
            print("  Links:")
            for link in v['links']:
                print(f"    - {link['text']}: {link['href']}")

# Run main if this script is executed directly
if __name__ == "__main__":
    main()
