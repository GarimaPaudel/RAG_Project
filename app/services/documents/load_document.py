import os
import logging
from langchain_community.document_loaders import PyPDFLoader
import camelot

logger = logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s' 
)

class DocumentTextExtractor:
    """
    A class that extract text from a pdf.
    """
    @staticmethod
    def extract_tables_as_structures(pdf_path):
        structured_tables = []
        # Try lattice first
        for flavor in ["lattice", "stream"]:
            try:
                tables = camelot.read_pdf(pdf_path, pages="all", flavor=flavor)
                for table in tables:
                    df = table.df
                    df = df.applymap(lambda x: x.replace('\n', ' ').strip())
                    structured_tables.append({
                        "markdown": df.to_markdown(index=False)
                    })
            except Exception as e:
                print(f"Error extracting with {flavor}: {e}")
        return structured_tables
    
    @staticmethod
    def extract_text_from_pdf(file):
        loader = PyPDFLoader(file)
        documents = loader.load()
        raw_text = "\n".join([doc.page_content for doc in documents])

        tables = DocumentTextExtractor.extract_tables_as_structures(file)

        return {
            "text": raw_text,
            "tables": tables
        }

    @staticmethod
    def extract_text(file_path):
        file_type = os.path.splitext(file_path)[-1].lower()
        if file_type == ".pdf":
            return DocumentTextExtractor.extract_text_from_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


if __name__ == "__main__":
    obj = DocumentTextExtractor()
    response = obj.extract_text(file_path="data/data.pdf")
    print(response)

