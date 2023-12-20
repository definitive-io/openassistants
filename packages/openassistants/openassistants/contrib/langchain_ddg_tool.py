import os
from typing import Dict, List, Literal, Optional, Sequence

from openassistants.data_models.function_output import FunctionOutput, TextOutput
from openassistants.functions.base import BaseFunction, FunctionExecutionDependency
from openassistants.functions.utils import AsyncStreamVersion


def ddgs_text(query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
    """Run query through DuckDuckGo text search and return results."""
    from duckduckgo_search import DDGS

    proxies = {}
    DDG_HTTP_PROXY = os.getenv("DDG_HTTP_PROXY")
    DDG_HTTPS_PROXY = os.getenv("DDG_HTTPS_PROXY")

    if DDG_HTTP_PROXY and DDG_HTTPS_PROXY:
        proxies = {"http://": DDG_HTTP_PROXY, "https://": DDG_HTTPS_PROXY}

    # Set environment variable for httpx SSL_CERT_FILE to DDG_SSL_CERT_FILE
    DDG_SSL_CERT_FILE = os.getenv("DDG_SSL_CERT_FILE")
    if DDG_SSL_CERT_FILE:
        os.environ["SSL_CERT_FILE"] = DDG_SSL_CERT_FILE
    original_ssl_cert_file = os.environ.get("SSL_CERT_FILE")
    with DDGS(proxies=proxies) as ddgs:
        ddgs_gen = ddgs.text(
            query,
            max_results=max_results,
        )
        results = [r for r in ddgs_gen] if ddgs_gen else []
    if original_ssl_cert_file is not None:
        os.environ["SSL_CERT_FILE"] = original_ssl_cert_file
    else:
        os.environ.pop("SSL_CERT_FILE", None)
    return results


class DuckDuckGoToolFunction(BaseFunction):
    type: Literal["DuckDuckGoToolFunction"] = "DuckDuckGoToolFunction"

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        try:
            if "query" in deps.arguments:
                query = deps.arguments["query"]

                results = ddgs_text(query, max_results=4)
                formatted_results = "\n\n".join(
                    f"**{result['title']}**  \n_{result['body']}_"
                    for index, result in enumerate(results)
                )
                yield [
                    TextOutput(
                        text=f"Found this on DuckDuckGo: \n\n{formatted_results}"
                    )
                ]
            else:
                raise ValueError(
                    f"Query not found in arguments for action function: {self.id}"
                )
        except Exception as e:
            raise RuntimeError(
                f"Error while executing action function {self.id}. function raised: {e}"
            ) from e
