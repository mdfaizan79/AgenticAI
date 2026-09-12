from google import genai

client = genai.Client(
    api_key="AIzaSyAFWtnYf1FEwrGo2Qdoo2yEfsUIr_yiSGU"
)

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Explain how AI works in a few words"
)

print(interaction.output_text)