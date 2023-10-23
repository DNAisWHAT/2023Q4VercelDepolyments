"""Welcome to Reflex! This file outlines the steps to create a basic app."""
from rxconfig import config
from reflexTest import style
import reflex as rx
import asyncio
import openai
import os

os.environ["OPENAI_API_KEY"] = "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"

docs_url = "https://reflex.dev/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


class State(rx.State):
    """The app state."""
    question: str
    chat_history: list[tuple[str, str]]

    async def answer(self):
        #answer 에 self.question을 인수로 하는 API 호출
        session = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": self.question}
        ],
        stop=None,
        temperature=0.7,
        stream=True,
    )
        answer = ""

        self.chat_history.append((self.question, answer))
        self.question = ""
        yield
        for item in session:
            if hasattr(item.choices[0].delta, "content"):
                answer += item.choices[0].delta.content
                self.chat_history[-1] = (
                    self.chat_history[-1][0],
                    answer,
                )
            yield


def chat() -> rx.Component:
    return rx.box(
        rx.foreach(
            State.chat_history, lambda messages: qa(messages[0], messages[1]),
        )
    )

def qa(question:str, answer:str) -> rx.Component:
    return rx.box(
        rx.box(question, text_align="left", style=style.question_style),
        rx.box(answer, text_align="right"),
        margin_y="1em",
    )

def action_bar() -> rx.Component:
    return rx.hstack(
        rx.input(placeholder="chatGPT에게 질문하기",
                 style=style.message_style,
                 on_change=State.set_question,
                 value=State.question
                 ),
        rx.button(
            "발송",
            on_click=State.answer
            )
    )

def index() -> rx.Component:
    return rx.fragment(
        rx.container(chat()),
        action_bar()
    )


# Add state and page to the app.
app = rx.App()
app.add_page(index)
app.compile()
