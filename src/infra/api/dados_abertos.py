import httpx
from fake_useragent import UserAgent
from xml.etree.ElementTree import ElementTree as ET


class ApiDadosAbertos:
    BASE_URL = "https://arquivos.receitafederal.gov.br"
    CAMINHO_MENSAL = f"{BASE_URL}/public.php/dav/files/YggdBLfdninEJX9"
    USER_AGENT = UserAgent()
    HEADERS = {
        "accept": "text/plain,application/xml",
        "user-agent": USER_AGENT.chrome,
        "Content-Type": "text/plain;charset=UTF-8",
    }

    def __init__(self):
        self.session = httpx.Client(timeout=3600.0)

    def consultar_data_base(self, data: str) -> ET.Element:
        response = self.session.request(
            "PROPFIND", f"{self.CAMINHO_MENSAL}/{data}", headers=self.HEADERS
        )
        response.raise_for_status()
        return ET.fromstring(response.text)

    def baixa_base_empresas(self, link_arquivo: str) -> bytes:
        headers = {
            k: v
            for k, v in self.HEADERS.items()
            if k not in {"accept", "Content-Type"}
        }
        response = self.session.get(f"{self.BASE_URL}{link_arquivo}", headers=headers)
        response.raise_for_status()
        return response.content
