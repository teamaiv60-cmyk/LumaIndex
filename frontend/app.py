import streamlit as st
import requests


BACKEND="http://127.0.0.1:8000"


st.set_page_config(
    page_title="Local RAG"
)

st.title(
    "📚 Local PDF RAG"
)


pdf=st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)


if pdf:

    files={

        "file":(
            pdf.name,
            pdf,
            "application/pdf"
        )

    }

    if st.button(
        "Upload"
    ):

        r=requests.post(

            f"{BACKEND}/upload",

            files=files

        )

        st.success(
            r.json()
        )


question=st.text_input(
"Ask Question"
)


if st.button(
"Ask"
):

    r=requests.get(

        f"{BACKEND}/ask",

        params={

            "question":
            question

        }

    )

    st.write(

        r.json()

    )


if st.button(
"Generate Summary"
):

    r=requests.get(

        f"{BACKEND}/summary"
    )

    st.write(
        r.json().getValue("answer")
    )