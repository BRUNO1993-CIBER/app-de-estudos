import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
import time

from backend import StudyRepository, DB_NAME, SUBJECTS_LIST, POMODORO_DURATION_SECONDS

class StudyController:
    def __init__(self):
        self.repo = StudyRepository(DB_NAME)
        self.repo.ensure_daily_plan_exists(SUBJECTS_LIST)
        self.current_subject_data = None

    def load_active_subject(self):
        self.current_subject_data = self.repo.get_current_subject()
        return self.current_subject_data

    def complete_pomodoro(self):
        if not self.current_subject_data:
            return
        self.repo.record_cycle(self.current_subject_data['id'], POMODORO_DURATION_SECONDS)
        self.load_active_subject()

    def finish_subject_and_advance(self):
        if self.current_subject_data:
            self.repo.mark_as_finished(self.current_subject_data['id'])
            self.load_active_subject()

    def continue_same_subject(self):
        self.load_active_subject()

    def get_report_data(self):
        return self.repo.get_all_stats()

class StudyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Estudos Pro")
        self.root.withdraw()  
        
        w, h = 500, 550
        self._center_window(self.root, w, h)
        self.root.resizable(False, False)
        self.root.after(0, lambda: None)
        time.sleep(0.3)  
        self.root.deiconify()  
        self.controller = StudyController()
        
        self.timer_running = False
        self.time_left = POMODORO_DURATION_SECONDS
        self.timer_id = None

        self._setup_ui()
        self._refresh_view()

    def _center_window(self, window, width, height):
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def _format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def _format_duration(self, total_seconds):
        hours, remainder = divmod(total_seconds, 3600)
        mins, _ = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins} min"

    def _setup_ui(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        self.lbl_date = tk.Label(main_frame, text=f"Data: {date.today().strftime('%d/%m/%Y')}", font=("Arial", 10))
        self.lbl_date.pack(pady=(0, 10))

        tk.Label(main_frame, text="Matéria Atual", font=("Arial", 12, "bold"), fg="gray").pack()
        self.lbl_subject = tk.Label(main_frame, text="---", font=("Helvetica", 24, "bold"), fg="#333")
        self.lbl_subject.pack(pady=(0, 15))

        self.lbl_timer = tk.Label(main_frame, text=self._format_time(POMODORO_DURATION_SECONDS), 
                                  font=("Courier New", 48, "bold"), fg="#0055AA")
        self.lbl_timer.pack(pady=10)

        self.lbl_progress = tk.Label(main_frame, text="Ciclos: 0 / 4", font=("Arial", 12))
        self.lbl_progress.pack(pady=5)

        self.btn_action = tk.Button(main_frame, text="INICIAR POMODORO", 
                                    font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                                    command=self.toggle_timer, height=2, width=22,
                                    cursor="hand2")
        self.btn_action.pack(pady=20)

        secondary_frame = tk.Frame(main_frame)
        secondary_frame.pack(pady=10)

        btn_stats = tk.Button(secondary_frame, text="Ver Relatório de Tempos", 
                              command=self._show_stats_window,
                              bg="#607D8B", fg="white", font=("Arial", 10))
        btn_stats.pack(side="left", padx=5)

        self.lbl_status = tk.Label(main_frame, text="Aguardando início...", font=("Arial", 9, "italic"))
        self.lbl_status.pack(side="bottom", pady=10)

    def _refresh_view(self):
        data = self.controller.load_active_subject()
        
        if not data:
            self.lbl_subject.config(text="Tudo Concluído!", fg="green")
            self.lbl_timer.config(text="00:00")
            self.lbl_progress.config(text="-")
            self.btn_action.config(state="disabled", text="Dia Finalizado", bg="gray", cursor="arrow")
            self.lbl_status.config(text="Parabéns! Estudos de hoje finalizados.")
            return

        self.lbl_subject.config(text=data['name'], fg="#333")
        self.lbl_progress.config(text=f"Ciclos Completos: {data['cycles']}")
        
        if not self.timer_running:
            self.lbl_timer.config(text=self._format_time(POMODORO_DURATION_SECONDS))
            self.time_left = POMODORO_DURATION_SECONDS

    def toggle_timer(self):
        if self.timer_running:
            self._stop_timer()
            self.btn_action.config(text="RETOMAR")
            self.lbl_status.config(text="Pausado.")
        else:
            self.timer_running = True
            self.btn_action.config(text="PAUSAR", bg="#FF9800")
            self.lbl_status.config(text="Foco total! O tempo está rodando.")
            self._tick()

    def _stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def _tick(self):
        if not self.timer_running:
            return

        if self.time_left > 0:
            self.lbl_timer.config(text=self._format_time(self.time_left))
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self._tick)
        else:
            self._finish_cycle()

    def _finish_cycle(self):
        self._stop_timer()
        self.lbl_timer.config(text="00:00")
        self.controller.complete_pomodoro()
        self.root.bell()
        self._check_cycle_rules()

    def _check_cycle_rules(self):
        self._refresh_view()
        data = self.controller.current_subject_data
        
        if data and data['cycles'] >= 4:
            self._show_decision_dialog(data['name'])
        else:
            self.btn_action.config(text="INICIAR PRÓXIMO", bg="#4CAF50")
            self.lbl_status.config(text="Ciclo finalizado. Respire e continue.")

    def _show_decision_dialog(self, subject_name):
        dialog = tk.Toplevel(self.root)
        dialog.title("Decisão de Estudo")
        w, h = 400, 250
        self._center_window(dialog, w, h)
        dialog.transient(self.root) 
        dialog.grab_set()           
        dialog.resizable(False, False)

        tk.Label(dialog, text="Meta Atingida!", font=("Arial", 16, "bold"), fg="green").pack(pady=10)
        
        msg = (f"Você completou 4 ciclos (100 min) de {subject_name}.\n\n"
               "O que deseja fazer?")
        tk.Label(dialog, text=msg, font=("Arial", 11), wraplength=350, justify="center").pack(pady=10)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)

        def on_next():
            self.controller.finish_subject_and_advance()
            dialog.destroy()
            self.btn_action.config(text="INICIAR POMODORO", bg="#4CAF50")
            self._refresh_view()
            messagebox.showinfo("Nova Matéria", "A próxima matéria foi carregada.")

        def on_continue():
            self.controller.continue_same_subject()
            dialog.destroy()
            self.btn_action.config(text="MAIS UM CICLO", bg="#2196F3")
            self._refresh_view()

        tk.Button(btn_frame, text="Encerrar e Ir p/ Próxima", command=on_next, 
                  bg="#FF5722", fg="white", font=("Arial", 10, "bold"), width=20,
                  cursor="hand2").pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Continuar nesta Matéria", command=on_continue, 
                  bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=20,
                  cursor="hand2").pack(side="right", padx=10)

        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    def _show_stats_window(self):
        stats_win = tk.Toplevel(self.root)
        stats_win.withdraw()
        stats_win.title("Histórico e Tempos")
        self._center_window(stats_win, 700, 500)

        title = tk.Label(stats_win, text="Registro de Atividades", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        stats_win.deiconify()

        cols = ("Data", "Matéria", "Ciclos", "Tempo Total", "Status")
        tree = ttk.Treeview(stats_win, columns=cols, show='headings')
        
        tree.heading("Data", text="Data")
        tree.heading("Matéria", text="Matéria")
        tree.heading("Ciclos", text="Ciclos")
        tree.heading("Tempo Total", text="Tempo Total")
        tree.heading("Status", text="Status")

        tree.column("Data", width=80, anchor="center")
        tree.column("Matéria", width=120)
        tree.column("Ciclos", width=60, anchor="center")
        tree.column("Tempo Total", width=100, anchor="center")
        tree.column("Status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(stats_win, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both", padx=10, pady=5)

        records = self.controller.get_report_data()
        for row in records:
            formatted_time = self._format_duration(row[3])
            tree.insert("", "end", values=(row[0], row[1], row[2], formatted_time, row[4]))

        btn_close = tk.Button(stats_win, text="Fechar", command=stats_win.destroy, bg="#333", fg="white")
        btn_close.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyApp(root)
    root.mainloop()