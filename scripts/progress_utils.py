# -*- coding: utf-8 -*-
"""
进度显示工具模块
提供进度条和状态显示功能
"""
import sys
import time
from datetime import datetime, timedelta
from threading import Thread, Event

from config import PROGRESS_CONFIG

class ProgressBar:
    """进度条显示类"""
    
    def __init__(self, total, description="", show_percentage=True, show_eta=True, bar_length=50):
        self.total = total
        self.current = 0
        self.description = description
        self.show_percentage = show_percentage
        self.show_eta = show_eta
        self.bar_length = bar_length
        self.start_time = datetime.now()
        self.last_update = 0
        
    def update(self, increment=1, description=None):
        """更新进度"""
        self.current += increment
        if description:
            self.description = description
        
        # 避免过于频繁的更新
        current_time = time.time()
        if current_time - self.last_update < PROGRESS_CONFIG['update_interval']:
            return
        
        self.last_update = current_time
        self._render()
    
    def set_progress(self, current, description=None):
        """设置当前进度"""
        self.current = current
        if description:
            self.description = description
        self._render()
    
    def _render(self):
        """渲染进度条"""
        if self.total <= 0:
            return
        
        percentage = min(self.current / self.total, 1.0)
        filled_length = int(self.bar_length * percentage)
        
        # 构建进度条
        bar = '█' * filled_length + '░' * (self.bar_length - filled_length)
        
        # 构建显示文本
        parts = []
        
        if self.description:
            parts.append(self.description)
        
        parts.append(f'[{bar}]')
        
        if self.show_percentage:
            parts.append(f'{percentage * 100:.1f}%')
        
        parts.append(f'({self.current}/{self.total})')
        
        if self.show_eta and self.current > 0:
            elapsed = datetime.now() - self.start_time
            if percentage > 0:
                eta_seconds = (elapsed.total_seconds() / percentage) * (1 - percentage)
                eta = str(timedelta(seconds=int(eta_seconds)))
                parts.append(f'ETA: {eta}')
        
        # 输出进度条
        line = ' '.join(parts)
        sys.stdout.write('\r' + line.ljust(120))
        sys.stdout.flush()
        
        if self.current >= self.total:
            print()  # 完成时换行

class SpinnerProgress:
    """旋转进度指示器"""
    
    def __init__(self, description="Loading"):
        self.description = description
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.running = False
        self.thread = None
        self.stop_event = Event()
        
    def start(self):
        """开始显示旋转指示器"""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, final_message=None):
        """停止旋转指示器"""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=1.0)
        
        # 清除旋转字符并显示最终消息
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        if final_message:
            print(final_message)
        sys.stdout.flush()
    
    def _spin(self):
        """旋转动画线程"""
        spinner_index = 0
        while self.running and not self.stop_event.is_set():
            char = self.spinner_chars[spinner_index]
            sys.stdout.write(f'\r{char} {self.description}')
            sys.stdout.flush()
            
            spinner_index = (spinner_index + 1) % len(self.spinner_chars)
            self.stop_event.wait(0.1)

class StepProgress:
    """步骤进度显示器"""
    
    def __init__(self, steps, title="执行进度"):
        self.steps = steps
        self.title = title
        self.current_step = 0
        self.start_time = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        print(f"总步骤数: {len(steps)}")
        print(f"预计总时间: {self._format_time(sum(step.get('estimated_time', 0) for step in steps))}")
        print()
    
    def start_step(self, step_index):
        """开始执行步骤"""
        if step_index >= len(self.steps):
            return
        
        self.current_step = step_index
        step = self.steps[step_index]
        
        print(f"[{step_index + 1}/{len(self.steps)}] {step['description']}")
        print(f"预计时间: {self._format_time(step.get('estimated_time', 0))}")
        
        if step.get('estimated_time', 0) > 60:  # 对于长时间任务显示进度条
            return ProgressBar(100, f"步骤 {step_index + 1}")
        else:
            return SpinnerProgress(f"执行中...")
    
    def complete_step(self, step_index, success=True, message=None):
        """完成步骤"""
        if step_index >= len(self.steps):
            return
        
        step = self.steps[step_index]
        status = "✅ 成功" if success else "❌ 失败"
        
        if message:
            print(f"{status}: {message}")
        else:
            print(f"{status}")
        
        print("-" * 60)
    
    def finish(self, success_count, total_time=None):
        """完成所有步骤"""
        if total_time is None:
            total_time = datetime.now() - self.start_time
        
        print(f"\n{'='*60}")
        print("执行完成!")
        print(f"成功步骤: {success_count}/{len(self.steps)}")
        print(f"总耗时: {self._format_time(total_time.total_seconds())}")
        print(f"{'='*60}\n")
    
    def _format_time(self, seconds):
        """格式化时间显示"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            return f"{int(seconds // 60)}分{int(seconds % 60)}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}小时{minutes}分钟"

class ConsoleColors:
    """控制台颜色常量"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'  # 结束颜色
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text, color=ConsoleColors.WHITE):
    """打印彩色文本"""
    print(f"{color}{text}{ConsoleColors.ENDC}")

def print_success(text):
    """打印成功消息"""
    print_colored(f"✅ {text}", ConsoleColors.GREEN)

def print_error(text):
    """打印错误消息"""
    print_colored(f"❌ {text}", ConsoleColors.RED)

def print_warning(text):
    """打印警告消息"""
    print_colored(f"⚠️  {text}", ConsoleColors.YELLOW)

def print_info(text):
    """打印信息消息"""
    print_colored(f"ℹ️  {text}", ConsoleColors.CYAN)

