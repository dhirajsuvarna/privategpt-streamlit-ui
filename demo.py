import streamlit as st
import requests
import constants
import pandas as pd
import json

st.title(constants.TITLE_STR)

if "messages" not in st.session_state:
    st.session_state["messages"] = list()


@st.cache_data
def get_ingested_list():
    response = requests.get(constants.INGESTED_LIST_URL)
    # st.write(response.json())
    file_data = {"File Name": [], "Doc ID": []}
    for file in response.json()["data"]:
        file_data["File Name"].append(file["doc_metadata"]["file_name"])
        file_data["Doc ID"].append(file["doc_id"])

    df = pd.DataFrame.from_dict(file_data)
    df = df.drop_duplicates(subset=["File Name"])
    return df


def parse_sse(isse_response):
    str_line = isse_response.decode("utf-8").strip()
    value = ""
    if str_line != "":
        # exctract data field
        value = str_line.split(":", 1)[1].strip()

    return value


def stream_chat(iRequestBody):
    with st.chat_message("assistant"):
        with st.spinner("Thinking"):
            assistant_message_placeholder = st.empty()
            assistant_response = ""
            with requests.post(
                constants.CHAT_COMPLETION_URL, json=iRequestBody, stream=True
            ) as r:
                for line in r.iter_lines():
                    # print(line)
                    data = parse_sse(line)
                    if data and data != "[DONE]":
                        json_data = json.loads(data)

                        # get the next word
                        delta = json_data["choices"][0]["delta"]["content"]
                        if delta:
                            print(delta, end="")
                            assistant_response = assistant_response + delta
                            assistant_message_placeholder.markdown(
                                assistant_response + "▌"
                            )
                assistant_message_placeholder.markdown(assistant_response)

                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_response}
                )


def chunk_reterival(iRequestBody):
    response = requests.post(constants.CHUNKS_RETRIEVAL_URL, json=iRequestBody)
    if response.status_code == requests.codes.ok:
        response_json = response.json()
        with st.status("Reteriving Chunks", expanded=True):
            all_data = response_json["data"]
            for index, data in enumerate(all_data):
                text = data["text"]
                filename = data["document"]["doc_metadata"].get("file_name")
                page_number = data["document"]["doc_metadata"].get("page_label")
                doc_id = data["document"].get("doc_id")

                st.write(f"{text}")
                st.write(f"**Additional Info:**")
                st.markdown(
                    f"""File Name: {filename}  
                            Page Number: {page_number}  
                            Doc ID: {doc_id}"""
                )
                st.divider()
            st.write(f"**Total Reterived Chunks: {len(all_data)}**")


def clear_messages():
    st.session_state["messages"].clear()


with st.sidebar:
    mode = st.radio(
        "Modes",
        constants.MODES,
        horizontal=True,
        captions=constants.MODE_CAPTIONS,
        on_change=clear_messages,
    )
    if uploaded_file := st.file_uploader("Upload File to chat with"):
        # ingest the data into vector store
        requestBody = {
            "file": (uploaded_file.name, uploaded_file.getvalue()),
        }
        response = requests.post(constants.INGEST_FILE_URL, files=requestBody)
        if response.status_code == requests.codes.ok:
            st.success(f"File Injested Successfully. Doc ID: ")
            num_of_docs = len(response.json()["data"])
            with st.expander(f"{num_of_docs} Number of Docs Generated"):
                st.json(response.json(), expanded=True)
        else:
            st.error(f"File Not Injested")
            st.json(response.json(), expanded=True)

    with st.expander("Ingested Files", expanded=True):
        # show the ingested data from vector store
        st.data_editor(get_ingested_list(), hide_index=True)

    if st.button("Check Health of Server"):
        response = requests.get(constants.HEALTH_URL)
        st.write(response.json())

if prompt := st.chat_input("Ask question on your docs"):
    st.session_state["messages"].append({"role": "user", "content": prompt})

# DISPLAY ALL THE MESSAGES IN THE UI
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# SEND THE QUESTION TO LLM
if (
    len(st.session_state["messages"]) > 0
    and st.session_state["messages"][-1]["role"] != "assistant"
):
    # send the message to LLM depending on the MODE selected by the user
    match mode:
        case "Query Docs":
            requestBody = {
                "include_sources": True,
                "messages": st.session_state["messages"],
                "stream": True,
                "use_context": True,
                "context_filter": {"docs_ids": []},
            }
            stream_chat(requestBody)
        case "LLM Chat":
            requestBody = {
                "include_sources": True,
                "messages": st.session_state["messages"],
                "stream": True,
                "use_context": False,
                "context_filter": {"docs_ids": []},
            }
            stream_chat(requestBody)

        case "Search in Docs":
            requestBody = {
                "text": prompt,
                "context_filter": {"docs_ids": []},
                "limit": 4,
                "prev_next_chunks": 0,
            }
            chunk_reterival(requestBody)
