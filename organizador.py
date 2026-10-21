import os
import shutil
import hashlib
from datetime import datetime
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox

def calcular_hash_arquivo(caminho_arquivo, tamanho_bloco=65536):
    """Calcula o MD5 do ficheiro para identificar cópias exatas."""
    hasher = hashlib.md5()
    try:
        with open(caminho_arquivo, 'rb') as f:
            buf = f.read(tamanho_bloco)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(tamanho_bloco)
        return hasher.hexdigest()
    except Exception:
        return None

def obter_ano_e_mes_midia(caminho_arquivo):
    """Obtém o ano e o mês da foto/vídeo via EXIF (se foto) ou pela data de modificação."""
    ano = None
    mes = None
    extensoes_foto = ('.jpg', '.jpeg', '.png', '.heic', '.webp')
    
    if caminho_arquivo.lower().endswith(extensoes_foto):
        try:
            imagem = Image.open(caminho_arquivo)
            exif_data = imagem._getexif()
            if exif_data and 36867 in exif_data:
                data_str = exif_data[36867] 
                partes = data_str.split(' ')[0].split(':')
                if len(partes) >= 2:
                    ano = partes[0].strip()
                    mes = partes[1].strip()
        except Exception:
            pass

    if not ano or not ano.isdigit() or not mes or not mes.isdigit():
        timestamp = os.path.getmtime(caminho_arquivo)
        dt = datetime.fromtimestamp(timestamp)
        ano = str(dt.year)
        mes = f"{dt.month:02d}"

    meses_nomes = {
        '01': '01_Janeiro', '02': '02_Fevereiro', '03': '03_Marco',
        '04': '04_Abril', '05': '05_Maio', '06': '06_Junho',
        '07': '07_Julho', '08': '08_Agosto', '09': '09_Setembro',
        '10': '10_Outubro', '11': '11_Novembro', '12': '12_Dezembro'
    }
    
    nome_mes = meses_nomes.get(mes, f"{mes}_Mes")
    return ano, nome_mes

def organizar_e_separar_copias(pasta_origem):
    extensoes_validas = (
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.webp',
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.3gp', '.m4v'
    )
    
    pasta_copias_raiz = os.path.join(pasta_origem, "Cópias")
    pasta_outros = os.path.join(pasta_origem, "Outros")
    
    hashes_conhecidos = set()
    arquivos_para_processar = []

    for raiz, _, arquivos in os.walk(pasta_origem):
        partes_caminho = raiz.split(os.sep)
        if "Cópias" in partes_caminho or "Outros" in partes_caminho:
            continue
        for arquivo in arquivos:
            arquivos_para_processar.append(os.path.join(raiz, arquivo))

    copias_encontradas = 0
    midias_organizadas = 0
    arquivos_outros = 0

    for caminho_atual in arquivos_para_processar:
        nome_arquivo = os.path.basename(caminho_atual)
        
        if not nome_arquivo.lower().endswith(extensoes_validas):
            if not os.path.exists(pasta_outros):
                os.makedirs(pasta_outros)
            
            destino_outro = os.path.join(pasta_outros, nome_arquivo)
            contador = 1
            nome_base, ext = os.path.splitext(nome_arquivo)
            while os.path.exists(destino_outro):
                destino_outro = os.path.join(pasta_outros, f"{nome_base}_{contador}{ext}")
                contador += 1
                
            shutil.move(caminho_atual, destino_outro)
            arquivos_outros += 1
            continue

        hash_midia = calcular_hash_arquivo(caminho_atual)
        if not hash_midia:
            continue

        ano, nome_mes = obter_ano_e_mes_midia(caminho_atual)

        if hash_midia in hashes_conhecidos:
            pasta_copias_destino = os.path.join(pasta_copias_raiz, ano, nome_mes)
            if not os.path.exists(pasta_copias_destino):
                os.makedirs(pasta_copias_destino)

            destino_copia = os.path.join(pasta_copias_destino, nome_arquivo)
            contador = 1
            nome_base, ext = os.path.splitext(nome_arquivo)
            while os.path.exists(destino_copia):
                destino_copia = os.path.join(pasta_copias_destino, f"{nome_base}_copia{contador}{ext}")
                contador += 1
                
            shutil.move(caminho_atual, destino_copia)
            copias_encontradas += 1

        else:
            hashes_conhecidos.add(hash_midia)
            pasta_destino = os.path.join(pasta_origem, ano, nome_mes)
            
            if not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino)

            destino_final = os.path.join(pasta_destino, nome_arquivo)

            if os.path.abspath(caminho_atual) != os.path.abspath(destino_final):
                contador = 1
                nome_base, ext = os.path.splitext(nome_arquivo)
                while os.path.exists(destino_final):
                    destino_final = os.path.join(pasta_destino, f"{nome_base}_{contador}{ext}")
                    contador += 1

                shutil.move(caminho_atual, destino_final)
                midias_organizadas += 1

    return midias_organizadas, copias_encontradas, arquivos_outros

def selecionar_pasta():
    pasta_selecionada = filedialog.askdirectory(title="Selecione a pasta com as fotos e vídeos")
    if pasta_selecionada:
        lbl_status.config(text="A processar ficheiros... Aguarde.", fg="blue")
        root.update()
        
        organizadas, copias, outros = organizar_e_separar_copias(pasta_selecionada)
        
        lbl_status.config(text="Concluído com sucesso!", fg="green")
        messagebox.showinfo(
            "Sucesso", 
            f"Processo finalizado!\n\n"
            f"• Ficheiros organizados por ano/mês: {organizadas}\n"
            f"• Cópias movidas para 'Cópias': {copias}\n"
            f"• Outros ficheiros movidos para 'Outros': {outros}"
        )

root = tk.Tk()
root.title("Organizador de Fotos e Vídeos")
root.geometry("420x220")

lbl_instrucao = tk.Label(root, text="Organizador de Fotos e Vídeos", font=("Arial", 14, "bold"))
lbl_instrucao.pack(pady=15)

btn_selecionar = tk.Button(root, text="Selecionar Pasta", command=selecionar_pasta, font=("Arial", 11), bg="#4CAF50", fg="white", padx=10, pady=5)
btn_selecionar.pack(pady=10)

lbl_status = tk.Label(root, text="Nenhuma pasta selecionada.", font=("Arial", 10))
lbl_status.pack(pady=10)

root.mainloop()