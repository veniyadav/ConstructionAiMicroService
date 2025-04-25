from groq import Groq
import base64
import os

# Function to encode the image
def encode_image(image_path):
  if not os.path.exists(image_path):
    raise FileNotFoundError(f"The file '{image_path}' does not exist.")
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
def ImageProcessing(imagepath):
    # Getting the base64 string
    base64_image = encode_image(image_path=imagepath)

    client = Groq(api_key="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")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """Analyze this image for any visible construction-related issues or failures,
                such as cracks in walls, broken wires, pipe leakages, sewage overflows, or structural damage. 
                Clearly identify each detected problem, describe its location in the image, and provide a brief 
                explanation of the cause. Then, suggest practical repair methods and list safety measures that 
                should be taken during inspection and repair.."""            
            },

            
            
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": "Please analyze this image and report any issues with suggestions."
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
                ]
            }
            ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )
    return chat_completion.choices[0].message.content

if __name__ == "__main__":
   image_path = r"image\istockphoto-1306206468-612x612.jpg"
   text=ImageProcessing(imagepath=image_path)
   print(text)