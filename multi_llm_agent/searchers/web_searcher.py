"""
Web検索（DuckDuckGoを使用した簡易実装）
"""

import aiohttp
import requests
from typing import List
from bs4 import BeautifulSoup
from .base import BaseSearcher, SearchResult


class WebSearcher(BaseSearcher):
    """Web検索クラス（DuckDuckGo HTML検索）"""

    @property
    def source_name(self) -> str:
        return "web"

    async def search(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """非同期Web検索"""
        try:
            # DuckDuckGo HTML検索
            url = "https://html.duckduckgo.com/html/"
            params = {"q": query}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    html = await response.text()

            return self._parse_results(html, max_results)

        except Exception as e:
            print(f"Web検索エラー: {e}")
            return []

    def search_sync(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """同期Web検索"""
        try:
            # DuckDuckGo HTML検索
            url = "https://html.duckduckgo.com/html/"
            params = {"q": query}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.post(
                url,
                data=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            return self._parse_results(response.text, max_results)

        except Exception as e:
            print(f"Web検索エラー: {e}")
            return []

    def _parse_results(self, html: str, max_results: int) -> List[SearchResult]:
        """検索結果HTMLをパース"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # DuckDuckGoの検索結果をパース
        result_divs = soup.find_all('div', class_='result', limit=max_results)

        for div in result_divs:
            try:
                # タイトルとURL
                title_tag = div.find('a', class_='result__a')
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                url = title_tag.get('href', '')

                # スニペット
                snippet_tag = div.find('a', class_='result__snippet')
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                result = SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source=self.source_name
                )
                results.append(result)

            except Exception as e:
                # パースエラーは無視して次へ
                continue

        return results
