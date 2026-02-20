#!/usr/bin/env python3
import re
import urllib.request
from html import unescape

def extract_table_rows(html_content):
    """Extract table rows from HTML content"""
    rows = []
    tr_pattern = r'<tr>(.*?)</tr>'
    for match in re.finditer(tr_pattern, html_content, re.DOTALL):
        row_html = match.group(1)
        td_pattern = r'<td[^>]*>(.*?)</td>'
        cells = re.findall(td_pattern, row_html, re.DOTALL)
        if cells:
            rows.append(cells)
    return rows

def clean_cell_content(content):
    """Clean up cell content while preserving structure"""
    content = re.sub(r'</br>', '|||BR|||', content)
    content = re.sub(r'<br\s*/>', '|||BR|||', content)
    content = re.sub(r'<br>', '|||BR|||', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'\|\|\|BR\|\|\|', ', ', content)
    content = re.sub(r'\s+', ' ', content)
    content = content.strip()
    return content

def extract_application_links(content):
    """Extract application links from HTML content"""
    if '🔒' in content:
        return '🔒'
    
    links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]*)</a>', content)
    
    if not links:
        img_links = re.findall(r'<a href="([^"]+)"[^>]*><img[^>]*alt="([^"]*)"[^>]*></a>', content)
        if img_links:
            for url, alt in img_links:
                if 'simplify.jobs' in url:
                    return f"[{alt}]({url})"
            if img_links:
                return f"[{img_links[0][1]}]({img_links[0][0]})"
        return ""
    
    if len(links) > 1:
        if 'simplify.jobs' in links[1][0]:
            url, text = links[1]
        else:
            url, text = links[0]
    else:
        url, text = links[0]
    
    return f"[{text}]({url})"

def contains_nyc(cell):
    """Check if a cell contains NYC, NY, or New York"""
    cell_lower = cell.lower()
    return 'nyc' in cell_lower or ' ny' in cell_lower or 'new york' in cell_lower

def row_has_nyc(row):
    """Check if any cell in row contains NYC"""
    return any(contains_nyc(cell) for cell in row)

def row_is_locked(row):
    """Check if row contains locked position indicator"""
    return any('🔒' in cell for cell in row)

def convert_to_markdown_row(row):
    """Convert a row of cells to markdown table format"""
    cells = []
    for i, cell in enumerate(row):
        if i == 3:
            app_link = extract_application_links(cell)
            cells.append(app_link)
        else:
            cell = re.sub(r'<a href="([^"]+)">([^<]+)</a>', r'[\2](\1)', cell)
            cell = clean_cell_content(cell)
            cells.append(cell)
    return '| ' + ' | '.join(cells) + ' |'

def fetch_and_parse(url):
    """Fetch content from URL and parse table rows"""
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
        
        section_match = re.search(r'## 💻 Software Engineering New Grad Roles.*?(?=##|$)', content, re.DOTALL)
        if not section_match:
            return []
        
        section_content = section_match.group(0)
        rows = extract_table_rows(section_content)
        
        filtered_rows = []
        for row in rows:
            if len(row) >= 5 and row_has_nyc(row) and not row_is_locked(row):
                filtered_rows.append(row)
        
        return filtered_rows
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def scrape_simple_format(url, keyword):
    """For repos that use simple markdown tables or lists"""
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
        
        lines = content.split('\n')
        results = []
        
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower() and '🔒' not in line:
                line = line.strip()
                # clean up </br> tags before removing HTML tags
                line = re.sub(r'</br>', ', ', line)
                line = re.sub(r'<br\s*/>', ', ', line)
                line = re.sub(r'<br>', ', ', line)
                # convert HTML links with images to markdown links
                line = re.sub(r'<a href="([^"]+)"><img[^>]*alt="([^"]*)"[^>]*></a>', r'[\2](\1)', line)
                # convert regular HTML links to markdown
                line = re.sub(r'<a href="([^"]+)">([^<]+)</a>', r'[\2](\1)', line)
                # remove other HTML tags
                line = re.sub(r'<[^>]+>', '', line)
                # Clean up extra whitespace
                line = re.sub(r'\s+', ' ', line)
                results.append(line)
        
        return results
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def main():
    pitt_url = "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/refs/heads/dev/README.md"
    vansh_url = "https://raw.githubusercontent.com/vanshb03/New-Grad-2026/refs/heads/dev/README.md"
    speedy_swe_url = "https://raw.githubusercontent.com/speedyapply/2026-SWE-College-Jobs/refs/heads/main/NEW_GRAD_USA.md"
    speedy_ai_url = "https://raw.githubusercontent.com/speedyapply/2026-AI-College-Jobs/refs/heads/main/NEW_GRAD_USA.md"
    
    output = []
    output.append("# Curated list of 2026 New York Tech Opportunities")
    output.append("A fork of [Pitt CSC & Simplify](https://github.com/SimplifyJobs/New-Grad-Positions?tab=readme-ov-file), [cvrve 2026-New-Grad](https://github.com/vanshb03/New-Grad-2026), [speedyapply swe](https://github.com/speedyapply/2026-SWE-College-Jobs) & [speedyapply AI](https://github.com/speedyapply/2026-AI-College-Jobs)")
    output.append("")
    output.append("Use this repository to keep track of software, tech, CS, PM, and quant new grad opportunities for 2026 in New York City.")
    output.append("")
    output.append("## The List 🚴🏔")
    output.append("### Legend")
    output.append(" - 🛂 - Does NOT offer Sponsorship")
    output.append(" - 🇺🇸 - Requires U.S. Citizenship")
    output.append("")
    output.append("| Company | Role | Location | Application/Link | Date Posted |")
    output.append("| ------- | ---- | -------- | ---------------- | ----------- |")
    
    print("Scraping SimplifyJobs...")
    pitt_rows = fetch_and_parse(pitt_url)
    for row in pitt_rows:
        markdown_row = convert_to_markdown_row(row[:5])
        output.append(markdown_row)
    
    print("Scraping vanshb03...")
    vansh_results = scrape_simple_format(vansh_url, "NYC")
    for line in vansh_results:
        if line and not line.startswith('#'):
            output.append(line)
    
    print("Scraping speedyapply SWE...")
    speedy_swe_results = scrape_simple_format(speedy_swe_url, "NYC")
    for line in speedy_swe_results:
        if line and not line.startswith('#'):
            output.append(line)
    
    print("Scraping speedyapply AI...")
    speedy_ai_results = scrape_simple_format(speedy_ai_url, "NYC")
    for line in speedy_ai_results:
        if line and not line.startswith('#'):
            output.append(line)
    
    with open('Readme.md', 'w') as f:
        f.write('\n'.join(output))
    
    print(f"NYC application has been written to Readme.md ({len(output)} lines)")

if __name__ == "__main__":
    main()
