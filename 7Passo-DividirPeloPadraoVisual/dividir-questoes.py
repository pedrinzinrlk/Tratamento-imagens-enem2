from PIL import Image
import os

# ==============================================================================
# CONFIGURAÇÃO DE OURO: DISTÂNCIA DO CORTE ATÉ A LINHA PRETA
# 60 pixels é a folga ideal para jogar o corte acima do título "QUESTÃO 05",
# deixando ele limpo para o início da próxima imagem.
# ==============================================================================
DISTANCIA_CORTE = 60  

def encontrar_linhas_gemeas_2015(imagem):
    """
    Detecta o padrão do ENEM PPL 2015: duas linhas pretas horizontais paralelas
    separadas por um pequeno espaço branco, vindo do lado direito da folha.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    x_inicio = largura - 120
    x_fim = largura - 20
    comprimento_busca = x_fim - x_inicio
    
    y = 10
    while y < altura - 15:
        pixels_pretos_linha1 = 0
        
        for x in range(x_inicio, x_fim):
            r, g, b = pixels[x, y][:3]
            tom_cinza = (r + g + b) // 3
            if tom_cinza < 100: 
                pixels_pretos_linha1 += 1
                
        if pixels_pretos_linha1 > (comprimento_busca * 0.65):
            linha_gemea_encontrada = False
            
            for dy in range(3, 8):
                pixels_pretos_linha2 = 0
                for x in range(x_inicio, x_fim):
                    r_2, g_2, b_2 = pixels[x, y + dy][:3]
                    tom_cinza_2 = (r_2 + g_2 + b_2) // 3
                    if tom_cinza_2 < 100:
                        pixels_pretos_linha2 += 1
                        
                if pixels_pretos_linha2 > (comprimento_busca * 0.65):
                    pixels_claros_meio = 0
                    meio_y = y + (dy // 2)
                    for x in range(x_inicio, x_fim):
                        r_m, g_m, b_m = pixels[x, meio_y][:3]
                        if (r_m + g_m + b_m) // 3 > 180: 
                            pixels_claros_meio += 1
                            
                    if pixels_claros_meio > (comprimento_busca * 0.50):
                        linha_gemea_encontrada = True
                        break
            
            if linha_gemea_encontrada:
                # Determina o ponto de corte perfeito acima da linha preta detectada
                posicao_corte = y - DISTANCIA_CORTE
                if posicao_corte < 0:
                    posicao_corte = 0
                    
                posicoes_corte.append(posicao_corte)
                print(f"Linha divisória achada em y={y}. Cortando no espaço vazio em y={posicao_corte}")
                y += 50  
                continue
                
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Gerencia o fatiamento e a divisão das questões de forma contínua e precisa.
    """
    if not os.path.exists(caminho_imagem):
        print(f"Erro: O arquivo '{caminho_imagem}' não foi encontrado.")
        return
        
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    print(f"Imagem carregada: {largura}x{altura} pixels.")
    print(f"Fatiando a prova com {DISTANCIA_CORTE}px de margem acima das linhas pretas...")
    
    posicoes_corte = encontrar_linhas_gemeas_2015(imagem)
    
    if not posicoes_corte:
        print("\n[AVISO]: O algoritmo não encontrou as linhas pretas paralelas.")
        return
        
    print(f"\nSucesso! Encontradas {len(posicoes_corte)} divisórias de questões.")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta o bloco atual
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{i+1:02d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo}")
        
        # CORREÇÃO CRÍTICA DO BUG: A próxima questão começa EXATAMENTE onde a anterior terminou.
        # Sem contas paralelas que travam o topo do arquivo seguinte!
        posicao_anterior = posicao_corte 

    # Salva a última questão restante no fim da folha
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        nome_arquivo = f"questao_{len(posicoes_corte)+1:02d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo (Parte final): {caminho_completo}")

if __name__ == "__main__":
    arquivo_da_prova = "colunas_concatenadas_verticalmente.png" 
    pasta_destino = "questoes_separadas_2015_CORRIGIDO"
    
    dividir_imagem_por_faixas(arquivo_da_prova, pasta_destino)
    print("\nProcesso finalizado com sucesso!")
