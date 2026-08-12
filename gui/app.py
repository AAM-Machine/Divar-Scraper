import tkinter as tk
from tkinter import ttk, messagebox
import requests
import webbrowser
import subprocess
import threading
import sys
import os
import atexit


API_URL = "http://127.0.0.1:8000/ads/"
SCRAPER_SCRIPT_PATH = "scraper/scraper.py"
API_SCRIPT_NAME = "api.main:app"


# رابط کاربری گرافیکی دسکتاپ
class DivarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Divar Ad Finder")
        self.geometry("750x800")
        self.configure(bg="#f0f2f5")
        self.server_process = None
        self.start_server_thread()
        atexit.register(self.stop_server)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f2f5")
        style.configure("TLabel", background="#f0f2f5", font=("Arial", 11))
        style.configure("Title.TLabel", font=("Arial", 18, "bold"))
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        style.configure("Accent.TButton", background="#0078d4", foreground="white")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        self.placeholder_text = "شناسه آگهی را وارد کنید..."
        self.create_widgets()

    def start_server_thread(self):
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

    def start_server(self):
        try:
            command = [
                sys.executable,
                "-m",
                "uvicorn",
                API_SCRIPT_NAME,
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--log-level",
                "warning",
            ]
            self.server_process = subprocess.Popen(command)
        except Exception as e:
            messagebox.showerror("خطای سرور", f"اجرای سرور با خطا مواجه شد: {e}")
            self.destroy()

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()

    def on_closing(self):
        self.destroy()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=(0, 20))
        self.scrape_button = ttk.Button(
            actions_frame, text="استخراج آگهی جدید", command=self.run_scraper_thread
        )
        self.scrape_button.pack(side=tk.RIGHT, padx=(10, 0))
        list_button = ttk.Button(
            actions_frame, text="لیست آگهی‌ها", command=self.show_ad_list
        )
        list_button.pack(side=tk.RIGHT)
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        self.id_entry = ttk.Entry(
            search_frame, font=("Arial", 12), width=40, foreground="grey"
        )
        self.id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.id_entry.insert(0, self.placeholder_text)
        self.id_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.id_entry.bind("<FocusOut>", self.on_entry_focus_out)
        search_button = ttk.Button(
            search_frame, text="جستجو", style="Accent.TButton", command=self.search_ad
        )
        search_button.pack(side=tk.RIGHT, padx=(10, 0))
        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

    def run_scraper_thread(self):
        scroll_count = 1
        export_to_excel = True
        self.scrape_button.config(state="disabled", text="در حال استخراج...")
        thread = threading.Thread(
            target=self.run_scraper_script, args=(scroll_count, export_to_excel)
        )
        thread.start()

    def run_scraper_script(self, scroll_count, export_to_excel):
        try:
            command = [sys.executable, SCRAPER_SCRIPT_PATH, f"--pages={scroll_count}"]
            if export_to_excel:
                command.append("--excel")
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                env=env,
                encoding="utf-8",
                errors="ignore",
            )
            messagebox.showinfo("موفق", "استخراج آگهی‌های جدید با موفقیت انجام شد.")
        except FileNotFoundError:
            messagebox.showerror(
                "خطا", f"فایل اسکرپر در مسیر '{SCRAPER_SCRIPT_PATH}' یافت نشد."
            )
        except subprocess.CalledProcessError as e:
            error_message = f"اسکریپت استخراج با خطا مواجه شد:\n\n--- Log ---\n{e.stdout}\n{e.stderr}"
            messagebox.showerror("خطا", error_message)
        finally:
            self.scrape_button.config(state="normal", text="استخراج آگهی جدید")

    def on_entry_focus_in(self, event):
        if self.id_entry.get() == self.placeholder_text:
            self.id_entry.delete(0, "end")
            self.id_entry.config(foreground="black")

    def on_entry_focus_out(self, event):
        if not self.id_entry.get():
            self.id_entry.insert(0, self.placeholder_text)
            self.id_entry.config(foreground="grey")

    def show_ad_list(self):
        try:
            response = requests.get(API_URL)
            if response.status_code != 200:
                messagebox.showerror(
                    "خطا", f"خطا در دریافت لیست آگهی‌ها: {response.status_code}"
                )
                return
            ads_data = response.json()
            list_window = tk.Toplevel(self)
            list_window.title("لیست آگهی‌های استخراج شده")
            list_window.geometry("700x500")
            cols = ("id", "title", "location")
            tree = ttk.Treeview(list_window, columns=cols, show="headings")
            tree.heading("id", text="شناسه")
            tree.column("id", width=50, anchor="center")
            tree.heading("title", text="عنوان")
            tree.column("title", width=450)
            tree.heading("location", text="محله")
            tree.column("location", width=150, anchor="e")
            for ad in ads_data:
                tree.insert("", "end", values=(ad["id"], ad["title"], ad["location"]))
            tree.pack(fill="both", expand=True)

            def on_double_click(event):
                try:
                    item_id = tree.item(tree.focus())["values"][0]
                    self.id_entry.delete(0, "end")
                    self.id_entry.config(foreground="black")
                    self.id_entry.insert(0, str(item_id))
                    self.search_ad()
                    list_window.destroy()
                except IndexError:
                    pass

            tree.bind("<Double-1>", on_double_click)
        except requests.exceptions.ConnectionError:
            messagebox.showerror("خطا در اتصال", "ارتباط با سرور برقرار نشد.")
        except Exception as e:
            messagebox.showerror("خطای ناشناخته", str(e))

    def search_ad(self):
        ad_id = self.id_entry.get().strip()
        if not ad_id.isdigit():
            messagebox.showerror("خطا", "لطفاً یک شناسه عددی معتبر وارد کنید.")
            return
        try:
            response = requests.get(f"{API_URL}{ad_id}")
            if response.status_code == 200:
                self.display_ad_details(response.json())
            elif response.status_code == 404:
                messagebox.showinfo("یافت نشد", "آگهی با این شناسه یافت نشد.")
            else:
                messagebox.showerror("خطا", f"خطای سرور با کد: {response.status_code}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("خطا در اتصال", "ارتباط با سرور برقرار نشد.")
        except Exception as e:
            messagebox.showerror("خطای ناشناخته", str(e))

    def display_ad_details(self, data):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.title_label = ttk.Label(
            self.results_frame, text=data.get("title", "-"), style="Title.TLabel"
        )
        self.title_label.pack(anchor="e", pady=(0, 5))
        self.date_label = ttk.Label(
            self.results_frame,
            text=f"تاریخ انتشار: {data.get('date', '-')}",
            foreground="#555",
        )
        self.date_label.pack(anchor="e", pady=(0, 20))
        info_cards_frame = ttk.Frame(self.results_frame)
        info_cards_frame.pack(fill=tk.X, pady=10)
        info_cards_frame.columnconfigure((0, 1, 2), weight=1)
        self.create_info_card(info_cards_frame, "متراژ", data.get("meter", "-")).grid(
            row=0, column=2, sticky="ew", padx=5
        )
        self.create_info_card(info_cards_frame, "سال ساخت", data.get("year", "-")).grid(
            row=0, column=1, sticky="ew", padx=5
        )
        self.create_info_card(
            info_cards_frame, "تعداد اتاق", data.get("room", "-")
        ).grid(row=0, column=0, sticky="ew", padx=5)
        price_frame = ttk.Frame(self.results_frame)
        price_frame.pack(fill=tk.X, pady=10)
        price_frame.columnconfigure((0, 1), weight=1)
        self.create_info_card(
            price_frame, "قیمت کل", data.get("total_price", "-")
        ).grid(row=0, column=1, sticky="ew", padx=5)
        self.create_info_card(
            price_frame, "قیمت هر متر", data.get("meter_price", "-")
        ).grid(row=0, column=0, sticky="ew", padx=5)
        self.create_section_label("محله یا موقعیت", data.get("location", "-"))
        self.create_section_label("امکانات", data.get("amenities", "-"))
        self.create_description_section("توضیحات", data.get("description", "-"))
        buttons_frame = ttk.Frame(self.results_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        ttk.Button(buttons_frame, text="پاک‌سازی", command=self.clear_results).pack(
            side=tk.RIGHT
        )
        ttk.Button(
            buttons_frame,
            text="باز کردن لینک آگهی",
            style="Accent.TButton",
            command=lambda: self.open_link(data.get("link")),
        ).pack(side=tk.RIGHT, padx=10)
        ttk.Button(
            buttons_frame,
            text="کپی همه اطلاعات",
            command=lambda: self.copy_to_clipboard(self.generate_full_text(data)),
        ).pack(side=tk.RIGHT, padx=10)

    def create_info_card(self, parent, title, value):
        card_frame = tk.Frame(
            parent, relief="solid", bd=1, borderwidth=1, bg="white", padx=10, pady=10
        )
        ttk.Label(
            card_frame, text=title, font=("Arial", 10, "bold"), background="white"
        ).pack(anchor="e")
        ttk.Label(card_frame, text=value, font=("Arial", 12), background="white").pack(
            anchor="e"
        )
        return card_frame

    def create_section_label(self, title, content):
        frame = ttk.Frame(self.results_frame)
        frame.pack(fill=tk.X, pady=(20, 5))
        ttk.Label(frame, text=title, style="Header.TLabel").pack(anchor="e")
        ttk.Label(frame, text=content, wraplength=700, justify="right").pack(
            anchor="e", fill=tk.X
        )

    def create_description_section(self, title, content):
        frame = ttk.Frame(self.results_frame)
        frame.pack(fill=tk.X, pady=(20, 5))
        ttk.Label(frame, text=title, style="Header.TLabel").pack(anchor="e")
        text_widget = tk.Text(
            frame,
            height=5,
            wrap="word",
            font=("Arial", 10),
            relief="flat",
            bg="white",
            padx=10,
            pady=10,
        )
        text_widget.insert(tk.END, content)
        text_widget.config(state="disabled")
        text_widget.pack(fill=tk.X, expand=True)

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def open_link(self, url):
        if url and url != "-":
            webbrowser.open(url)
        else:
            messagebox.showinfo("لینک ناموجود", "این آگهی لینکی برای باز کردن ندارد.")

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("کپی شد", "تمام اطلاعات در کلیپ‌بورد کپی شد.")

    def generate_full_text(self, data):
        return "\n".join(
            [
                f"عنوان: {data.get('title', '-')}",
                f"تاریخ انتشار: {data.get('date', '-')}",
                f"محله: {data.get('location', '-')}",
                f"متراژ: {data.get('meter', '-')}",
                f"سال ساخت: {data.get('year', '-')}",
                f"تعداد اتاق: {data.get('room', '-')}",
                f"قیمت کل: {data.get('total_price', '-')}",
                f"قیمت هر متر: {data.get('meter_price', '-')}",
                f"طبقه: {data.get('floor', '-')}",
                f"امکانات: {data.get('amenities', '-')}",
                f"توضیحات: {data.get('description', '-')}",
                f"لینک: {data.get('link', '-')}",
            ]
        )


if __name__ == "__main__":
    app = DivarApp()
    app.mainloop()
