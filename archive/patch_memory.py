import gc
import gc
import gc
import os

def patch_file(path):
    with open(path, 'r') as f:
        content = f.read()
    
    if 'import gc' not in content:
        content = "import gc\n" + content
    
    # Inserisce gc.collect() alla fine del loop principale se trova un time.sleep
    if 'time.sleep' in content and 'gc.collect()' not in content:
        content = content.replace('time.sleep', 'gc.collect()\n            time.sleep')
        
    with open(path, 'w') as f:
        f.write(content)

scripts = [f for f in os.listdir('.') if f.endswith('.py')]
strategies = [os.path.join('strategies', f) for f in os.listdir('strategies') if f.endswith('.py')]

for s in scripts + strategies:
    try:
        patch_file(s)
    except:
        pass
