#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝直播间LABUBU商品搜索演示程序 - Playwright版本
注意：这是一个演示程序，不会实际执行购买操作
"""

import asyncio
import logging
import random
import subprocess
import sys
import os
import yaml
import pyttsx3
from playwright.async_api import async_playwright

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TaobaoLiveSearcher:
    def __init__(self, config_file="config.yaml"):
        """初始化搜索器"""
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

        # 初始化TTS引擎
        self.tts_engine = self.init_tts()

        # 加载配置文件
        self.config = self.load_config(config_file)

        self.user_data_dir = os.path.join(
            os.getcwd(), self.config["browser"]["user_data_dir"]
        )
        self.target_url = self.config["target_url"]
        self.search_keywords = self.config["search_keywords"]
        self.is_running = True  # 控制循环运行
        self.check_count = 0  # 检查次数计数器

    def init_tts(self):
        """初始化TTS语音引擎"""
        try:
            engine = pyttsx3.init()
            # 设置语音属性
            engine.setProperty("rate", 150)  # 语速
            engine.setProperty("volume", 0.8)  # 音量

            # 尝试设置中文语音
            voices = engine.getProperty("voices")
            for voice in voices:
                if (
                    "chinese" in voice.name.lower()
                    or "mandarin" in voice.name.lower()
                    or "zh" in voice.id.lower()
                ):
                    engine.setProperty("voice", voice.id)
                    break

            logger.info("✅ TTS语音引擎初始化成功")
            return engine
        except Exception as e:
            logger.warning(f"⚠️ TTS初始化失败: {e}")
            return None

    def speak(self, text):
        """播放TTS语音"""
        try:
            if self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                logger.info(f"🔊 TTS: {text}")
        except Exception as e:
            logger.error(f"❌ TTS播放失败: {e}")

    def load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            logger.info(f"✅ 成功加载配置文件: {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"❌ 配置文件未找到: {config_file}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"❌ 配置文件格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 加载配置文件失败: {e}")
            raise

    def install_playwright_browsers(self):
        """安装Playwright浏览器"""
        try:
            logger.info("📥 正在安装Playwright浏览器，请稍候...")
            logger.info("⏳ 这可能需要几分钟时间，请耐心等待...")

            # 运行playwright install命令
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时
            )

            if result.returncode == 0:
                logger.info("✅ Playwright浏览器安装成功")
                return True
            else:
                logger.error(f"❌ 浏览器安装失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ 浏览器安装超时")
            return False
        except Exception as e:
            logger.error(f"❌ 安装浏览器时出错: {e}")
            return False

    async def setup_browser(self):
        """设置Playwright浏览器"""
        try:
            logger.info("🚀 正在启动Playwright浏览器...")
            self.playwright = await async_playwright().start()

            # 确保用户数据目录存在
            if not os.path.exists(self.user_data_dir):
                os.makedirs(self.user_data_dir)
                logger.info(f"📁 创建用户数据目录: {self.user_data_dir}")
            else:
                logger.info(f"📁 使用现有用户数据目录: {self.user_data_dir}")

            # 尝试启动Chromium浏览器
            try:
                self.browser = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=self.config["browser"]["headless"],
                    args=self.config["browser"]["args"],
                    user_agent=self.config["browser"]["user_agent"],
                )
                # 使用persistent_context时，browser就是context
                self.context = self.browser

            except Exception as browser_error:
                logger.warning(f"⚠️ 浏览器启动失败: {browser_error}")
                logger.info("🔄 检测到浏览器未安装，正在自动安装...")

                # 自动安装浏览器
                if self.install_playwright_browsers():
                    logger.info("🔄 重新尝试启动浏览器...")
                    # 重新尝试启动浏览器
                    self.browser = (
                        await self.playwright.chromium.launch_persistent_context(
                            user_data_dir=self.user_data_dir,
                            headless=self.config["browser"]["headless"],
                            args=self.config["browser"]["args"],
                            user_agent=self.config["browser"]["user_agent"],
                        )
                    )
                    self.context = self.browser
                else:
                    logger.error("❌ 无法安装浏览器，程序无法继续")
                    return False

            logger.info("✅ Playwright浏览器启动成功 (持久化模式)")
            logger.info("🔐 登录状态将会保持，下次启动无需重新登录")
            return True

        except Exception as e:
            logger.error(f"❌ 浏览器设置失败: {e}")
            logger.info(
                "💡 如果是首次运行，可能需要安装浏览器，请运行: playwright install chromium"
            )
            return False

    async def open_live_room(self):
        """打开淘宝直播间"""
        try:
            # 使用现有页面或创建新页面
            pages = self.context.pages
            if pages:
                self.page = pages[0]

                # 检查当前页面是否已经是目标直播间
                current_url = self.page.url
                if (
                    self.target_url in current_url
                    or "tbzb.taobao.com/live" in current_url
                ):
                    logger.info("✅ 直播间页面已经打开，无需重复打开")
                    return True
            else:
                self.page = await self.context.new_page()

            logger.info(f"正在打开直播间: {self.target_url}")
            await self.page.goto(
                self.target_url,
                wait_until="domcontentloaded",
                timeout=self.config["monitoring"]["page_timeout"],
            )

            await self.page.wait_for_timeout(500)
            logger.info("✅ 直播间页面加载成功")
            return True

        except Exception as e:
            logger.error(f"❌ 打开直播间失败: {e}")
            return False

    async def clear_search_input(self):
        """清空搜索框内容"""
        try:
            logger.info("🧹 正在清空搜索框内容...")

            # 使用配置文件中的选择器
            search_input_selector = self.config["selectors"]["search_input"]
            search_btn_selector = self.config["selectors"]["search_button"]

            # 等待搜索框出现
            await self.page.wait_for_selector(
                search_input_selector,
                timeout=self.config["monitoring"]["search_timeout"],
            )

            # 清空搜索框内容
            search_input = await self.page.query_selector(search_input_selector)
            if search_input:
                await search_input.fill("")
                logger.info("✅ 搜索框内容已清空")

                # 点击搜索按钮
                search_btn = await self.page.query_selector(search_btn_selector)
                if search_btn:
                    await search_btn.click()
            else:
                logger.warning("❌ 未找到搜索框")

        except Exception as e:
            logger.error(f"❌ 清空搜索框失败: {e}")

    async def input_search_keyword(self, keyword):
        """在搜索框中输入指定关键字并点击搜索"""
        try:
            logger.info(f"🔍 正在输入搜索关键字: {keyword}")

            # 使用配置文件中的选择器
            search_input_selector = self.config["selectors"]["search_input"]
            search_btn_selector = self.config["selectors"]["search_button"]

            # 等待搜索框出现
            await self.page.wait_for_selector(
                search_input_selector,
                timeout=self.config["monitoring"]["search_timeout"],
            )

            # 清空搜索框并输入关键字
            search_input = await self.page.query_selector(search_input_selector)
            if search_input:
                # 输入关键字
                await search_input.fill(keyword)
                logger.info(f"✅ 已输入关键字: {keyword}")

                # 点击搜索按钮
                search_btn = await self.page.query_selector(search_btn_selector)
                if search_btn:
                    await search_btn.click()
                    logger.info("✅ 已点击搜索按钮")
                else:
                    # 如果没找到搜索按钮，尝试按回车
                    logger.info("未找到搜索按钮，使用回车键搜索")
                    await search_input.press("Enter")

                # 等待搜索结果加载
                await self.page.wait_for_timeout(500)
                return True
            else:
                logger.warning("❌ 未找到搜索框")
                return False

        except Exception as e:
            self.speak("输入搜索关键字失败")
            logger.error(f"❌ 输入搜索关键字失败: {e}")
            return False

    async def search_products_for_keyword(self, keyword):
        """搜索指定关键字的商品"""
        try:
            logger.info(f"🔍 搜索关键字: {keyword}")
            await self.page.wait_for_timeout(500)

            # 使用配置文件中的商品选择器
            selectors = [self.config["selectors"]["product_title"]]
            products_found = []

            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        logger.info(f"找到 {len(elements)} 个元素 ({selector})")

                        for i, element in enumerate(elements[:20]):  # 增加搜索数量
                            try:
                                text = await element.text_content()

                                # 检查是否包含当前关键字
                                if text and keyword.lower() in text.lower():
                                    logger.info(f"✅ 找到商品: {text.strip()[:100]}...")

                                    # 记录当前页面数量
                                    current_pages = len(self.context.pages)

                                    # 点击商品链接
                                    await element.click()
                                    logger.info("🖱️ 已点击商品")

                                    # 等待新页面加载
                                    await self.page.wait_for_timeout(2000)

                                    # 检查是否有新页面打开
                                    new_pages = len(self.context.pages)
                                    if new_pages > current_pages:
                                        # 切换到新页面
                                        logger.info("🔄 切换到新打开的商品页面")
                                        new_page = self.context.pages[-1]  # 最新的页面
                                        await self.handle_product_page(
                                            new_page, keyword, text.strip()
                                        )
                                    else:
                                        # 在当前页面查找购买按钮
                                        logger.info("🔄 在当前页面处理商品")
                                        await self.handle_product_page(
                                            self.page, keyword, text.strip()
                                        )

                                    # 获取商品编号
                                    goods_num = await self.get_goods_number(element)

                                    product_info = {
                                        "keyword": keyword,
                                        "index": i,
                                        "text": text.strip(),
                                        "selector": selector,
                                        "goods_num": goods_num,
                                    }

                                    products_found.append(product_info)
                                    if goods_num:
                                        logger.info(f"   商品编号: {goods_num}")
                            except:
                                continue
                except:
                    continue

            return products_found

        except Exception as e:
            logger.error(f"❌ 搜索关键字 {keyword} 出错: {e}")
            return []

    async def handle_product_page(self, page, keyword, product_text):
        """处理商品详情页面，查找并点击购买按钮"""
        try:
            logger.info(f"📄 正在处理商品页面: {product_text[:50]}...")

            # 等待页面加载
            await page.wait_for_timeout(1000)

            # 使用配置文件中的购买按钮选择器
            buy_button_selectors = [self.config["selectors"]["buy_button"]]

            for selector in buy_button_selectors:
                try:
                    buy_buttons = await page.query_selector_all(selector)

                    buy_button = None
                    if len(buy_buttons) > 1:
                        logger.info("找到多个购买按钮，选择第二个")
                        buy_button = buy_buttons[1]
                    elif len(buy_buttons) == 1:
                        buy_button = buy_buttons[0]

                    if not buy_button:
                        logger.warning(f"❌ 未找到购买按钮: {selector}")
                        continue

                    logger.info(f"🛒 找到购买按钮: (选择器: {selector})")

                    # 点击购买按钮
                    await buy_button.click()

                    # 播放声音，提示购买按钮已点击
                    self.speak("购买按钮已点击")
                    logger.info("🔊 已播放提示音 - 购买按钮已点击")

                    break
                except:
                    continue

            # 等待一下再继续
            await page.wait_for_timeout(200)

        except Exception as e:
            logger.error(f"❌ 处理商品页面失败: {e}")

    async def search_all_keywords(self):
        """搜索所有关键字"""
        try:
            all_products = []

            logger.info(f"🎯 开始搜索 {len(self.search_keywords)} 个关键字")

            for i, keyword in enumerate(self.search_keywords):
                logger.info(f"📍 搜索进度: {i+1}/{len(self.search_keywords)}")

                # 输入搜索关键字
                if await self.input_search_keyword(keyword):
                    # 搜索当前关键字的商品
                    products = await self.search_products_for_keyword(keyword)

                    if products:
                        logger.info(
                            f"✅ 关键字 '{keyword}' 找到 {len(products)} 个商品"
                        )
                        all_products.extend(products)
                    else:
                        logger.info(f"⚠️ 关键字 '{keyword}' 未找到商品")
                        # 在页面文本中搜索
                        await self.search_keyword_in_page_text(keyword)
                else:
                    logger.warning(f"❌ 关键字 '{keyword}' 搜索输入失败")

                # 每个关键字搜索之间等待一下
                await asyncio.sleep(2)

            await self.clear_search_input()

            if all_products:
                logger.info(f"🎉 总共找到 {len(all_products)} 个相关商品")
                self.display_products_by_keyword(all_products)
            else:
                logger.info("❌ 所有关键字都未找到商品")

            return all_products

        except Exception as e:
            logger.error(f"❌ 搜索所有关键字出错: {e}")
            return []

    async def search_keyword_in_page_text(self, keyword):
        """在页面文本中搜索指定关键字"""
        try:
            page_text = await self.page.text_content("body")

            if keyword.lower() in page_text.lower():
                logger.info(f"✅ 在页面中找到关键词: {keyword}")
                start_index = page_text.lower().find(keyword.lower())
                context_start = max(0, start_index - 50)
                context_end = min(len(page_text), start_index + len(keyword) + 50)
                context = page_text[context_start:context_end]
                logger.info(f"上下文: ...{context}...")
            else:
                logger.info(f"❌ 页面中未找到关键词: {keyword}")

        except Exception as e:
            logger.error(f"❌ 搜索页面文本出错: {e}")

    def display_products_by_keyword(self, products):
        """按关键字分组显示商品信息"""
        print("\n" + "=" * 60)
        print("🎯 找到的商品汇总:")
        print("=" * 60)

        # 按关键字分组
        products_by_keyword = {}
        for product in products:
            keyword = product["keyword"]
            if keyword not in products_by_keyword:
                products_by_keyword[keyword] = []
            products_by_keyword[keyword].append(product)

        # 显示每个关键字的搜索结果
        for keyword, keyword_products in products_by_keyword.items():
            print(f"\n🔍 关键字: {keyword}")
            print(f"找到 {len(keyword_products)} 个商品")
            print("-" * 50)

            for i, product in enumerate(keyword_products):
                print(f"  商品 {i+1}:")
                print(f"  内容: {product['text'][:150]}...")
                if product.get("goods_num"):
                    print(f"  商品编号: {product['goods_num']}")
                else:
                    print("  商品编号: 未找到")
                print("  " + "-" * 30)

        print(f"\n📊 总计找到 {len(products)} 个商品")
        print("=" * 60)

    async def get_goods_number(self, element):
        """获取商品编号 - 从元素的祖父节点查找"""
        try:
            # 使用配置文件中的商品编号选择器
            goods_selector = self.config["selectors"]["goods_number"]

            # 使用 evaluate 在浏览器中执行查找，直接返回商品编号文本
            goods_num = await element.evaluate(
                f"""
                element => {{
                    const greatGrandparent = element.parentElement?.parentElement?.parentElement;
                    if (greatGrandparent) {{
                        const goodsNumElement = greatGrandparent.querySelector("{goods_selector}");
                        return goodsNumElement ? goodsNumElement.textContent?.trim() : null;
                    }}
                    return null;
                }}
            """
            )

            return goods_num if goods_num else None

        except Exception as e:
            logger.error(f"❌ 获取商品编号失败: {e}")
            return None

    async def search_in_page_text(self):
        """在页面文本中搜索"""
        try:
            page_text = await self.page.text_content("body")

            for keyword in self.search_keywords:
                if keyword.lower() in page_text.lower():
                    logger.info(f"✅ 在页面中找到关键词: {keyword}")
                    start_index = page_text.lower().find(keyword.lower())
                    context_start = max(0, start_index - 50)
                    context_end = min(len(page_text), start_index + len(keyword) + 50)
                    context = page_text[context_start:context_end]
                    logger.info(f"上下文: ...{context}...")

        except Exception as e:
            logger.error(f"❌ 搜索页面文本出错: {e}")

    def display_products(self, products):
        """显示商品信息"""
        print("\n" + "=" * 50)
        print("🎯 找到的LABUBU相关商品:")
        print("=" * 50)

        for i, product in enumerate(products):
            # print(f"\n商品 {i+1}:")
            print(f"内容: {product['text'][:200]}...")
            if product.get("goods_num"):
                print(f"商品编号: {product['goods_num']}")
            else:
                print("商品编号: 未找到")
            print("-" * 30)

    async def run_continuous(self):
        """持续运行程序，使用配置文件中的检查间隔"""
        try:
            logger.info("🚀 启动持续监控程序...")

            # 初始化浏览器
            if not await self.setup_browser():
                return False

            if not await self.open_live_room():
                return False

            min_interval = self.config["monitoring"]["min_interval"]
            max_interval = self.config["monitoring"]["max_interval"]

            logger.info("🔄 开始持续监控模式...")
            logger.info(f"⏰ 每{min_interval}-{max_interval}秒随机执行一次检查")
            logger.info("🛑 按 Ctrl+C 可停止程序")

            while self.is_running:
                try:
                    self.check_count += 1
                    logger.info(f"🔍 第 {self.check_count} 次检查开始...")

                    # 执行搜索
                    products = await self.search_all_keywords()

                    if products:
                        logger.info(
                            f"✅ 第 {self.check_count} 次检查完成 - 找到 {len(products)} 个商品"
                        )
                    else:
                        logger.info(f"⚠️ 第 {self.check_count} 次检查完成 - 未找到商品")

                    # 使用配置文件中的随机等待时间
                    wait_time = random.randint(min_interval, max_interval)
                    logger.info(f"⏳ 等待 {wait_time} 秒后进行下次检查...")

                    # 等待指定时间，期间可以被中断
                    await asyncio.sleep(wait_time)

                except KeyboardInterrupt:
                    logger.info("⭕ 接收到中断信号，停止监控...")
                    self.is_running = False
                    break
                except Exception as e:
                    logger.error(f"❌ 第 {self.check_count} 次检查出错: {e}")
                    # 出错后等待30秒再继续
                    logger.info("⏳ 等待30秒后重试...")
                    await asyncio.sleep(30)

            logger.info(f"🏁 监控结束，总共执行了 {self.check_count} 次检查")
            return True

        except KeyboardInterrupt:
            logger.info("⭕ 程序被用户中断")
            self.is_running = False
            return False
        except Exception as e:
            logger.error(f"❌ 持续监控程序出错: {e}")
            return False
        finally:
            await self.cleanup()

    async def cleanup(self):
        """清理资源"""
        try:
            if self.browser:
                await self.browser.close()
                logger.info("🧹 浏览器已关闭")

            if self.playwright:
                await self.playwright.stop()
                logger.info("🧹 Playwright资源已清理")
        except Exception as e:
            logger.error(f"❌ 清理失败: {e}")


async def main():
    """主函数"""
    print("🎭 淘宝直播间LABUBU商品搜索程序")
    print("=" * 50)
    print("📋 功能说明：")
    print("✅ 使用Playwright自带的Chromium浏览器")
    print("✅ 自动下载浏览器（如需要）")
    print("✅ 保持登录状态 (持久化用户数据)")
    print("✅ 使用YAML配置文件管理设置")
    print("✅ 自动搜索LABUBU相关商品")
    print("✅ 智能点击购买按钮")
    print("✅ 持续监控模式")
    print("=" * 50)
    print("📝 配置文件说明：")
    print("• 可在config.yaml中修改搜索关键字")
    print("• 可调整监控间隔和超时设置")
    print("• 可自定义浏览器启动参数")
    print("=" * 50)
    print("📝 首次运行说明：")
    print("1. 程序会自动打开浏览器")
    print("2. 请手动登录淘宝账号")
    print("3. 登录后关闭程序，下次启动无需重新登录")
    print("=" * 50)
    print()

    try:
        searcher = TaobaoLiveSearcher()

        # 显示当前配置信息
        print(f"📍 目标直播间: {searcher.target_url}")
        print(f"🔍 搜索关键字数量: {len(searcher.search_keywords)}")
        print(
            f"⏰ 监控间隔: {searcher.config['monitoring']['min_interval']}-{searcher.config['monitoring']['max_interval']}秒"
        )
        print("=" * 50)

        print("持续监控模式")
        print("=" * 50)

        # 让用户选择运行模式
        while True:
            try:
                await searcher.run_continuous()
            except KeyboardInterrupt:
                print("\n❌ 程序已取消")
                return
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        print("请确保config.yaml文件存在且格式正确")
        return


if __name__ == "__main__":
    asyncio.run(main())
