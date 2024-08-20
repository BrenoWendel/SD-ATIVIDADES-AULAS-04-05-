import os
import rpyc
from rpyc.utils.server import ThreadedServer
from collections import defaultdict

class FileServerService(rpyc.Service):
    def __init__(self):
        self.file_dir = "./uploads"
        os.makedirs(self.file_dir, exist_ok=True)
        self.interests = defaultdict(list)  # Para armazenar interesses dos clientes

    def exposed_upload_file(self, filename, content):
        """Faz upload de um arquivo para o servidor"""
        file_path = os.path.join(self.file_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        self.check_interests(filename)  # Checa se algum cliente estava interessado nesse arquivo
        return "Arquivo enviado"

    def exposed_list_files(self):
        """Lista os arquivos disponíveis no servidor"""
        return os.listdir(self.file_dir)

    def exposed_download_file(self, filename):
        """Permite que o cliente faça download de um arquivo"""
        file_path = os.path.join(self.file_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read()
        else:
            return "Arquivo não encontrado"

    def exposed_register_interest(self, filename, client_reference, validity_period):
        """Registra o interesse do cliente em um arquivo não disponível"""
        if filename not in os.listdir(self.file_dir):
            self.interests[filename].append((client_reference, validity_period))
            return "Interesse registrado"
        else:
            return "O arquivo já está disponível"

    def exposed_cancel_interest(self, filename, client_reference):
        """Cancela o registro de interesse do cliente em um arquivo"""
        if filename in self.interests:
            self.interests[filename] = [
                (ref, time) for ref, time in self.interests[filename]
                if ref != client_reference
            ]
            return "interesse cacelado"
        return "Nenhum interesse registrado"

    def check_interests(self, filename):
        """Verifica se algum cliente estava interessado no arquivo e envia notificação"""
        if filename in self.interests:
            for client_ref, validity in self.interests[filename]:
                try:
                    client_ref.notify_file_available(filename)
                except Exception as e:
                    print(f"Erro ao notificar o cliente: {e}")
            del self.interests[filename]  # Remove a lista de interesses para o arquivo agora disponível

class FileServer:
    def start(self):
        server = ThreadedServer(FileServerService(), port=18812)
        server.start()

if __name__ == "__main__":
    server = FileServer()
    server.start()
    
