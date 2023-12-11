import grpc
import sala_pb2
import sala_pb2_grpc

def registro_entrada(stub, identificador):
    response = stub.registra_entrada(sala_pb2.RegistroEntradaRequest(id=identificador))
    if response.numero_programas == -1:
        print("Já existe um programa de envio com esse identificador.")
    else:
        print(f"Registrado com sucesso. Número de programas de envio: {response.numero_programas}")

def registro_saida(stub, identificador, fqdn, porto):
    response = stub.registra_saida(sala_pb2.RegistroSaidaRequest(id=identificador, fqdn=fqdn, port=porto))
    if response.numero_programas == -1:
        print("Já existe um programa exibidor com esse identificador.")
    else:
        print(f"Registrado com sucesso. Número de programas exibidores: {response.numero_programas}")

def lista_programas(stub):
    response = stub.lista(sala_pb2.ListaRequest())
    print("Programas registrados:")
    for programa in response.programas:
        print(programa)

def finaliza_registro(stub, identificador):
    response = stub.finaliza_registro(sala_pb2.FinalizaRegistroRequest(id=identificador))
    if response.terminado:
        print("Registro finalizado com sucesso.")
    else:
        print("Não foi possível finalizar o registro.")

def termina_servidor(stub):
    stub.termina(sala_pb2.TerminaRequest())

def envia_mensagem(stub, mensagem, destino):
    response = stub.envia(sala_pb2.EnviaRequest(msg=mensagem, destino=destino))
    print(f"A mensagem foi enviada {response.vezes_enviada} vezes.")

def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = sala_pb2_grpc.ChatRoomStub(channel)

    while True:
        print("\nEscolha uma opção:")
        print("1. Registrar entrada")
        print("2. Registrar saída")
        print("3. Lista programas registrados")
        print("4. Finalizar registro")
        print("5. Terminar servidor")
        print("6. Enviar mensagem")
        print("7. Sair")

        opcao = input("Opção: ")

        if opcao == '1':
            identificador = input("Identificador: ")
            registro_entrada(stub, identificador)
        elif opcao == '2':
            identificador = input("Identificador: ")
            fqdn = input("FQDN: ")
            porto = int(input("Porto: "))
            registro_saida(stub, identificador, fqdn, porto)
        elif opcao == '3':
            lista_programas(stub)
        elif opcao == '4':
            identificador = input("Identificador: ")
            finaliza_registro(stub, identificador)
        elif opcao == '5':
            termina_servidor(stub)
            break
        elif opcao == '6':
            mensagem = input("Mensagem: ")
            destino = input("Destino ('todos' para todos os exibidores): ")
            envia_mensagem(stub, mensagem, destino)
        elif opcao == '7':
            break
        else:
            print("Opção inválida.")

if __name__ == '__main__':
    main()
