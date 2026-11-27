from langextract.inference import OllamaLanguageModel
import langextract as lx

input_text = "What is the capital of India?"
prompt = "Extract the main entity (country and capital) from text."

examples = [
    lx.data.ExampleData(
        text="What is the capital of Germany?",
        extractions=[
            lx.data.Extraction(
                extraction_class="country",
                extraction_text="Germany",
                attributes={"capital": "Berlin"}
            )
        ]
    )
]

result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    language_model_type=lx.inference.OllamaLanguageModel,
    model_id="llama3.2:3b",  # or your model
    model_url="http://localhost:11434",
    fence_output=False,
    use_schema_constraints=False
)

print("\n--------------------------------")
print(result)

print("\n--------------------------------")
# First extraction object
# ext = result.extractions[0]

# country = ext.extraction_text
# capital = ext.attributes.get("capital")

# print("Country:", country)
# print("Capital:", capital)


for ext in result.extractions:
    print("Extraction class:", ext.extraction_class)
    print("Extracted text:", ext.extraction_text)
    print("Attributes:", ext.attributes)



