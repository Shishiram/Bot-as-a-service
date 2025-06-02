import boto3
import json


def llm():
    prompt_data="""
    Act as shakespeare and write a poem on machine learning
    """

    bedrock = boto3.client(service_name="bedrock-runtime")

    payload = {
        "prompt": "Act as shakespeare and write a poem on machine learning",
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    body = json.dumps(payload)

    model_id = "meta.llama3-70b-instruct-v1:0"
    response = bedrock.invoke_model(
        body=body,
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
    )

    response_body = json.loads(response.get("body").read())
    response_text = response_body['generation']
    print(response_text)

if __name__ == "__main__":
    print("HELLO")
    llm()