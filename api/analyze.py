from groq import Groq
import base64
import os
import json

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def encode_image_bytes(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        image_file = request.files.get("image")

        if not image_file:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No image uploaded"})
            }

        image_data = image_file.read()
        encoded_image = encode_image_bytes(image_data)

        messages = [
            {"role": "system", 
             "content": """
                You are a helpful assistant, which classifies the type of waste in the image and provides
                instructions on how to sort it properly for recycling. You can also provide additional information about the waste type, such as its environmental impact and tips for reducing waste. Always respond in a clear and concise manner, and provide actionable advice to help users make informed decisions about waste sorting and recycling. If the image is unclear or does not contain recognizable waste, politely ask the user to upload a clearer image or provide more information about the waste item. Remember to be friendly and supportive in your responses, encouraging users to participate in waste sorting and recycling efforts to help protect the environment. If the image contains multiple waste items, classify each item separately and provide sorting instructions for each one. Always prioritize providing accurate and helpful information to assist users in making environmentally responsible choices.
                """,
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please analyze the following image of waste and provide sorting instructions. Also, include any relevant information about the waste type and tips for reducing waste. If the image has multiple items, classify each one separately, and provide sorting instructions for each, like bottle cap and bottle itself, what to do with each, also tell about the environmental impact of each item and how to reduce waste related to it., also tell the alternative materials that can be used instead of this waste item to reduce environmental impact. aslo tell the waste should be sorted into which bin, like plastic, paper, glass, metal, or compost."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model='meta-llama/llama-4-scout-17b-16e-instruct',
        )

        answer = chat_completion.choices[0].message.content

        

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"result": answer})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"{str(e)}"})
        }