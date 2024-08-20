import rpyc
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import threading
import time

class FileClient(rpyc.Service):
    def __init__(self, server_host):
        self.conn = rpyc.connect(server_host, 18812)
        self.root = tk.Tk()
        self.root.title("Cliente de Arquivos")
        self.create_ui()

        # Inicia uma thread em segundo plano para escutar notificações
        self.notification_thread = threading.Thread(target=self.listen_for_notifications)
        self.notification_thread.daemon = True
        self.notification_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def create_ui(self):
        self.upload_button = tk.Button(self.root, text="Enviar Arquivo", command=self.upload_file_prompt)
        self.upload_button.pack(pady=5)

        self.list_button = tk.Button(self.root, text="Listar Arquivos", command=self.list_files)
        self.list_button.pack(pady=5)

        self.download_button = tk.Button(self.root, text="Baixar Arquivo", command=self.download_file_prompt)
        self.download_button.pack(pady=5)

        self.register_button = tk.Button(self.root, text="Registrar Interesse", command=self.register_interest_prompt)
        self.register_button.pack(pady=5)

        self.cancel_button = tk.Button(self.root, text="Cancelar Interesse", command=self.cancel_interest_prompt)
        self.cancel_button.pack(pady=5)

    def upload_file_prompt(self):
        file_path = filedialog.askopenfilename(title="Selecione o arquivo para envio")
        if file_path:
            with open(file_path, 'rb') as file:
                content = file.read()
                filename = file_path.split('/')[-1]
                self.upload_file(filename, content)

    def download_file_prompt(self):
        filename = simpledialog.askstring("Baixar Arquivo", "Digite o nome do arquivo para baixar:")
        if filename:
            self.download_file(filename)

    def register_interest_prompt(self):
        filename = simpledialog.askstring("Registrar Interesse", "Digite o nome do arquivo para registrar interesse:")
        if filename:
            self.register_interest(filename, 3600)

    def cancel_interest_prompt(self):
        filename = simpledialog.askstring("Cancelar Interesse", "Digite o nome do arquivo para cancelar interesse:")
        if filename:
            self.cancel_interest(filename)

    def upload_file(self, filename, content):
        response = self.conn.root.upload_file(filename, content)
        self.show_message("Enviar Arquivo", response)

    def list_files(self):
        files = self.conn.root.list_files()
        files_list = "\n".join(files)
        self.show_message("Lista de Arquivos", f"Arquivos disponíveis:\n{files_list}")

    def download_file(self, filename):
        content = self.conn.root.download_file(filename)
        if content != "Arquivo não encontrado":
            save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Todos os Arquivos", "*.*")])
            if save_path:
                with open(save_path, 'wb') as file:
                    file.write(content)
                self.show_message("Baixar Arquivo", f"{filename} baixado com sucesso.")
        else:
            self.show_message("Baixar Arquivo", content)

    def register_interest(self, filename, validity_period):
        response = self.conn.root.register_interest(filename, self, validity_period)
        self.show_message("Registrar Interesse", response)

    def cancel_interest(self, filename):
        response = self.conn.root.cancel_interest(filename, self)
        self.show_message("Cancelar Interesse", response)

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def notify_file_available(self, filename):
        # Atualiza a GUI para mostrar que o arquivo está disponível
        self.root.after(0, lambda: self.show_message("Notificação", f"Arquivo '{filename}' está disponível agora!"))

    def listen_for_notifications(self):
        while True:
            try:
                # Simulando a verificação periódica de notificações.
                # Implemente a lógica real de escuta de notificações aqui.
                time.sleep(1)
            except Exception as e:
                print(f"Erro na thread de notificações: {e}")
                break

    def on_closing(self):
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    client = FileClient("localhost")
