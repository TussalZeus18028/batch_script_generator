import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import base64
import zlib
import glob
import json
import subprocess
import sys
import threading
from datetime import datetime

class BatchScriptGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("批处理脚本释放器生成工具")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        self.auto_run_var = tk.BooleanVar(value=False)  # 是否启用自动运行
        self.auto_run_script_var = tk.StringVar()       # 要自动运行的脚本名称
        
        # 初始化设置文件路径
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bsg_settings.json")
        
        # 加载设置
        self.settings = self.load_settings()
        
        # 首先初始化 scripts 属性
        self.scripts = {}
        self.current_script = None
        
        # 设置应用图标
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 设置主题样式
        self.setup_theme()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 脚本编辑标签页
        self.script_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.script_tab, text="脚本编辑")
        
        # 生成器标签页
        self.generator_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.generator_tab, text="生成释放器")
        
        # 批量操作标签页
        self.batch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_tab, text="批量操作")
        
        # 设置标签页
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="设置")
        
        # 打包标签页
        self.package_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.package_tab, text="打包为EXE")
        
        # 关于标签页
        self.about_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.about_tab, text="关于")
        
        # 初始化标签页
        self.setup_script_tab()
        self.setup_generator_tab()
        self.setup_batch_tab()
        self.setup_settings_tab()
        self.setup_package_tab()
        self.setup_about_tab()
        
        # 添加示例脚本（在所有GUI元素初始化完成后）
        if self.settings.get("add_example_scripts", True):
             self.root.after(100, self.add_example_scripts)
    
    def setup_theme(self):
        """根据设置配置主题"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
    
        # 获取当前主题设置
        theme = self.settings.get("theme", "light")
    
        if theme == "dark":
            # 深色主题
            self.bg_color = "#2c3e50"          # 深蓝色背景
            self.frame_bg = "#34495e"          # 框架背景
            self.header_bg = "#2c3e50"         # 标题背景
            self.text_bg = "#2c3e50"           # 文本区域背景
            self.text_fg = "#ecf0f1"           # 文本前景色
            self.accent_color = "#3498db"      # 强调色(蓝色)
            self.button_bg = "#2980b9"         # 按钮背景
            self.button_hover = "#3498db"      # 按钮悬停色
            self.success_color = "#27ae60"     # 成功提示色
            self.warning_color = "#f39c12"     # 警告提示色
            self.error_color = "#e74c3c"       # 错误提示色
            # 配置样式
            self.root.configure(bg=self.bg_color)
            self.style.configure('.', background=self.frame_bg, foreground=self.text_fg)
            self.style.configure('TFrame', background=self.frame_bg)
            self.style.configure('TLabel', background=self.frame_bg, foreground=self.text_fg, font=('Arial', 10))
            self.style.configure('TButton', background=self.button_bg, foreground='white', 
                                font=('Arial', 10), padding=5, borderwidth=1)
            self.style.configure('TNotebook', background=self.bg_color)
            self.style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.text_fg, 
                                font=('Arial', 10, 'bold'), padding=[10, 5])
            self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'), 
                                foreground=self.text_fg, background=self.header_bg)

            # 配置输入框背景和前景色
            self.style.configure('TEntry', 
                                fieldbackground=self.text_bg,  # 输入区域背景色
                                background=self.text_bg,      # 整体背景色
                                foreground=self.text_fg)      # 文本颜色
        
            # 配置下拉框样式
            self.style.configure('TCombobox', 
                                fieldbackground=self.text_bg,  # 输入区域背景色
                                background=self.text_bg,      # 下拉箭头区域背景
                                foreground=self.text_fg)       # 文本颜色
        
            # 配置只读状态的下拉框
            self.style.map('TCombobox', 
                          fieldbackground=[('readonly', self.text_bg)],
                          background=[('readonly', self.text_bg)])
        
            # 配置复选框样式
            self.style.configure('TCheckbutton',
                                background=self.frame_bg,  # 背景色与框架相同
                                foreground=self.text_fg)   # 文字颜色与文本相同
        
            # 配置复选框的悬停状态
            self.style.map('TCheckbutton',
                          background=[('active', '#3a506b')],  # 悬停时使用稍亮的深蓝色
                          foreground=[('active', self.text_fg)]) # 文字颜色保持不变
        
            self.style.map('TButton', background=[('active', self.button_hover)])
            self.style.map('TNotebook.Tab', background=[('selected', self.accent_color)])
        else:
            # 浅色主题
            self.bg_color = "#f0f0f0"
            self.frame_bg = "#f0f0f0"
            self.header_bg = "#ffffff"
            self.text_bg = "#ffffff"
            self.text_fg = "#000000"
            self.accent_color = "#4a86e8"
            self.button_bg = "#e0e0e0"
            self.button_hover = "#d0d0d0"
            self.success_color = "green"
            self.warning_color = "orange"
            self.error_color = "red"
        
            # 配置样式
            self.root.configure(bg=self.bg_color)  # 设置根窗口背景
            self.style.configure('TFrame', background=self.frame_bg)
            self.style.configure('TLabel', background=self.frame_bg, foreground=self.text_fg, font=('Arial', 10))  # 添加前景色
            self.style.configure('TButton', font=('Arial', 10), padding=5, background=self.button_bg)
            self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground=self.accent_color)
            self.style.configure('TNotebook', background=self.bg_color)
            self.style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.text_fg,  # 添加前景色
                                font=('Arial', 10, 'bold'), padding=[10, 5])
            self.style.map('TButton', background=[('active', self.button_hover)])
            self.style.map('TNotebook.Tab', background=[('selected', self.accent_color)])
    
    def load_settings(self):
        """加载设置文件，如果不存在则使用默认设置"""
        default_settings = {
            "default_output_dir": "",
            "default_export_dir": os.path.join(os.path.expanduser("~"), "Desktop"),
            "default_batch_dir": os.path.join(os.path.expanduser("~"), "Desktop"),
            "default_encoding": "ANSI",
            "default_create_launcher": True,
            "default_show_confirmation": True,
            "default_exe_name": "script_release.py",
            "default_icon": "",
            "pyinstaller_path": self.find_pyinstaller(),
            "last_export_dir": os.path.join(os.path.expanduser("~"), "Desktop"),
            "last_output_dir": os.path.join(os.path.expanduser("~"), "Desktop"),
            "theme": "light",  # 默认浅色主题
            "temp_scripts": None  # 用于保存重启时的临时脚本
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # 合并设置，确保所有键都存在
                    for key in default_settings:
                        if key not in loaded_settings:
                            loaded_settings[key] = default_settings[key]
                    return loaded_settings
            except:
                return default_settings
        return default_settings
    
    def save_settings(self, temp_scripts=False):
        """保存当前设置到文件"""
        try:
            # 如果需要保存临时脚本
            if temp_scripts and self.scripts:
                self.settings["temp_scripts"] = self.scripts
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("保存设置错误", f"无法保存设置: {str(e)}")
            return False
    
    def find_pyinstaller(self):
        """尝试在系统路径中找到PyInstaller"""
        try:
            # 在Windows上
            if sys.platform == 'win32':
                paths = [
                    os.path.join(os.environ.get('PROGRAMFILES'), 'Python', '*', 'Scripts', 'pyinstaller.exe'),
                    os.path.join(os.environ.get('LOCALAPPDATA'), 'Programs', 'Python', '*', 'Scripts', 'pyinstaller.exe')
                ]
                
                # 检查所有可能的路径
                for pattern in paths:
                    matches = glob.glob(pattern)
                    if matches:
                        # 返回最新版本的路径
                        matches.sort(key=os.path.getmtime, reverse=True)
                        return matches[0]
            
            # 在非Windows系统或未找到时，尝试直接调用
            result = subprocess.run(['where' if sys.platform == 'win32' else 'which', 'pyinstaller'], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
                
        except:
            pass
        return ""
    
    def setup_script_tab(self):
        # 左侧面板 - 脚本列表
        left_frame = ttk.Frame(self.script_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        ttk.Label(left_frame, text="批处理脚本列表", style='Header.TLabel').pack(pady=10)
        
        # 创建带滚动条的脚本列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.script_listbox = tk.Listbox(
            list_frame, 
            width=30, 
            height=15, 
            font=('Arial', 10),
            selectbackground=self.accent_color,
            selectforeground="white",
            bg=self.text_bg,
            fg=self.text_fg
        )
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.script_listbox.yview)
        self.script_listbox.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.script_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.script_listbox.bind('<<ListboxSelect>>', self.on_script_select)
        
        # 按钮框架
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="添加脚本", command=self.add_script).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="删除脚本", command=self.delete_script).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="导入脚本", command=self.import_script).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # 右侧面板 - 脚本编辑器
        right_frame = ttk.Frame(self.script_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(right_frame, text="脚本编辑器", style='Header.TLabel').pack(pady=10)
        
        # 文件名输入
        file_frame = ttk.Frame(right_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="文件名:").pack(side=tk.LEFT)
        self.filename_var = tk.StringVar()
        filename_entry = ttk.Entry(file_frame, textvariable=self.filename_var, width=30)
        filename_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 脚本内容编辑器
        content_frame = ttk.LabelFrame(right_frame, text="脚本内容")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.script_editor = scrolledtext.ScrolledText(
            content_frame, 
            wrap=tk.WORD, 
            font=('Courier New', 10),
            undo=True,
            padx=10,
            pady=10,
            bg=self.text_bg,
            fg=self.text_fg,
            insertbackground=self.text_fg
        )
        self.script_editor.pack(fill=tk.BOTH, expand=True)
        
        # 状态信息
        self.status_var = tk.StringVar()
        ttk.Label(right_frame, textvariable=self.status_var, foreground=self.success_color).pack(pady=5)
        
        # 保存按钮
        ttk.Button(right_frame, text="保存脚本", command=self.save_script).pack(pady=10)
    
    def toggle_auto_run_combobox(self):
        """根据复选框状态启用/禁用下拉菜单"""
        if self.auto_run_var.get():
            self.auto_run_combobox.config(state="readonly")
            self.update_auto_run_scripts()  # 启用时刷新列表
        else:
            self.auto_run_combobox.config(state="disabled")
    
    def update_auto_run_scripts(self):
        """更新自动运行脚本的下拉菜单选项"""
        scripts = list(self.scripts.keys())
        self.auto_run_combobox['values'] = scripts
        
        # 如果有脚本，设置默认选择第一个
        if scripts:
            self.auto_run_script_var.set(scripts[0])
    
    def setup_generator_tab(self):
        frame = ttk.Frame(self.generator_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(frame, text="生成释放器程序", style='Header.TLabel').pack(pady=5)
        
        # 释放器设置
        settings_frame = ttk.LabelFrame(frame, text="释放器设置")
        settings_frame.pack(fill=tk.X, pady=5)
        
        # 输出目录设置
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="默认输出目录:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value=self.settings["default_output_dir"])
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=30)
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="浏览...", command=self.browse_output_dir).pack(side=tk.LEFT, padx=5)
        
        # 释放器文件名
        exe_frame = ttk.Frame(settings_frame)
        exe_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(exe_frame, text="释放器文件名:").pack(side=tk.LEFT)
        self.exe_name_var = tk.StringVar(value=self.settings["default_exe_name"])
        exe_entry = ttk.Entry(exe_frame, textvariable=self.exe_name_var, width=30)
        exe_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 编码选项
        encoding_frame = ttk.Frame(settings_frame)
        encoding_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(encoding_frame, text="脚本编码:").pack(side=tk.LEFT)
        self.encoding_var = tk.StringVar(value=self.settings["default_encoding"])
        encoding_combo = ttk.Combobox(
            encoding_frame, 
            textvariable=self.encoding_var, 
            width=10,
            state="readonly"
        )
        encoding_combo['values'] = ('ANSI', 'GBK', 'UTF-8', 'LATIN-1')
        encoding_combo.pack(side=tk.LEFT, padx=5)
        
        # 高级选项
        advanced_frame = ttk.Frame(settings_frame)
        advanced_frame.pack(fill=tk.X, pady=5)
        
        self.create_launcher_var = tk.BooleanVar(value=self.settings["default_create_launcher"])
        ttk.Checkbutton(
            advanced_frame, 
            text="创建启动所有脚本的批处理文件", 
            variable=self.create_launcher_var
        ).pack(side=tk.LEFT, padx=5)
        
        self.show_confirmation_var = tk.BooleanVar(value=self.settings["default_show_confirmation"])
        ttk.Checkbutton(
            advanced_frame, 
            text="在释放前显示确认对话框", 
            variable=self.show_confirmation_var
        ).pack(side=tk.LEFT, padx=5)
        
        # 自动运行选项框架
        auto_run_frame = ttk.Frame(settings_frame)
        auto_run_frame.pack(fill=tk.X, pady=5)
        
        # 启用自动运行的复选框
        ttk.Checkbutton(
            auto_run_frame, 
            text="在释放完文件后自动运行脚本：", 
            variable=self.auto_run_var,
            command=self.toggle_auto_run_combobox  # 当状态改变时启用/禁用下拉菜单
        ).pack(side=tk.LEFT, padx=5)
        
        # 脚本选择下拉菜单
        self.auto_run_combobox = ttk.Combobox(
            auto_run_frame, 
            textvariable=self.auto_run_script_var,
            width=20,
            state="disabled"  # 初始状态为禁用
        )
        self.auto_run_combobox.pack(side=tk.LEFT, padx=5)
        
        # 刷新脚本列表按钮
        ttk.Button(
            auto_run_frame,
            text="刷新列表",
            command=self.update_auto_run_scripts
        ).pack(side=tk.LEFT, padx=5)
        
        # 预览
        preview_frame = ttk.LabelFrame(frame, text="释放器预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame, 
            wrap=tk.WORD, 
            font=('Courier New', 9),
            padx=10,
            pady=10,
            bg=self.text_bg,
            fg=self.text_fg,
            insertbackground=self.text_fg
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)
        
        # 生成按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 左侧按钮区域
        button_container = ttk.Frame(button_frame)
        button_container.pack(side=tk.LEFT, padx=10)
        
        # 按钮在左侧容器中
        ttk.Button(button_container, text="预览释放器", command=self.update_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_container, text="生成释放器", command=self.generate_releaser).pack(side=tk.LEFT, padx=5)

        # 状态信息紧挨着按钮容器
        self.generator_status = tk.StringVar()
        status_label = ttk.Label(button_frame, textvariable=self.generator_status, foreground=self.success_color)
        status_label.pack(side=tk.LEFT, padx=10)  # 减少间距
    
    def setup_batch_tab(self):
        frame = ttk.Frame(self.batch_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="批量操作", style='Header.TLabel').pack(pady=10)
        
        # 批量导入区域
        import_frame = ttk.LabelFrame(frame, text="批量导入批处理脚本")
        import_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(import_frame, text="选择包含批处理脚本的文件夹:").pack(anchor=tk.W, pady=5)
        
        dir_frame = ttk.Frame(import_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        self.batch_dir_var = tk.StringVar(value=self.settings["default_batch_dir"])
        ttk.Entry(dir_frame, textvariable=self.batch_dir_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="浏览...", command=self.browse_batch_dir).pack(side=tk.LEFT, padx=5)
        
        # 文件过滤选项
        filter_frame = ttk.Frame(import_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="文件过滤:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="*.*")
        ttk.Entry(filter_frame, textvariable=self.filter_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(import_frame, text="导入文件夹中的所有批处理文件", command=self.batch_import).pack(pady=10)
        
        # 批量导出区域
        export_frame = ttk.LabelFrame(frame, text="批量导出批处理脚本")
        export_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(export_frame, text="导出所有脚本到文件夹:").pack(anchor=tk.W, pady=5)
        
        export_dir_frame = ttk.Frame(export_frame)
        export_dir_frame.pack(fill=tk.X, pady=5)
        
        self.export_dir_var = tk.StringVar(value=self.settings["default_export_dir"])
        ttk.Entry(export_dir_frame, textvariable=self.export_dir_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(export_dir_frame, text="浏览...", command=self.browse_export_dir).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_frame, text="导出所有脚本", command=self.batch_export).pack(pady=10)
        
        # 批量删除区域
        delete_frame = ttk.LabelFrame(frame, text="批量删除脚本")
        delete_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(delete_frame, text="删除所有脚本:").pack(anchor=tk.W, pady=5)
        ttk.Button(delete_frame, text="删除所有脚本", command=self.delete_all_scripts).pack(pady=10)
        
        # 状态信息
        self.batch_status = tk.StringVar()
        ttk.Label(frame, textvariable=self.batch_status, foreground=self.success_color).pack(pady=10)
    
    def setup_settings_tab(self):
        frame = ttk.Frame(self.settings_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="程序设置", style='Header.TLabel').pack(pady=10)
        
        # 设置说明
        settings_info = ttk.Label(
            frame, 
            text="配置默认选项，这些设置将在下次启动程序时自动加载",
            font=('Arial', 9),
            foreground="#555555"
        )
        settings_info.pack(anchor=tk.W, pady=5)
        
        # 设置表单框架
        form_frame = ttk.LabelFrame(frame, text="默认设置")
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 使用网格布局
        row = 0
        
        # 主题模式
        ttk.Label(form_frame, text="主题模式:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.settings_theme_var = tk.StringVar(value=self.settings.get("theme", "light"))
        theme_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.settings_theme_var, 
            width=10,
            state="readonly",
            values=["light", "dark"]
        )
        theme_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # 默认输出目录
        ttk.Label(form_frame, text="默认输出目录:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.settings_output_dir_var = tk.StringVar(value=self.settings["default_output_dir"])
        ttk.Entry(form_frame, textvariable=self.settings_output_dir_var, width=40).grid(
            row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(form_frame, text="浏览...", 
                  command=lambda: self.browse_directory(self.settings_output_dir_var)).grid(
            row=row, column=2, padx=5, pady=5)
        row += 1
        
        # 默认导出目录
        ttk.Label(form_frame, text="默认导出目录:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.settings_export_dir_var = tk.StringVar(value=self.settings["default_export_dir"])
        ttk.Entry(form_frame, textvariable=self.settings_export_dir_var, width=40).grid(
            row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(form_frame, text="浏览...", 
                  command=lambda: self.browse_directory(self.settings_export_dir_var)).grid(
            row=row, column=2, padx=5, pady=5)
        row += 1
        
        # 默认批量导入目录
        ttk.Label(form_frame, text="默认批量导入目录:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.settings_batch_dir_var = tk.StringVar(value=self.settings["default_batch_dir"])
        ttk.Entry(form_frame, textvariable=self.settings_batch_dir_var, width=40).grid(
            row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(form_frame, text="浏览...", 
                  command=lambda: self.browse_directory(self.settings_batch_dir_var)).grid(
            row=row, column=2, padx=5, pady=5)
        row += 1
        
        # 默认编码
        ttk.Label(form_frame, text="默认脚本编码:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.settings_encoding_var = tk.StringVar(value=self.settings["default_encoding"])
        encoding_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.settings_encoding_var, 
            width=10,
            state="readonly"
        )
        encoding_combo['values'] = ('ANSI', 'GBK', 'UTF-8', 'LATIN-1')
        encoding_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1

        # 是否添加示例脚本
        self.settings_add_examples_var = tk.BooleanVar(value=self.settings.get("add_example_scripts", True))
        ttk.Checkbutton(
            form_frame, 
            text="启动时添加示例脚本", 
            variable=self.settings_add_examples_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        row += 1
        
        # 默认创建启动器
        self.settings_create_launcher_var = tk.BooleanVar(value=self.settings["default_create_launcher"])
        ttk.Checkbutton(
            form_frame, 
            text="默认创建启动所有脚本的批处理文件", 
            variable=self.settings_create_launcher_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        row += 1
        
        # 默认显示确认对话框
        self.settings_show_confirmation_var = tk.BooleanVar(value=self.settings["default_show_confirmation"])
        ttk.Checkbutton(
            form_frame, 
            text="默认在释放前显示确认对话框", 
            variable=self.settings_show_confirmation_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        row += 1
        
        # 默认释放器文件名
        ttk.Label(form_frame, text="默认释放器文件名:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.settings_exe_name_var = tk.StringVar(value=self.settings["default_exe_name"])
        ttk.Entry(form_frame, textvariable=self.settings_exe_name_var, width=30).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        # PyInstaller路径
        ttk.Label(form_frame, text="PyInstaller路径:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.settings_pyinstaller_var = tk.StringVar(value=self.settings["pyinstaller_path"])
        ttk.Entry(form_frame, textvariable=self.settings_pyinstaller_var, width=40).grid(
            row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(form_frame, text="浏览...", 
                  command=lambda: self.browse_file(self.settings_pyinstaller_var, "选择PyInstaller可执行文件", [("可执行文件", "*.exe")])).grid(
            row=row, column=2, padx=5, pady=5)
        row += 1
        
        # 默认图标文件
        ttk.Label(form_frame, text="默认图标文件:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.settings_icon_var = tk.StringVar(value=self.settings["default_icon"])
        ttk.Entry(form_frame, textvariable=self.settings_icon_var, width=40).grid(
            row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(form_frame, text="浏览...", 
                  command=lambda: self.browse_file(self.settings_icon_var, "选择图标文件", [("图标文件", "*.ico")])).grid(
            row=row, column=2, padx=5, pady=5)
        row += 1
        
        # 保存按钮
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="保存设置", command=self.save_settings_changes).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="恢复默认设置", command=self.restore_default_settings).pack(side=tk.LEFT, padx=10)
        
        # 状态信息
        self.settings_status = tk.StringVar()
        ttk.Label(frame, textvariable=self.settings_status, foreground=self.success_color).pack(pady=10)
    
    def setup_package_tab(self):
        frame = ttk.Frame(self.package_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="打包为EXE文件", style='Header.TLabel').pack(pady=10)
        
        # 说明文本
        info_text = """
        将生成的释放器脚本打包为独立的可执行文件(.exe)，可以在没有Python环境的计算机上运行。
        
        要求:
        1. 确保已经安装了PyInstaller (pip install pyinstaller)
        2. 确保在"设置"标签页中配置了PyInstaller的路径
        """
        info_label = ttk.Label(frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W, pady=10)
        
        # 打包设置框架
        settings_frame = ttk.LabelFrame(frame, text="打包设置")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # 选择要打包的脚本
        script_frame = ttk.Frame(settings_frame)
        script_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(script_frame, text="选择要打包的脚本:").pack(side=tk.LEFT, padx=(10, 5))
        self.package_script_var = tk.StringVar()
        ttk.Entry(script_frame, textvariable=self.package_script_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(script_frame, text="浏览...", command=self.browse_package_script).pack(side=tk.LEFT, padx=5)
        
        # 输出目录
        output_frame = ttk.Frame(settings_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT, padx=(10, 5))
        self.package_output_var = tk.StringVar(value=self.settings["last_output_dir"])
        ttk.Entry(output_frame, textvariable=self.package_output_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="浏览...", command=self.browse_package_output).pack(side=tk.LEFT, padx=5)
        
        # 图标文件
        icon_frame = ttk.Frame(settings_frame)
        icon_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(icon_frame, text="图标文件(.ico):").pack(side=tk.LEFT, padx=(10, 5))
        self.package_icon_var = tk.StringVar(value=self.settings["default_icon"])
        ttk.Entry(icon_frame, textvariable=self.package_icon_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(icon_frame, text="浏览...", command=lambda: self.browse_file(self.package_icon_var, "选择图标文件", [("图标文件", "*.ico")])).pack(side=tk.LEFT, padx=5)
        
        # 高级选项
        advanced_frame = ttk.Frame(settings_frame)
        advanced_frame.pack(fill=tk.X, pady=5)
        
        self.package_console_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_frame, 
            text="显示控制台窗口", 
            variable=self.package_console_var
        ).pack(side=tk.LEFT, padx=10)
        
        self.package_onefile_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_frame, 
            text="打包为单个文件", 
            variable=self.package_onefile_var
        ).pack(side=tk.LEFT, padx=10)
        
        # 打包按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="开始打包", command=self.package_exe).pack(pady=10, ipadx=20, ipady=5)
        
        # 日志输出
        log_frame = ttk.LabelFrame(frame, text="打包日志")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.package_log = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            font=('Courier New', 9),
            padx=10,
            pady=10,
            bg=self.text_bg,
            fg=self.text_fg,
            insertbackground=self.text_fg
        )
        self.package_log.pack(fill=tk.BOTH, expand=True)
        self.package_log.config(state=tk.DISABLED)
        
        # 状态信息
        self.package_status = tk.StringVar()
        ttk.Label(frame, textvariable=self.package_status, foreground=self.success_color).pack(pady=5)
    
    def setup_about_tab(self):
        frame = ttk.Frame(self.about_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        ttk.Label(frame, text="批处理脚本释放器生成工具", style='Header.TLabel').pack(pady=10)
        
        about_text = """
        **关于此工具**
        
        此工具可以帮助您创建自定义的批处理脚本释放器。您可以：
        1. 添加、编辑多个批处理脚本
        2. 批量导入和导出脚本
        3. 配置释放器设置
        4. 生成一个可执行的Python程序
        5. 将释放器打包为独立的EXE文件
        
        生成的释放器程序可以：
        - 默认在释放器所在目录输出批处理脚本
        - 当指定目录时，在指定目录输出
        - 自动创建必要的目录结构
        - 处理不同的文件编码（包括ANSI）
        
        **支持批量操作**
        - 支持一次导入多个批处理脚本
        - 支持导出所有脚本到文件夹
        - 支持创建启动所有脚本的批处理文件
        
        **ANSI编码支持**
        - 生成的批处理脚本默认使用ANSI编码
        - 适合在Windows系统上运行
        
        版本: 1.3 (支持深色/浅色主题切换)
        作者: By-B站负重之地捉蛐蛐
        """
        
        about_label = tk.Label(
            frame, 
            text=about_text, 
            justify=tk.LEFT,
            font=('Arial', 10),
            bg=self.frame_bg,
            fg=self.text_fg
        )
        about_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 添加版权信息
        copyright_label = ttk.Label(
            frame, 
            text="© 2025 批处理脚本释放器生成工具 - 保留所有权利",
            foreground="#666666"
        )
        copyright_label.pack(side=tk.BOTTOM, pady=10)
    
    def browse_directory(self, var):
        """浏览并选择目录"""
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            var.set(directory)
    
    def browse_file(self, var, title, filetypes):
        """浏览并选择文件"""
        filepath = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if filepath:
            var.set(filepath)
    
    def save_settings_changes(self):
        """保存设置更改"""
        self.settings["default_output_dir"] = self.settings_output_dir_var.get()
        self.settings["default_export_dir"] = self.settings_export_dir_var.get()
        self.settings["default_batch_dir"] = self.settings_batch_dir_var.get()
        self.settings["default_encoding"] = self.settings_encoding_var.get()
        self.settings["default_create_launcher"] = self.settings_create_launcher_var.get()
        self.settings["default_show_confirmation"] = self.settings_show_confirmation_var.get()
        self.settings["default_exe_name"] = self.settings_exe_name_var.get()
        self.settings["pyinstaller_path"] = self.settings_pyinstaller_var.get()
        self.settings["default_icon"] = self.settings_icon_var.get()
        self.settings["add_example_scripts"] = self.settings_add_examples_var.get()
        
        # 检查主题是否改变
        theme_changed = False
        new_theme = self.settings_theme_var.get()
        if new_theme != self.settings.get("theme", "light"):
            theme_changed = True
            self.settings["theme"] = new_theme
        
        # 保存设置到文件
        if self.save_settings():
            self.settings_status.set("设置已成功保存!")
            # 更新其他标签页的设置
            self.output_dir_var.set(self.settings["default_output_dir"])
            self.export_dir_var.set(self.settings["default_export_dir"])
            self.batch_dir_var.set(self.settings["default_batch_dir"])
            self.encoding_var.set(self.settings["default_encoding"])
            self.create_launcher_var.set(self.settings["default_create_launcher"])
            self.show_confirmation_var.set(self.settings["default_show_confirmation"])
            self.exe_name_var.set(self.settings["default_exe_name"])
            
            # 如果主题改变，保存脚本并重启
            if theme_changed:
                # 保存当前脚本到临时设置
                self.save_settings(temp_scripts=True)
                
                # 提示用户程序将重启
                self.settings_status.set("主题已更改，程序将在3秒后重启...")
                
                # 重启
                self.root.after(3000, self.restart_application)
    
    def restart_application(self):
        """重启应用程序"""
        python = sys.executable
        args = [python] + sys.argv
        try:
            # 在Windows上使用CREATE_NEW_CONSOLE标志
            if sys.platform == "win32":
                subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(args)
        except:
            # 如果上述方法失败，尝试直接启动
            os.startfile(sys.argv[0])
        
        # 关闭当前程序
        self.root.destroy()
    
    def restore_default_settings(self):
        """恢复默认设置"""
        default_settings = {
            "default_output_dir": "",
            "default_export_dir": os.path.join(os.path.expanduser("~"), "Desktop"),
            "default_batch_dir": os.path.join(os.path.expanduser("~"), "Desktop"),
            "default_encoding": "ANSI",
            "default_create_launcher": True,
            "default_show_confirmation": True,
            "default_exe_name": "script_release.py",
            "default_icon": "",
            "pyinstaller_path": self.find_pyinstaller(),
            "add_example_scripts": True,
            "theme": "light"  # 默认浅色主题
        }
        
        # 更新UI
        self.settings_output_dir_var.set(default_settings["default_output_dir"])
        self.settings_export_dir_var.set(default_settings["default_export_dir"])
        self.settings_batch_dir_var.set(default_settings["default_batch_dir"])
        self.settings_encoding_var.set(default_settings["default_encoding"])
        self.settings_create_launcher_var.set(default_settings["default_create_launcher"])
        self.settings_show_confirmation_var.set(default_settings["default_show_confirmation"])
        self.settings_exe_name_var.set(default_settings["default_exe_name"])
        self.settings_pyinstaller_var.set(default_settings["pyinstaller_path"])
        self.settings_icon_var.set(default_settings["default_icon"])
        self.settings_add_examples_var.set(default_settings["add_example_scripts"])
        self.settings_theme_var.set(default_settings["theme"])
        
        self.settings_status.set("已恢复默认设置")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
            # 更新设置中的最后输出目录
            self.settings["last_output_dir"] = directory
    
    def browse_package_script(self):
        """浏览要打包的脚本"""
        filepath = filedialog.askopenfilename(
            title="选择要打包的脚本",
            filetypes=[("Python 文件", "*.py"), ("所有文件", "*.*")]
        )
        if filepath:
            self.package_script_var.set(filepath)
    
    def browse_package_output(self):
        """浏览打包输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.package_output_var.set(directory)
            # 更新设置中的最后输出目录
            self.settings["last_output_dir"] = directory
    
    def package_exe(self):
        """打包为EXE文件"""
        script_path = self.package_script_var.get()
        output_dir = self.package_output_var.get()
        icon_path = self.package_icon_var.get()
        pyinstaller_path = self.settings_pyinstaller_var.get()
        
        # 验证输入
        if not script_path or not os.path.isfile(script_path):
            self.package_status.set("错误: 请选择有效的Python脚本")
            return
        
        if not output_dir:
            self.package_status.set("错误: 请选择输出目录")
            return
        
        if not pyinstaller_path or not os.path.isfile(pyinstaller_path):
            self.package_status.set("错误: PyInstaller路径无效")
            return
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建PyInstaller命令
        cmd = [pyinstaller_path]
        
        # 添加选项
        if self.package_onefile_var.get():
            cmd.append('--onefile')
        
        if not self.package_console_var.get():
            cmd.append('--noconsole')
        
        if icon_path and os.path.isfile(icon_path):
            cmd.append(f'--icon={icon_path}')
        
        cmd.extend([
            '--distpath', output_dir,
            '--workpath', os.path.join(output_dir, 'build'),
            '--specpath', output_dir,
            script_path
        ])
        
        # 更新日志
        self.update_package_log(f"开始打包: {script_path}")
        self.update_package_log(f"命令: {' '.join(cmd)}")
        
        # 在单独的线程中运行打包过程
        threading.Thread(target=self.run_packaging, args=(cmd,), daemon=True).start()
    
    def run_packaging(self, cmd):
        """在单独的线程中运行打包过程"""
        try:
            # 执行打包命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 实时读取输出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.update_package_log(output.strip())
            
            return_code = process.poll()
            
            if return_code == 0:
                self.package_status.set("打包成功完成!")
                self.update_package_log("\n打包成功完成!")
                messagebox.showinfo("打包成功", "EXE文件已成功生成!")
            else:
                self.package_status.set(f"打包失败，退出码: {return_code}")
                self.update_package_log(f"\n打包失败，退出码: {return_code}")
                messagebox.showerror("打包失败", "EXE文件生成失败，请检查日志")
                
        except Exception as e:
            self.package_status.set(f"打包出错: {str(e)}")
            self.update_package_log(f"\n打包出错: {str(e)}")
            messagebox.showerror("打包错误", f"打包过程中发生错误:\n{str(e)}")
    
    def update_package_log(self, message):
        """更新打包日志"""
        self.package_log.config(state=tk.NORMAL)
        self.package_log.insert(tk.END, message + "\n")
        self.package_log.see(tk.END)
        self.package_log.config(state=tk.DISABLED)
        self.package_log.update_idletasks()
    
    def add_example_scripts(self):
        # 检查是否有临时脚本需要恢复
        temp_scripts = self.settings.get("temp_scripts")
        if temp_scripts:
            self.scripts = temp_scripts
            # 清除设置中的临时脚本
            if "temp_scripts" in self.settings:
                del self.settings["temp_scripts"]
            self.save_settings()
        else:
            # 添加示例脚本
            examples = {
                "install_deps.bat": r"""@echo off
echo 正在安装必要的依赖...
pip install requests numpy pandas
echo 依赖安装成功!
pause""",
                
                "setup_environment.bat": r"""@echo off
echo 正在设置环境变量...
setx PYTHONPATH "C:\MyProject;%%PYTHONPATH%%"
echo 环境配置完成!
pause""",
                
                "start_service.bat": r"""@echo off
echo 正在启动应用程序服务...
start python app_main.py
echo 服务已在后台启动!
pause"""
            }
            self.scripts = examples
        
        # 更新脚本列表
        self.script_listbox.delete(0, tk.END)
        for filename in self.scripts:
            self.script_listbox.insert(tk.END, filename)
        
        # 更新状态和预览
        self.status_var.set(f"已添加示例脚本 - 脚本总数: {len(self.scripts)}")
        self.update_preview()
    
    def add_script(self):
        # 生成唯一的文件名
        counter = 1
        while f"new_script_{counter}" in self.scripts:
            counter += 1
        
        # 不再自动添加.bat后缀
        filename = f"new_script_{counter}"
        self.scripts[filename] = "@echo off\r\necho 这是新批处理脚本\r\npause"
        self.script_listbox.insert(tk.END, filename)
        self.script_listbox.selection_clear(0, tk.END)
        self.script_listbox.selection_set(tk.END)
        self.script_listbox.activate(tk.END)
        self.on_script_select()
        self.status_var.set(f"已添加新脚本: {filename}")
    
    def delete_script(self):
        selection = self.script_listbox.curselection()
        if not selection:
            self.status_var.set("请先选择一个脚本")
            return
            
        index = selection[0]
        filename = self.script_listbox.get(index)
        if messagebox.askyesno("确认删除", f"确定要删除脚本 '{filename}' 吗?"):
            del self.scripts[filename]
            self.script_listbox.delete(index)
            
            # 选择下一个项目
            if self.script_listbox.size() > 0:
                new_index = min(index, self.script_listbox.size()-1)
                self.script_listbox.selection_set(new_index)
                self.script_listbox.activate(new_index)
                self.on_script_select()
            
            self.status_var.set(f"已删除脚本: {filename}")
            self.update_preview()
    
    def import_script(self):
        filepath = filedialog.askopenfilename(
            title="选择脚本文件",
            filetypes=[("所有文件", "*.*"), ("批处理文件", "*.bat"), ("Python 文件", "*.py")]
        )
        
        if not filepath:
            return
            
        # 使用原始文件名，不再自动添加.bat后缀
        filename = os.path.basename(filepath)
            
        # 处理重名
        base_name, ext = os.path.splitext(filename)
        counter = 1
        original_filename = filename
        while filename in self.scripts:
            filename = f"{base_name}_{counter}{ext}"
            counter += 1
            
        try:
            # 读取文件内容，尝试使用ANSI编码
            try:
                with open(filepath, 'r', encoding='ansi') as f:
                    content = f.read()
            except:
                # 如果ANSI失败，尝试使用GBK
                with open(filepath, 'r', encoding='gbk') as f:
                    content = f.read()
                    
            self.scripts[filename] = content
            self.script_listbox.insert(tk.END, filename)
            self.script_listbox.selection_clear(0, tk.END)
            self.script_listbox.selection_set(tk.END)
            self.script_listbox.activate(tk.END)
            self.on_script_select()
            
            self.status_var.set(f"已成功导入脚本: {filename}")
            self.update_preview()
        except Exception as e:
            messagebox.showerror("导入错误", f"导入文件时出错:\n{str(e)}")
    
    def on_script_select(self, event=None):
        selection = self.script_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        filename = self.script_listbox.get(index)
        self.current_script = filename
        
        self.filename_var.set(filename)
        self.script_editor.delete(1.0, tk.END)
        self.script_editor.insert(tk.END, self.scripts[filename])
        
        self.status_var.set(f"当前编辑: {filename} - 脚本总数: {len(self.scripts)}")
    
    def save_script(self):
        if not self.current_script:
            self.status_var.set("请先选择一个脚本")
            return
            
        filename = self.filename_var.get().strip()
        if not filename:
            messagebox.showerror("错误", "文件名不能为空!")
            return
            
        # 不再自动添加.bat后缀 - 保留用户输入的文件名
        content = self.script_editor.get(1.0, tk.END).strip()
        
        # 如果文件名改变了
        if filename != self.current_script:
            # 检查是否已存在
            if filename in self.scripts:
                messagebox.showerror("错误", f"脚本 '{filename}' 已存在!")
                return
                
            # 从列表中移除旧文件名
            index = self.script_listbox.get(0, tk.END).index(self.current_script)
            self.script_listbox.delete(index)
            del self.scripts[self.current_script]
            
            # 添加新文件名
            self.scripts[filename] = content
            self.script_listbox.insert(index, filename)
            self.script_listbox.selection_set(index)
            self.script_listbox.activate(index)
            self.current_script = filename
            self.filename_var.set(filename)
        else:
            self.scripts[filename] = content
        
        self.update_preview()
        self.status_var.set(f"脚本 '{filename}' 已保存!")
    
    def update_preview(self):
        if not hasattr(self, 'preview_text'):
            return
            
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        try:
            # 生成预览代码
            preview_code = self.generate_releaser_code(preview=True)
            self.preview_text.insert(tk.END, preview_code)
            self.generator_status.set(f"预览已更新 - 脚本总数: {len(self.scripts)}")
        except Exception as e:
            self.preview_text.insert(tk.END, f"# 生成预览时出错: {str(e)}")
            self.generator_status.set(f"预览更新失败: {str(e)}")
        
        self.preview_text.config(state=tk.DISABLED)
    
    def generate_releaser_code(self, preview=False):
        # 生成释放器的Python代码
        encoding = self.encoding_var.get().lower()
        default_dir = self.output_dir_var.get()
        create_launcher = self.create_launcher_var.get()
        show_confirmation = self.show_confirmation_var.get()
        auto_run_enabled = self.auto_run_var.get()
        auto_run_script = self.auto_run_script_var.get()
        
        # 创建编码映射
        encoding_map = {
            'ansi': 'mbcs',  # Windows ANSI编码对应mbcs
            'gbk': 'gbk',
            'utf-8': 'utf-8',
            'latin-1': 'latin-1'
        }
        py_encoding = encoding_map.get(encoding, 'mbcs')  # 默认使用mbcs
        
        code = f"""# 批处理脚本释放器
# 由批处理脚本释放器生成工具创建
# 生成时间: {self.get_current_time()}
# 脚本总数: {len(self.scripts)}
# 编码: {encoding} (实际使用: {py_encoding})

import os
import sys
import base64
import zlib
import time
"""

        # 添加确认对话框选项
        if show_confirmation:
            code += """
def show_confirmation_dialog():
    \"\"\"显示确认对话框并返回用户选择\"\"\"
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        result = messagebox.askyesno(
            "确认执行",
            "即将释放批处理脚本到当前目录。\\n是否继续执行？",
            icon='question'
        )
        root.destroy()
        return result
    except ImportError:
        # 如果tkinter不可用，使用命令行确认
        print("\\n即将释放批处理脚本到当前目录")
        response = input("是否继续执行? (Y/N): ").strip().lower()
        return response in ('y', 'yes')
"""

        code += """
def create_batch_files(output_dir=None):
    # 如果没有指定输出目录
    if output_dir is None:
        # 判断是否是打包后的可执行文件
        if getattr(sys, 'frozen', False):
            # 可执行文件所在的目录
            output_dir = os.path.dirname(sys.executable)
        else:
            # 非打包环境使用当前工作目录
            output_dir = os.getcwd()
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 批处理脚本数据 (文件名: 压缩的base64内容)
    batch_scripts = {
"""
        
        # 添加脚本数据
        for filename, content in self.scripts.items():
            # 压缩内容
            compressed = zlib.compress(content.encode('utf-8'))
            b64_content = base64.b64encode(compressed).decode('ascii')
            
            # 为了可读性，每行显示60个字符
            formatted_content = ""
            for i in range(0, len(b64_content), 60):
                formatted_content += f'        "{b64_content[i:i+60]}" \\\n'
            formatted_content = formatted_content.rstrip('\\\n').rstrip()
            
            code += f'    "{filename}": (\n{formatted_content}\n    ),\n'
        
        code += f"""    }}
    
    # 写入文件
    for filename, b64_data in batch_scripts.items():
        filepath = os.path.join(output_dir, filename)
        
        # 解码并解压缩内容
        compressed = base64.b64decode(''.join(b64_data))
        content = zlib.decompress(compressed).decode('utf-8')
        
        # 使用指定编码写入
        with open(filepath, "w", encoding='{py_encoding}') as f:
            f.write(content)
        
        print(f"已创建: {{filepath}}")
    
    # 创建启动所有脚本的批处理文件
    if {create_launcher}:
        launcher_path = os.path.join(output_dir, "RUN_ALL.bat")
        with open(launcher_path, "w", encoding='{py_encoding}') as f:
            f.write("@echo off\\r\\n")
            f.write("echo 正在运行所有批处理脚本...\\r\\n\\r\\n")
            
            for script in batch_scripts.keys():
                f.write(f'call "{{script}}"\\r\\n')
            
            f.write("\\r\\necho 所有脚本执行完成!\\r\\n")
            f.write("pause\\r\\n")
        
        print(f"已创建启动器: {{launcher_path}}")
    
    # 自动运行指定的脚本
    if {auto_run_enabled} and "{auto_run_script}" in batch_scripts:
        auto_script_path = os.path.join(output_dir, "{auto_run_script}")
        print(f"\\n正在自动运行脚本: {{auto_script_path}}")
        os.system(f'call "{{auto_script_path}}"')
    
    print(f"\\n所有批处理文件已释放到: {{os.path.abspath(output_dir)}}")
    print("操作完成!")
    time.sleep(5)

if __name__ == "__main__":
"""
        # 添加确认对话框调用
        if show_confirmation:
            code += """    # 显示确认对话框
    if not show_confirmation_dialog():
        print("用户取消操作。")
        sys.exit(0)
    
"""
        else:
            code += """    # 没有启用确认对话框
"""
        
        code += """    # 如果没有参数，则使用None表示默认目录
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = None

    try:
        create_batch_files(target_dir)
    except Exception as e:
        print(f"\\n发生错误: {{str(e)}}")
        print("请检查写入权限或磁盘空间")
        sys.exit(1)
"""
        return code
    
    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_releaser(self):
        if not hasattr(self, 'scripts') or not self.scripts:
            messagebox.showerror("错误", "没有可用的脚本! 请先添加批处理脚本。")
            return
            
        # 获取保存路径
        filename = self.exe_name_var.get().strip()
        if not filename:
            messagebox.showerror("错误", "请指定释放器文件名!")
            return
            
        # 不再自动添加.py后缀 - 保留用户输入的文件名
        filepath = filedialog.asksaveasfilename(
            title="保存释放器程序",
            initialfile=filename,
            filetypes=[("Python 文件", "*.py"), ("所有文件", "*.*")]
        )
        
        if not filepath:
            return
            
        try:
            code = self.generate_releaser_code()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
                
            # 更新设置中的最后输出目录
            self.settings["last_output_dir"] = os.path.dirname(filepath)
                
            self.generator_status.set(f"释放器已成功生成: {filepath}")
            messagebox.showinfo("生成成功", 
                f"释放器程序已成功生成:\n{filepath}\n\n"
                "使用方法:\n"
                f"1. 运行: python {os.path.basename(filepath)} (默认在释放器所在目录输出)\n"
                f"2. 或指定目录: python {os.path.basename(filepath)} \"C:\\目标目录\"")
        except Exception as e:
            messagebox.showerror("生成错误", f"生成释放器时出错:\n{str(e)}")
    
    def browse_batch_dir(self):
        directory = filedialog.askdirectory(title="选择包含批处理脚本的文件夹")
        if directory:
            self.batch_dir_var.set(directory)
    
    def browse_export_dir(self):
        directory = filedialog.askdirectory(title="选择导出目录")
        if directory:
            self.export_dir_var.set(directory)
    
    def batch_import(self):
        directory = self.batch_dir_var.get()
        if not directory or not os.path.isdir(directory):
            self.batch_status.set("请先选择一个有效的文件夹")
            return
            
        file_filter = self.filter_var.get()
        filepaths = glob.glob(os.path.join(directory, file_filter))
        
        if not filepaths:
            self.batch_status.set(f"在 '{directory}' 中没有找到匹配 '{file_filter}' 的文件")
            return
            
        success_count = 0
        skip_count = 0
        
        for filepath in filepaths:
            if not os.path.isfile(filepath):
                continue
                
            filename = os.path.basename(filepath)
            
            # 如果文件已存在，跳过
            if filename in self.scripts:
                skip_count += 1
                continue
                
            try:
                # 尝试使用ANSI编码读取
                try:
                    with open(filepath, 'r', encoding='ansi') as f:
                        content = f.read()
                except:
                    # 如果ANSI失败，尝试GBK
                    with open(filepath, 'r', encoding='gbk') as f:
                        content = f.read()
                
                self.scripts[filename] = content
                self.script_listbox.insert(tk.END, filename)
                success_count += 1
            except Exception as e:
                print(f"导入文件 {filepath} 时出错: {str(e)}")
        
        # 更新状态
        self.batch_status.set(f"批量导入完成: 成功导入 {success_count} 个脚本, 跳过 {skip_count} 个已存在的脚本")
        
        # 更新列表选择
        if success_count > 0:
            self.script_listbox.selection_clear(0, tk.END)
            self.script_listbox.selection_set(tk.END)
            self.script_listbox.activate(tk.END)
            self.on_script_select()
            self.update_preview()
    
    def batch_export(self):
        directory = self.export_dir_var.get()
        if not directory or not os.path.isdir(directory):
            self.batch_status.set("请先选择一个有效的导出目录")
            return
            
        if not hasattr(self, 'scripts') or not self.scripts:
            self.batch_status.set("没有脚本可以导出")
            return
            
        success_count = 0
        encoding = self.encoding_var.get()
        
        for filename, content in self.scripts.items():
            try:
                filepath = os.path.join(directory, filename)
                with open(filepath, 'w', encoding=encoding) as f:
                    f.write(content)
                success_count += 1
            except Exception as e:
                print(f"导出脚本 {filename} 时出错: {str(e)}")
        
        # 更新设置中的默认导出目录
        self.settings["default_export_dir"] = directory
        self.export_dir_var.set(directory)
        
        self.batch_status.set(f"批量导出完成: 成功导出 {success_count} 个脚本到 '{directory}'")
    
    def delete_all_scripts(self):
        if not hasattr(self, 'scripts') or not self.scripts:
            self.batch_status.set("没有脚本可以删除")
            return
            
        if messagebox.askyesno("确认删除", f"确定要删除所有 {len(self.scripts)} 个脚本吗?"):
            self.scripts.clear()
            self.script_listbox.delete(0, tk.END)
            self.current_script = None
            self.filename_var.set("")
            self.script_editor.delete(1.0, tk.END)
            self.batch_status.set(f"已删除所有脚本")
            self.update_preview()

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchScriptGenerator(root)
    root.mainloop()
