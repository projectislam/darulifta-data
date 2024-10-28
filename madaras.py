from bs4 import BeautifulSoup
import csv

# Define paths for input and output files
input_path = "./madaras/madaras.html"
output_path = "./madaras/madaras.csv"

# Read the HTML file
with open(input_path, "r", encoding="utf-8") as file:
    content = file.read()

# Parse the HTML content
soup = BeautifulSoup(content, "html.parser")

# Find all 'a' tags within the grid container
links = soup.select("div.grid a")

# Prepare data to write to CSV
data = []
for link in links:
    title = link.select_one("div.text-center").get_text(strip=True)
    url = link["href"]
    count_text = link.select_one("span").get_text(strip=True)
    
    # Extract count number from the text before "فتوی"
    count = count_text.split()[0]
    
    data.append([title, url, count])

# Write data to './madaras/madaras.csv'
with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Title", "Link", "Count"])  # Header row
    writer.writerows(data)

print("Data has been written to madaras.csv successfully.")
