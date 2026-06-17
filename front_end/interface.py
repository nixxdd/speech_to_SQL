import streamlit as st
import os
import pandas as pd
from streamlit_mic_recorder import mic_recorder,speech_to_text
import requests
from utils.check_system import check_ffmpeg, check_speechmatics_api

st.set_page_config(
    page_title="Speech to SQL",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.dialog("⚠️ Error")
def error_dialog(message: str, callback):
    st.error(message)
    callback()
    if st.button("OK"):
        st.rerun()

@st.dialog("⚙️ Setup")
def speechmatics_dialog():
    st.text("Please create an account on Speechmatics and create ane API key, then paste it here.\n Go to https://portal.speechmatics.com/settings/ to create an API Key.")
    api = st.text_input("Speechmatics API Key", key="api_key_input", type="password")
    if st.button("Save"):
        if check_speechmatics_api(api) == True:
            with open("speechmatics_key.txt", "w") as f:
                f.write(api)
            st.session_state.requirements["speechmatics"] = api
            st.rerun()

st.session_state["requirements"] = {
    "speechmatics": False,
    "ffmpeg": False,
    "backend": False
}


class Interface:
    DEFAULTS = {
        "page": "home",
        "selected_model": "Whisper",
        "transcript": "",
        "corrected_text": "",
        "generated_sql": "",
        "query_result": None,
        "audio_bytes": None,
        "is_database_loaded": False,
        "requirements": {
            "speechmatics": False,
            "ffmpeg": False,
            "backend": False
        },
        "just_cleared": False
    }


    def __init__(self):
        for k, v in self.DEFAULTS.items():
            if k not in st.session_state:
                st.session_state[k] = v
        if os.path.exists("speechmatics_key.txt"):
            with open("speechmatics_key.txt", 'r') as f: 
                st.session_state.requirements["speechmatics"] = f.read().strip()
        self._load_db_tables()
        def callback():
            st.session_state.requirements["ffmpeg"] = check_ffmpeg()
        callback()
        if not st.session_state.requirements["ffmpeg"]:
            error_dialog("Please make sure 'ffmpeg' is installed!", callback=callback)
        

    def _get_tables(self) -> list[str]:
        response = requests.get(
            "http://localhost:8000/get_tables",
        )
        if response.ok:
            result = response.json()
            return result
    
    def _query_database(self, query: str) -> pd.DataFrame:
        try:
            response = requests.post(
                        "http://localhost:8000/run_sql",
                        json={
                            'sql_query': query
                        }
                    )
            if response.ok:
                result = response.json()
                print(f"RESULT: {result['records']}")
                return pd.DataFrame(result['records'])
            else:
                print(f'Error {response.status_code}: {response.text}')
        except Exception as e:
            print(e)

    def _load_db_tables(self) -> list[str]:
        if "table_names" not in st.session_state:
            tables = [table.title() for table in self._get_tables()]
            st.session_state.table_names = tables
            st.session_state.requirements["backend"] = True
        
    def display_header(self):
        st.title(":rainbow[:material/mic: Voice2Query]")
        st.caption("Speech-to-SQL dashboard for interactive database exploration")
        st.divider()

    def show_nav_bar(self):
        cols = st.columns(10)  
        for i, col in enumerate(cols):
            with col:
                st.button(f"Button {i+1}")

    def show_database(self):
        st.subheader("Database preview")
        st.caption("Inspect the schema before asking a voice query.")

        if not st.session_state.is_database_loaded:
            self._load_db_tables()
            st.session_state.is_database_loaded = True

        tabs = st.tabs(st.session_state.table_names)
        for (i,tab) in enumerate(tabs):
            with tab:
                current_table_name = st.session_state.table_names[i]
                if current_table_name not in st.session_state:
                    st.session_state[current_table_name] = self._query_database(f"SELECT * FROM {current_table_name};")
                st.dataframe(st.session_state[current_table_name], width="stretch", height=350, hide_index=True)
    
    def side_bar(self):
        st.markdown(
                """
                <style>
                    section[data-testid="stSidebar"] {
                        width: 350px !important; # Set the width to your desired value
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )

        with st.sidebar:
            st.header(":material/mic: Query input")
            st.caption("Choose the ASR model")
            
            col1, col2 = st.columns(2, gap="small", vertical_alignment='center')
            with col1:
                whisper_button = st.button("**Whisper**", icon=":material/record_voice_over:", disabled=False, width="stretch", )#on_click=self.style_button_row, args=(1, 2))
            with col2:
                speechmatics_button = st.button("**Speechmatics**", icon=":material/record_voice_over:", disabled=False, width="stretch", )#on_click=self.style_button_row, args=(2, 2))
            
            if whisper_button:
                st.session_state.selected_model = "Whisper"
            if speechmatics_button:
                if not st.session_state.requirements["speechmatics"]:
                    speechmatics_dialog()
                st.session_state.selected_model = "Speechmatics"

            st.markdown(
                f':color[Model: **{st.session_state.selected_model}**]{{foreground="#8cf7f6"}}'
            , text_alignment="center")
            
            st.divider()

            st.markdown("**Record your query**")

            audio = mic_recorder(
                start_prompt="🔴 Start recording",
                stop_prompt="⏹️ Stop recording",
                use_container_width=True,
                format="wav",
                key="recorder",
            )

            if audio and audio["bytes"] and audio["bytes"] != st.session_state.audio_bytes:
                if st.session_state.get("just_cleared"):
                    st.session_state.just_cleared = False
                else:
                    st.session_state.audio_bytes = audio["bytes"]
                    with st.spinner("🎙️ Transcribing..."):
                        result = self._transcribe_audio(st.session_state.selected_model, audio_blob=audio)
                        if result:
                            st.session_state.transcript = result['transcription']
                            print(f'Transcription: {st.session_state.transcript}')
                    st.rerun()
            
            if st.session_state.audio_bytes:
                st.success(":material/done_outline: Audio captured")
                st.audio(st.session_state.audio_bytes, format="audio/wav")

            if st.session_state.get("transcript"):
                transcribed_text = st.text_area(
                    "Transcription:",
                    value=st.session_state.transcript,
                    height=150,
                    disabled=False
                )
            
            has_content = bool(st.session_state.transcript.strip())
            if st.button("▶ Run", width="stretch", type="primary", disabled= not has_content):
                # self._transcribe_audio(st.session_state.selected_model, audio_blob=audio)
                if st.session_state.transcript != transcribed_text:
                    st.session_state["transcript"] = transcribed_text
                with st.spinner("Processing..."):
                    self._generate_sql_from_text(st.session_state.transcript)
                self.fake_backend_pipeline()

            # with col2:
            #     if st.session_state.get("audio_bytes") or st.session_state.get("transcript"):
            #         if st.button("✕ Clear", width="stretch"):
            #             # requirements = st.session_state.requirements
            #             # selected_model = st.session_state.selected_model
            #             # clear_toggle = True
            #             for k, v in self.DEFAULTS.items():
            #                 st.session_state[k] = v
            #             st.session_state.just_cleared = True
            #             # st.session_state.selected_model = selected_model
            #             # st.session_state.requirements = requirements
            #             st.rerun()

    def _transcribe_audio(self, model_name, audio_blob=None):
        if model_name == "Speechmatics":
            self._store_speechmatics(st.session_state.requirements["speechmatics"])
        st.session_state.transcript= "No Transcription yet"
        response = requests.post(
            "http://localhost:8000/transcribe",
            files={
                'file': ('audio.wav', audio_blob['bytes'], 'audio/wav')
            },
            data={
                'model_name': model_name
            }
        )

        if response.ok:
            result = response.json()
            return result
        else:
            st.error(f'Error {response.status_code}: {response.text}')
            return None
        

    def _fix_wrenai_table_name(self, query: str) -> str:
        while "public_" in query:
            query = query.replace('public_', '')
        return query


    def _store_speechmatics(self, key):
        response =requests.get("http://localhost:8000/store_speechmatics_key",
        params={
            "api_key": key
        })
        return response.json()

    def _generate_sql_from_text(self, question):
        st.session_state.generated_sql  = (
           ""
        )
        response = requests.post(
            "http://localhost:8000/generate_sql",
            json={
                'question': question
            }
        )
        if response.ok:
            result = response.json()
            result_cleaned = self._fix_wrenai_table_name(result['data'])
            st.session_state.generated_sql = result_cleaned
            print(f'SQL: {st.session_state.generated_sql}')
        else:
            st.error(f'Error {response.status_code}: {response.text}')



    def fake_backend_pipeline(self):
        #Old Logic
        """
        Placeholder — replace each step with real backend calls:
        1. transcribe_audio(audio_bytes, model)
        2. refine_text(transcript)
        3. generate_sql(text, schema)
        4. execute_sql(query)
        """
        
        
        st.session_state.corrected_text = "Show me the games with rating greater than 8."
        st.session_state.query_result = pd.DataFrame({
            "game_name": ["The Witcher 3", "Portal 2", "Hades"],
            "rating":    [9.8, 9.4, 8.9],
        })
        st.session_state.page = "review"
        st.rerun()
    
    def home_page(self):
        self.display_header()

     
        self.show_database()
        
        st.divider()
        st.markdown("#### :primary[Pipeline overview]", text_alignment="left")
        col_info, col_img = st.columns([1, 2], gap="small", vertical_alignment="center")
        with col_info:
            st.markdown(
                ":small[:primary["
                "1. **Speech input**  \n"
                "2. **ASR transcription**  \n"
                "3. **Text → SQL with the selected model**  \n"
                "4. ▶ **Query execution**  \n"
                "5. **Results dashboard**"
                "]]",
                text_alignment="left",
                width="stretch",
            )
        with col_img:
            st.image("files/pipeline_overview.svg", width="stretch")

            

        self.side_bar()

    def review_page(self):
        self.display_header()
        st.subheader("Review pipeline output")

        col_left, col_right = st.columns(2, gap="medium", border=True)

        with col_left:
            st.markdown("#### :blue[**ASR transcript**]")
            st.info(st.session_state.transcript or "_No transcript yet._")

            st.markdown("**Selected model**")
            st.markdown(f"`{st.session_state.selected_model}`")

        with col_right:
            st.markdown("#### :orange[**Generated SQL**]")
            st.code(st.session_state.generated_sql, language="sql", wrap_lines=True)

        st.divider()
        col_ok, col_back = st.columns(2)
        with col_ok:
            if st.button(":material/play_arrow: **Run query**", width="stretch", type="primary"):
                st.session_state.query_result = self._query_database(st.session_state.generated_sql)
                print(f'QUERY RESULTS: {st.session_state.query_result}')

                st.session_state.page = "results"
                st.rerun()
        with col_back:
            if st.button(":material/replay: **Re-record**", width="stretch"):
                st.session_state.page = "home"
                st.rerun()

    def results_page(self):
        self.display_header()
        st.subheader("Query results")

        col_sql, col_data = st.columns([1, 2], gap="medium")

        with col_sql:
            st.markdown("#### :orange[**Executed SQL**]")
            st.code(st.session_state.generated_sql, language="sql")

            st.divider()
            if st.button(":material/keyboard_return: **New query**", width="stretch"):
                st.session_state.page = "home"
                st.rerun()

        with col_data:
            st.markdown("#### :primary[**Returned rows**]")
            if st.session_state.query_result is not None:
                st.dataframe(
                    st.session_state.query_result,
                    width="stretch",
                    height=350,
                )
            else:
                st.warning("No result available yet.")


    def display(self):
        if st.session_state.page == "home":
            self.home_page()
        elif st.session_state.page == "review":
            self.review_page()
        elif st.session_state.page == "results":
            self.results_page()

if __name__ == "__main__":
    interface = Interface()
    interface.display()



