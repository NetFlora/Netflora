"""

File Name: credentials.py
Origin: Netflora (https://github.com/NetFlora/Netflora)

"""


from ipywidgets import Button, Text, Dropdown, Output, VBox, HTML, Checkbox
from IPython.display import display, clear_output
import requests
import re
from google.colab import drive

def format_cep(cep):
    if len(cep) == 8 and "-" not in cep:
        return f"{cep[:5]}-{cep[5:]}"
    return cep

def fetch_cep_data(cep):
    cep = cep.replace("-", "")
    if len(cep) == 8:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            cep_data = response.json()
            if "erro" not in cep_data:
                logradouro = cep_data.get('logradouro', '')
                bairro = cep_data.get('bairro', '')
                cidade = cep_data.get('localidade', '')
                estado = cep_data.get('uf', '')
                pais = 'Brasil'
                return True, logradouro, bairro, cidade, estado, pais
    return False, "", "", "", "", ""

def validar_email(email):
    pattern = r"^\w+([\.-]?\w+)@\w+([\.-]?\w+)(\.\w{2,3})+$"
    return re.match(pattern, email) is not None

def credentials():
    email_input = Text(placeholder='Informe seu e-mail', description='E-mail:')
    name_input = Text(placeholder='Informe seu nome', description='Nome:')
    cep_input = Text(placeholder='Informe seu CEP', description='CEP:')
    area_input = Text(placeholder='Informe a área mapeada em hectares', description='Área (ha):', tooltip='Informe o tamanho da área mapeada em hectares.')
    non_brazil_checkbox = Checkbox(value=False, description="Não resido no Brasil")
    country_input = Text(placeholder='Informe seu país', description='País:', disabled=True)
    translate_dropdown = Dropdown(options=[('Português', 'pt'), ('English', 'en'), ('Español', 'es')], value='pt', description='Translate:')
    confirm_button = Button(description='Aceitar e enviar', button_style='success', tooltip='Enviar dados')
    form_output = Output()
    terms_checkbox = Checkbox(value=False, description='Eu li e aceito o termo de uso')
    terms_text = HTML()

    def toggle_country_input(*args):
        country_input.disabled = not non_brazil_checkbox.value

    non_brazil_checkbox.observe(toggle_country_input, 'value')

    messages = {
        'pt': {
            'accept_terms': 'Por favor, aceite os termos de uso para continuar.',
            'valid_email': 'Por favor, forneça um email válido.',
            'enter_name': 'Por favor, informe seu nome.',
            'enter_area': 'Por favor, informe a área em hectares.',
            'enter_country': 'Por favor, informe o país em que reside.',
            'cep_not_found': 'CEP não encontrado.',
            'mounting_drive': 'Montando Google Drive, por favor aguarde...',
            'data_submitted': 'Dados enviados. Drive montado com sucesso.'
        },
        'en': {
            'accept_terms': 'Please accept the terms of use to continue.',
            'valid_email': 'Please provide a valid email.',
            'enter_name': 'Please enter your name.',
            'enter_area': 'Please enter the mapped area in hectares.',
            'enter_country': 'Please enter the country you reside in.',
            'cep_not_found': 'ZIP not found.',
            'mounting_drive': 'Mounting Google Drive, please wait...',
            'data_submitted': 'Data submitted. Drive mounted successfully.'
        },
        'es': {
            'accept_terms': 'Por favor, acepte los términos de uso para continuar.',
            'valid_email': 'Por favor, proporcione un correo electrónico válido.',
            'enter_name': 'Por favor, ingrese su nombre.',
            'enter_area': 'Por favor, ingrese el área mapeada en hectáreas.',
            'enter_country': 'Por favor, indique el país en que reside.',
            'cep_not_found': 'Código postal no encontrado.',
            'mounting_drive': 'Montando Google Drive, por favor espere...',
            'data_submitted': 'Datos enviados. Drive montado con éxito.'
        }
    }

    def update_translate(*args):
        lang = translate_dropdown.value
        if lang == 'en':
            email_input.placeholder = 'Enter your email'
            name_input.placeholder = 'Enter your name'
            cep_input.placeholder = 'Enter your ZIP code'
            area_input.placeholder = 'Enter mapped area in hectares'
            country_input.placeholder = 'Enter your country'
            confirm_button.description = 'Accept and Send'
            non_brazil_checkbox.description = "I do not reside in Brazil"
            terms_checkbox.description = 'I agree to the term of use'
        elif lang == 'es':
            email_input.placeholder = 'Ingrese su correo electrónico'
            name_input.placeholder = 'Ingrese su nombre'
            cep_input.placeholder = 'Ingrese su código postal'
            area_input.placeholder = 'Ingrese el área mapeada en hectáreas'
            country_input.placeholder = 'Ingrese su país'
            confirm_button.description = 'Aceptar y enviar'
            non_brazil_checkbox.description = "No resido en Brasil"
            terms_checkbox.description = 'He leído y acepto los términos de uso'
        else:  # Default to Portuguese
            email_input.placeholder = 'Informe seu e-mail'
            name_input.placeholder = 'Informe seu nome'
            cep_input.placeholder = 'Informe seu CEP'
            area_input.placeholder = 'Informe a área em hectares'
            country_input.placeholder = 'Informe seu país'
            confirm_button.description = 'Aceitar e enviar'
            non_brazil_checkbox.description = "Não resido no Brasil"
            terms_checkbox.description = 'Eu li e aceito o termo de uso'

        update_terms_text(lang)

    def update_terms_text(lang):
        if lang == 'en':
            terms_text.value = '<p>Please read the <a href="https://www.embrapa.br/web/portal/acre/netflora/perguntas-e-respostas/termo-de-uso/" target="_blank">term of use</a> carefully before submitting your data. By checking the box below, you agree to the terms of use.</p>'
        elif lang == 'es':
            terms_text.value = '<p>Por favor, lea cuidadosamente el <a href="https://www.embrapa.br/web/portal/acre/netflora/perguntas-e-respostas/termo-de-uso/" target="_blank">término de uso</a> antes de enviar sus datos. Al marcar la casilla a continuación, usted acepta el término de uso.</p>'
        else:  # Default to Portuguese
            terms_text.value = '<p>Por favor, leia cuidadosamente o <a href="https://www.embrapa.br/web/portal/acre/netflora/perguntas-e-respostas/termo-de-uso/" target="_blank">termo de uso</a> antes de enviar seus dados. Ao marcar a caixa abaixo, você concorda com o termo de uso.</p>'

    translate_dropdown.observe(update_translate, names='value')
    update_translate()  


    def confirm_send(b):
        lang = translate_dropdown.value
        msg = messages[lang]
        with form_output:
            clear_output()

            if not validar_email(email_input.value):
                display(HTML(f'<span style="color: red;">{msg["valid_email"]}</span>'))
                return

            if not name_input.value.strip():
                display(HTML(f'<span style="color: red;">{msg["enter_name"]}</span>'))
                return

            cidade = ""
            estado = ""
            cep_valid = True
            if not non_brazil_checkbox.value:
                formatted_cep = format_cep(cep_input.value)
                cep_valid, logradouro, bairro, cidade, estado, pais = fetch_cep_data(formatted_cep)
                if not cep_valid:
                    display(HTML(f'<span style="color: red;">{msg["cep_not_found"]}</span>'))
                    return

            if not area_input.value.strip():
                display(HTML(f'<span style="color: red;">{msg["enter_area"]}</span>'))
                return

            if non_brazil_checkbox.value and not country_input.value:
                display(HTML(f'<span style="color: red;">{msg["enter_country"]}</span>'))
                return

            if not terms_checkbox.value:
                display(HTML(f'<span style="color: red;">{msg["accept_terms"]}</span>'))
                return

            display(HTML(f'<span style="color: blue;">{msg["mounting_drive"]}</span>'))
            drive.mount('/content/drive')
            display(HTML(f'<span style="color: green;">{msg["data_submitted"]}</span>'))

            country = country_input.value if country_input.value else 'Brasil'

            form_data = {
                'entry.79837568': name_input.value,
                'entry.31901897': email_input.value,
                'entry.1472348248': cep_input.value if cep_valid else "",
                'entry.276405757': cidade if cep_valid else "",
                'entry.839721720': estado if cep_valid else "",
                'entry.807575090': country,
                'entry.1662418940': area_input.value,
            }
            url = 'https://docs.google.com/forms/u/0/d/e/1FAIpQLSeiyE0r9ddUEMWVSbaRNGzoHhjRIp4DQH5branuxqO1eHg2Ag/formResponse'
            response = requests.post(url, data=form_data)
            if response.status_code != 200:
                display(HTML('<span style="color: red;">Falha ao enviar o formulário. Status Code: ' + str(response.status_code) + '</span>'))

    confirm_button.on_click(confirm_send)
    display(VBox([translate_dropdown, email_input, name_input, cep_input, area_input, non_brazil_checkbox, country_input, terms_text, terms_checkbox, confirm_button, form_output]))

if __name__ == "__main__":
    credentials()
