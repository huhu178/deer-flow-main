from Bio import Entrez
from typing import List, Dict, Any
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from typing import Optional, Type
from pydantic import BaseModel, Field # For defining tool arguments schema
import logging

logger = logging.getLogger(__name__)

class PubMedAPIWrapper:
    """
    Wrapper for PubMed API using Bio.Entrez.
    
    This class handles searching PubMed and fetching article details.
    It requires an email address to be provided to NCBI for API usage.
    """
    def __init__(self, email: str = "huhu123178@gmail.com"):
        """
        Initializes the PubMedAPIWrapper.

        Args:
            email: Your email address for NCBI Entrez API. 
                   It's crucial to change this to your actual email if it's still the placeholder.
        """
        if email == "your_email@example.com": 
            print(
                """
                Warning: Please provide a valid email address for PubMed API access.
                Using the default 'your_email@example.com' might lead to issues.
                You should set this to your actual email, for example, in the constructor 
                when creating an instance of PubMedAPIWrapper, or by changing the default value here.
                """
            )
        elif not email or "@" not in email:
            print(
                f"""
                Warning: The provided email '{email}' for PubMed API access appears invalid.
                Please ensure you set a valid email address.
                """
            )
        
        Entrez.email = email # Set your email here for NCBI
        print(f"PubMedAPIWrapper initialized. NCBI Entrez email set to: {Entrez.email}")

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Searches PubMed for articles matching the query.

        Args:
            query: The search query string (e.g., "cancer AND immunotherapy").
            max_results: The maximum number of results to return.

        Returns:
            A list of dictionaries, where each dictionary represents an article
            with keys like 'title', 'abstract', 'authors', 'pmid', 'url', 'doi', etc.
            Returns an empty list if an error occurs or no results are found.
        """
        papers_info = []
        try:
            # 1. Use Entrez.esearch to get PMIDs
            handle = Entrez.esearch(db="pubmed", term=query, retmax=str(max_results), sort="relevance")
            record = Entrez.read(handle)
            handle.close()
            id_list = record["IdList"]

            if not id_list:
                print(f"PubMedAPIWrapper: No PMIDs found for query: '{query}'")
                return []

            # 2. Use Entrez.efetch to get article details from PMIDs
            handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="xml")
            records = Entrez.read(handle) # This will be a list of PubmedArticle records
            handle.close()

            # 3. Parse the results and format them
            for article_xml in records.get('PubmedArticle', []):
                paper_data = {}
                
                # Basic article information
                medline_citation = article_xml.get('MedlineCitation', {})
                article_info = medline_citation.get('Article', {})

                paper_data['pmid'] = str(medline_citation.get('PMID', 'N/A'))
                paper_data['title'] = article_info.get('ArticleTitle', 'N/A')
                
                # Abstract
                abstract_texts = []
                abstract_node = article_info.get('Abstract', {})
                if abstract_node:
                    for abst_text_node in abstract_node.get('AbstractText', []):
                        # AbstractText can be a string or a structured object
                        if isinstance(abst_text_node, str):
                            abstract_texts.append(abst_text_node)
                        elif hasattr(abst_text_node, 'attributes') and 'Label' in abst_text_node.attributes:
                            # Handle structured abstracts (e.g., BACKGROUND:, OBJECTIVE:)
                            label = abst_text_node.attributes['Label']
                            text_content = str(abst_text_node) if abst_text_node else ''
                            abstract_texts.append(f"{label}: {text_content}")
                        elif abst_text_node: # if it's just a plain string content
                             abstract_texts.append(str(abst_text_node))
                paper_data['abstract'] = "\\n".join(abstract_texts) if abstract_texts else 'N/A'

                # Authors
                authors_list = []
                author_nodes = article_info.get('AuthorList', [])
                if author_nodes:
                    for author_node in author_nodes:
                        if author_node.get('LastName') and author_node.get('ForeName'):
                            authors_list.append(f"{author_node.get('ForeName')} {author_node.get('LastName')}")
                        elif author_node.get('CollectiveName'):
                             authors_list.append(author_node.get('CollectiveName'))
                paper_data['authors'] = ", ".join(authors_list) if authors_list else 'N/A'
                
                # Journal Info (optional, but useful)
                journal_info = article_info.get('Journal', {})
                paper_data['journal'] = journal_info.get('Title', 'N/A')
                
                pub_date_node = journal_info.get('JournalIssue', {}).get('PubDate', {})
                year = pub_date_node.get('Year', '')
                month = pub_date_node.get('Month', '') # Month can be an abbreviation or number
                day = pub_date_node.get('Day', '')
                paper_data['publication_date'] = f"{year}-{month}-{day}".strip('-') if year else 'N/A'

                # DOI
                doi = 'N/A'
                article_id_list = article_xml.get('PubmedData', {}).get('ArticleIdList', [])
                for article_id in article_id_list:
                    if article_id.attributes.get('IdType') == 'doi':
                        doi = str(article_id)
                        break
                paper_data['doi'] = doi
                
                # URL to PubMed article
                paper_data['url'] = f"https://pubmed.ncbi.nlm.nih.gov/{paper_data['pmid']}/"
                
                papers_info.append(paper_data)
            
            print(f"PubMedAPIWrapper: Found {len(papers_info)} articles for query: '{query}'")
            return papers_info

        except Exception as e:
            print(f"PubMedAPIWrapper: Error during PubMed search for query '{query}': {e}")
            return []

# Define the input schema for the tool
class PubMedSearchInput(BaseModel):
    query: str = Field(description="The search query string for PubMed. Should use PubMed query syntax.")
    max_results: int = Field(default=5, description="Maximum number of articles to return. Default is 5.")

class PubMedSearchTool(BaseTool):
    """Tool for searching PubMed for medical and scientific articles."""

    name: str = "PubMedSearch"
    description: str = (
        "A search tool for querying the PubMed database. "
        "Use this tool to find medical and scientific articles, research papers, and literature. "
        "Input should be a PubMed query string (e.g., 'COVID-19 vaccine AND 2023[pdat]'). "
        "You can specify the maximum number of results. "
        "Prioritize this tool for questions related to medicine, biology, health, and life sciences."
    )
    args_schema: Type[BaseModel] = PubMedSearchInput
    pubmed_api_wrapper: PubMedAPIWrapper = Field(default_factory=lambda: PubMedAPIWrapper(email="huhu123178@gmail.com")) # Ensure email is set

    def _run(
        self,
        query: str,
        max_results: int = 5, # Default here should match Field default if possible or be clear
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        try:
            logger.info(f"🔍 PubMed搜索开始: '{query}', max_results={max_results}")
            print(f"PubMedSearchTool: Received query='{query}', max_results={max_results}")
            results = self.pubmed_api_wrapper.search(query=query, max_results=max_results)
            
            if not results:
                logger.warning(f"⚠️ PubMed搜索返回空结果: '{query}'")
                return "No results found on PubMed for your query. 在PubMed中未找到相关的医学文献。请尝试调整搜索关键词或使用其他搜索工具。"

            logger.info(f"✅ PubMed搜索成功，找到 {len(results)} 篇文献")
            formatted_results = []
            for i, paper in enumerate(results):
                # Truncate abstract for brevity in the initial response to the LLM
                abstract_snippet = paper.get('abstract', 'N/A')
                if abstract_snippet and abstract_snippet != 'N/A' and len(abstract_snippet) > 300:
                    abstract_snippet = abstract_snippet[:297] + "..."
                
                entry = (
                    f"Result {i+1}:\n"
                    f"  Title: {paper.get('title', 'N/A')}\n"
                    f"  Authors: {paper.get('authors', 'N/A')}\n"
                    f"  Abstract Snippet: {abstract_snippet}\n"
                    f"  PMID: {paper.get('pmid', 'N/A')}\n"
                    f"  URL: {paper.get('url', 'N/A')}\n"
                    f"  DOI: {paper.get('doi', 'N/A')}\n"
                    f"  Publication Date: {paper.get('publication_date', 'N/A')}\n"
                    f"  Journal: {paper.get('journal', 'N/A')}"
                )
                formatted_results.append(entry)
            
            return "\n\n".join(formatted_results)
        except Exception as e:
            logger.error(f"❌ PubMed搜索失败: {e}")
            error_msg = f"PubMed搜索出现错误: {str(e)}"
            
            # 检查是否是网络问题
            if "network" in str(e).lower() or "connection" in str(e).lower() or "timeout" in str(e).lower():
                error_msg += "\n可能的原因：网络连接问题，请检查网络设置。"
            
            # 检查是否是API问题
            if "entrez" in str(e).lower() or "ncbi" in str(e).lower():
                error_msg += "\n可能的原因：NCBI Entrez API访问问题，请检查网络连接。"
            
            return error_msg

    # async def _arun(
    #     self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    # ) -> str:
    #     """Use the tool asynchronously."""
    #     # If PubMedAPIWrapper.search can be made async, implement this
    #     # For now, can raise NotImplementedError or run the sync version if allowed by BaseTool
    #     raise NotImplementedError("PubMedSearchTool does not support asynchronous execution yet.")


if __name__ == '__main__':
    # Example usage (for testing purposes)
    # IMPORTANT: Ensure Entrez.email is set, preferably in the PubMedAPIWrapper constructor
    your_ncbi_email_for_testing = "huhu123178@gmail.com" 
    
    # It's good practice to ensure the email isn't a placeholder if you are directly testing.
    # However, the main Entrez.email setting is handled within PubMedAPIWrapper.
    if "@example.com" in your_ncbi_email_for_testing or not your_ncbi_email_for_testing:
        print("Warning: Testing with a placeholder or empty email. Update 'your_ncbi_email_for_testing' for real tests.")
        # Optionally, you could prevent tests from running with a bad email:
        # exit()

    # The PubMedAPIWrapper will use the email passed to its constructor,
    # or the default if none is passed and the default is changed from the placeholder.
    # For this test, we explicitly pass the email.
    wrapper = PubMedAPIWrapper(email=your_ncbi_email_for_testing)
    
    # Test query 1
    test_query_1 = "COVID-19 vaccine"
    print(f"\nTesting with query: '{test_query_1}'")
    results_1 = wrapper.search(test_query_1, max_results=3)
    if results_1:
        for i, paper in enumerate(results_1):
            print(f"  Result {i+1}:")
            print(f"    Title: {paper.get('title')}")
            print(f"    PMID: {paper.get('pmid')}")
            print(f"    URL: {paper.get('url')}")
            print(f"    Abstract: {paper.get('abstract', 'N/A')[:200]}...") # Showing more of abstract
    else:
        print("  No results found or an error occurred.")

    # Test query 2 (more specific)
    test_query_2 = "artificial intelligence AND radiology AND (lung cancer OR breast cancer) AND 2023[pdat]"
    print(f"\nTesting with query: '{test_query_2}'")
    results_2 = wrapper.search(test_query_2, max_results=2)
    if results_2:
        for i, paper in enumerate(results_2):
            print(f"  Result {i+1}:")
            print(f"    Title: {paper.get('title')}")
            print(f"    PMID: {paper.get('pmid')}")
            print(f"    URL: {paper.get('url')}")
            print(f"    Authors: {paper.get('authors')}")
            print(f"    Journal: {paper.get('journal')}")
            print(f"    DOI: {paper.get('doi')}")
    else:
        print("  No results found or an error occurred.")
    
    # Example of a query that might yield few or no results
    test_query_3 = "unobtainium flux capacitor clinical trial"
    print(f"\nTesting with query: '{test_query_3}'")
    results_3 = wrapper.search(test_query_3, max_results=1)
    if results_3:
        for paper in results_3:
            print(f"    Title: {paper.get('title')}")
    else:
        print("  No results found or an error occurred, as expected for this query.")

    print("\n\n--- Testing PubMedSearchTool ---")
    # Ensure the email used by the tool's internal wrapper is correctly set.
    # The PubMedSearchTool's default_factory for pubmed_api_wrapper already sets the email.
    pubmed_tool = PubMedSearchTool()
    
    # Test case 1 for the tool
    tool_query_1 = "cancer immunotherapy"
    print(f"Tool Test 1 - Query: '{tool_query_1}', Max Results: 2")
    # When BaseTool uses args_schema, parameters are often passed as a single dictionary 
    # to tool.run(), or directly as keyword arguments if the _run method is structured so.
    # Langchain typically expects a single argument for run() which is a dictionary 
    # or a string based on how the tool is defined. Given our Pydantic schema,
    # it expects a dictionary matching the schema fields.
    tool_output_1 = pubmed_tool.run({"query": tool_query_1, "max_results": 2})
    print("Tool Output 1:")
    print(tool_output_1)

    # Test case 2 for the tool (using default max_results from Pydantic model)
    tool_query_2 = "diabetes treatment guidelines 2023[pdat]"
    print(f"\nTool Test 2 - Query: '{tool_query_2}' (default max_results)")
    # The _run method has a default for max_results, but the Pydantic model also has one.
    # The call to tool.run() will pass the arguments, and Pydantic will validate them.
    # If max_results is not provided in the dict, the default from PubMedSearchInput (5) will be used.
    tool_output_2 = pubmed_tool.run({"query": tool_query_2 })
    print("Tool Output 2:")
    print(tool_output_2)

    # Test case 3 - query that might return no results
    tool_query_3 = "quadringenarian narcolepsy in Martian felines"
    print(f"\nTool Test 3 - Query: '{tool_query_3}'")
    tool_output_3 = pubmed_tool.run({"query": tool_query_3, "max_results": 1})
    print("Tool Output 3:")
    print(tool_output_3) 