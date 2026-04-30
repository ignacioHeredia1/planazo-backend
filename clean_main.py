import re

with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We want to find the first occurrence of the end of the file.
# We can search for the start of `admin_logout` and we know the file structure repeats.
# Let's find how many times `def admin_panel` appears
chunks = content.split('def admin_panel')
print(f"admin_panel appears {len(chunks)-1} times")

if len(chunks) > 2:
    # There are multiple admin_panels. We only want the first one!
    # Wait, the duplication could be huge. Let's just find the last legitimate function.
    # The original file ended with `regenerar_plan`.
    
    # Let's write a regex to capture everything from the start up to the FIRST `def regenerar_plan` and its body.
    match = re.search(r'(.*?def regenerar_plan.*?return JSONResponse[^\n]+\n)', content, re.DOTALL)
    if match:
        clean_content = match.group(1)
        with open('app/main_clean.py', 'w', encoding='utf-8') as f:
            f.write(clean_content)
        print("Cleaned file saved to main_clean.py")
    else:
        print("Could not find regenerar_plan")
