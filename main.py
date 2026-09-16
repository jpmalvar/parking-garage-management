# -*- coding: utf-8 -*-

# Importações necessárias
import re
from datetime import datetime

# --- BANCO DE DADOS (Estrutura de Dados) ---

# É importante manter o usuário admin para gerenciar o sistema!
usuarios = {
    'admin': {'password': 'admin123', 'type': 'admin'}
}

# Todas as vagas começam como 'L' (Livre).
vagas = [
    ['L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L'],  # Andar 1 com 15 vagas
    ['L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L'],  # Andar 2 com 15 vagas
    ['L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L']   # Andar 3 com 15 vagas
]

# O dicionário de veículos começa vazio.
veiculosEstacionados = {}

# O primeiro ticket a ser gerado.
ticketCounter = 1001

# O histórico de veículos também começa vazio.
historicoVeiculos = []

# Configurações do sistema
configuracoes = {
    'valor_por_hora': 10.00,
    'valor_hora_moto': 5.00
}


# --- FUNÇÕES PARA SALVAR OS DADOS ---
def salvarDados():
    """Salva os arquivos manualmente em arquivos.txt"""
    # Usuários:
    arqUsuarios = None
    try:
        arqUsuarios = open('usuarios.txt','w')
        for user, data in usuarios.items():
            linha = f'{user},{data['password']},{data['type']}\n'
            arqUsuarios.write(linha)
    except Exception as e:
        print(f"[SISTEMA] Erro ao salvar 'usuarios.txt': {e}")
    finally:
        if arqUsuarios:
            arqUsuarios.close()

    # Veículos estacionados:
    arqEstacionados = None
    try:
        arqEstacionados = open('estacionados.txt','w')
        for ticket, data in veiculosEstacionados.items():
            entrada_str = data['entrada'].strftime('%Y-%m-%d %H:%M:%S.%f')
            andar, vaga = data['posicao']
            tipo_veiculo = data.get('tipo', 'carro') 
            linha = f"{ticket},{data['usuario']},{data['placa']},{entrada_str},{andar},{vaga},{tipo_veiculo}\n"
            arqEstacionados.write(linha)
    except Exception as e:
        print(f"[SISTEMA] Erro ao salvar 'estacionados.txt': {e}")
    finally:
        if arqEstacionados:
            arqEstacionados.close()

    # Histórico:
    arqHistorico = None
    try:
        arqHistorico = open('historico.txt','w')
        for veiculo in historicoVeiculos:
            linha = f"{veiculo['usuario']},{veiculo['placa']},{veiculo['entrada']},{veiculo['saida']},{veiculo['valor_pago']}\n"
            arqHistorico.write(linha)
    except Exception as e:
        print(f"[SISTEMA] Erro ao salvar 'historico.txt': {e}")
    finally:
        if arqHistorico:
            arqHistorico.close()
    
    # Configurações do sistema:
    arqSistema = None
    try:
        arqSistema = open('sistema.txt','w')
        arqSistema.write(f'ticketCounter,{ticketCounter}\n')
        arqSistema.write(f"valor_por_hora,{configuracoes['valor_por_hora']}\n")
        arqSistema.write(f"valor_hora_moto,{configuracoes['valor_hora_moto']}\n")
    except Exception as e:
        print(f"[SISTEMA] Erro ao salvar 'sistema.txt': {e}")
    finally:
        if arqSistema:
            arqSistema.close()

    print("[SISTEMA] Dados salvos com sucesso!")

def carregarDados():
    """Carrega todos os dados manualmente dos arquivos.txt."""
    global usuarios, veiculosEstacionados, historicoVeiculos, ticketCounter
    
    # Carregar usuários
    arqUsuarios = None
    try:
        arqUsuarios = open("usuarios.txt", "r")
        for linha in arqUsuarios:
            user, password, user_type = linha.strip().split(',')
            if user not in usuarios:
                usuarios[user] = {'password': password, 'type': user_type}
    except FileNotFoundError:
        print("[SISTEMA] Arquivo 'usuarios.txt' não encontrado. Carregando admin padrão.")
    except Exception as e:
        print(f"[SISTEMA] Erro ao ler 'usuarios.txt': {e}")
    finally:
        if arqUsuarios:
            arqUsuarios.close()

    # Carregar veículos estacionados
    arqEstacionados = None
    try:
        arqEstacionados = open("estacionados.txt", "r")
        for linha in arqEstacionados:
            dados_linha = linha.strip().split(',')
            
            if len(dados_linha) == 6:
                ticket, user, placa, entrada_str, andar_str, vaga_str = dados_linha
                tipo_veiculo = 'carro'
            elif len(dados_linha) == 7:
                ticket, user, placa, entrada_str, andar_str, vaga_str, tipo_veiculo = dados_linha
            else:
                continue

            entrada_dt = datetime.strptime(entrada_str, '%Y-%m-%d %H:%M:%S.%f')
            andar = int(andar_str)
            vaga = int(vaga_str)
            veiculosEstacionados[ticket] = {
                'usuario': user,
                'placa': placa,
                'entrada': entrada_dt,
                'posicao': (andar, vaga),
                'tipo': tipo_veiculo
            }
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[SISTEMA] Erro ao ler 'estacionados.txt': {e}")
    finally:
        if arqEstacionados:
            arqEstacionados.close()

    # Sincroniza o mapa 'vagas' com os veículos carregados
    print("[SISTEMA] Sincronizando mapa de vagas...")
    for veiculo in veiculosEstacionados.values():
        try:
            andar, vaga = veiculo['posicao']
            if 0 <= andar < len(vagas) and 0 <= vaga < len(vagas[andar]):
                vagas[andar][vaga] = 'O'
            else:
                print(f"[SISTEMA] Aviso: Posição inválida {veiculo['posicao']} no 'estacionados.txt'.")
        except Exception as e:
             print(f"[SISTEMA] Erro ao sincronizar vaga: {e}")

    # Carregar histórico
    arqHistorico = None
    try:
        arqHistorico = open("historico.txt", "r")
        for linha in arqHistorico:
            user, placa, entrada, saida, valor_str = linha.strip().split(',')
            historicoVeiculos.append({
                'usuario': user,
                'placa': placa,
                'entrada': entrada,
                'saida': saida,
                'valor_pago': float(valor_str)
            })
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[SISTEMA] Erro ao ler 'historico.txt': {e}")
    finally:
        if arqHistorico:
            arqHistorico.close()

    # Carregar configurações do sistema
    arqSistema = None
    try:
        arqSistema = open("sistema.txt", "r")
        for linha in arqSistema:
            chave, valor = linha.strip().split(',')
            if chave == 'ticketCounter':
                ticketCounter = int(valor)
            elif chave == 'valor_por_hora':
                configuracoes['valor_por_hora'] = float(valor)
            elif chave == 'valor_hora_moto':
                configuracoes['valor_hora_moto'] = float(valor)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[SISTEMA] Erro ao ler 'sistema.txt': {e}")
    finally:
        if arqSistema:
            arqSistema.close()

    print("[SISTEMA] Dados carregados.")

# --- FUNÇÕES GERAIS ---


def visualizarGaragem():
    """Mostra um mapa visual da ocupação da garagem."""
    print("\n--- MAPA DA GARAGEM ---")
    print("[L] = Livre | [O] = Ocupada")
    for i, andar in enumerate(vagas):
        print(f"\nAndar {i+1}: ", end="")
        numerosVagas = ""
        for j in range(len(andar)):
            numerosVagas += f" {j+1:^3}  "
        print(numerosVagas)
        
        print("Vagas:   ", end="")
        representacaoAndar = ""
        for vaga in andar:
            representacaoAndar += f" [{vaga}]  "
        print(representacaoAndar)

# --- FUNÇÕES DE CADASTRO ---

def cadastrarUsuario():
    """Realiza o cadastro de um novo usuário comum."""
    print("\n--- Cadastro de Novo Usuário ---")
    while True:
        novoUsuario = input("Digite o nome de usuário desejado: ").lower().strip()
        
        if ',' in novoUsuario:
            print("O nome de usuário não pode conter vírgulas. Tente novamente.")
            continue
            
        if not novoUsuario:
            print("O nome de usuário não pode ser vazio. Tente novamente.")
            continue
        if novoUsuario in usuarios:
            print("Este nome de usuário já existe! Por favor, escolha outro.")
            continue

        senha = input("Digite a senha desejada: ")
        
        if ',' in senha:
            print("A senha não pode conter vírgulas. Tente novamente.")
            continue
            
        confirmaSenha = input("Confirme a senha: ")
        if not senha:
            print("A senha não pode ser vazia. Tente novamente.")
            continue
        if senha != confirmaSenha:
            print("As senhas não coincidem! Tente novamente.")
            continue
        
        usuarios[novoUsuario] = {'password': senha, 'type': 'user'}
        print("\nUsuário cadastrado com sucesso! Agora você já pode fazer o login.")
        break

# --- FUNÇÕES DO ADMINISTRADOR ---

def menuAdmin():
    """Exibe o menu de opções para o administrador."""
    print("\n--- MENU DO ADMINISTRADOR ---")
    print("1. Ver Relatório Geral de Veículos")
    print("2. Ver Faturamento Total")
    print("3. Editar Valor por Hora")
    print("4. Visualizar Ocupação da Garagem")
    print("5. Buscar Veículo por Placa")
    print("6. Deslogar")
    return input("Escolha uma opção: ")

def relatorioGeral():
    print("\n--- Relatório Geral de Veículos ---")
    if not historicoVeiculos:
        print("Nenhum veículo no histórico.")
        return
    for veiculo in historicoVeiculos:
        print(f"Usuário: {veiculo['usuario']}, Placa: {veiculo['placa']}, Entrada: {veiculo['entrada']}, Saída: {veiculo['saida']}, Pago: R$ {veiculo['valor_pago']:.2f}")

def verFaturamento():
    print("\n--- Faturamento Total ---")
    faturamentoTotal = 0.0
    for veiculo in historicoVeiculos:
        faturamentoTotal += veiculo['valor_pago']
    print(f"O faturamento total do estacionamento é: R$ {faturamentoTotal:.2f}")

def editarValorHora():
    print("\n--- Editar Valor por Hora ---")
    valorCarro = configuracoes['valor_por_hora']
    valorMoto = configuracoes.get('valor_hora_moto', 5.0)
    
    print(f"O valor atual por hora para CARRO é: R$ {valorCarro:.2f}")
    print(f"O valor atual por hora para MOTO é: R$ {valorMoto:.2f}")
    
    try:
        novoValorCarro = float(input("Digite o novo valor por hora para CARRO (ex: 12.50): "))
        novoValorMoto = float(input("Digite o novo valor por hora para MOTO (ex: 6.00): "))
        
        configuracoes['valor_por_hora'] = novoValorCarro
        configuracoes['valor_hora_moto'] = novoValorMoto
        
        print("\nValores atualizados com sucesso!")
        print(f"Novo valor CARRO: R$ {configuracoes['valor_por_hora']:.2f}")
        print(f"Novo valor MOTO: R$ {configuracoes['valor_hora_moto']:.2f}")
    except ValueError:
        print("Valor inválido. Por favor, insira um número.")

def buscarPorPlaca():
    """Busca um veículo atualmente estacionado pela sua placa."""
    print("\n--- Buscar Veículo por Placa ---")
    placaBusca = input("Digite a placa do veículo que deseja encontrar: ").upper().strip()
    veiculoEncontrado = False
    for ticketId, infoVeiculo in veiculosEstacionados.items():
        if infoVeiculo['placa'] == placaBusca:
            print("\n--- Veículo Encontrado! ---")
            print(f"Placa: {infoVeiculo['placa']}")
            print(f"Tipo: {infoVeiculo.get('tipo', 'Carro').capitalize()}")
            print(f"Ticket de Entrada: {ticketId}")
            print(f"Usuário que estacionou: {infoVeiculo['usuario']}")
            entradaFormatada = infoVeiculo['entrada'].strftime('%d/%m/%Y às %H:%M:%S')
            print(f"Horário de Entrada: {entradaFormatada}")
            andar, vaga = infoVeiculo['posicao']
            print(f"Localização: Andar {andar + 1}, Vaga {vaga + 1}")
            veiculoEncontrado = True
            break
    if not veiculoEncontrado:
        print(f"\nNão há nenhum veículo com a placa '{placaBusca}' estacionado no momento.")

# --- FUNÇÕES DO USUÁRIO COMUM ---

def menuUsuario(username):
    """Exibe o menu de opções para o usuário comum."""
    print(f"\n--- BEM-VINDO, {username.upper()} ---")
    print("1. Estacionar Veículo (Gerar Ticket)")
    print("2. Pagar e Sair (Usar Ticket)")
    print("3. Ver Vagas Disponíveis por Andar")
    print("4. Ver Tabela de Preços")
    print("5. Ver Meu Histórico de Gastos")
    print("6. Deslogar")
    return input("Escolha uma opção: ")

def estacionarVeiculo(username):
    """Guia o usuário no processo de estacionar o veículo."""
    global ticketCounter
    
    print("\n--- Estacionar Veículo ---")
    visualizarGaragem()
    try:
        andarEscolhido = int(input("Escolha o andar (ex: 1): ")) - 1
        vagaEscolhida = int(input("Escolha a vaga (ex: 1): ")) - 1
        
        if not (0 <= andarEscolhido < len(vagas) and 0 <= vagaEscolhida < len(vagas[andarEscolhido])):
            print("Posição inválida. Tente novamente.")
            return
        if vagas[andarEscolhido][vagaEscolhida] == 'O':
            print("Esta vaga já está ocupada. Por favor, escolha outra.")
            return
            
        while True:
            placa = input("Digite a placa do seu veículo: ").upper().strip()
            
            if ',' in placa:
                print("A placa não pode conter vírgulas. Tente novamente.")
                continue
                
            placaSemHifen = placa.replace('-', '')
            padraoAntigo = re.compile(r"^[A-Z]{3}[0-9]{4}$")
            padraoMercosul = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")
            
            if not (padraoAntigo.match(placaSemHifen) or padraoMercosul.match(placaSemHifen)):
                print("Formato de placa inválido! Tente novamente (Ex: ABC-1234 ou BRA2E19).")
                continue

            placaJaEstacionada = False
            for veiculo in veiculosEstacionados.values():
                if veiculo['placa'] == placa:
                    placaJaEstacionada = True
                    break
            
            if placaJaEstacionada:
                print(f"\nERRO: O veículo com a placa {placa} já está na garagem.")
                print("Por favor, verifique a placa ou saia com o veículo primeiro.")
                continue

            break
        
        while True:
            tipo_input = input("Qual o tipo de veículo? (1 - Carro / 2 - Moto): ").strip()
            if tipo_input == '1':
                tipo_veiculo = 'carro'
                break
            elif tipo_input == '2':
                tipo_veiculo = 'moto'
                break
            else:
                print("Opção inválida. Digite 1 para Carro ou 2 para Moto.")

        vagas[andarEscolhido][vagaEscolhida] = 'O'
        ticketId = f"{ticketCounter:04d}"
        horaEntrada = datetime.now()
        
        veiculosEstacionados[ticketId] = {
            'usuario': username,
            'placa': placa,
            'entrada': horaEntrada,
            'posicao': (andarEscolhido, vagaEscolhida),
            'tipo': tipo_veiculo
        }
        ticketCounter += 1
        
        print("\n" + "="*40)
        print("      TICKET DE ESTACIONAMENTO")
        print(f"  Tipo de Veículo: {tipo_veiculo.capitalize()}")
        print(f"  Número do Ticket: {ticketId}")
        print(f"  Placa do Veículo: {placa}")
        print(f"  Data de Entrada: {horaEntrada.strftime('%d/%m/%Y')}")
        print(f"  Hora de Entrada: {horaEntrada.strftime('%H:%M:%S')}")
        print(f"  Posição: Andar {andarEscolhido+1}, Vaga {vagaEscolhida+1}")
        print("="*40)
        print("\nGUARDE ESTE TICKET! Você precisará dele para sair.")

    except (ValueError, IndexError):
        print("Entrada inválida. Por favor, digite números para andar e vaga.")

def pagarESair():
    """Processa a saída e o pagamento de um veículo."""
    print("\n--- Pagar e Sair com Veículo ---")
    ticketId = input("Digite o número do seu ticket: ")
    placaVeiculo = input("Digite a placa do seu veículo para confirmar: ").upper()
    
    if ticketId not in veiculosEstacionados:
        print("Ticket inválido ou não encontrado.")
        return
        
    veiculo = veiculosEstacionados[ticketId]
    if veiculo['placa'] != placaVeiculo:
        print("A placa do veículo não corresponde à registrada para este ticket.")
        return
        
    horaSaida = datetime.now()
    horaEntrada = veiculo['entrada']
    tempoTotal = horaSaida - horaEntrada
    horasEstacionado = (tempoTotal.total_seconds() / 3600)
    
    if horasEstacionado < 1:
        horasEstacionado = 1
    else:
        horasEstacionado = int(horasEstacionado) + (1 if horasEstacionado % 1 != 0 else 0)

    tipo_veiculo = veiculo.get('tipo', 'carro')
    valor_hora_usado = configuracoes['valor_por_hora']

    if tipo_veiculo == 'moto':
        valor_hora_usado = configuracoes.get('valor_hora_moto', configuracoes['valor_por_hora'])

    valorAPagar = horasEstacionado * valor_hora_usado
    
    print("\n--- Resumo para Pagamento ---")
    print(f"Placa: {veiculo['placa']} ({tipo_veiculo.capitalize()})")
    print(f"Tempo de permanência: Aprox. {horasEstacionado} hora(s).")
    print(f"Valor por hora (tarifa {tipo_veiculo}): R$ {valor_hora_usado:.2f}")
    print(f"Valor a pagar: R$ {valorAPagar:.2f}")
    
    confirmacao = input("Confirmar pagamento? (s/n): ").lower()
    if confirmacao == 's':
        
        andar, vaga = veiculo['posicao']
        vagas[andar][vaga] = 'L'
        
        historicoVeiculos.append({
            'usuario': veiculo['usuario'],
            'placa': veiculo['placa'],
            'entrada': horaEntrada.strftime('%Y-%m-%d %H:%M'),
            'saida': horaSaida.strftime('%Y-%m-%d %H:%M'),
            'valor_pago': valorAPagar
        })
        
        del veiculosEstacionados[ticketId]
        print("\nPagamento efetuado com sucesso! Saída liberada. Volte sempre!")
    else:
        print("\nPagamento cancelado.")

def verVagasDisponiveis():
    print("\n--- Vagas Disponíveis ---")
    for i, andar in enumerate(vagas):
        vagasLivres = andar.count('L')
        totalVagas = len(andar)
        print(f"Andar {i+1}: {vagasLivres} de {totalVagas} vagas disponíveis.")

def verTabelaPrecos():
    print("\n--- Tabela de Preços ---")
    valorCarro = configuracoes['valor_por_hora']
    valorMoto = configuracoes.get('valor_hora_moto', 5.0)
    print(f"O valor atual para CARRO é de R$ {valorCarro:.2f} por hora.")
    print(f"O valor atual para MOTO é de R$ {valorMoto:.2f} por hora.")

def relatorioUsuario(username):
    print("\n--- Meu Histórico de Gastos ---")
    gastosUsuario = [v for v in historicoVeiculos if v['usuario'] == username]
    if not gastosUsuario:
        print("Você ainda não utilizou nossos serviços.")
        return
    totalGasto = 0
    for veiculo in gastosUsuario:
        print(f"Placa: {veiculo['placa']}, Entrada: {veiculo['entrada']}, Saída: {veiculo['saida']}, Pago: R$ {veiculo['valor_pago']:.2f}")
        totalGasto += veiculo['valor_pago']
    print("-" * 30)
    print(f"Seu gasto total foi de: R$ {totalGasto:.2f}")

# --- LÓGICA PRINCIPAL ---

def main():
    """Função principal que executa o programa."""
    usuarioLogado = None
    while True:
        if usuarioLogado is None:
            print("\n" + "#"*40)
            print("### BEM-VINDO AO SISTEMA DE GARAGEM ###")
            print("#"*40)
            print("1. Fazer Login")
            print("2. Cadastrar Novo Usuário")
            print("3. Sair do Sistema")
            opcaoInicial = input("Escolha uma opção: ")

            if opcaoInicial == '1':
                username = input("Digite seu usuário: ").lower()
                password = input("Digite sua senha: ")
                if username in usuarios and usuarios[username]['password'] == password:
                    usuarioLogado = {'username': username, 'type': usuarios[username]['type']}
                    print(f"\nLogin bem-sucedido! Bem-vindo, {username}.")
                else:
                    print("\nUsuário ou senha incorretos. Tente novamente.")
            elif opcaoInicial == '2':
                cadastrarUsuario()
            elif opcaoInicial == '3':
                print("\nObrigado por usar nosso sistema. Até logo!")
                salvarDados()
                break
            else:
                print("\nOpção inválida. Por favor, tente novamente.")
            input("\nPressione Enter para continuar...")
        
        else:
            if usuarioLogado['type'] == 'admin':
                opcao = menuAdmin()
                if opcao == '1': relatorioGeral()
                elif opcao == '2': verFaturamento()
                elif opcao == '3': editarValorHora()
                elif opcao == '4': visualizarGaragem()
                elif opcao == '5': buscarPorPlaca()
                elif opcao == '6':
                    usuarioLogado = None
                    print("\nDeslogado com sucesso.")
                else: print("Opção inválida!")
            
            elif usuarioLogado['type'] == 'user':
                opcao = menuUsuario(usuarioLogado['username'])
                if opcao == '1': estacionarVeiculo(usuarioLogado['username'])
                elif opcao == '2': pagarESair()
                elif opcao == '3': verVagasDisponiveis()
                elif opcao == '4': verTabelaPrecos()
                elif opcao == '5': relatorioUsuario(usuarioLogado['username'])
                elif opcao == '6':
                    usuarioLogado = None
                    print("\nDeslogado com sucesso.")
                else: print("Opção inválida!")
            input("\nPressione Enter para continuar...")

# --- INICIA O PROGRAMA ---
if __name__ == "__main__":
    carregarDados()
    main()
