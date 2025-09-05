import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import threading
import webbrowser
import os
import cv2  # Importado para o player
from PIL import Image, ImageTk  # Importado para o player

SERVER_URL = "http://127.0.0.1:5000"


class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente de Processamento de Vídeo")
        self.root.geometry("900x650")  # Aumentei um pouco a altura para a barra de status
        self.selected_filepath = None
        self.stop_playback = False  # Flag para parar o player de vídeo

        # --- Frames ---
        upload_frame = ttk.LabelFrame(root, text="1. Enviar Novo Vídeo", padding=10)
        upload_frame.pack(fill=tk.X, padx=10, pady=5)

        history_frame = ttk.LabelFrame(root, text="2. Histórico de Vídeos", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        status_frame = ttk.Frame(root, padding=(10, 5))
        status_frame.pack(fill=tk.X)

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

        # --- BOTÕES DE AÇÃO MODIFICADOS E NOVOS ---
        ttk.Button(action_frame, text="▶ Ver Original", command=lambda: self.play_video_in_app('original')).pack(pady=5,
                                                                                                                 fill=tk.X)
        ttk.Button(action_frame, text="▶ Ver Processado", command=lambda: self.play_video_in_app('processed')).pack(
            pady=5, fill=tk.X)
        ttk.Button(action_frame, text="⤓ Baixar Processado", command=self.start_download_thread).pack(pady=5, fill=tk.X)
        ttk.Button(action_frame, text="↻ Atualizar Histórico", command=self.refresh_history).pack(pady=20, fill=tk.X)

        # --- BARRA DE STATUS ---
        self.status_label = ttk.Label(status_frame, text="Pronto.", anchor="w")
        self.status_label.pack(fill=tk.X)

        self.video_data = {}
        self.refresh_history()

    def select_file(self):
        # (Esta função permanece igual)
        self.selected_filepath = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if self.selected_filepath:
            self.file_label.config(text=os.path.basename(self.selected_filepath))
            self.upload_btn.config(state="normal")
        else:
            self.file_label.config(text="Nenhum arquivo selecionado")
            self.upload_btn.config(state="disabled")

    def start_upload_thread(self):
        # (Esta função permanece igual)
        self.status_label.config(text="Enviando vídeo...")
        self.progress.start(10)
        self.upload_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
        upload_thread = threading.Thread(target=self.upload_video, daemon=True)
        upload_thread.start()

    def upload_video(self):
        # (Esta função permanece igual)
        if not self.selected_filepath:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
            return
        url = f"{SERVER_URL}/upload"
        filter_choice = self.filter_var.get()
        try:
            with open(self.selected_filepath, 'rb') as f:
                files = {'video': (os.path.basename(self.selected_filepath), f)}
                data = {'filter': filter_choice}
                response = requests.post(url, files=files, data=data, timeout=300)
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
            self.status_label.config(text="Pronto.")

    def refresh_history(self):
        # (Esta função permanece igual)
        try:
            response = requests.get(f"{SERVER_URL}/history")
            if response.status_code == 200:
                history_data = response.json()
                self.history_tree.delete(*self.history_tree.get_children())
                self.video_data.clear()
                for item in history_data:
                    video_id = item['id']
                    self.video_data[video_id] = item
                    display_data = (
                        item['original_name'] + item['original_ext'],
                        item['filter'],
                        item['created_at'][:16].replace('T', ' '),
                        f"{item['duration_sec']:.2f}"
                    )
                    self.history_tree.insert('', tk.END, iid=video_id, values=display_data)
            else:
                self.status_label.config(text="Erro ao carregar histórico do servidor.")
        except requests.exceptions.RequestException:
            self.status_label.config(text="Servidor offline. Não foi possível carregar o histórico.")

    # --- NOVA FUNÇÃO DE DOWNLOAD ---
    def start_download_thread(self):
        selected_items = self.history_tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione um vídeo no histórico para baixar.")
            return

        video_id = selected_items[0]
        video_info = self.video_data.get(video_id)
        video_path = video_info.get('path_processed')

        if not video_path:
            messagebox.showerror("Erro", "Caminho do vídeo processado não encontrado.")
            return

        url = f"{SERVER_URL}/media/{video_path}"
        original_filename = os.path.basename(video_path)

        save_path = filedialog.asksaveasfilename(
            initialfile=original_filename,
            defaultextension=os.path.splitext(original_filename)[1],
            filetypes=[("Video Files", f"*{os.path.splitext(original_filename)[1]}"), ("All files", "*.*")]
        )

        if not save_path:
            return  # Usuário cancelou

        self.status_label.config(text=f"Baixando '{original_filename}'...")
        self.progress['mode'] = 'determinate'

        download_thread = threading.Thread(target=self._download_file, args=(url, save_path), daemon=True)
        download_thread.start()

    def _download_file(self, url, save_path):
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                self.progress['maximum'] = total_size
                self.progress['value'] = 0

                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        self.progress['value'] += len(chunk)

            self.status_label.config(text="Download concluído!")
            messagebox.showinfo("Sucesso", f"Vídeo salvo em:\n{save_path}")
        except Exception as e:
            self.status_label.config(text="Erro no download.")
            messagebox.showerror("Erro de Download", f"Falha ao baixar o vídeo: {e}")
        finally:
            self.progress['value'] = 0
            self.progress['mode'] = 'determinate'  # Reset

    # --- NOVO PLAYER DE VÍDEO INTEGRADO ---
    def on_player_close(self, player_window):
        self.stop_playback = True
        player_window.destroy()

    def play_video_in_app(self, video_type):
        selected_items = self.history_tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione um vídeo no histórico para reproduzir.")
            return

        video_id = selected_items[0]
        video_info = self.video_data.get(video_id)
        path_key = 'path_original' if video_type == 'original' else 'path_processed'
        video_path = video_info.get(path_key)

        if not video_path:
            messagebox.showerror("Erro", "Caminho do vídeo não encontrado.")
            return

        url = f"{SERVER_URL}/media/{video_path}"

        player_window = tk.Toplevel(self.root)
        player_window.title(f"Reproduzindo: {os.path.basename(video_path)}")

        video_label = tk.Label(player_window)
        video_label.pack()

        self.stop_playback = False
        player_window.protocol("WM_DELETE_WINDOW", lambda: self.on_player_close(player_window))

        player_thread = threading.Thread(target=self._video_loop, args=(video_label, url), daemon=True)
        player_thread.start()

    def _video_loop(self, label, url):
        try:
            cap = cv2.VideoCapture(url)
            fps = cap.get(cv2.CAP_PROP_FPS)
            delay = int(1000 / fps) if fps > 0 else 33  # Fallback para ~30 FPS

            while not self.stop_playback:
                ret, frame = cap.read()
                if not ret:
                    break  # Fim do vídeo

                # Converte o frame para um formato que o Tkinter possa usar
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)

                # Atualiza a imagem na GUI
                label.imgtk = imgtk
                label.configure(image=imgtk)

                # Aguarda o tempo correto para o próximo frame
                self.root.after(delay)

        except Exception as e:
            print(f"Erro ao reproduzir o vídeo: {e}")
        finally:
            cap.release()


if __name__ == '__main__':
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()