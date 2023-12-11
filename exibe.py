import grpc
import exibe_pb2
import exibe_pb2_grpc
import time
import socket
from concurrent import futures  # Importa o ThreadPoolExecutor do módulo concurrent.futures

class DisplayServicer(exibe_pb2_grpc.DisplayServerServicer):
    def __init__(self):
        self.server_terminado = False

    def exibe(self, request, context):
        print(f"Mensagem de {request.origem}: {request.msg}")
        return exibe_pb2.ExibeResponse(status=0)

    def termina(self, request, context):
        print("Servidor de exibição encerrado.")
        self.server_terminado = True
        return exibe_pb2.TerminaResponse(status=0)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # Utiliza futures.ThreadPoolExecutor
    exibe_pb2_grpc.add_DisplayServerServicer_to_server(DisplayServicer(), server)
    server.add_insecure_port('[::]:50052')  # Define a porta apropriada
    server.start()

    try:
        while not DisplayServicer().server_terminado:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
