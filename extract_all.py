import os
import re

files_to_process = {
    'auth_login': 'app/blueprints/auth/templates/auth/login.html',
    'auth_forgot': 'app/blueprints/auth/templates/auth/forgot_password.html',
    'auth_reset': 'app/blueprints/auth/templates/auth/reset_password.html',
    'auth_verify': 'app/blueprints/auth/templates/auth/verify_otp.html',
    'dashboard': 'app/blueprints/dashboard/templates/dashboard/dashboard.html',
    'employees': 'app/blueprints/employees/templates/employees/index.html',
    'products': 'app/blueprints/products/templates/products/products.html',
    'reports': 'app/blueprints/reports/templates/reports/index.html',
    'users': 'app/blueprints/users/templates/users/index.html',
}

for name, path in files_to_process.items():
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    styles = re.findall(r'<style>(.*?)</style>', html, flags=re.DOTALL)
    scripts = re.findall(r'<script>(.*?)</script>', html, flags=re.DOTALL)
    
    if not styles and not scripts:
        continue
        
    if styles:
        css = '\n'.join(styles).strip()
        css_path = f'app/static/css/{name}.css'
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css)
            
        html = re.sub(r'<style>.*?</style>', '', html, flags=re.DOTALL)
        
        link_tag = f'<link rel="stylesheet" href="{{{{ url_for(\'static\', filename=\'css/{name}.css\') }}}}">'
        
        # If block styles exists
        if '{% block styles %}' in html:
            html = re.sub(r'{% block styles %}(.*?){% endblock %}', 
                          lambda m: '{% block styles %}' + m.group(1).rstrip() + '\n' + link_tag + '\n{% endblock %}', 
                          html, flags=re.DOTALL)
        else:
            # append after extends/title
            html = re.sub(r'({% block title %}.*?{% endblock %})', 
                          r'\1\n\n{% block styles %}\n' + link_tag + '\n{% endblock %}', 
                          html, flags=re.DOTALL)
                          
    if scripts:
        js = '\n'.join(scripts).strip()
        js_path = f'app/static/js/{name}.js'
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js)
            
        html = re.sub(r'<script>.*?</script>', '', html, flags=re.DOTALL)
        
        script_tag = f'<script src="{{{{ url_for(\'static\', filename=\'js/{name}.js\') }}}}"></script>'
        
        if '{% block scripts %}' in html:
            html = re.sub(r'{% block scripts %}(.*?){% endblock %}', 
                          lambda m: '{% block scripts %}' + m.group(1).rstrip() + '\n' + script_tag + '\n{% endblock %}', 
                          html, flags=re.DOTALL)
        else:
            html = html.replace('{% endblock %}\n\n', '') # if there are empty ones? No just substitute
            # Just append at the end
            html += f'\n{{% block scripts %}}\n{script_tag}\n{{% endblock %}}\n'
            
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
        
print("All CSS and JS extracted properly")
