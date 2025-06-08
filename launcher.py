#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABUBU商品搜索程序启动器
跨平台自动环境检查和配置工具
"""

import os
import sys
import platform
import subprocess
import shutil
import urllib.request
import tempfile
from pathlib import Path
import json


class LabubuLauncher:
    def __init__(self):
        self.system = platform.system().lower()
        self.script_dir = Path(__file__).parent.absolute()
        self.python_cmd = None

        # 标记文件
        self.pip_upgraded_flag = self.script_dir / ".pip_upgraded"
        self.deps_installed_flag = self.script_dir / ".deps_installed"
        self.browser_installed_flag = self.script_dir / ".browser_installed"

        print("🎭 LABUBU商品搜索程序启动器")
        print("=" * 50)
        print(f"🖥️ 操作系统: {platform.system()} {platform.release()}")
        print(f"📁 工作目录: {self.script_dir}")
        print("=" * 50)

    def print_step(self, message):
        """打印步骤信息"""
        print(f"\n🔧 {message}")

    def print_success(self, message):
        """打印成功信息"""
        print(f"✅ {message}")

    def print_error(self, message):
        """打印错误信息"""
        print(f"❌ {message}")

    def print_warning(self, message):
        """打印警告信息"""
        print(f"⚠️ {message}")

    def run_command(self, cmd, check=True, shell=False):
        """运行命令"""
        try:
            if isinstance(cmd, str):
                cmd = cmd.split() if not shell else cmd

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=check, shell=shell
            )
            return result
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e
        except FileNotFoundError:
            if check:
                raise
            return None

    def check_python(self):
        """检查Python环境"""
        self.print_step("检查Python环境...")

        # 检查python3
        result = self.run_command(["python3", "--version"], check=False)
        if result and result.returncode == 0:
            self.python_cmd = "python3"
            self.print_success(f"Python3已安装: {result.stdout.strip()}")
            return True

        # 检查python
        result = self.run_command(["python", "--version"], check=False)
        if result and result.returncode == 0:
            version_output = result.stdout.strip()
            if "Python 3" in version_output:
                self.python_cmd = "python"
                self.print_success(f"Python已安装: {version_output}")
                return True
            else:
                self.print_warning(f"检测到Python 2: {version_output}")

        # 检查py命令（Windows）
        if self.system == "windows":
            result = self.run_command(["py", "-3", "--version"], check=False)
            if result and result.returncode == 0:
                self.python_cmd = "py -3"
                self.print_success(f"Python已安装: {result.stdout.strip()}")
                return True

        self.print_error("未找到Python 3")
        return False

    def install_python_windows(self):
        """在Windows上安装Python"""
        self.print_step("在Windows上安装Python...")

        try:
            # 下载Python安装程序
            python_url = (
                "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
            )
            temp_dir = Path(tempfile.mkdtemp())
            installer_path = temp_dir / "python-installer.exe"

            print("📥 正在下载Python安装程序...")
            urllib.request.urlretrieve(python_url, installer_path)

            print("🔧 正在安装Python...")
            result = self.run_command(
                [
                    str(installer_path),
                    "/quiet",
                    "InstallAllUsers=1",
                    "PrependPath=1",
                    "Include_test=0",
                ]
            )

            if result.returncode == 0:
                self.print_success("Python安装成功！")
                # 清理临时文件
                shutil.rmtree(temp_dir)
                return True
            else:
                self.print_error("Python安装失败")
                return False

        except Exception as e:
            self.print_error(f"Python安装出错: {e}")
            return False

    def install_python_macos(self):
        """在macOS上安装Python"""
        self.print_step("在macOS上安装Python...")

        # 检查Homebrew
        if shutil.which("brew"):
            try:
                result = self.run_command(["brew", "install", "python3"])
                if result.returncode == 0:
                    self.print_success("Python安装成功！")
                    return True
            except:
                pass

        self.print_error("请手动安装Homebrew或Python")
        print(
            '💡 安装Homebrew: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        )
        print("💡 或直接下载Python: https://www.python.org/downloads/")
        return False

    def install_python_linux(self):
        """在Linux上安装Python"""
        self.print_step("在Linux上安装Python...")

        package_managers = [
            (
                ["apt", "update"],
                ["apt", "install", "-y", "python3", "python3-pip", "python3-venv"],
            ),
            (["yum", "update"], ["yum", "install", "-y", "python3", "python3-pip"]),
            (["dnf", "update"], ["dnf", "install", "-y", "python3", "python3-pip"]),
            (
                ["pacman", "-Sy"],
                ["pacman", "-S", "--noconfirm", "python", "python-pip"],
            ),
        ]

        for update_cmd, install_cmd in package_managers:
            if shutil.which(update_cmd[0]):
                try:
                    print(f"🐧 使用{update_cmd[0]}安装Python...")
                    if (
                        "apt" in update_cmd[0]
                        or "yum" in update_cmd[0]
                        or "dnf" in update_cmd[0]
                    ):
                        self.run_command(["sudo"] + update_cmd)
                        self.run_command(["sudo"] + install_cmd)
                    else:
                        self.run_command(["sudo"] + install_cmd)

                    self.print_success("Python安装成功！")
                    return True
                except:
                    continue

        self.print_error("无法自动安装Python，请手动安装")
        return False

    def install_python(self):
        """安装Python"""
        if self.system == "windows":
            return self.install_python_windows()
        elif self.system == "darwin":
            return self.install_python_macos()
        elif self.system == "linux":
            return self.install_python_linux()
        else:
            self.print_error(f"不支持的操作系统: {self.system}")
            return False

    def check_pip(self):
        """检查pip"""
        self.print_step("检查pip环境...")

        cmd = self.python_cmd.split() + ["-m", "pip", "--version"]
        result = self.run_command(cmd, check=False)

        if result and result.returncode == 0:
            self.print_success("pip可用")
            return True
        else:
            self.print_warning("pip不可用，尝试安装...")
            try:
                cmd = self.python_cmd.split() + ["-m", "ensurepip", "--upgrade"]
                self.run_command(cmd)
                self.print_success("pip安装成功")
                return True
            except:
                self.print_error("pip安装失败")
                return False

    def upgrade_pip(self):
        """升级pip"""
        if self.pip_upgraded_flag.exists():
            self.print_success("pip已升级，跳过升级步骤")
            return True

        self.print_step("升级pip...")
        try:
            cmd = self.python_cmd.split() + ["-m", "pip", "install", "--upgrade", "pip"]
            result = self.run_command(cmd)

            if result.returncode == 0:
                self.pip_upgraded_flag.write_text("pip upgraded successfully")
                self.print_success("pip升级完成")
                return True
        except:
            self.print_warning("pip升级失败，但不影响程序运行")
            return True

    def install_dependencies(self):
        """安装依赖"""
        requirements_file = self.script_dir / "requirements.txt"

        if not requirements_file.exists():
            self.print_error("未找到requirements.txt文件")
            return False

        if self.deps_installed_flag.exists():
            self.print_success("依赖已安装，跳过安装步骤")
            return self.verify_dependencies()

        self.print_step("安装项目依赖...")

        try:
            cmd = self.python_cmd.split() + [
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements_file),
            ]
            result = self.run_command(cmd, check=False)

            if result.returncode != 0:
                self.print_warning("使用国内镜像源重试...")
                cmd.extend(["-i", "https://pypi.tuna.tsinghua.edu.cn/simple/"])
                result = self.run_command(cmd)

            if result.returncode == 0:
                self.deps_installed_flag.write_text(
                    "Dependencies installed successfully"
                )
                self.print_success("依赖安装完成")
                return True
            else:
                self.print_error("依赖安装失败")
                return False

        except Exception as e:
            self.print_error(f"依赖安装出错: {e}")
            return False

    def verify_dependencies(self):
        """验证依赖"""
        self.print_step("验证关键依赖...")

        required_modules = ["playwright", "yaml"]

        for module in required_modules:
            cmd = self.python_cmd.split() + ["-c", f"import {module}"]
            result = self.run_command(cmd, check=False)

            if result.returncode != 0:
                self.print_warning(f"{module}未正确安装，重新安装依赖...")
                self.deps_installed_flag.unlink(missing_ok=True)
                return self.install_dependencies()

        self.print_success("所有依赖验证通过")
        return True

    def install_playwright_browser(self):
        """安装Playwright浏览器"""
        if self.browser_installed_flag.exists():
            self.print_success("Playwright浏览器已安装，跳过安装步骤")
            return True

        self.print_step("安装Playwright浏览器...")

        try:
            cmd = self.python_cmd.split() + ["-m", "playwright", "install", "chromium"]
            result = self.run_command(cmd)

            if result.returncode == 0:
                self.browser_installed_flag.write_text(
                    "Playwright browser installed successfully"
                )
                self.print_success("Playwright浏览器安装完成")
                return True
            else:
                self.print_warning(
                    "Playwright浏览器安装失败，程序会在运行时自动尝试安装"
                )
                return True

        except Exception as e:
            self.print_warning(f"Playwright浏览器安装出错: {e}")
            return True

    def check_config(self):
        """检查配置文件"""
        self.print_step("检查配置文件...")

        config_file = self.script_dir / "config.yaml"
        if not config_file.exists():
            self.print_error("未找到config.yaml配置文件")
            return False

        self.print_success("配置文件检查完成")
        return True

    def run_main_program(self):
        """运行主程序"""
        self.print_step("启动LABUBU商品搜索程序...")
        print("=" * 50)

        main_file = self.script_dir / "main.py"
        if not main_file.exists():
            self.print_error("未找到main.py文件")
            return False

        try:
            # 切换到脚本目录
            os.chdir(self.script_dir)

            cmd = self.python_cmd.split() + [str(main_file)]
            subprocess.run(cmd)

        except KeyboardInterrupt:
            print("\n❌ 程序被用户中断")
        except Exception as e:
            self.print_error(f"运行主程序出错: {e}")
            return False

        print("\n" + "=" * 50)
        print("🏁 程序已结束")
        return True

    def run(self):
        """主运行流程"""
        try:
            # 检查Python环境
            if not self.check_python():
                if not self.install_python():
                    input("按回车键退出...")
                    return False
                # 重新检查Python
                if not self.check_python():
                    self.print_error("Python安装后仍无法使用")
                    input("按回车键退出...")
                    return False

            # 检查pip
            if not self.check_pip():
                input("按回车键退出...")
                return False

            # 升级pip
            if not self.upgrade_pip():
                pass

            # 安装依赖
            if not self.install_dependencies():
                input("按回车键退出...")
                return False

            # 安装Playwright浏览器
            if not self.install_playwright_browser():
                pass

            # 检查配置文件
            if not self.check_config():
                input("按回车键退出...")
                return False

            # 运行主程序
            self.run_main_program()

            input("按回车键退出...")
            return True

        except KeyboardInterrupt:
            print("\n❌ 程序被用户中断")
            input("按回车键退出...")
            return False
        except Exception as e:
            self.print_error(f"启动器运行出错: {e}")
            input("按回车键退出...")
            return False


def main():
    """主函数"""
    launcher = LabubuLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
