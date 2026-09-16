import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
import subprocess
import threading
import sys
import shutil

def resource_path(relative_path):
    """ PyInstaller 단일 실행 파일을 위한 절대 경로 반환 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MINDWAVE Demo 한글패치 프로그램")
        self.root.geometry("700x620")
        self.root.configure(bg="#f0f2f5")
        self.root.resizable(False, False)

        self.setup_styles()
        self.create_widgets()
        self.log("패치 프로그램을 실행했습니다.\n'자동 감지' 버튼을 클릭하거나 게임 경로를 직접 선택해주세요.")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#f0f2f5")
        style.configure("TLabel", background="#f0f2f5", font=("Malgun Gothic", 10))
        style.configure("Title.TLabel", font=("Malgun Gothic", 24, "bold"), foreground="#2c3e50")
        style.configure("Sub.TLabel", font=("Malgun Gothic", 10), foreground="#7f8c8d")
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("Credit.TLabel", font=("Malgun Gothic", 9), foreground="#7f8c8d")
        style.configure("Version.TLabel", font=("Malgun Gothic", 8), foreground="#aab0b7")
        style.configure("green.Horizontal.TProgressbar", troughcolor="#e0e0e0", background="#4CAF50", thickness=18)

    def create_widgets(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", pady=(30, 20))
        
        ttk.Label(header_frame, text="MINDWAVE Demo", style="Title.TLabel").pack(anchor="center")
        ttk.Label(header_frame, text="한글패치 프로그램", style="Sub.TLabel").pack(anchor="center", pady=(5, 0))
        ttk.Label(header_frame, text="번역 : Pancat_Silly, geminican | 검수 : Pancat_Silly", style="Credit.TLabel").pack(anchor="center", pady=(4, 0))
        ttk.Label(header_frame, text="스프라이트 번역 : Pancat_Silly | 프로그래밍 : Pancat_Silly", style="Credit.TLabel").pack(anchor="center", pady=(2, 0))

        path_frame = tk.Frame(self.root, bg="white", highlightbackground="#d1d5db", highlightthickness=1, padx=20, pady=20)
        path_frame.pack(fill="x", padx=30, pady=10)

        ttk.Label(path_frame, text="게임 경로", background="white", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(0, 10))

        self.path_var = tk.StringVar()
        entry_frame = tk.Frame(path_frame, bg="white")
        entry_frame.pack(fill="x", pady=(0, 10))
        
        path_entry = ttk.Entry(entry_frame, textvariable=self.path_var, font=("Malgun Gothic", 10))
        path_entry.pack(fill="x", ipady=5)

        btn_frame = tk.Frame(path_frame, bg="white")
        btn_frame.pack(fill="x", pady=(5, 0))

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

        ttk.Button(btn_frame, text="자동 감지", command=self.auto_detect).grid(row=0, column=0, sticky="ew", padx=(0, 3))
        ttk.Button(btn_frame, text="찾아보기", command=self.browse_folder).grid(row=0, column=1, sticky="ew", padx=3)
        start_btn = tk.Button(btn_frame, text="설치 시작", font=("Malgun Gothic", 10, "bold"),
                              bg="#4CAF50", fg="white", activebackground="#45a049", activeforeground="white",
                              relief="flat", cursor="hand2", command=self.start_patch_thread)
        start_btn.grid(row=0, column=2, sticky="ew", padx=(3, 0), ipady=3)

        # 진행바 프레임
        progress_frame = tk.Frame(self.root, bg="white", highlightbackground="#d1d5db", highlightthickness=1, padx=20, pady=14)
        progress_frame.pack(fill="x", padx=30, pady=(0, 10))

        ttk.Label(progress_frame, text="설치 진행", background="white", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(0, 8))
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style="green.Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x")
        self.progress_label = ttk.Label(progress_frame, text="0%", background="white", font=("Malgun Gothic", 9), foreground="#7f8c8d")
        self.progress_label.pack(anchor="e", pady=(4, 0))

        log_frame = tk.Frame(self.root, bg="white", highlightbackground="#d1d5db", highlightthickness=1, padx=20, pady=20)
        log_frame.pack(fill="both", expand=True, padx=30, pady=(0, 5))

        ttk.Label(log_frame, text="설치 로그", background="white", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", font=("Consolas", 9), height=8, borderwidth=0, bg="#fafafa")
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled")

        # 버전 표기 (우측 하단)
        version_frame = tk.Frame(self.root, bg="#f0f2f5")
        version_frame.pack(fill="x", padx=30, pady=(0, 8))
        ttk.Label(version_frame, text="MINDWAVE Demo v1.0.3 한글패치 v1.0.5.2", style="Version.TLabel").pack(anchor="e")

    # ──────────────────────────────────────────────
    # 로그 출력
    # ──────────────────────────────────────────────
    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ──────────────────────────────────────────────
    # 공통 오류 창 (스레드 안전: root.after 로 호출)
    # ──────────────────────────────────────────────
    def _show_error(self, title, message):
        """메인 스레드에서 모달 오류 창을 띄운다."""
        error_win = tk.Toplevel(self.root)
        error_win.title(title)
        error_win.geometry("380x150")
        error_win.resizable(False, False)
        error_win.configure(bg="white")
        error_win.grab_set()

        tk.Label(
            error_win,
            text=f"⚠  {title}",
            font=("Malgun Gothic", 12, "bold"),
            fg="#c0392b",
            bg="white"
        ).pack(pady=(22, 6))

        tk.Label(
            error_win,
            text=message,
            font=("Malgun Gothic", 10),
            fg="#2c3e50",
            bg="white",
            wraplength=340,
            justify="center"
        ).pack(pady=(0, 16))

        tk.Button(
            error_win,
            text="확인",
            font=("Malgun Gothic", 10, "bold"),
            bg="#4CAF50", fg="white",
            activebackground="#45a049", activeforeground="white",
            relief="flat", cursor="hand2", width=10,
            command=error_win.destroy
        ).pack()

    def show_error(self, title, message):
        """스레드에서 호출해도 안전한 래퍼."""
        self.root.after(0, self._show_error, title, message)

    # ──────────────────────────────────────────────
    # 경로 관련
    # ──────────────────────────────────────────────
    def auto_detect(self):
        target_paths = [r"C:\Program Files (x86)\Steam\steamapps\common\MINDWAVE Demo",r"C:\Program Files\Steam\steamapps\common\MINDWAVE Demo",r"D:\Program Files (x86)\Steam\steamapps\common\MINDWAVE Demo",r"C:\SteamLibrary\steamapps\MINDWAVE Demo",r"D:\SteamLibrary\steamapps\MINDWAVE Demo",r"E:\SteamLibrary\steamapps\MINDWAVE Demo"]
        for target_path in target_paths:
            if os.path.exists(target_path):
                self.path_var.set(target_path)
                self.log("자동 감지: 경로를 찾았습니다.")
                return
        
        self.log("자동 감지 실패: 해당 경로에 폴더가 존재하지 않습니다.")

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(title="게임이 설치된 폴더를 선택하세요")
        if folder_selected:
            self.path_var.set(folder_selected)
            self.log(f"경로 선택됨: {folder_selected}")

    # ──────────────────────────────────────────────
    # 패치 실행
    # ──────────────────────────────────────────────
    def start_patch_thread(self):
        target_dir = self.path_var.get().strip()
        if not target_dir:
            self.log("오류: 게임 경로를 먼저 지정해주세요.")
            self.show_error("경로 오류", "게임 경로를 먼저 지정해주세요.")
            return
        
        threading.Thread(target=self.run_patch, args=(target_dir,), daemon=True).start()

    def set_progress(self, value):
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}%")
        self.root.update_idletasks()

    def run_patch(self, target_dir):
        self.set_progress(0)

        # data.win 존재 확인
        data_file = os.path.join(target_dir, "data.win")
        if not os.path.exists(data_file):
            msg = f"지정된 경로에 'data.win' 파일이 없습니다.\n({data_file})"
            self.log(f"오류: {msg}")
            self.show_error("파일 오류", msg)
            return

        # .xdelta 패치 파일 탐색
        base_dir = resource_path("")
        patch_file = None
        for file in os.listdir(base_dir):
            if file.endswith(".xdelta"):
                patch_file = os.path.join(base_dir, file)
                break

        if not patch_file:
            msg = "패치 파일(.xdelta)을 찾을 수 없습니다."
            self.log(f"오류: {msg}")
            self.show_error("패치 파일 오류", msg)
            return

        # xdelta3.exe 존재 확인
        xdelta_exe = resource_path("xdelta3.exe")
        if not os.path.exists(xdelta_exe):
            msg = "'xdelta3.exe' 파일이 없습니다."
            self.log(f"오류: {msg}")
            self.show_error("실행 파일 오류", msg)
            return

        output_file = os.path.join(target_dir, "data_patched.win")
        backup_file = os.path.join(target_dir, "data.win.bak")

        self.set_progress(10)
        self.log("data.win 델타 패치를 진행 중입니다...")
        command = [xdelta_exe, "-d", "-s", data_file, patch_file, output_file]
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(command, capture_output=True, text=True, startupinfo=startupinfo)
            
            if result.returncode == 0:
                self.set_progress(60)
                self.log("델타 패치 적용 완료!")
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                os.rename(data_file, backup_file)
                os.rename(output_file, data_file)
            else:
                self.log(f"오류 발생: 델타 패치 적용 실패\n{result.stderr}")
                self.show_error(
                    "델타 패치 적용 실패!",
                    "MINDWAVE Demo의 버전이 1.0.3인지 확인해주세요."
                )
                return

            # loc, scripts 폴더 복사
            folders = [f for f in ["loc", "scripts"] if os.path.exists(resource_path(f))]
            total = len(folders)
            for i, folder in enumerate(["loc", "scripts"]):
                src_folder = resource_path(folder)
                dst_folder = os.path.join(target_dir, folder)
                
                if os.path.exists(src_folder):
                    self.log(f"'{folder}' 폴더를 적용하는 중...")
                    shutil.copytree(src_folder, dst_folder, dirs_exist_ok=True)
                    self.log(f"'{folder}' 폴더 적용 완료!")
                    self.set_progress(60 + (i + 1) * (35 // max(total, 1)))
                else:
                    self.log(f"참고: 패치 파일에 '{folder}' 폴더가 없어 건너뜁니다.")

            self.set_progress(100)
            self.log("===============================")
            self.log("한글패치 설치가 모두 완료되었습니다!")
            self.log("===============================")
                
        except Exception as e:
            msg = str(e)
            self.log(f"예기치 않은 오류 발생: {msg}")
            self.show_error("예기치 않은 오류", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = PatcherApp(root)
    root.mainloop()
