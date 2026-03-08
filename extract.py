import re

html_file = 'app/blueprints/pos/templates/pos/pos.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 1. Extract CSS
styles = re.findall(r'<style>(.*?)</style>', html_content, flags=re.DOTALL)
css_content = '\n'.join(styles).strip()

# 2. Extract JS
scripts = re.findall(r'<script>(.*?)</script>', html_content, flags=re.DOTALL)
js_content = '\n'.join(scripts).strip()

# Handle Jinja variables in JS
# We need to replace "{{ sys_currency }}" with "window.POS_CONFIG.currency"
js_content = js_content.replace('{{ sys_currency }}', 'window.POS_CONFIG.currency')
js_content = js_content.replace('{{ Setting.get_val(\'vat_rate\', \'15\') }}', 'window.POS_CONFIG.vatRate')
# Also remove quotes around window config variables if they were literal strings
js_content = js_content.replace('const cur = "window.POS_CONFIG.currency";', 'const cur = window.POS_CONFIG.currency;')
js_content = js_content.replace('parseFloat("window.POS_CONFIG.vatRate")', 'parseFloat(window.POS_CONFIG.vatRate)')


# Write CSS
with open('app/static/css/pos.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

# Write JS
with open('app/static/js/pos.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

# 3. Replace in HTML
# Remove all style tags
html_content = re.sub(r'<style>.*?</style>', '', html_content, flags=re.DOTALL)
# Remove all script tags
html_content = re.sub(r'<script>.*?</script>', '', html_content, flags=re.DOTALL)

# Inject proper links
css_link = '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/pos.css\') }}">'
js_link = """<script>
    window.POS_CONFIG = {
        currency: "{{ sys_currency }}",
        vatRate: "{{ Setting.get_val('vat_rate', '15') }}"
    };
</script>
<script src="{{ url_for('static', filename='js/pos.js') }}"></script>"""

# Add CSS to block styles
html_content = html_content.replace('{% block styles %}\n', '{% block styles %}\n' + css_link + '\n')
# Add JS to block scripts (it might not exist, checking...)
if '{% block scripts %}' in html_content:
    html_content = html_content.replace('{% block scripts %}\n', '{% block scripts %}\n' + js_link + '\n')
else:
    # Just append before {% endblock %} at the very end
    html_content = html_content.replace('{% endblock %}\n\n', js_link + '\n{% endblock %}\n\n')

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("POS CSS and JS extracted successfully.")
