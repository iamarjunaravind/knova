import os
import re

def fix_expo_map():
    path = 'templates/core/expo_map.html'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    static_marker = '<!-- Static featured booths -->'
    dynamic_marker = '<!-- Dynamic booths from DB -->'
    
    if static_marker in text and dynamic_marker in text:
        static_start = text.index(static_marker)
        dynamic_start = text.index(dynamic_marker)
        
        # Remove the static block
        text = text[:static_start] + text[dynamic_start:]
        
        # Add {% empty %} before {% endfor %} if not already present
        if '{% empty %}' not in text:
            endfor_pos = text.find('{% endfor %}')
            empty_block = """        {% empty %}
        <div style="text-align: center; padding: 30px 15px; color: #94a3b8; font-size: 13px;">
          <i class="ti ti-layout-grid" style="font-size: 24px; display: block; margin-bottom: 8px; opacity: 0.6;"></i>
          No floor booths allocated yet.
        </div>
        """
            text = text[:endfor_pos] + empty_block + text[endfor_pos:]
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Fixed expo_map.html")
    else:
        print("expo_map.html static marker not found or already fixed.")

if __name__ == '__main__':
    fix_expo_map()

