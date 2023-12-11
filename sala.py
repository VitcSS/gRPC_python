import grpc
from concurrent import futures
import sala_pb2
import sala_pb2_grpc

class ChatRoomServicer(sala_pb2_grpc.ChatRoomServicer):
    def __init__(self):
        self.registrados_entrada = {}
        self.registrados_saida = {}

    def registra_entrada(self, request, context):
        if request.id not in self.registrados_entrada:
            self.registrados_entrada[request.id] = True
            return sala_pb2.RegistroEntradaResponse(numero_programas=len(self.registrados_entrada))
        else:
            return sala_pb2.RegistroEntradaResponse(numero_programas=-1)

    def registra_saida(self, request, context):
        if request.id not in self.registrados_saida:
            self.registrados_saida[request.id] = {'fqdn': request.fqdn, 'port': request.port}
            return sala_pb2.RegistroSaidaResponse(numero_programas=len(self.registrados_saida))
        else:
            return sala_pb2.RegistroSaidaResponse(numero_programas=-1)

    def lista(self, request, context):
        programas_registrados = []
        for id, _ in self.registrados_entrada.items():
            programas_registrados.append(f"Entrada: {id}")
        for id, _ in self.registrados_saida.items():
            programas_registrados.append(f"Saida: {id}")
        return sala_pb2.ListaResponse(programas=programas_registrados)

    def finaliza_registro(self, request, context):
        if request.id in self.registrados_entrada:
            del self.registrados_entrada[request.id]
            if request.id in self.registrados_saida:
                del self.registrados_saida[request.id]
                return sala_pb2.FinalizaRegistroResponse(terminado=True)
            return sala_pb2.FinalizaRegistroResponse(terminado=False)

    def termina(self, request, context):
        for id, data in self.registrados_saida.items():
            # Encerra os exibidores
            with grpc.insecure_channel(f"{data['fqdn']}:{data['port']}") as channel:
                stub = sala_pb2_grpc.DisplayServerStub(channel)
                stub.termina(sala_pb2.TerminaRequest())
        # Encerra o servidor
        context.abort(grpc.StatusCode.OK, "Servidor terminado")

    def envia(self, request, context):
        if request.destino == "todos":
            for id, data in self.registrados_saida.items():
                with grpc.insecure_channel(f"{data['fqdn']}:{data['port']}") as channel:
                    stub = sala_pb2_grpc.DisplayServerStub(channel)
                    stub.exibe(sala_pb2.ExibeRequest(msg=request.msg, origem="Servidor"))
            return sala_pb2.EnviaResponse(vezes_enviada=len(self.registrados_saida))
        else:
            if request.destino in self.registrados_saida:
                data = self.registrados_saida[request.destino]
                with grpc.insecure_channel(f"{data['fqdn']}:{data['port']}") as channel:
                    stub = sala_pb2_grpc.DisplayServerStub(channel)
                    stub.exibe(sala_pb2.ExibeRequest(msg=request.msg, origem="Servidor"))
                return sala_pb2.EnviaResponse(vezes_enviada=1)
            else:
                return sala_pb2.EnviaResponse(vezes_enviada=0)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sala_pb2_grpc.add_ChatRoomServicer_to_server(ChatRoomServicer(), server)
    server.add_insecure_port('[::]:50051')  # Defina a porta apropriada
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
