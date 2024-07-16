from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as condicao_esperada
from selenium.common.exceptions import *
import os
from time import sleep
import smtplib
from email.message import EmailMessage
import schedule


def Bot_pegar_tempo():
    def iniciar_driver():
            

            chrome_options = Options()

            arguments = ['--lang=en-US', "--start-minimized"]

            for argument in arguments:
                chrome_options.add_argument(argument)

            chrome_options.add_experimental_option('prefs', {
                'download.prompt_for_download': False,
                'profile.default_content_setting_values.notifications': 2,
                'profile.default_content_setting_values.automatic_downloads': 1

            })

            driver = webdriver.Chrome(service=ChromeService(
                ChromeDriverManager().install()), options=chrome_options)
            
            wait = WebDriverWait(
                driver,
                10,
                poll_frequency=1,
                ignored_exceptions=[
                    NoSuchElementException,
                    ElementNotVisibleException,
                    ElementNotSelectableException,
                ]
            )
            return driver, wait

    def pegar_temperatura():
        driver, wait = iniciar_driver()
        # 1 abrir um navegador e acessar um site de previsão de tempo
        driver.get('https://www.tempo.com/sao-paulo.htm')

        # 2 Coleta de Dados
        #  temperatura atual
        tempo_atual = wait.until(condicao_esperada.element_to_be_clickable((By.XPATH, "//span[@class='dato-temperatura changeUnitT']")))
        # tempo_atual = driver.find_element(By.XPATH, "//span[@class='dato-temperatura changeUnitT']")
        temperatura_atual = tempo_atual.text

        #  condição do tempo atual (ensolarado, nublado, etc)
        condicao_tempo_atual = wait.until(condicao_esperada.element_to_be_clickable((By.XPATH, "//span[@class='descripcion']")))
        # condicao_tempo_atual = driver.find_element(By.XPATH, "//span[@class='descripcion']")
        condicao_tempo = condicao_tempo_atual.text
        with open('tempo.txt', 'w', newline='', encoding='utf-8') as arquivo:
            arquivo.write(f'A temperatura atual é de {temperatura_atual}, hoje o tempo está, {condicao_tempo}'+ os.linesep)
        # #  previsão para os próximos 3 dias (temperatura e condição do tempo)
        dias_semana = driver.find_elements(By.XPATH, "//span[@class='col day_col']")
        condicao_tempo_semana= driver.find_elements(By.XPATH, "//img[@class='simbW']")
        for i in range(3):
            temperatura = dias_semana[i+1].text.split('\n')[-2]
            dia = dias_semana[i+1].text.split('\n')[0]
            condicao_tempo_esperada = condicao_tempo_semana[i].get_attribute('alt')
            with open('tempo.txt', 'a', newline='', encoding='utf-8') as arquivo:
                arquivo.write(f'{dia} a temperatura máxima e minima é de {temperatura} e a condição do tempo será {condicao_tempo_esperada}' + os.linesep)
                
                
            if i == 3:
                break

    def enviar_mensagem():
        EMAIL_ADDRESS = '********************'
        EMAIL_PASSWORD = '********************'
        mail = EmailMessage()
        mail['Subject'] = 'temperatura do tempo'
        mensagem = 'segue o tempo de hoje e dos próximos 3 dias'
        mail['From'] = EMAIL_ADDRESS
        mail['TO'] = '********************'
        mail.add_header('Content-Type', 'text/html')
        mail.set_payload(mensagem.encode('utf-8'))

        #anexo de arquivos
        arquivo = 'tempo.txt'

        with open(arquivo,'rb') as arquivo:
            dados = arquivo.read()
            nome_arquivo = arquivo.name
            mail.add_attachment(dados,maintype='application',subtype='octet-stream', filename=nome_arquivo)

        with smtplib.SMTP_SSL('smtp.gmail.com',465) as email:
            email.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
            email.send_message(mail)
    pegar_temperatura()
    enviar_mensagem()

schedule.every().day.at('06:00').do(Bot_pegar_tempo)

while True:
    schedule.run_pending()
    sleep(1)
