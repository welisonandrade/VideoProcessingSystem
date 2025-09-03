import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import os
import webbrowser

# --- Configurações ---
# ATENÇÃO: Altere para o IP da máquina onde o servidor está rodando!
SERVER_URL = "http://127.0.0.1:5000"


class VideoClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente de Processamento de Vídeo")
        self.root.geometry("800x600")

        self.filepath = None
        self.video_history = []

        # --- Frame Principal ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Seção de Upload ---
        upload_frame = ttk.LabelFrame(main_frame, text="Enviar Novo Vídeo", padding="10")
        upload_frame.pack(fill=tk.X, pady=5)

        self.select_button = ttk.Button(upload_frame, text="Selecionar Vídeo", command=self.select_file)
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.selected_file_label = ttk.Label(upload_frame, text="Nenhum arquivo selecionado")
        self.selected_file_label.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.filter_var = tk.StringVar(value='grayscale')
        self.filter_menu = ttk.OptionMenu(upload_frame, self.filter_var, 'grayscale', 'grayscale', 'pixelate',
                                          'edge_detection')
        self.filter_menu.pack(side=tk.LEFT, padx=5)

        self.upload_button = ttk.Button(upload_frame, text="Enviar", command=self.upload_video)
        self.upload_button.pack(side=tk.LEFT, padx=5)
        self.upload_button['state'] = 'disabled'

        # --- Seção de Histórico ---
        history_frame = ttk.LabelFrame(main_frame, text="Histórico de Vídeos", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        cols = ('Nome Original', 'Filtro', 'Data')
        self.history_tree = ttk.Treeview(history_frame, columns=cols, show='headings')
        for col in cols:
            self.history_tree.heading(col, text=col)
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botões de ação do histórico
        action_frame = ttk.Frame(history_frame)
        action_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Button(action_frame, text="Ver Original", command=lambda: self.play_video('original')).pack(pady=5)
        ttk.Button(action_frame, text="Ver Processado", command=lambda: self.play_video('processed')).pack(pady=5)
        ttk.Button(action_frame, text="Atualizar Histórico", command=self.refresh_history).pack(pady=20)

        # --- Inicialização ---
        self.refresh_history()

    def select_file(self):
        self.filepath = filedialog.askopenfilename(
            title="Selecione um arquivo de vídeo",
            filetypes=(("Arquivos de Vídeo", "*.mp4 *.avi *.mov *.mkv"), ("Todos os arquivos", "*.*"))
        )
        if self.filepath:
            self.selected_file_label.config(text=os.path.basename(self.filepath))
            self.upload_button['state'] = 'normal'
        else:
            self.selected_file_label.config(text="Nenhum arquivo selecionado")
            self.upload_button['state'] = 'disabled'

    def upload_video(self):
        if not self.filepath:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado para upload.")
            return

        url = f"{SERVER_URL}/upload"
        filter_choice = self.filter_var.get()

        try:
            with open(self.filepath, 'rb') as f:
                files = {'file': (os.path.basename(self.filepath), f)}
                data = {'filter': filter_choice}

                # Exibe uma mensagem de "enviando"
                self.selected_file_label.config(text=f"Enviando para o servidor...")
                self.root.update_idletasks()

                response = requests.post(url, files=files, data=data, timeout=300)  # Timeout de 5 minutos

                if response.status_code == 201:
                    messagebox.showinfo("Sucesso", "Vídeo enviado e processado com sucesso!")
                    self.refresh_history()
                else:
                    messagebox.showerror("Erro no Servidor",
                                         f"Erro: {response.status_code}\n{response.json().get('error', '')}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao servidor: {e}")
        finally:
            self.selected_file_label.config(text="Selecione um novo arquivo")
            self.filepath = None
            self.upload_button['state'] = 'disabled'

    def refresh_history(self):
        try:
            response = requests.get(f"{SERVER_URL}/videos")
            if response.status_code == 200:
                self.video_history = response.json()
                self.update_history_tree()
            else:
                messagebox.showwarning("Aviso", "Não foi possível carregar o histórico do servidor.")
        except requests.exceptions.RequestException:
            messagebox.showwarning("Aviso", "Servidor offline. Não foi possível carregar o histórico.")

    def update_history_tree(self):
        # Limpa a árvore
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)
        # Preenche com novos dados
        for video in self.video_history:
            self.history_tree.insert("", "end", iid=video['id'], values=(
                video['original_name'],
                video['filter'],
                video['created_at'][:19].replace('T', ' ')
            ))

    def play_video(self, video_type):
        selected_item = self.history_tree.focus()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um vídeo na lista primeiro.")
            return

        video_id = selected_item
        video_data = next((v for v in self.video_history if v['id'] == video_id), None)

        if video_data:
            if video_type == 'original':
                path = video_data['path_original']
            else:
                path = video_data['path_processed']

            video_url = f"{SERVER_URL}/media/{path}"
            webbrowser.open(video_url)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoClientApp(root)
    root.mainloop()