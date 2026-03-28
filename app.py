from groq import Groq
import base64
from flask import Flask, request, jsonify, send_from_directory

import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is required")

client = Groq(api_key=GROQ_API_KEY)


app = Flask(__name__, static_url_path='', static_folder="")


def encode_image_bytes(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')


@app.route('/')
def index():
    return app.send_static_file('index.html')



@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify(error='No image file uploaded'), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify(error='No selected file'), 400

    image_data = image_file.read()
    if not image_data:
        return jsonify(error='Empty file content'), 400

    encoded_image = encode_image_bytes(image_data)
    
    # Build prompt once and send to Groq in a single request
    messages = [
        {
            'role': 'system',
            'content': """
                You are a helpful assistant, which classifies the type of waste in the image and provides
                instructions on how to sort it properly for recycling. You can also provide additional information about the waste type, such as its environmental impact and tips for reducing waste. Always respond in a clear and concise manner, and provide actionable advice to help users make informed decisions about waste sorting and recycling. If the image is unclear or does not contain recognizable waste, politely ask the user to upload a clearer image or provide more information about the waste item. Remember to be friendly and supportive in your responses, encouraging users to participate in waste sorting and recycling efforts to help protect the environment. If the image contains multiple waste items, classify each item separately and provide sorting instructions for each one. Always prioritize providing accurate and helpful information to assist users in making environmentally responsible choices.
                """,
        },
        {
            'role': 'user',
            'content': [
                {'type': 'text',
                  'text': "Please analyze the following image of waste and provide sorting instructions. Also, include any relevant information about the waste type and tips for reducing waste. If the image has multiple items, classify each one separately, and provide sorting instructions for each, like bottle cap and bottle itself, what to do with each, also tell about the environmental impact of each item and how to reduce waste related to it., also tell the alternative materials that can be used instead of this waste item to reduce environmental impact. aslo tell the waste should be sorted into which bin, like plastic, paper, glass, metal, or compost."
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:image/jpeg;base64,{encoded_image}",
                    },
                },
            ],
        },
    ]

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model='meta-llama/llama-4-scout-17b-16e-instruct',
        )
        answer = chat_completion.choices[0].message.content
        return jsonify(result=answer)

    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
