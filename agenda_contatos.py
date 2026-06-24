import struct
import os

# Configurações do Programa
ARQUIVO_DADOS = "agenda.bin"
TAMANHO_NOME = 50
TAMANHO_SOBRENOME = 50
TAMANHO_EMAIL = 50
TAMANHO_ENDERECO = 100
TAMANHO_OBSERVACOES = 100
FORMATO_REGISTRO = "I" + str(TAMANHO_NOME) + "s" + str(TAMANHO_SOBRENOME) + "s" + str(TAMANHO_EMAIL) + "s" + str(TAMANHO_ENDERECO) + "s" + "s" + "sssI" + "I" + "I" + "s" + str(TAMANHO_OBSERVACOES) + "s"

# Estrutura: Cod(I), Nome(50s), Sobrenome(50s), Email(50s), Endereco(100s), TelRes(s), TelCom(s), TelCel(s), Sexo(s), DataAniver(I), DataPrimEncontro(I), Local(s), TipoRelacao(s), Observacoes(100s)
TAMANHO_STRUCT = struct.calcsize(FORMATO_REGISTRO)
REGISTROS_POR_TELA = 3

# Dicionário para mapear tipos de relação
TIPOS_RELACAO = {"A": "Amigo", "P": "Parente", "C": "Comercial", "T": "Trabalho"}
LOCAIS = {"EB": "Ensino Básico", "EM": "Ensino Médio", "FA": "Faculdade", "LT": "Locais de Trabalho"}

# ======================== FUNÇÕES AUXILIARES ========================

def converter_para_bytes(texto, tamanho):
    """Converte texto para bytes com tamanho fixo."""
    if isinstance(texto, str):
        texto = texto.encode('utf-8')
    return texto[:tamanho].ljust(tamanho, b'\x00')

def converter_para_string(dados_bytes):
    """Converte bytes para string removendo null bytes."""
    if isinstance(dados_bytes, bytes):
        return dados_bytes.decode('utf-8').rstrip('\x00')
    return str(dados_bytes)

def gerar_codigo():
    """Gera novo código sequencial para contato."""
    if not os.path.exists(ARQUIVO_DADOS):
        return 1
    
    with open(ARQUIVO_DADOS, 'rb') as arq:
        arq.seek(0, 2)  # Vai ao final
        tamanho = arq.tell()
        if tamanho == 0:
            return 1
        
        arq.seek(tamanho - TAMANHO_STRUCT)
        dados = arq.read(TAMANHO_STRUCT)
        
        if len(dados) == TAMANHO_STRUCT:
            registro = struct.unpack(FORMATO_REGISTRO, dados)
            return registro[0] + 1
    
    return 1

def converter_data_para_int(dia, mes, ano):
    """Converte data para inteiro (formato: DDMMAAAA)."""
    return int(f"{dia:02d}{mes:02d}{ano:04d}")

def converter_int_para_data(data_int):
    """Converte inteiro para data (formato: DDMMAAAA)."""
    texto = str(data_int).zfill(8)
    return int(texto[:2]), int(texto[2:4]), int(texto[4:])

def validar_data(dia, mes, ano):
    """Valida se a data é válida."""
    if mes < 1 or mes > 12:
        return False
    dias_mes = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if dia < 1 or dia > dias_mes[mes - 1]:
        return False
    return True

def obter_mes_atual():
    """Retorna o mês atual sem usar datetime."""
    # Lê do arquivo e retorna o mês do último contato como referência
    # Ou você pode permitir que o usuário digite o mês
    return None

def limpar_tela():
    """Limpa a tela do console."""
    os.system('cls' if os.name == 'nt' else 'clear')

# ======================== FUNÇÕES DE MANIPULAÇÃO DE ARQUIVO ========================

def criar_contato(nome, sobrenome, sexo, endereco, tel_residencial, tel_comercial, tel_celular, 
                  data_aniversario, email, data_primeiro_encontro, local_encontro, tipo_relacao, observacoes):
    """Cria um novo registro de contato e salva no arquivo."""
    
    codigo = gerar_codigo()
    
    # Monta a tupla com os dados
    registro = (
        codigo,
        converter_para_bytes(nome, TAMANHO_NOME),
        converter_para_bytes(sobrenome, TAMANHO_SOBRENOME),
        converter_para_bytes(email, TAMANHO_EMAIL),
        converter_para_bytes(endereco, TAMANHO_ENDERECO),
        converter_para_bytes(tel_residencial, 20),
        converter_para_bytes(tel_comercial, 20),
        converter_para_bytes(tel_celular, 20),
        converter_para_bytes(sexo, 1),
        data_aniversario,
        data_primeiro_encontro,
        converter_para_bytes(local_encontro, 2),
        converter_para_bytes(tipo_relacao, 1),
        converter_para_bytes(observacoes, TAMANHO_OBSERVACOES)
    )
    
    # Salva no arquivo
    with open(ARQUIVO_DADOS, 'ab') as arq:
        dados_empacotados = struct.pack(FORMATO_REGISTRO, *registro)
        arq.write(dados_empacotados)
    
    return codigo

def ler_todos_contatos(mostrar_apagados=False):
    """Lê todos os contatos do arquivo binário."""
    contatos = []
    
    if not os.path.exists(ARQUIVO_DADOS):
        return contatos
    
    with open(ARQUIVO_DADOS, 'rb') as arq:
        while True:
            dados = arq.read(TAMANHO_STRUCT)
            if not dados:
                break
            
            registro = struct.unpack(FORMATO_REGISTRO, dados)
            
            # Verifica se o primeiro byte de observações é 0 (apagado logicamente)
            apagado = registro[13][:1] == b'\x00'
            
            if (not apagado) or (apagado and mostrar_apagados):
                contatos.append(registro)
    
    return contatos

def pesquisar_por_codigo(codigo):
    """Pesquisa contato por código."""
    contatos = ler_todos_contatos()
    
    for contato in contatos:
        if contato[0] == codigo:
            return contato
    
    return None

def pesquisar_por_nome(nome_pesquisa):
    """Pesquisa contatos por nome (parcial)."""
    contatos = ler_todos_contatos()
    resultados = []
    
    for contato in contatos:
        nome = converter_para_string(contato[1]) + " " + converter_para_string(contato[2])
        if nome_pesquisa.lower() in nome.lower():
            resultados.append(contato)
    
    return resultados

def pesquisar_por_mes_aniversario(mes):
    """Pesquisa contatos que fazem aniversário em um mês."""
    contatos = ler_todos_contatos()
    resultados = []
    
    for contato in contatos:
        dia, mes_armazenado, ano = converter_int_para_data(contato[9])
        if mes_armazenado == mes:
            resultados.append(contato)
    
    return resultados

def pesquisar_por_tipo_relacao(tipo):
    """Pesquisa contatos por tipo de relação."""
    contatos = ler_todos_contatos()
    resultados = []
    
    for contato in contatos:
        tipo_relacao = converter_para_string(contato[12])
        if tipo_relacao == tipo:
            resultados.append(contato)
    
    return resultados

def pesquisar_por_mes_e_tipo_relacao(mes, tipo):
    """Pesquisa contatos por mês de aniversário E tipo de relação."""
    contatos = ler_todos_contatos()
    resultados = []
    
    for contato in contatos:
        dia, mes_armazenado, ano = converter_int_para_data(contato[9])
        tipo_relacao = converter_para_string(contato[12])
        
        if mes_armazenado == mes and tipo_relacao == tipo:
            resultados.append(contato)
    
    return resultados

def atualizar_contato(codigo, **campos):
    """Atualiza campos de um contato existente."""
    contatos = ler_todos_contatos(mostrar_apagados=True)
    encontrado = False
    
    with open(ARQUIVO_DADOS, 'r+b') as arq:
        for idx, contato in enumerate(contatos):
            if contato[0] == codigo:
                encontrado = True
                
                # Monta novo registro com atualizações
                novo_registro = list(contato)
                
                if 'nome' in campos:
                    novo_registro[1] = converter_para_bytes(campos['nome'], TAMANHO_NOME)
                if 'sobrenome' in campos:
                    novo_registro[2] = converter_para_bytes(campos['sobrenome'], TAMANHO_SOBRENOME)
                if 'email' in campos:
                    novo_registro[3] = converter_para_bytes(campos['email'], TAMANHO_EMAIL)
                if 'endereco' in campos:
                    novo_registro[4] = converter_para_bytes(campos['endereco'], TAMANHO_ENDERECO)
                if 'tel_residencial' in campos:
                    novo_registro[5] = converter_para_bytes(campos['tel_residencial'], 20)
                if 'tel_comercial' in campos:
                    novo_registro[6] = converter_para_bytes(campos['tel_comercial'], 20)
                if 'tel_celular' in campos:
                    novo_registro[7] = converter_para_bytes(campos['tel_celular'], 20)
                if 'sexo' in campos:
                    novo_registro[8] = converter_para_bytes(campos['sexo'], 1)
                if 'data_aniversario' in campos:
                    novo_registro[9] = campos['data_aniversario']
                if 'data_primeiro_encontro' in campos:
                    novo_registro[10] = campos['data_primeiro_encontro']
                if 'local_encontro' in campos:
                    novo_registro[11] = converter_para_bytes(campos['local_encontro'], 2)
                if 'tipo_relacao' in campos:
                    novo_registro[12] = converter_para_bytes(campos['tipo_relacao'], 1)
                if 'observacoes' in campos:
                    novo_registro[13] = converter_para_bytes(campos['observacoes'], TAMANHO_OBSERVACOES)
                
                # Escreve o registro atualizado
                arq.seek(idx * TAMANHO_STRUCT)
                dados_empacotados = struct.pack(FORMATO_REGISTRO, *novo_registro)
                arq.write(dados_empacotados)
                break
    
    return encontrado

def excluir_logico(codigo):
    """Marca um contato como apagado (exclusão lógica)."""
    contatos = ler_todos_contatos(mostrar_apagados=True)
    
    with open(ARQUIVO_DADOS, 'r+b') as arq:
        for idx, contato in enumerate(contatos):
            if contato[0] == codigo:
                novo_registro = list(contato)
                novo_registro[13] = b'\x00' + b'\x00' * (TAMANHO_OBSERVACOES - 1)
                
                arq.seek(idx * TAMANHO_STRUCT)
                dados_empacotados = struct.pack(FORMATO_REGISTRO, *novo_registro)
                arq.write(dados_empacotados)
                return True
    
    return False

def excluir_fisico():
    """Remove fisicamente todos os registros apagados logicamente."""
    contatos = ler_todos_contatos(mostrar_apagados=True)
    contatos_validos = [c for c in contatos if c[13][:1] != b'\x00']
    
    if not contatos_validos:
        if os.path.exists(ARQUIVO_DADOS):
            os.remove(ARQUIVO_DADOS)
    else:
        with open(ARQUIVO_DADOS, 'wb') as arq:
            for contato in contatos_validos:
                dados_empacotados = struct.pack(FORMATO_REGISTRO, *contato)
                arq.write(dados_empacotados)

def listar_contatos(contatos=None, pagina=0):
    """Exibe contatos de forma paginada (3 em 3)."""
    if contatos is None:
        contatos = ler_todos_contatos()
    
    if not contatos:
        print("Nenhum contato encontrado.")
        return
    
    inicio = pagina * REGISTROS_POR_TELA
    fim = inicio + REGISTROS_POR_TELA
    
    print(f"\n{'Cód':<5} {'Nome':<20} {'Sobrenome':<20} {'Email':<25}")
    print("-" * 75)
    
    for contato in contatos[inicio:fim]:
        print(f"{contato[0]:<5} {converter_para_string(contato[1]):<20} {converter_para_string(contato[2]):<20} {converter_para_string(contato[3]):<25}")
    
    total_paginas = (len(contatos) + REGISTROS_POR_TELA - 1) // REGISTROS_POR_TELA
    print(f"\nPágina {pagina + 1} de {total_paginas}")
    
    return len(contatos)

def exibir_contato_completo(contato):
    """Exibe todos os dados de um contato."""
    if not contato:
        print("Contato não encontrado.")
        return
    
    dia, mes, ano = converter_int_para_data(contato[9])
    dia_enc, mes_enc, ano_enc = converter_int_para_data(contato[10])
    
    print(f"\n{'='*60}")
    print(f"Código: {contato[0]}")
    print(f"Nome: {converter_para_string(contato[1])} {converter_para_string(contato[2])}")
    print(f"Sexo: {converter_para_string(contato[8])}")
    print(f"Email: {converter_para_string(contato[3])}")
    print(f"Endereço: {converter_para_string(contato[4])}")
    print(f"Tel. Residencial: {converter_para_string(contato[5])}")
    print(f"Tel. Comercial: {converter_para_string(contato[6])}")
    print(f"Tel. Celular: {converter_para_string(contato[7])}")
    print(f"Data Aniversário: {dia:02d}/{mes:02d}/{ano}")
    print(f"Data 1º Encontro: {dia_enc:02d}/{mes_enc:02d}/{ano_enc}")
    print(f"Local: {LOCAIS.get(converter_para_string(contato[11]), 'N/A')}")
    print(f"Tipo de Relação: {TIPOS_RELACAO.get(converter_para_string(contato[12]), 'N/A')}")
    print(f"Observações: {converter_para_string(contato[13])}")
    print(f"{'='*60}\n")

def fazer_backup():
    """Cria backup do arquivo com timestamp."""
    if not os.path.exists(ARQUIVO_DADOS):
        print("Nenhum arquivo para fazer backup.")
        return
    
    print("\nPara criar o backup, digite a data e hora atual:")
    dia_backup = int(input("Dia (DD): "))
    mes_backup = int(input("Mês (MM): "))
    ano_backup = int(input("Ano (AAAA): "))
    hora_backup = int(input("Hora (HH): "))
    minuto_backup = int(input("Minuto (MM): "))
    
    nome_backup = f"bkp{dia_backup:02d}{mes_backup:02d}{ano_backup:04d}{hora_backup:02d}{minuto_backup:02d}.bkp"
    
    with open(ARQUIVO_DADOS, 'rb') as arq_origem:
        conteudo = arq_origem.read()
    
    with open(nome_backup, 'wb') as arq_backup:
        arq_backup.write(conteudo)
    
    print(f"✓ Backup criado: {nome_backup}")

def listar_aniversariantes_mes_especifico():
    """Lista todos os contatos que fazem aniversário em um mês específico."""
    print("\nDigite o mês que deseja verificar (1-12):")
    mes_verificacao = int(input("Mês: "))
    
    contatos_mes = pesquisar_por_mes_aniversario(mes_verificacao)
    
    if contatos_mes:
        limpar_tela()
        print(f"\n{'*'*60}")
        print(f"ANIVERSARIANTES DO MÊS {mes_verificacao:02d}")
        print(f"{'*'*60}\n")
        listar_contatos(contatos_mes)
    else:
        print(f"Nenhum aniversariante no mês {mes_verificacao:02d}.")

def listar_nomes_emails():
    """Lista nomes e emails de todos os contatos."""
    contatos = ler_todos_contatos()
    
    if not contatos:
        print("Nenhum contato cadastrado.")
        return
    
    print(f"\n{'Nome Completo':<50} {'Email':<30}")
    print("-" * 80)
    
    for contato in contatos:
        nome_completo = converter_para_string(contato[1]) + " " + converter_para_string(contato[2])
        email = converter_para_string(contato[3])
        print(f"{nome_completo:<50} {email:<30}")

# ======================== MENU PRINCIPAL ========================

def menu_inserir():
    """Menu para inserir novo contato."""
    limpar_tela()
    print("\n=== INSERIR NOVO CONTATO ===\n")
    
    nome = input("Nome: ").strip()
    sobrenome = input("Sobrenome: ").strip()
    sexo = input("Sexo (M/F): ").strip().upper()
    endereco = input("Endereço: ").strip()
    tel_residencial = input("Tel. Residencial: ").strip()
    tel_comercial = input("Tel. Comercial: ").strip()
    tel_celular = input("Tel. Celular: ").strip()
    
    while True:
        try:
            dia = int(input("Data Aniversário (dia): "))
            mes = int(input("Data Aniversário (mês): "))
            ano = int(input("Data Aniversário (ano): "))
            if validar_data(dia, mes, ano):
                data_aniversario = converter_data_para_int(dia, mes, ano)
                break
            else:
                print("Data inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida.")
    
    email = input("Email: ").strip()
    
    while True:
        try:
            dia_enc = int(input("Data 1º Encontro (dia): "))
            mes_enc = int(input("Data 1º Encontro (mês): "))
            ano_enc = int(input("Data 1º Encontro (ano): "))
            if validar_data(dia_enc, mes_enc, ano_enc):
                data_primeiro_encontro = converter_data_para_int(dia_enc, mes_enc, ano_enc)
                break
            else:
                print("Data inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida.")
    
    print("\nLocais: EB=Ensino Básico, EM=Ensino Médio, FA=Faculdade, LT=Locais de Trabalho")
    local = input("Local: ").strip().upper()
    
    print("\nTipos de Relação: A=Amigo, P=Parente, C=Comercial, T=Trabalho")
    tipo_relacao = input("Tipo de Relação: ").strip().upper()
    
    observacoes = input("Observações: ").strip()
    
    codigo = criar_contato(nome, sobrenome, sexo, endereco, tel_residencial, tel_comercial, 
                          tel_celular, data_aniversario, email, data_primeiro_encontro, 
                          local, tipo_relacao, observacoes)
    
    print(f"\n✓ Contato inserido com código: {codigo}")
    input("Pressione ENTER para continuar...")

def menu_consultar():
    """Menu para consultar contatos."""
    while True:
        limpar_tela()
        print("\n=== CONSULTAR CONTATOS ===")
        print("1 - Pesquisar por Código")
        print("2 - Pesquisar por Nome")
        print("3 - Pesquisar por Mês de Aniversário")
        print("4 - Pesquisar por Tipo de Relação")
        print("5 - Pesquisar por Mês de Aniversário E Tipo de Relação")
        print("0 - Voltar")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            limpar_tela()
            codigo = int(input("Digite o código: "))
            contato = pesquisar_por_codigo(codigo)
            exibir_contato_completo(contato)
            input("Pressione ENTER para continuar...")
        
        elif opcao == "2":
            limpar_tela()
            nome = input("Digite o nome (ou parte dele): ").strip()
            contatos = pesquisar_por_nome(nome)
            listar_contatos(contatos)
            input("Pressione ENTER para continuar...")
        
        elif opcao == "3":
            limpar_tela()
            mes = int(input("Digite o mês (1-12): "))
            contatos = pesquisar_por_mes_aniversario(mes)
            listar_contatos(contatos)
            input("Pressione ENTER para continuar...")
        
        elif opcao == "4":
            limpar_tela()
            print("Tipos: A=Amigo, P=Parente, C=Comercial, T=Trabalho")
            tipo = input("Digite o tipo: ").strip().upper()
            contatos = pesquisar_por_tipo_relacao(tipo)
            listar_contatos(contatos)
            input("Pressione ENTER para continuar...")
        
        elif opcao == "5":
            limpar_tela()
            mes = int(input("Digite o mês (1-12): "))
            print("Tipos: A=Amigo, P=Parente, C=Comercial, T=Trabalho")
            tipo = input("Digite o tipo: ").strip().upper()
            contatos = pesquisar_por_mes_e_tipo_relacao(mes, tipo)
            listar_contatos(contatos)
            input("Pressione ENTER para continuar...")
        
        elif opcao == "0":
            break
        
        else:
            print("Opção inválida!")
            input("Pressione ENTER para continuar...")

def menu_alterar():
    """Menu para alterar contato."""
    limpar_tela()
    print("\n=== ALTERAR CONTATO ===\n")
    
    codigo = int(input("Digite o código do contato: "))
    contato = pesquisar_por_codigo(codigo)
    
    if not contato:
        print("Contato não encontrado!")
        input("Pressione ENTER para continuar...")
        return
    
    exibir_contato_completo(contato)
    
    print("\nCampos que podem ser alterados:")
    print("1 - Telefone Residencial")
    print("2 - Telefone Comercial")
    print("3 - Telefone Celular")
    print("4 - Endereço")
    print("5 - Email")
    print("6 - Observações")
    print("0 - Cancelar")
    
    opcao = input("\nOpção: ").strip()
    
    campos_atualizacao = {}
    
    if opcao == "1":
        campos_atualizacao['tel_residencial'] = input("Novo telefone residencial: ").strip()
    elif opcao == "2":
        campos_atualizacao['tel_comercial'] = input("Novo telefone comercial: ").strip()
    elif opcao == "3":
        campos_atualizacao['tel_celular'] = input("Novo telefone celular: ").strip()
    elif opcao == "4":
        campos_atualizacao['endereco'] = input("Novo endereço: ").strip()
    elif opcao == "5":
        campos_atualizacao['email'] = input("Novo email: ").strip()
    elif opcao == "6":
        campos_atualizacao['observacoes'] = input("Novas observações: ").strip()
    elif opcao == "0":
        return
    
    if campos_atualizacao:
        if atualizar_contato(codigo, **campos_atualizacao):
            print("\n✓ Contato atualizado com sucesso!")
        else:
            print("\n✗ Erro ao atualizar contato!")
    
    input("Pressione ENTER para continuar...")

def menu_excluir():
    """Menu para excluir contato."""
    limpar_tela()
    print("\n=== EXCLUIR CONTATO ===\n")
    
    codigo = int(input("Digite o código do contato a excluir: "))
    contato = pesquisar_por_codigo(codigo)
    
    if not contato:
        print("Contato não encontrado!")
        input("Pressione ENTER para continuar...")
        return
    
    exibir_contato_completo(contato)
    
    confirmacao = input("Tem certeza que deseja excluir? (S/N): ").strip().upper()
    
    if confirmacao == 'S':
        if excluir_logico(codigo):
            print("\n✓ Contato excluído logicamente!")
        else:
            print("\n✗ Erro ao excluir contato!")
    else:
        print("Operação cancelada!")
    
    input("Pressione ENTER para continuar...")

def menu_listar():
    """Menu para listar contatos."""
    limpar_tela()
    print("\n=== LISTAR CONTATOS ===\n")
    
    contatos = ler_todos_contatos()
    pagina = 0
    
    while True:
        limpar_tela()
        total = listar_contatos(contatos, pagina)
        
        if total <= REGISTROS_POR_TELA:
            break
        
        print("\n(P)róxima | (A)nterior | (S)air")
        opcao = input("Opção: ").strip().upper()
        
        if opcao == 'P':
            total_paginas = (total + REGISTROS_POR_TELA - 1) // REGISTROS_POR_TELA
            if pagina < total_paginas - 1:
                pagina += 1
        elif opcao == 'A':
            if pagina > 0:
                pagina -= 1
        elif opcao == 'S':
            break

def menu_aniversariantes_mes():
    """Menu para listar aniversariantes de um mês específico."""
    limpar_tela()
    print("\n=== ANIVERSARIANTES DO MÊS ===\n")
    
    listar_aniversariantes_mes_especifico()
    input("Pressione ENTER para continuar...")

def menu_nomes_emails():
    """Menu para listar nomes e emails."""
    limpar_tela()
    print("\n=== NOMES E EMAILS ===\n")
    
    listar_nomes_emails()
    input("Pressione ENTER para continuar...")

def menu_finalizar():
    """Menu para finalizar e fazer backup."""
    limpar_tela()
    print("\n=== FINALIZANDO PROGRAMA ===\n")
    
    fazer_backup()
    print("\nExecutando exclusão física dos registros apagados...")
    excluir_fisico()
    print("✓ Programa finalizado com sucesso!")

def menu_principal():
    """Menu principal do programa."""
    while True:
        limpar_tela()
        print("\n╔════════════════════════════════╗")
        print("║   AGENDA DE CONTATOS          ║")
        print("╚════════════════════════════════╝")
        print("\n1 - Inserir Contato")
        print("2 - Consultar")
        print("3 - Alterar")
        print("4 - Excluir")
        print("5 - Listar")
        print("6 - Aniversariantes do Mês")
        print("7 - Nomes e Emails")
        print("0 - Finalizar")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            menu_inserir()
        elif opcao == "2":
            menu_consultar()
        elif opcao == "3":
            menu_alterar()
        elif opcao == "4":
            menu_excluir()
        elif opcao == "5":
            menu_listar()
        elif opcao == "6":
            menu_aniversariantes_mes()
        elif opcao == "7":
            menu_nomes_emails()
        elif opcao == "0":
            menu_finalizar()
            break
        else:
            print("Opção inválida!")
            input("Pressione ENTER para continuar...")

# ======================== EXECUÇÃO ========================

if __name__ == "__main__":
    menu_principal()
