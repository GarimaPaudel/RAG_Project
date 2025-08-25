import os
import logging
from langchain_community.document_loaders import PDFPlumberLoader

logger = logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s' 
)

class DocumentTextExtractor:
    """
    A class that extract text from a pdf.
    """

    @staticmethod
    def extract_text(file_path):
        file_type = os.path.splitext(file_path)[-1].lower()
        if file_type == ".pdf":
            return DocumentTextExtractor.extract_text_from_pdf(file_path)
        # elif file_type == ".docx" or file_type == ".txt" or file_type == ".md":
        #     return DocumentTextExtractor.extract_text_from_docx_txt_md(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def extract_text_from_pdf(file):
        try:
            loader = PDFPlumberLoader(file)
            documents = loader.load()
            text = ""
            for doc in documents:
                text += doc.page_content
            return text
        except Exception as e:
            print(f"Error extracting text from {file}: {e}")
            return None
        

if __name__ == "__main__":
    obj = DocumentTextExtractor()
    response = obj.extract_text(file_path="data/data.pdf")
    print(response)