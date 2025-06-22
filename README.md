# Exam Topics Discussion Scraper

A containerized Python scraper for extracting discussion content from examtopics.com. This tool allows you to scrape exam discussions for any company and exam ID with configurable options.

## Features

- 🎯 **Dynamic Parameters**: Specify company and exam ID via command line arguments
- 🐳 **Containerized**: Runs in Docker for easy deployment and consistency
- 📁 **Organized Output**: Saves discussions in structured folders
- ⚙️ **Configurable**: Multiple options for customization (delays, max pages, output directory)
- 🤖 **Headless Operation**: Runs without GUI by default (perfect for servers)
- 📊 **Progress Tracking**: Shows scraping progress and statistics

## Quick Start

### Using Docker (Recommended)

1. **Clone/Download the files:**
   ```bash
   # Create project directory
   mkdir web-scrapper && cd web-scrapper
   
   # Download the files (scraper.py, Dockerfile, requirements.txt, docker-compose.yml)
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t web-scrapper .
   ```

3. **Run the scraper:**
   ```bash
   # Basic usage
   docker run --rm -v $(pwd)/output:/app/output web-scrapper \
     --company vmware --exam-id 2v0-11.25
   
   # With additional options
   docker run --rm -v $(pwd)/output:/app/output web-scrapper \
     --company cisco --exam-id 200-301 --max-pages 5 --verbose
   ```

### Using Docker Compose

1. **Edit docker-compose.yml** to set your desired parameters:
   ```yaml
   command: ["--company", "vmware", "--exam-id", "2v0-11.25", "--verbose"]
   ```

2. **Run with docker-compose:**
   ```bash
   docker-compose up --build
   ```

### Local Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Chrome and ChromeDriver:**
   - Install Google Chrome browser
   - Download ChromeDriver and add to PATH

3. **Run the scraper:**
   ```bash
   python scraper.py --company vmware --exam-id 2v0-11.25
   ```

## Command Line Options

```
usage: scraper.py [-h] -c COMPANY -e EXAM_ID [-o OUTPUT_DIR] [--max-pages MAX_PAGES] 
                  [--delay DELAY] [--headless] [--no-headless] [-v]

required arguments:
  -c, --company         Company name (e.g., vmware, cisco, microsoft)
  -e, --exam-id         Exam ID (e.g., 2v0-11.25, 200-301, az-104)

optional arguments:
  -h, --help            Show help message
  -o, --output-dir      Output directory (default: ./output)
  --max-pages          Maximum pages to scrape (default: 50)
  --delay              Delay between requests in seconds (default: 2.0)
  --headless           Run browser in headless mode (default: True)
  --no-headless        Run browser with GUI
  -v, --verbose        Enable verbose output
```

## Examples

### Docker Examples

```bash
# VMware certification
docker run --rm -v $(pwd)/output:/app/output web-scrapper \
  --company vmware --exam-id 2v0-11.25

# Cisco certification with custom settings
docker run --rm -v $(pwd)/output:/app/output web-scrapper \
  --company cisco --exam-id 200-301 --max-pages 10 --delay 1.5

# Microsoft certification with verbose output
docker run --rm -v $(pwd)/output:/app/output web-scrapper \
  --company microsoft --exam-id az-104 --verbose

# Custom output directory
docker run --rm -v /path/to/custom/output:/app/output web-scrapper \
  --company comptia --exam-id sy0-601
```

### Local Examples

```bash
# Basic usage
python scraper.py --company vmware --exam-id 2v0-11.25

# With custom output directory
python scraper.py --company cisco --exam-id 200-301 --output-dir /custom/path

# Fast scraping (shorter delays, fewer pages)
python scraper.py --company microsoft --exam-id az-104 --max-pages 5 --delay 1.0

# Non-headless mode (show browser)
python scraper.py --company comptia --exam-id sy0-601 --no-headless --verbose
```

## Output Structure

The scraper creates the following directory structure:

```
output/
└── [exam-id]/
    ├── 2v0-11.25-question-1-discussion.txt
    ├── 2v0-11.25-question-2-discussion.txt
    └── ...
```

Each discussion file contains:
- 📘 Question text
- 📝 Answer choices
- ✅ Suggested answer
- 💬 Comments and replies

## Supported Companies

The scraper works with any company available on examtopics.com, including:
- vmware
- cisco
- microsoft
- comptia
- amazon
- google
- oracle
- and many more...

## Configuration Tips

### Performance Tuning
- **Faster scraping**: Reduce `--delay` (minimum 1.0 recommended)
- **Respectful scraping**: Increase `--delay` to 3-5 seconds
- **Limited scraping**: Use `--max-pages` to limit scope

### Docker Volume Mounting
- **Windows**: `docker run --rm -v %cd%/output:/app/output ...`
- **Linux/Mac**: `docker run --rm -v $(pwd)/output:/app/output ...`
- **Absolute path**: `docker run --rm -v /full/path/to/output:/app/output ...`

## Troubleshooting

### Docker Issues
```bash
# Check if container is running
docker ps -a

# View container logs
docker logs web-scrapper

# Remove old containers
docker container prune
```

### Chrome/ChromeDriver Issues
- Make sure you have the latest Chrome browser
- ChromeDriver version should match Chrome version
- On Docker, this is handled automatically

### Permission Issues
```bash
# Fix output directory permissions
sudo chown -R $USER:$USER ./output
```

## Legal Notice

This tool is for educational purposes only. Please respect the website's terms of service and robots.txt file. Use appropriate delays between requests to avoid overloading the server.

## License

This project is open source. Use responsibly and at your own risk.