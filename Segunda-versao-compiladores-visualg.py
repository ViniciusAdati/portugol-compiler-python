import tkinter as tk
from tkinter import simpledialog, scrolledtext
import re

def criar_interface():
    janela = tk.Tk()
    janela.title("Analisador Léxico - Visualg")
    janela.geometry("600x400")

    rotulo = tk.Label(janela, text="Digite o código Visualg abaixo:", font=("Arial", 14))
    rotulo.pack(pady=10)

    codigo_inicial = '''algoritmo "semnome"
// Função :
// Autor :
// Data :
// Seção de Declarações

inicio

fimalgoritmo'''

    area_codigo = scrolledtext.ScrolledText(janela, width=70, height=15, wrap=tk.WORD, font=("Arial", 12))
    area_codigo.pack(padx=10, pady=10)
    area_codigo.insert(tk.END, codigo_inicial)

#FUNCAO
    def analisar_FUNCAO():
        codigo = area_codigo.get("1.0", tk.END).strip()
        linhas = codigo.splitlines()

        try:
            inicio_idx = linhas.index("inicio")
            fim_idx = linhas.index("fimalgoritmo")
        except ValueError:
            resultado_label.config(text="Erro: Bloco 'inicio' ou 'fimalgoritmo' não encontrado.")
            return

        variaveis = {}
        funcoes = {}
        for idx, linha in enumerate(linhas):
            linha = linha.strip().lower()
            if linha.startswith("funcao "):
                match = re.match(r"funcao (\w+)\((.*?)\): (\w+)", linha)
                if match:
                    nome_funcao, parametros, tipo_retorno = match.groups()
                    parametros = [param.strip().split(":") for param in parametros.split(",")]
                    parametros = {param[0]: param[1] for param in parametros}
                    funcoes[nome_funcao] = {
                        "parametros": parametros,
                        "tipo_retorno": tipo_retorno,
                        "inicio": idx + 1,
                        "linhas": []
                    }
            elif linha.startswith("fimfuncao"):
                for funcao in funcoes.values():
                    if not funcao["linhas"]:
                        funcao["linhas"] = linhas[funcao["inicio"]:idx]
                        break

        # Função para executar uma função definida
        def executar_funcao(nome_funcao, args):
            if nome_funcao not in funcoes:
                raise Exception(f"Função '{nome_funcao}' não encontrada.")

            funcao = funcoes[nome_funcao]
            contexto_local = {param: args[idx] for idx, param in enumerate(funcao["parametros"])}
            for linha in funcao["linhas"]:
                linha = linha.strip()
                if linha.startswith("retorno"):
                    retorno = eval(linha.split("retorno")[1].strip(), {}, contexto_local)
                    return retorno

        # Processa os comandos do algoritmo principal
        for linha in linhas[inicio_idx + 1:fim_idx]:
            linha = linha.strip()
            if "=" in linha and not linha.startswith("escreva"):
                var, expr = map(str.strip, linha.split("="))
                if "(" in expr and ")" in expr:  # Verifica se é uma chamada de função
                    nome_funcao, parametros = re.match(r"(\w+)\((.*?)\)", expr).groups()
                    parametros = [int(param.strip()) for param in parametros.split(",")]
                    variaveis[var] = executar_funcao(nome_funcao, parametros)
                else:
                  variaveis[var] = eval(expr)
            elif linha.startswith("escreva"):
                conteudo = linha[7:].strip().strip("()")
                partes = re.split(r',\s*', conteudo)
                saida = ""
                for parte in partes:
                    if parte.startswith('"') and parte.endswith('"'):  # É uma string literal
                        saida += parte.strip('"')
                    elif parte in variaveis:  # É uma variável
                        saida += str(variaveis[parte])
                    else:
                        saida += parte  # Caso não seja reconhecido, mantém como está
                print(saida)
#FINAL FUNCAO
#Declaração de variaveis
    def analisar_codigo():
        codigo = area_codigo.get("1.0", tk.END).strip()
        linhas = codigo.splitlines()

        try:
            inicio_idx = linhas.index("inicio")
            fim_idx = linhas.index("fimalgoritmo")
        except ValueError:
            resultado_label.config(text="Erro: Bloco 'inicio' ou 'fimalgoritmo' não encontrado.")
            return

        variaveis = {}
        funcoes = {}

        for idx, linha in enumerate(linhas):
            linha = linha.strip().lower()
            if linha.startswith("funcao "):
                match = re.match(r"funcao (\w+)\((.*?)\): (\w+)", linha)
                if match:
                    nome_funcao, parametros, tipo_retorno = match.groups()
                    parametros = [param.strip().split(":") for param in parametros.split(",")]
                    parametros = {param[0]: param[1] for param in parametros}
                    funcoes[nome_funcao] = {
                        "parametros": parametros,
                        "tipo_retorno": tipo_retorno,
                        "inicio": idx + 1,
                        "linhas": []
                    }
            elif linha.startswith("fimfuncao"):
                for funcao in funcoes.values():
                    if not funcao["linhas"]:
                        funcao["linhas"] = linhas[funcao["inicio"]:idx]
                        break
                    
        for linha in linhas[:inicio_idx]:
            linha = linha.strip().lower()
            if linha.startswith(("inteiro", "real", "caractere", "logico")):
                tipo, *nomes = re.split(r"[, ]+", linha)
                for nome in nomes:
                    if nome:
                        variaveis[nome] = {
                            "tipo": tipo,
                            "valor": 0 if tipo == "inteiro" else \
                                     0.0 if tipo == "real" else \
                                     "" if tipo == "caractere" else \
                                     False
                        }                    
        # Processa comandos dentro do bloco principal
        i = inicio_idx + 1
        while i < fim_idx:
            linha = linhas[i].strip()
            if not linha or linha.startswith("//"):
                i += 1
                continue
            
            else:
                processar_comando(linha, variaveis)
            i += 1

        resultado = "\nResultados das variáveis:\n"
        for var, props in variaveis.items():
            resultado += f"{var} = {props['valor']} ({props['tipo']})\n"
        resultado_label.config(text=resultado)

    def processar_comando(linha, variaveis):
        linha = linha.strip()
        if linha.count('=') == 1 and not linha.startswith("escreva"):
            esquerda, direita = linha.split("=")
            esquerda = esquerda.strip()
            direita = direita.strip().lower()

            if esquerda in variaveis:
                tipo = variaveis[esquerda]["tipo"]
                try:
                    direita = (direita.replace("^", "**")
                                       .replace("%", "%")
                                       .replace("==", "==")
                                       .replace("<>", "!=")
                                       .replace(" e ", " and ")
                                       .replace(" ou ", " or ")
                                       .replace(" nao ", " not ")
                                       .replace(" xou ", " != "))

                    for var in variaveis:
                        direita = re.sub(rf'\b{var}\b', str(variaveis[var]["valor"]), direita)

                    if tipo == "logico" and direita in ("verdadeiro", "falso"):
                        resultado = direita == "verdadeiro"
                    else:
                        resultado = eval(direita)

                    if tipo == "inteiro":
                        variaveis[esquerda]["valor"] = int(resultado)
                    elif tipo == "real":
                        variaveis[esquerda]["valor"] = float(resultado)
                    elif tipo == "logico":
                        variaveis[esquerda]["valor"] = bool(resultado)
                    elif tipo == "caractere":
                        variaveis[esquerda]["valor"] = str(resultado).strip('"')
                except Exception as e:
                    print(f"Erro ao processar '{linha}': {e}")

        elif linha.lower().startswith("escreva"):
            conteudo = linha[7:].strip().strip('()')
            partes = [parte.strip().strip('"') for parte in conteudo.split(',')]
            saida = "".join(str(variaveis.get(parte, {"valor": parte})["valor"]) for parte in partes)
            print(saida)

        elif linha.lower().startswith("leia"):
            nome_var = linha[5:].strip().strip('()')
            if nome_var in variaveis:
                tipo = variaveis[nome_var]["tipo"]
                valor = simpledialog.askstring("Entrada", f"Digite o valor para {nome_var} ({tipo}):")
                try:
                    if tipo == "inteiro":
                        variaveis[nome_var]["valor"] = int(valor)
                    elif tipo == "real":
                        variaveis[nome_var]["valor"] = float(valor)
                    elif tipo == "logico":
                        variaveis[nome_var]["valor"] = valor.lower() == "verdadeiro"
                    elif tipo == "caractere":
                        variaveis[nome_var]["valor"] = valor
                except ValueError:
                    print(f"Erro: Tipo de entrada inválido para {nome_var} ({tipo}).")
#FINAL DA DECLARAÇÃO DE VARIAVEIS
# COMEÇO DO SE SENAO
    def analisar_se_senao():
        codigo = area_codigo.get("1.0", tk.END).strip()
        linhas = codigo.splitlines()

        try:
            inicio_idx = linhas.index("inicio")
            fim_idx = linhas.index("fimalgoritmo")
        except ValueError:
            resultado_label.config(text="Erro: Bloco 'inicio' ou 'fimalgoritmo' não encontrado.")
            return

        variaveis = {}

        # Processa as declarações de variáveis
        for linha in linhas[:inicio_idx]:
            linha = linha.strip().lower()
            if linha.startswith(("inteiro", "real", "caractere", "logico")):
                tipo, *nomes = re.split(r"[, ]+", linha)
                for nome in nomes:
                    if nome:
                        variaveis[nome] = {
                            "tipo": tipo,
                            "valor": 0 if tipo == "inteiro" else \
                                     0.0 if tipo == "real" else \
                                     "" if tipo == "caractere" else \
                                     False
                        }

        def processar_comando(linha, variaveis):
            linha = linha.strip()
            if linha.count('=') == 1 and not linha.startswith("escreva"):
                esquerda, direita = linha.split("=")
                esquerda = esquerda.strip()
                direita = direita.strip()

                if esquerda in variaveis:
                    tipo = variaveis[esquerda]["tipo"]
                    try:
                        direita = (direita.replace("^", "**")
                                           .replace("<>", "!=")
                                           .replace(" e ", " and ")
                                           .replace(" ou ", " or ")
                                           .replace(" nao ", " not "))

                        for var in variaveis:
                            direita = re.sub(rf'\b{var}\b', str(variaveis[var]["valor"]), direita)

                        resultado = eval(direita)
                        if tipo == "inteiro":
                            variaveis[esquerda]["valor"] = int(resultado)
                        elif tipo == "real":
                            variaveis[esquerda]["valor"] = float(resultado)
                        elif tipo == "logico":
                            variaveis[esquerda]["valor"] = bool(resultado)
                        elif tipo == "caractere":
                            variaveis[esquerda]["valor"] = str(resultado).strip('"')
                    except Exception as e:
                        print(f"Erro ao processar '{linha}': {e}")

            elif linha.lower().startswith("escreva"):
                conteudo = linha[7:].strip().strip('()')
                partes = [parte.strip().strip('"') for parte in conteudo.split(',')]

                saida = ""
                for parte in partes:
                    saida += str(variaveis.get(parte, {"valor": parte})["valor"])
                print(saida)

            elif linha.lower().startswith("leia"):
                nome_var = linha[5:].strip().strip('()')
                if nome_var in variaveis:
                    tipo = variaveis[nome_var]["tipo"]
                    valor = simpledialog.askstring("Entrada", f"Digite o valor para {nome_var} ({tipo}):")
                    try:
                        if tipo == "inteiro":
                            variaveis[nome_var]["valor"] = int(valor)
                        elif tipo == "real":
                            variaveis[nome_var]["valor"] = float(valor)
                        elif tipo == "logico":
                            variaveis[nome_var]["valor"] = bool(valor)
                        elif tipo == "caractere":
                            variaveis[nome_var]["valor"] = valor
                    except ValueError:
                        print(f"Erro: Tipo de entrada inválido para {nome_var} ({tipo}).")

        def processar_condicional(linhas, i, variaveis):
            condicao = linhas[i][3:].strip("entao").strip()
            condicao = (condicao.replace("<>", "!=")
                                  .replace(" e ", " and ")
                                  .replace(" ou ", " or "))

            for var in variaveis:
                condicao = re.sub(rf'\b{var}\b', str(variaveis[var]["valor"]), condicao)

            try:
                if eval(condicao):
                    i += 1
                    while not linhas[i].strip().lower().startswith("senão") and not linhas[i].strip().lower().startswith("fimse"):
                        processar_comando(linhas[i], variaveis)
                        i += 1
                    while i < len(linhas) and not linhas[i].strip().lower().startswith("fimse"):
                        i += 1
                else:
                    while not linhas[i].strip().lower().startswith("senão"):
                        i += 1
                    i += 1
                    while not linhas[i].strip().lower().startswith("fimse"):
                        processar_comando(linhas[i], variaveis)
                        i += 1
            except Exception as e:
                print(f"Erro ao avaliar condicional: {e}")
            return i

        # Processa comandos dentro do bloco principal
        i = inicio_idx + 1
        while i < fim_idx:
            linha = linhas[i].strip()
            if not linha or linha.startswith("//"):
                i += 1
                continue

            if linha.lower().startswith("se"):
                i = processar_condicional(linhas, i, variaveis)
            else:
                processar_comando(linha, variaveis)
            i += 1

        resultado = "\nResultados das variáveis:\n"
        for var, props in variaveis.items():
            resultado += f"{var} = {props['valor']} ({props['tipo']})\n"
        resultado_label.config(text=resultado)
# #FINAL DO SE senão

# #CASO DE
    def funcao_sem_nome():
        texto_codigo = area_codigo.get("1.0", tk.END).strip()
        linhas_codigo = texto_codigo.splitlines()

        try:
            bloco_inicio = linhas_codigo.index("inicio")
            bloco_fim = linhas_codigo.index("fimalgoritmo")
        except ValueError:
              resultado_label.config(text="Erro: Bloco 'inicio' ou 'fimalgoritmo' não encontrado.")
            

        mapa_variaveis = {}

        # Processa as definições de variáveis
        for linha_atual in linhas_codigo[:bloco_inicio]:
            linha_atual = linha_atual.strip().lower()
            if linha_atual.startswith(("inteiro", "real", "caractere", "logico")):
                tipo_dado, *nomes_variaveis = re.split(r"[, ]+", linha_atual)
                for nome_var in nomes_variaveis:
                    if nome_var:
                        mapa_variaveis[nome_var] = {
                            "tipo": tipo_dado,
                            "valor": 0 if tipo_dado == "inteiro" else \
                                     0.0 if tipo_dado == "real" else \
                                     "" if tipo_dado == "caractere" else \
                                     False
                        }

        # Processa comandos dentro do bloco principal
        indice = bloco_inicio + 1
        while indice < bloco_fim:
            linha_atual = linhas_codigo[indice].strip()
            if not linha_atual or linha_atual.startswith("//"):
                indice += 1
                continue

            elif linha_atual.lower().startswith("escolha"):
                subindice = indice + 1
                caso_resolvido = False
                while subindice < bloco_fim:
                    linha_sub = linhas_codigo[subindice].strip().lower()

                    if linha_sub.startswith("caso") and not caso_resolvido:
                        condicao_caso = linha_sub[5:].strip(":").strip()
                        condicao_caso = condicao_caso.replace("<>", "!=").replace(" e ", " and ").replace(" ou ", " or ")

                        for chave_var in mapa_variaveis:
                            condicao_caso = re.sub(rf'\b{chave_var}\b', str(mapa_variaveis[chave_var]["valor"]), condicao_caso)

                        try:
                            if eval(condicao_caso):
                                caso_resolvido = True
                                indice_caso = subindice + 1
                                while indice_caso < bloco_fim:
                                    linha_dentro_caso = linhas_codigo[indice_caso].strip().lower()
                                    if linha_dentro_caso.startswith("caso") or linha_dentro_caso == "outrocaso" or linha_dentro_caso == "fimescolha":
                                        break
                                    executa_comando(linhas_codigo[indice_caso], mapa_variaveis)
                                    indice_caso += 1
                        except Exception as erro:
                              resultado_label.config(text=f"Erro na condição do caso: {condicao_caso}\n{erro}")
                            

                    elif linha_sub == "outrocaso" and not caso_resolvido:
                        indice_caso = subindice + 1
                        while indice_caso < bloco_fim:
                            linha_dentro_caso = linhas_codigo[indice_caso].strip().lower()
                            if linha_dentro_caso.startswith("caso") or linha_dentro_caso == "fimescolha":
                                break
                            executa_comando(linhas_codigo[indice_caso], mapa_variaveis)
                            indice_caso += 1
                        caso_resolvido = True

                    elif linha_sub == "fimescolha":
                        break

                    subindice += 1

                indice = subindice

            else:
                executa_comando(linha_atual, mapa_variaveis)
            indice += 1

    def executa_comando(linha_comando, mapa_variaveis):
        linha_comando = linha_comando.strip()
        if linha_comando.count('=') == 1 and not linha_comando.startswith("escreva"):
            lado_esquerdo, lado_direito = linha_comando.split("=")
            lado_esquerdo = lado_esquerdo.strip()
            lado_direito = lado_direito.strip()
        elif linha_comando.lower().startswith("escreva"):
            conteudo_escreva = linha_comando[7:].strip().strip('()')
            partes_conteudo = [parte.strip().strip('"') for parte in conteudo_escreva.split(',')]

            saida_final = ""
            for item in partes_conteudo:
                saida_final += str(mapa_variaveis.get(item, {"valor": item})["valor"])
            print(saida_final)

        elif linha_comando.lower().startswith("leia"):
            nome_variavel = linha_comando[5:].strip().strip('()')
            if nome_variavel in mapa_variaveis:
                tipo_entrada = mapa_variaveis[nome_variavel]["tipo"]
                valor_recebido = simpledialog.askstring("Entrada", f"Digite o valor para {nome_variavel} ({tipo_entrada}):")
                try:
                    if tipo_entrada == "inteiro":
                        mapa_variaveis[nome_variavel]["valor"] = int(valor_recebido)
                    elif tipo_entrada == "real":
                        mapa_variaveis[nome_variavel]["valor"] = float(valor_recebido)
                    elif tipo_entrada == "logico":
                        mapa_variaveis[nome_variavel]["valor"] = bool(valor_recebido)
                    elif tipo_entrada == "caractere":
                        mapa_variaveis[nome_variavel]["valor"] = valor_recebido
                except ValueError:
                    print(f"Erro: Tipo de entrada inválido para {nome_variavel} ({tipo_entrada}).")

#FINAL DE CASO DE 

#botao analisar tudo
    # def botaozao():
    #     analisar_codigo()
    #     funcao_sem_nome()
    #     analisar_se_senao()
        # caso_de_uso()
        
#final do botao
#ate para 
    def analisar_para_ate():
        codigo = area_codigo.get("1.0", tk.END).strip()
        linhas = codigo.splitlines()

        try:
            inicio_idx = linhas.index("inicio")
            fim_idx = linhas.index("fimalgoritmo")
        except ValueError:
            resultado_label.config(text="Erro: Bloco 'inicio' ou 'fimalgoritmo' não encontrado.")
            return

        variaveis = {}

        i = inicio_idx + 1
        while i < fim_idx:
            linha = linhas[i].strip()
            if not linha or linha.startswith("//"):
                i += 1
                continue

            if linha.lower().startswith("se "):
                # Processa o bloco SE
                condicao = linha[3:].strip()
                condicao = condicao.replace("<>", "!=").replace(" e ", " and ").replace(" ou ", " or ").replace(" nao ", " not ")

                for var in variaveis:
                    condicao = re.sub(rf'\b{var}\b', str(variaveis[var]["valor"]), condicao)
                    
            elif linha.lower().startswith("para "):
                # Bloco PARA
                _, var, _, inicio, _, fim, *_ = linha.lower().split()
                inicio = int(inicio)
                fim = int(fim)

                if var not in variaveis:
                    variaveis[var] = {"tipo": "inteiro", "valor": inicio}
                else:
                    variaveis[var]["valor"] = inicio

                j = i + 1
                while j < fim_idx:
                    sublinha = linhas[j].strip().lower()
                    if sublinha == "fimpara":
                        break

                    for valor in range(inicio, fim + 1):
                        variaveis[var]["valor"] = valor
                        processar_comando(linhas[j], variaveis)

                    j += 1

                i = j

            else:
                processar_comando(linha, variaveis)
            i += 1

    def processar_comando(linha, variaveis):
        linha = linha.strip()
        if linha.count('=') == 1 and not linha.startswith("escreva"):
            esquerda, direita = linha.split("=")
            esquerda = esquerda.strip()
            direita = direita.strip()

            if esquerda in variaveis:
                tipo = variaveis[esquerda]["tipo"]
                try:
                    direita = (direita.replace("^", "**")
                                       .replace("%", "%")
                                       .replace("==", "==")
                                       .replace("<>", "!=")
                                       .replace(" e ", " and ")
                                       .replace(" ou ", " or ")
                                       .replace(" nao ", " not ")
                                       .replace(" xou ", " != "))

                    for var in variaveis:
                        direita = re.sub(rf'\b{var}\b', str(variaveis[var]["valor"]), direita)

                    if tipo == "logico" and direita in ("verdadeiro", "falso"):
                        resultado = direita == "verdadeiro"
                    else:
                        resultado = eval(direita)

                    if tipo == "inteiro":
                        variaveis[esquerda]["valor"] = int(resultado)
                    elif tipo == "real":
                        variaveis[esquerda]["valor"] = float(resultado)
                    elif tipo == "logico":
                        variaveis[esquerda]["valor"] = bool(resultado)
                    elif tipo == "caractere":
                        variaveis[esquerda]["valor"] = str(resultado).strip('"')
                except Exception as e:
                    print(f"")
        elif linha.lower().startswith("escreva"):
            conteudo = linha[7:].strip().strip('()')
            partes = [parte.strip().strip('"') for parte in conteudo.split(',')]

            saida = ""
            for parte in partes:
                saida += str(variaveis.get(parte, {"valor": parte})["valor"])
            print(saida)


    def botaozao():
        analisar_codigo()
        funcao_sem_nome()
#del teste

    
    botao_analisar = tk.Button(janela, text="Operadores", font=("Arial", 12), command=analisar_codigo)
    botao_analisar.pack(pady=10)
    botao_analisar = tk.Button(janela, text="caso de uso", font=("Arial", 12), command=funcao_sem_nome)
    botao_analisar.pack(pady=10)
    botao_analisar = tk.Button(janela, text="Se senão", font=("Arial", 12), command=analisar_se_senao)
    botao_analisar.pack(pady=10)
    botao_analisar = tk.Button(janela, text="funcao", font=("Arial", 12), command=analisar_FUNCAO)
    botao_analisar.pack(pady=10)
    botao_analisar = tk.Button(janela, text="para_ate", font=("Arial", 12), command=analisar_para_ate)
    botao_analisar.pack(pady=10)

    resultado_label = tk.Label(janela, text="", font=("Arial", 12))
    resultado_label.pack(pady=10)

    janela.mainloop()

criar_interface()