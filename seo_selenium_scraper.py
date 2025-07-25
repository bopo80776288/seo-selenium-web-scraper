import time
import random
import json
import csv
import re
from collections import Counter, defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Anti-bot setup ---
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

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
                for idx, cell in enumerate(row):
                    if cell.strip() == '關鍵字':
                        col_idx = idx
                        header_found = True
                        break
                continue
            if header_found and col_idx is not None:
                if len(row) > col_idx and row[col_idx].strip():
                    keywords.append(row[col_idx].strip())
    print(f"[INFO] Loaded {len(keywords)} keywords from CSV: {keywords}")
    return keywords

KEYWORDS = load_keywords_from_csv('keywords.csv')

# --- Selenium options ---
chrome_options = Options()
chrome_options.add_argument(f"user-agent={USER_AGENT}")
# chrome_options.add_argument("--headless")  # Uncomment if you want headless mode
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

def random_sleep(a=2, b=4):
    time.sleep(random.uniform(a, b))

def scroll_page(driver, scroll_pause=1, scroll_count=3):
    """Scroll down the page to load more content."""
    for _ in range(scroll_count):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(scroll_pause)

def click_show_more(driver):
    # Try to click the 'Show More' button if present
    try:
        show_more = driver.find_element(By.XPATH, '//button[contains(text(), "Show more") or contains(text(), "顯示更多")]')
        show_more.click()
        print("[INFO] Clicked 'Show More' button.")
        time.sleep(2)
    except Exception:
        pass

def click_link_icon(driver):
    try:
        icon = driver.find_element(By.CLASS_NAME, 'niO4u')
        icon.click()
        print("[INFO] Clicked the link icon to reveal sources.")
        time.sleep(2)
    except Exception as e:
        print(f"[DEBUG] Could not click link icon: {e}")

def get_aio_content(driver):
    scroll_page(driver, scroll_pause=1, scroll_count=5)
    click_show_more(driver)
    click_link_icon(driver)  
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    aio_sections = soup.find_all('div', class_='WaaZC')
    aio_texts = []
    for section in aio_sections:
        text = section.get_text(separator='\n', strip=True)
        if text:
            aio_texts.append(text)
    # Extract only AIO source links with class KEVENd
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

def save_results_csv(results, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['關鍵字', 'AIO內容', '來源連結'])
        for keyword, data in results.items():
            text = data['text'] if data['text'] else ''

            links = '\n'.join([l['href'] for l in data['links']]) if data['links'] else ''
            writer.writerow([keyword, text, links])
    print(f"[INFO] Results saved to {csv_path}")

def save_domain_analysis_csv(results, csv_path):
    domain_counts_per_keyword = defaultdict(Counter)
    for keyword, data in results.items():
        for link in data['links']:
            domain = extract_domain(link['href'])
            domain_counts_per_keyword[keyword][domain] += 1
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['關鍵字', '網域', '次數'])
        for keyword, counter in domain_counts_per_keyword.items():
            for domain, count in counter.most_common():
                writer.writerow([keyword, domain, count])
    print(f"[INFO] Domain analysis saved to {csv_path}")

# --- Word cloud ---
def generate_wordcloud(all_text):
    if not all_text.strip():
        print("[INFO] No AIO text to generate word cloud.")
        return
    font_path = 'NotoSansMonoCJKtc-VF.otf'  # Use downloaded font
    wc = WordCloud(font_path=font_path, width=800, height=400, background_color='white', collocations=False).generate(all_text)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('AIO內容 Word Cloud')
    plt.savefig('aio_wordcloud.png', bbox_inches='tight')
    plt.show()

# --- Domain analysis ---
def extract_domain(url):
    match = re.search(r'https?://([^/]+)/?', url)
    return match.group(1) if match else url

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

# --- Main ---
def main():
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1200, 900)
    results = {}
    for keyword in KEYWORDS:
        print(f"Searching: {keyword}")
        driver.get("https://www.google.com/")
        random_sleep(2, 4)
        try:
            search_box = driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(keyword)
            random_sleep(1, 2)
            search_box.send_keys(Keys.RETURN)
            random_sleep(3, 5)
            # Save the full page HTML for manual inspection
            with open('full_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("[INFO] Saved full page HTML to full_page.html. Please open this file and search for your AIO content.")
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
    driver.quit()
    # Save results to a JSON file for quick review
    with open('aio_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nResults saved to aio_results.json")
    # Save results to CSV
    save_results_csv(results, 'aio_results.csv')
    # Save domain analysis to CSV
    save_domain_analysis_csv(results, 'aio_domain_analysis.csv')
    # Generate word cloud from all AIO texts (excluding NO_AIO_FOUND)
    all_text = '\n'.join([v['text'] for v in results.values() if v['text'] and v['text'] != 'NO_AIO_FOUND'])
    generate_wordcloud(all_text)
    # Domain analysis (print to terminal)
    domain_analysis(results)
    print("\nSummary of results:")
    for k, v in results.items():
        print(f"{k}: {v['text'][:100]}{'...' if v['text'] and len(v['text']) > 100 else ''}")
        if v['links']:
            print("  Links:")
            for link in v['links']:
                print(f"    - {link['text']}: {link['href']}")

if __name__ == "__main__":
    main()
