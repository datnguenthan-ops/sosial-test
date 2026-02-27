import docx
import sys

def read_docx(file_path):
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        content = read_docx(sys.argv[1])
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Content written to {sys.argv[2]}")
    else:
        print("Usage: python read_docx.py <input_docx> <output_txt>")
