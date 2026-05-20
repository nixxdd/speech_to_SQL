import streamlit as st
import os
import pandas as pd
from streamlit_mic_recorder import mic_recorder,speech_to_text
import requests

st.set_page_config(
    page_title="Speech to SQL",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


class Interface:

    DEFAULTS = {
        "page": "home",
        "selected_model": "Whisper",
        "transcript": "",
        "corrected_text": "",
        "generated_sql": "",
        "query_result": None,
        "audio_bytes": None,
        "is_database_loaded": False
    }



    def __init__(self):
        self.SQL_TEMPLATES_PATH = r'sql_query_templates'

        for k, v in self.DEFAULTS.items():
            if k not in st.session_state:
                st.session_state[k] = v
    
    def _query_database(self, query: str) -> pd.DataFrame:
        try:
            response = requests.post(
                        "http://localhost:8000/database_query",
                        json={
                            'query_text': query
                        }
                    )

            if response.ok:
                result = response.json()
                print(f'RESULT: {result}')
                return pd.DataFrame(result['data'])
            else:
                print(f'Error {response.status_code}: {response.text}')
        except Exception as e:
            print(e)

    def _load_sql_templates(self, folder_path: str) -> dict[str, str]:
        templates = {}
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    template_name = filename.replace('.txt', '')
                    templates[template_name] = f.read()
        return templates
    
    def _load_db_in_session_state(self):
        if "sql_query_templates" not in st.session_state:
            st.session_state.sql_query_templates = self._load_sql_templates(self.SQL_TEMPLATES_PATH)
        if "games_df" not in st.session_state:
            st.session_state.games_df = self._query_database(st.session_state.sql_query_templates['get_all_games_query'])
        if "reviews_df" not in st.session_state:
            st.session_state.reviews_df = self._query_database(st.session_state.sql_query_templates['get_all_reviews_query'])
        if "users_df" not in st.session_state:
            st.session_state.users_df = self._query_database(st.session_state.sql_query_templates['get_all_users_query'])

    def display_header(self):
        st.title(":rainbow[:material/mic: Voice2Query]")
        st.caption("Speech-to-SQL dashboard for interactive database exploration")
        st.divider()

    def show_database(self):
        st.subheader("Database preview")
        st.caption("Inspect the schema before asking a voice query.")

        if not st.session_state.is_database_loaded:
            self._load_db_in_session_state()
            st.session_state.is_database_loaded = True

        tab1, tab2, tab3 = st.tabs([":material/gamepad: **Games**", ":material/star_shine: **Reviews**", ":material/person_pin: **Users**"])

        with tab1:
            st.dataframe(st.session_state.games_df, width="stretch", height=350, hide_index=True)
        with tab2:
            st.dataframe(st.session_state.reviews_df, width="stretch", height=350, hide_index=True)
        with tab3:
            st.dataframe(st.session_state.users_df, width="stretch", height=350, hide_index=True) 
    
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
            st.markdown("**Record your query**")

            audio = mic_recorder(
                start_prompt="🔴 Start recording",
                stop_prompt="⏹️ Stop recording",
                use_container_width=True,
                format="wav",
                key="recorder",
            )

            if audio and audio["bytes"] != st.session_state.audio_bytes:
                st.session_state.audio_bytes = audio["bytes"]

            st.divider()

            st.caption("Choose the ASR model")
            
            col1, col2 = st.columns(2, gap="small", vertical_alignment='center')
            with col1:
                whisper_botton = st.button("**Whisper**", icon=":material/record_voice_over:", disabled=False, width="stretch", )#on_click=self.style_button_row, args=(1, 2))
            with col2:
                speechmatics_botton = st.button("**Speechmatics**", icon=":material/record_voice_over:", disabled=False, width="stretch", )#on_click=self.style_button_row, args=(2, 2))
            
            if whisper_botton:
                st.session_state.selected_model = "Whisper"
            if speechmatics_botton:
                st.session_state.selected_model = "Speechmatics"
        
            st.markdown(
                f':color[Model: **{st.session_state.selected_model}**]{{foreground="#8cf7f6"}}'
            , text_alignment="center")
            
            st.divider()
            
            
            if st.session_state.audio_bytes:
                st.success(":material/done_outline: Audio captured")
                st.audio(st.session_state.audio_bytes, format="audio/wav")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶ Run", width="stretch", type="primary"):
                    self._transcribe_audio(st.session_state.selected_model, audio_blob=audio)
                    self._generate_sql_from_text(st.session_state.transcript)
                    self.fake_backend_pipeline()
            with col2:
                if st.button("✕ Clear", width="stretch"):
                    clear_toggle = True
                    for k, v in self.DEFAULTS.items():
                        st.session_state[k] = v
                    st.rerun()  


    def _transcribe_audio(self, model_name, audio_blob=None):
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
            st.session_state.transcript = result['transcription']
            print(f'Transcription: {st.session_state.transcript}')
        else:
            st.error(f'Error {response.status_code}: {response.text}')

    def _fix_wrenai_table_name(self, query: str) -> str:
        while "public_" in query:
            query = query.replace('public_', '')
        return query

    def _generate_sql_from_text(self, question):
        st.session_state.generated_sql  = (
            "SELECT game_name, rating\n"
            "FROM games\n"
            "WHERE rating > 8\n"
            "ORDER BY rating DESC;"
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
            st.image("files/pipeline_overview.png", width="stretch")

            

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



