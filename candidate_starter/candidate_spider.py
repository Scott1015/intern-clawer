from framework import BaseSpider, CrawlResult
from framework.models import money_to_cents


from framework.http import SimpleResponse
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from DrissionPage import ChromiumPage, ChromiumOptions
import time



class CandidateSpider(BaseSpider):
    platform = "evaless_com"

    # Add site-specific headers here when needed.
    default_headers = {
        **BaseSpider.default_headers,
    }

    def __init__(self, project_dir: str):
        super().__init__(project_dir)
        # 新增：持久的浏览器对象
        self._browser = None

    def _close_subscribe_popup(self, page):
        """关闭可能出现的订阅弹窗"""
        try:
            # 查找弹窗中的关闭按钮（X）
            close_btn = page.ele('x://div[@class="_ymcart_subscribe_popup subscribe_step_2"]/div[@class="subscribe_popup_con"]/span[@class="subscribe_popup_con_close"][1]', timeout=3)
            if close_btn:
                print("Closing subscribe popup...")
                close_btn.click()
                time.sleep(1)  # 等待弹窗消失
                # 可选：等待弹窗容器消失
                page.ele('.ymcart_subscribe_popup_box', timeout=5, show=False)  # 如果还存在则继续等待
        except Exception as e:
            # 没有弹窗或者已消失，忽略
            pass

    def _get_browser(self):
        """获取或创建浏览器实例（单例）"""
        if self._browser is None:
            co = ChromiumOptions()
            co.auto_port()
            co.set_argument('--no-sandbox')
            co.headless(False)  # 可改为 False 调试
            co.set_argument('--disable-blink-features=AutomationControlled')
            co.set_argument('--disable-gpu')
            co.set_argument('--window-size=1920,1080')
            self._browser = ChromiumPage(co)
        return self._browser

    def fetch_seed(self, seed):
        if seed.get("fixture"):
            return self.http.from_fixture(seed["fixture"], self.project_dir)
        url = seed.get("category_url") or seed.get("list_url") or seed.get("product_url")
        if not url:
            raise ValueError("seed missing url")
        return self._fetch_with_drissionpage(url)

    def _fetch_with_drissionpage(self, url):
        page = self._get_browser()
        page.get(url)

        # 等待页面基础框架加载（body 出现）
        try:
            page.ele('body', timeout=15)
        except:
            pass  # 极端情况仍继续

        # 关闭可能出现的订阅弹窗
        self._close_subscribe_popup(page)

        # 等待页面主体出现（原逻辑）
        try:
            page.ele('#body_box', timeout=30)
        except Exception:
            page.ele('body', timeout=15)

        # 检测挑战页面（原逻辑）
        if "请稍候" in page.html or "challenge" in page.html.lower():
            print(f"Challenge detected for {url}, refreshing...")
            page.refresh()
            time.sleep(5)
            try:
                page.ele('#body_box', timeout=30)
            except Exception:
                page.ele('body', timeout=15)

        html = page.html
        return SimpleResponse(
            status_code=200,
            url=url,
            text=html,
            headers={},
        )

    # 在析构或爬虫结束时关闭浏览器（可选）
    def __del__(self):
        if self._browser:
            self._browser.close()

    def _build_absolute_url(self, base_url, relative_url):
        """absolute URL"""
        if not relative_url:
            return ""
        if relative_url.startswith("http"):
            return relative_url
        return urljoin(base_url, relative_url)

    def iter_category_seeds(self, input_seeds):
        """
        Return category/list-page seeds.

        You may use seeds.json directly, or fetch homepage/navigation here and
        generate category seeds dynamically.
        """
        for seed in input_seeds:
            url = seed.get("category_url")
            print(f"Processing seed: {url}")
            if not url:
                continue

            # 判断是否为首页
            if url.rstrip("/") in ["https://evaless.com", "https://evaless.com/"]:
                print("Fetching homepage...")
                resp = self.fetch_seed(seed)
                print(resp.text[:2000])
                print(f"Status code: {resp.status_code}")
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")

                # 从导航菜单提取分类链接
                # 选择器：.menu_wrapper_bottom .nav-category-new a
                nav_links = soup.select(".menu_wrapper_bottom .nav-category-new a")
                print(f"Found {len(nav_links)} nav links")
                for a in nav_links:
                    href = a.get("href")
                    if href and ("/collections/" in href or href == "/daily-new.html"):
                        cat_name = a.text.strip()
                        cat_id = href.split("/")[-1].split("?")[0]
                        cat_seed = {
                            "category_id": cat_id,
                            "category_name": cat_name,
                            "category_url": self._build_absolute_url(resp.url, href),
                        }
                        yield from self._generate_pagination_seeds(cat_seed)
            else:
                # 直接是分类页，生成其分页
                yield from self._generate_pagination_seeds(seed)

    def _generate_pagination_seeds(self, seed):
        """
        请求第一页，解析分页链接，返回每个分页的种子。
        """
        first_resp = self.fetch_seed(seed)
        if first_resp.status_code != 200:
            yield seed
            return

        soup = BeautifulSoup(first_resp.text, "html.parser")
        # 分类页分页选择器：.common_pages a
        pagination_links = soup.select(".common_pages a")
        page_urls = set()
        for a in pagination_links:
            href = a.get("href")
            if href:
                full_url = self._build_absolute_url(first_resp.url, href)
                page_urls.add(full_url)

        if not page_urls:
            yield seed
            return

        page_urls.add(first_resp.url)
        for page_url in page_urls:
            new_seed = seed.copy()
            new_seed["category_url"] = page_url
            yield new_seed

    def parse_list(self, html_text, seed, final_url):
        """
        Parse a category/list/search page and return product detail seeds.

        Return a list like:
        [
            {
                "product_id": "...",
                "product_url": "https://...",
                "product_name": "...",
                "category_id": seed.get("category_id", ""),
                "category_name": seed.get("category_name", "")
            }
        ]
        """
        soup = BeautifulSoup(html_text, "html.parser")
        products = []

        # 商品卡片选择器：li.foreach_product_2 或 li.product_inner
        cards = soup.select("li.foreach_product_2")
        for card in cards:
            # 获取商品链接
            link = card.select_one(".pro-pic a.pic")
            if not link:
                continue

            href = link.get("href")
            if not href:
                continue

            product_url = self._build_absolute_url(final_url, href)
            # 从 URL 中提取 product_id，如 "dirty-blue-fake-two-piece-top-lc25231196-p1005"
            product_id = href.split("/")[-1].split("?")[0]

            # 商品标题
            name_elem = card.select_one(".pro_content .name")
            name = name_elem.text.strip() if name_elem else ""

            products.append({
                "product_id": product_id,
                "product_url": product_url,
                "product_name": name,
                "category_id": seed.get("category_id", ""),
                "category_name": seed.get("category_name", ""),
            })

        return products

    def parse_product(self, html_text, seed, final_url):
        """
        Parse one product detail page.

        Return:
            CrawlResult(spu=[...], skc=[...], sku=[...])

        See examples/static_shop_spider.py for a small runnable reference.
        """
        soup = BeautifulSoup(html_text, "html.parser")

        # ===== SPU 级别信息 =====
        title_elem = soup.select_one("h1.product_detail_h1")
        title = title_elem.text.strip() if title_elem else ""

        main_img = soup.select_one(".bigimgbox img#middleimag")
        main_image = self._build_absolute_url(
            final_url,
            main_img.get("src") or main_img.get("data-src")
        ) if main_img else ""

        thumbnails = soup.select("#goodsimagelist li a.smallimage")
        pic_list = []
        for img in thumbnails:
            data_pic = img.get("data_pic")
            if data_pic:
                pic_list.append(self._build_absolute_url(final_url, data_pic))
        if not pic_list and main_image:
            pic_list = [main_image]

        price_elem = soup.select_one(".goods_price_info .goods_price")
        if not price_elem:
            price_elem = soup.select_one(".pricebox .goods_price")
        price_text = price_elem.text.strip().replace("$", "").strip() if price_elem else ""
        discounted_price = self.price_to_cents(price_text)

        through_elem = soup.select_one(".goods_market_price_info .goods_market_price")
        through_price = self.price_to_cents(
            through_elem.text.strip().replace("$", "").strip()) if through_elem else None

        currency = "USD"
        brand_info = ""

        desc_elem = soup.select_one("#product-description .card-collapsible_content .rte")
        detail_description = desc_elem.text.strip() if desc_elem else ""

        stock_elem = soup.select_one("#goods_stock_num")
        stock_status = "in stock" if stock_elem and int(stock_elem.text) > 0 else "out of stock"

        spu_id = seed.get("product_id") or final_url.split("/")[-1].split("?")[0]

        spu_record = {
            "spu_id": spu_id,
            "spu_product_title": title,
            "spu_detail_page_url": final_url,
            "spu_main_image_url": main_image,
            "spu_pic_list": pic_list,
            "spu_discounted_price": discounted_price,
            "spu_currency_unit": currency,
            "spu_brand_info": brand_info,
            "spu_detail_description": detail_description,
            "spu_through_price": through_price,
            "spu_stock_status": stock_status,
            "spu_stock_count": "",
            "spu_category": seed.get("category_name", ""),
        }

        # ===== 颜色选项（从 group_codeno_box 获取） =====
        color_box = soup.select_one('dd.group_codeno_box')
        color_options = []
        if color_box:
            for a in color_box.select('a'):
                label = a.select_one('label')
                if label and label.get('color'):
                    color_name = label.get('color')
                    style = label.get('style', '')
                    import re
                    match = re.search(r'url\((.*?)\)', style)
                    color_img = match.group(1) if match else main_image
                    color_options.append({
                        'name': color_name,
                        'img': color_img,
                        'href': a.get('href')
                    })

        # ===== 尺码选项（从 sale_property_box 获取） =====
        size_box = soup.select_one('dl.viewdl.picsize .sale_property_box[property_name="Size"]')
        size_options = []
        if size_box:
            size_options = size_box.select('a.sale_property')

        skc_list = []
        sku_list = []

        def build_skc(color_val, color_img):
            skc_id = f"{spu_id}-{color_val}" if color_val else f"{spu_id}-default"
            return {
                "spu_id": spu_id,
                "skc_id": skc_id,
                "skc_color": color_val or "Default",
                "skc_product_title": title,
                "skc_detail_page_url": final_url,
                "skc_main_image_url": self._build_absolute_url(final_url, color_img or main_image),
                "skc_pic_list": pic_list,
                "skc_discounted_price": discounted_price,
                "skc_currency_unit": currency,
                "skc_through_price": through_price,
                "skc_stock_status": stock_status,
                "skc_stock_count": "",
                "skc_detail_description": detail_description,
            }

        # 处理颜色和尺码组合
        if color_options and size_options:
            for color in color_options:
                skc = build_skc(color['name'], color['img'])
                skc_list.append(skc)
                for size in size_options:
                    size_val = size.text.strip()
                    sku_id = f"{skc['skc_id']}-{size_val}"
                    sku_list.append({
                        "spu_id": spu_id,
                        "skc_id": skc["skc_id"],
                        "sku_id": sku_id,
                        "sku_size": size_val,
                        "sku_image_url": skc["skc_main_image_url"],
                        "sku_discounted_price": discounted_price,
                        "sku_currency_unit": currency,
                        "sku_through_price": through_price,
                        "sku_stock_status": stock_status,
                        "sku_stock_count": "",
                        "sku_attrs": [{"name": "Size", "value": size_val}],
                    })
        elif color_options and not size_options:
            for color in color_options:
                skc = build_skc(color['name'], color['img'])
                skc_list.append(skc)
                sku_id = f"{skc['skc_id']}-default"
                sku_list.append({
                    "spu_id": spu_id,
                    "skc_id": skc["skc_id"],
                    "sku_id": sku_id,
                    "sku_size": "One Size",
                    "sku_image_url": skc["skc_main_image_url"],
                    "sku_discounted_price": discounted_price,
                    "sku_currency_unit": currency,
                    "sku_through_price": through_price,
                    "sku_stock_status": stock_status,
                    "sku_stock_count": "",
                    "sku_attrs": [],
                })
        elif size_options and not color_options:
            skc = build_skc(None, main_image)
            skc_list.append(skc)
            for size in size_options:
                size_val = size.text.strip()
                sku_id = f"{skc['skc_id']}-{size_val}"
                sku_list.append({
                    "spu_id": spu_id,
                    "skc_id": skc["skc_id"],
                    "sku_id": sku_id,
                    "sku_size": size_val,
                    "sku_image_url": main_image,
                    "sku_discounted_price": discounted_price,
                    "sku_currency_unit": currency,
                    "sku_through_price": through_price,
                    "sku_stock_status": stock_status,
                    "sku_stock_count": "",
                    "sku_attrs": [{"name": "Size", "value": size_val}],
                })
        else:  # 无变体
            skc = build_skc(None, main_image)
            skc_list.append(skc)
            sku_id = f"{skc['skc_id']}-default"
            sku_list.append({
                "spu_id": spu_id,
                "skc_id": skc["skc_id"],
                "sku_id": sku_id,
                "sku_size": "One Size",
                "sku_image_url": main_image,
                "sku_discounted_price": discounted_price,
                "sku_currency_unit": currency,
                "sku_through_price": through_price,
                "sku_stock_status": stock_status,
                "sku_stock_count": "",
                "sku_attrs": [],
            })

        return CrawlResult(spu=[spu_record], skc=skc_list, sku=sku_list)

    @staticmethod
    def price_to_cents(value):
        return money_to_cents(value)
