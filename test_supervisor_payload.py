"""
Test Supervisor with Actual Payload

Test the enhanced supervisor with the user's actual payload.
"""

import json
import requests

def test_supervisor():
    """Test the supervisor with the actual payload."""
    
    # The user's actual payload
    payload = {
        "agent_output": {
            "summary": "Transparency, often hailed as a cornerstone of trust in digital ecosystems, has been variously interpreted across scholarly discussions. In the realm of blockchain, transparency is not just a technical feature but a philosophical cornerstone that impacts how trust and accountability are constructed within digital networks. The selected papers, although not directly accessible in content, span a range of applications from blockchain's role in food security, biobanking, to its potential in environmental agreements, suggesting a broad field of inquiry into how transparency is operationalized (English and Nezhadian, 2024; Coppoolse et al., 2024; Desira et al., not dated; Franke et al., not dated). However, it can be argued that while these papers collectively affirm the value of blockchain for transparency, they also hint at a broader debate concerning the limits of this transparency. The literature often overlooks the nuanced challenges posed by blockchain's transparency, such as privacy concerns, the complexity of understanding blockchain operations for laypersons, and the risk of false transparency where data integrity might be compromised before being recorded on the blockchain.",
            "key_findings": [],
            "research_gaps": [
                "#### Justification for Thematic Analysis"
            ],
            "methodologies": [],
            "future_directions": [
                "---",
                "**Reference List**",
                "- Coppoolse, K., Ginkel, M. van, Kruseman, G.K., Maarseveen, B. van, Ruyter de Wildt, M. de, & Walton, J. (2024). *Blockchain For Food: Making Sense of Technology and the Impact on Biofortified Seeds*.",
                "- Desira, M., Ebejer, J.P., Ellul, B., Mamo, N., & Martin, G.M. (Not dated). *Dwarna: a blockchain solution for dynamic consent in biobanking*.",
                "- English, S. Matthew & Nezhadian, E. (2024). *Conditions of Full Disclosure: The Blockchain Remuneration Model*.",
                "- Franke, L., Salomo, S., & Schletz, M. (Not dated). *Designing a Blockchain Model for the Paris Agreement's Carbon Market Mechanism*."
            ],
            "full_literature_review": "### Literature Review: Transparency in Blockchain Protocol Layers\n\nThe concept of transparency within blockchain, Web3, and artificial intelligence (AI) has been a hot topic among scholars, with a diverse range of conceptualizations, debates, and identified gaps. This literature review aims to synthesize key academic publications to better understand how transparency is approached across these domains.\n\n#### Contextual Framing\n\nTransparency, often hailed as a cornerstone of trust in digital ecosystems, has been variously interpreted across scholarly discussions. In the realm of blockchain, transparency is not just a technical feature but a philosophical cornerstone that impacts how trust and accountability are constructed within digital networks. The selected papers, although not directly accessible in content, span a range of applications from blockchain's role in food security, biobanking, to its potential in environmental agreements, suggesting a broad field of inquiry into how transparency is operationalized (English and Nezhadian, 2024; Coppoolse et al., 2024; Desira et al., not dated; Franke et al., not dated).\n\n#### Comparative Synthesis\n\nAcross the discussed papers, there appears to be a consensus that blockchain inherently promotes transparency through its immutable and decentralized ledger system. For instance, the application of blockchain in food security, as explored by Coppoolse et al. (2024), underscores the technology's capacity to enhance traceability and accountability in the supply chain. Similarly, Desira et al. (not dated) highlight blockchain's potential in biobanking to ensure dynamic consent, thereby enhancing transparency in how individuals' data are used. This notion aligns with Franke et al.'s (not dated) examination of blockchain in the context of the Paris Agreement, suggesting that blockchain can provide transparent mechanisms for carbon trading.\n\nHowever, it can be argued that while these papers collectively affirm the value of blockchain for transparency, they also hint at a broader debate concerning the limits of this transparency. The literature often overlooks the nuanced challenges posed by blockchain's transparency, such as privacy concerns, the complexity of understanding blockchain operations for laypersons, and the risk of false transparency where data integrity might be compromised before being recorded on the blockchain.\n\n#### Identify Gaps\n\nDespite the rich discussions, there are evident gaps in the literature. Most notably, there is a lack of critical analysis on the paradox of transparency and privacy, especially in sensitive applications like biobanking (Desira et al., not dated). Furthermore, there's an underexplored area concerning the user's ability to interpret and act upon the transparent information provided by blockchain systems. This highlights a need for empirical research on the impact of blockchain's transparency on user trust and engagement. Additionally, the literature seldom addresses the scalability of transparency mechanisms as blockchain applications grow in complexity and size.\n\n#### Justification for Thematic Analysis\n\nGiven the identified gaps, a thematic analysis is justified to delve deeper into the nuances of how transparency is conceptualized and operationalized across different blockchain applications. Such an analysis can unearth the underlying assumptions about transparency that guide current blockchain solutions and identify potential areas for enhancing transparency in a way that balances with other critical values like privacy and usability.\n\n#### Conclusion\n\nIn effect, while the literature underscores the potential of blockchain to enhance transparency across various domains, it also opens up critical debates on the nature of this transparency, its limits, and its implications. As such, a thematic analysis is not only warranted but necessary to advance our understanding of transparency in blockchain applications, providing a nuanced perspective that can guide future research and development efforts.\n\n---\n\n**Reference List**\n\n- Coppoolse, K., Ginkel, M. van, Kruseman, G.K., Maarseveen, B. van, Ruyter de Wildt, M. de, & Walton, J. (2024). *Blockchain For Food: Making Sense of Technology and the Impact on Biofortified Seeds*.\n- Desira, M., Ebejer, J.P., Ellul, B., Mamo, N., & Martin, G.M. (Not dated). *Dwarna: a blockchain solution for dynamic consent in biobanking*.\n- English, S. Matthew & Nezhadian, E. (2024). *Conditions of Full Disclosure: The Blockchain Remuneration Model*.\n- Franke, L., Salomo, S., & Schletz, M. (Not dated). *Designing a Blockchain Model for the Paris Agreement's Carbon Market Mechanism*.",
            "generated_at": "2025-07-25T18:19:07.476645+00:00",
            "documents_analyzed": 5,
            "research_domain": "About blockchain protocol layers, what are they?"
        },
        "agent_type": "literature_review",
        "original_agent_input": {
            "documents": [
                {
                    "title": "Agent-based chatbot in corporate environment",
                    "authors": "{'name': 'Dybedokken, Ole'}, {'name': 'Nilsen, Henrik'}",
                    "year": 2025,
                    "content": "t, the platform is built by Langchain and therefore works seamlessly\nwith their library. It is straightforward to incorporate with an already ex-\nisting Langchain-based application. The platform will show you which tools\nthe agent uses at a certain prompt, with metadata and time spent on cer-\ntain tools. When the LLM is generating text, it has the possibility to show\nthe text created, the number of tokens, and the price. This greatly helps\nwhen using models to see how expensive they are [46].\n39\n--- Page 52 ---\n2.8 Indexing\n2.7.2 Langgraph\nLangraph is as the name may denote, a library built on Langchain and\nshould be incorporated with Langchain. It is built for creating language\nagents as graphs with cycles and the possibility to freely choose the LLM\nframework. It extends the LangChain Expression Language but supports\nthe possibility of adding different chains in cycles. The agent has the re-\nsponsibility to break the cycle when it seems fit. If the agent is a directed\nacyclic graph (",
                    "doi": "None",
                    "source": "",
                    "paper_id": "None",
                    "chunk_index": 74,
                    "research_domain": "Concept of Langraph",
                    "uuid": "db7ff43d-c961-403c-95b4-f9cd2e8ae262",
                    "metadata": {
                        "distance": 0.20376646518707275,
                        "certainty": 0.8981167674064636
                    }
                }
            ],
            "research_domain": "Blockchain Governance",
            "review_type": "thematic"
        }
    }
    
    print("Testing Enhanced Supervisor with Actual Payload")
    print("=" * 50)
    print()
    print("Payload structure:")
    print(f"- agent_type: {payload['agent_type']}")
    print(f"- research_domain (from output): {payload['agent_output']['research_domain']}")
    print(f"- research_domain (from input): {payload['original_agent_input']['research_domain']}")
    print(f"- documents count: {len(payload['original_agent_input']['documents'])}")
    print()
    
    # Test the API endpoint
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/agents/supervisor/check-quality",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_supervisor() 