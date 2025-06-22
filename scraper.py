#!/usr/bin/env python3
"""
Exam Topics Discussion Scraper
Scrapes discussion content from examtopics.com for specified exams
"""

import argparse
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os 

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Scrape exam discussion content from examtopics.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scraper.py --company vmware --exam-id 2v0-11.25
  python scraper.py -c cisco -e 200-301
  python scraper.py --company microsoft --exam-id az-104 --output-dir /custom/path
        """
    )
    
    parser.add_argument(
        "-c", "--company",
        required=True,
        help="Company name (e.g., vmware, cisco, microsoft)"
    )
    
    parser.add_argument(
        "-e", "--exam-id",
        required=True,
        help="Exam ID (e.g., 2v0-11.25, 200-301, az-104)"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        default="./output",
        help="Output directory for scraped content (default: ./output)"
    )
    
    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to scrape (default: 50)"
    )
    
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between requests in seconds (default: 2.0)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    
    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Run browser with GUI (overrides --headless)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()

def setup_driver(headless=True, verbose=False):
    """Setup Chrome WebDriver with appropriate options"""
    options = Options()
    
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    
    # Additional options for better compatibility
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    
    if not verbose:
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=options)
        if verbose:
            print("✅ Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize Chrome WebDriver: {e}")
        print("Make sure ChromeDriver is installed and in your PATH")
        sys.exit(1)

def safe_filename(name):
    """Convert string to safe filename"""
    return re.sub(r"[^\w\-\.]", "_", name)

def extract_full_content(html):
    """Extract content from discussion page HTML"""
    soup = BeautifulSoup(html, "html.parser")
    output = []

    # Question
    question = soup.select_one("div.question-body p.card-text")
    if question:
        output.append("📘 Question:\n" + question.get_text(strip=True))

    # Answer choices
    choices = soup.select("div.question-choices-container li.multi-choice-item")
    if choices:
        output.append("\n📝 Choices:")
        for li in choices:
            output.append(li.get_text(strip=True))

    # Suggested answer
    suggested = soup.select_one("div.question-answer span.correct-answer")
    if suggested:
        output.append("\n✅ Suggested Answer:\n" + suggested.get_text(strip=True))

    # Comments and replies
    comments = soup.select("div.comment-container")
    if comments:
        output.append("\n💬 Comments:")
        for comment in comments:
            user = comment.select_one(".comment-username")
            text = comment.select_one(".comment-content")
            reply_texts = comment.select(".comment-replies .comment-content")
            if user and text:
                output.append(f"\n👤 {user.get_text(strip=True)}: {text.get_text(strip=True)}")
            for reply in reply_texts:
                output.append(f"  ↪️ {reply.get_text(strip=True)}")

    return "\n".join(output) if output else "[No content found]"

def scrape_discussions(company, exam_id, output_dir, max_pages=50, delay=2.0, verbose=False):
    """Main scraping function"""
    
    # Setup
    base_url = f"https://www.examtopics.com/discussions/{company}"
    exam_folder = os.path.join(output_dir, exam_id)
    os.makedirs(exam_folder, exist_ok=True)
    
    if verbose:
        print(f"📁 Created output directory: {exam_folder}")
    
    driver = setup_driver(verbose=verbose)
    
    try:
        page = 1
        total_saved = 0
        
        while page <= max_pages:
            if verbose:
                print(f"\n🔄 Scraping page {page}")
            else:
                print(f"Page {page}...", end=" ", flush=True)
            
            driver.get(f"{base_url}/{page}/")
            time.sleep(delay)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            links = soup.select("a.discussion-link")

            if not links:
                print("\n❌ No more discussion links found.")
                break

            found_on_page = 0
            for link in links:
                title = link.text.strip().lower()
                if exam_id.lower() in title:
                    found_on_page += 1
                    href = link.get("href")
                    full_url = "https://www.examtopics.com" + href

                    # Extract exam and question number
                    match = re.search(rf"({re.escape(exam_id)}).*?(question\s*\d+)", title, re.IGNORECASE)
                    if match:
                        exam = match.group(1).replace(" ", "-")
                        question = match.group(2).replace(" ", "-")
                        filename = f"{exam}-{question}-discussion.txt"
                    else:
                        filename = f"{exam_id}-unknown-discussion-{total_saved + 1}.txt"

                    if verbose:
                        print(f"📄 {title} -> {filename}")
                    
                    driver.get(full_url)
                    time.sleep(delay)

                    html = driver.page_source
                    text = extract_full_content(html)

                    file_path = os.path.join(exam_folder, safe_filename(filename))
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(text)

                    total_saved += 1
                    if verbose:
                        print(f"✅ Saved to {filename}")
                    
                    time.sleep(delay * 0.5)  # Shorter delay between individual discussions

            if found_on_page == 0:
                if verbose:
                    print("✅ No matches found on this page.")
                else:
                    print("no matches", end=" ")
            else:
                if not verbose:
                    print(f"found {found_on_page}", end=" ")

            page += 1

        print(f"\n\n🎉 Scraping completed! Total discussions saved: {total_saved}")
        print(f"📁 Files saved in: {exam_folder}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n\n❌ An error occurred: {e}")
    finally:
        driver.quit()
        if verbose:
            print("🔒 WebDriver closed")

def main():
    """Main entry point"""
    args = parse_arguments()
    
    print("🚀 Exam Topics Discussion Scraper")
    print("=" * 40)
    print(f"Company: {args.company}")
    print(f"Exam ID: {args.exam_id}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Max Pages: {args.max_pages}")
    print(f"Delay: {args.delay}s")
    print(f"Headless Mode: {args.headless}")
    print("=" * 40)
    
    scrape_discussions(
        company=args.company.lower(),
        exam_id=args.exam_id,
        output_dir=args.output_dir,
        max_pages=args.max_pages,
        delay=args.delay,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()