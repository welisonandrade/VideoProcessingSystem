import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import threading
import webbrowser
import os

SERVER_URL = "http://127.0.0.1:5000"  # Mude se o servidor estiver em outro IP


class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente de Processamento de Vídeo")
        self.root.geometry("900x600")
        self.selected_filepath = None

        # --- Frames ---
        upload_frame = ttk.LabelFrame(root, text="1. Enviar Novo Vídeo", padding=10)
        upload_frame.pack(fill=tk.X, padx=10, pady=5)

        history_frame = ttk.LabelFrame(root, text="2. Histórico de Vídeos", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Seção de Upload ---
        self.select_btn = ttk.Button(upload_frame, text="Selecionar Arquivo...", command=self.select_file)
        self.select_btn.grid(row=0, column=0, padx=5, pady=5)

        self.file_label = ttk.Label(upload_frame, text="Nenhum arquivo selecionado")
        self.file_label.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(upload_frame, text="Filtro:").grid(row=0, column=2, padx=5)
        self.filter_var = tk.StringVar(value='grayscale')
        self.filter_combo = ttk.Combobox(upload_frame, textvariable=self.filter_var,
                                         values=['grayscale', 'pixelate', 'canny_edges'])
        self.filter_combo.grid(row=0, column=3, padx=5)

        self.upload_btn = ttk.Button(upload_frame, text="Enviar Vídeo", command=self.start_upload_thread,
                                     state="disabled")
        self.upload_btn.grid(row=0, column=4, padx=5)

        upload_frame.grid_columnconfigure(1, weight=1)
        self.progress = ttk.Progressbar(upload_frame, orient="horizontal", mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=5, sticky="ew", padx=5, pady=5)

        # --- Seção de Histórico ---
        cols = ('Nome Original', 'Filtro', 'Data', 'Duração (s)')
        self.history_tree = ttk.Treeview(history_frame, columns=cols, show='headings')
        for col in cols:
            self.history_tree.heading(col, text=col)
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        action_frame = ttk.Frame(history_frame)
        action_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Button(action_frame, text="Ver Original", command=lambda: self.view_video('original')).pack(pady=5)
        ttk.Button(action_frame, text="Ver Processado", command=lambda: self.view_video('processed')).pack(pady=5)
        ttk.Button(action_frame, text="Atualizar Histórico", command=self.refresh_history).pack(pady=20)

        # Armazenar dados completos dos vídeos
        self.video_data = {}

        self.refresh_history()

    def select_file(self):
        self.selected_filepath = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if self.selected_filepath:
            self.file_label.config(text=os.path.basename(self.selected_filepath))
            self.upload_btn.config(state="normal")
        else:
            self.file_label.config(text="Nenhum arquivo selecionado")
            self.upload_btn.config(state="disabled")

    def start_upload_thread(self):
        self.progress.start(10)  # Modo indeterminado
        self.upload_btn.config(state="disabled")
        self.select_btn.config(state="disabled")

        upload_thread = threading.Thread(target=self.upload_video, daemon=True)
        upload_thread.start()

    def upload_video(self):
        if not self.selected_filepath:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
            return

        url = f"{SERVER_URL}/upload"
        filter_choice = self.filter_var.get()

        try:
            with open(self.selected_filepath, 'rb') as f:
                files = {'video': (os.path.basename(self.selected_filepath), f)}
                data = {'filter': filter_choice}
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
            self.progress.stop()
            self.progress['value'] = 0
            self.upload_btn.config(state="normal")
            self.select_btn.config(state="normal")

    def refresh_history(self):
        try:
            response = requests.get(f"{SERVER_URL}/history")
            if response.status_code == 200:
                history_data = response.json()
                self.history_tree.delete(*self.history_tree.get_children())
                self.video_data.clear()

                for item in history_data:
                    video_id = item['id']
                    self.video_data[video_id] = item  # Armazena dados completos

                    display_data = (
                        item['original_name'] + item['original_ext'],
                        item['filter'],
                        item['created_at'][:16].replace('T', ' '),
                        f"{item['duration_sec']:.2f}"
                    )
                    self.history_tree.insert('', tk.END, iid=video_id, values=display_data)
            else:
                messagebox.showwarning("Aviso", "Não foi possível carregar o histórico do servidor.")
        except requests.exceptions.RequestException:
            messagebox.showwarning("Aviso", "Servidor offline. Não foi possível carregar o histórico.")

    def view_video(self, video_type):
        selected_items = self.history_tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione um vídeo no histórico.")
            return

        video_id = selected_items[0]
        video_info = self.video_data.get(video_id)

        if video_type == 'original':
            path_key = 'path_original'
        else:
            path_key = 'path_processed'

        video_path = video_info.get(path_key)
        if video_path:
            url = f"{SERVER_URL}/media/{video_path}"
            webbrowser.open(url)
        else:
            messagebox.showerror("Erro", "Caminho do vídeo não encontrado.")


if __name__ == '__main__':
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()