from langchain.chat_models.base import BaseChatModel
from langchain.schema.messages import HumanMessage


def image_url_to_text(
    vision_model: BaseChatModel, image_url: str, text_context: str
) -> str:
    description_prompt = (
        "Describe this image in detail."
        " Only use one or two sentences, but include specific details."
        "The image needs to be described in the context"
        " of the following user question:"
        f"START_CONTEXT\n{text_context}\nEND_CONTEXT."
    )
    msg = vision_model.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": description_prompt},
                    {"type": "image_url", "image_url": image_url},
                ]
            )
        ]
    )

    return msg.content
