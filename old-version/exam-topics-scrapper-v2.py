from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os 

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)  # Add executable_path="..." if needed


company = "amazon" #vmware
exam_id = "associate saa-c03" #2v0-11.25
base_url = f"https://www.examtopics.com/discussions/{company}/"
script_dir = os.path.dirname(os.path.abspath(__file__))
exam_folder = os.path.join(script_dir, exam_id)
os.makedirs(exam_folder, exist_ok=True)

def safe_filename(name):
    return re.sub(r"[^\w\-\.]", "_", name)

def extract_full_content(html):
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

def scrape(exam_id):
    page = 1
    while True:
        print(f"\n🔄 Page {page}")
        driver.get(f"{base_url}/{page}/")
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = soup.select("a.discussion-link")

        if not links:
            print("❌ No more discussion links.")
            break

        found = False
        for link in links:
            title = link.text.strip().lower()
            if exam_id in title:
                found = True
                href = link.get("href")
                full_url = "https://www.examtopics.com" + href

                # Extract exam and question number
                print (title)
                match = re.search(r"(question\s*\d+)", title, re.IGNORECASE)
                if match:
                    question = match.group(1).replace(" ", "-").lower()
                    filename = f"{question}-discussion.txt"
                else:
                    filename = "unknown-discussion.txt"

                print(f"📄 {title} -> {filename}")
                driver.get(full_url)
                time.sleep(2)

                html = driver.page_source
                text = extract_full_content(html)

                file_path = os.path.join(exam_folder, safe_filename(filename))
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)


                print(f"✅ Saved to {filename}")
                time.sleep(1)

        if not found:
            print("✅ No matches on this page.")

        page += 1
        time.sleep(2)

    driver.quit()

scrape(exam_id)
