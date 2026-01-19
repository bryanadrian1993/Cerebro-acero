import requests
import xml.etree.ElementTree as ET

# Probar un feed RSS
url = 'https://www.bbc.com/news/rss.xml'

response = requests.get(url, timeout=10, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

if response.status_code == 200:
    root = ET.fromstring(response.content)
    items = root.findall('.//item')
    
    print(f"Total items: {len(items)}")
    
    # Examinar primer item en detalle
    if len(items) > 0:
        item = items[0]
        print("\n=== PRIMER ITEM COMPLETO ===")
        print(ET.tostring(item, encoding='unicode'))
        
        print("\n=== ELEMENTOS DEL ITEM ===")
        for child in item:
            print(f"Tag: {child.tag}")
            print(f"Text: {child.text}")
            print(f"Attrib: {child.attrib}")
            print("---")
