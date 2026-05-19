import streamlit as st
import os
import pandas as pd
from streamlit_mic_recorder import mic_recorder,speech_to_text

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
    }

    def __init__(self):
        self.database_path = r"database_example"

        for k, v in self.DEFAULTS.items():
            if k not in st.session_state:
                st.session_state[k] = v
    
    def open_database(self):
        files = ["games.csv", "reviews.csv", "users.csv"]
        data = []

        for name in files:
            path = os.path.join(self.database_path, name)
            if os.path.exists(path):
                data.append(pd.read_csv(path))
            else:
                data.append(pd.DataFrame())

        return data
    
    def display_header(self):
        st.title("🎙️ Voice2Query")
        st.caption("Speech-to-SQL dashboard for interactive database exploration")
        st.divider()

    def show_database(self):
        st.subheader("Database preview")
        st.caption("Inspect the schema before asking a voice query.")

        data = self.open_database()
        tab1, tab2, tab3 = st.tabs(["🎮 Games", "⭐ Reviews", "👤 Users"])

        with tab1:
            st.dataframe(data[0], width="stretch", height=350)
        with tab2:
            st.dataframe(data[1], width="stretch", height=350)
        with tab3:
            st.dataframe(data[2], width="stretch", height=350) 

    
    ## RAWWWWWWWWWWWRRRRRRRRRRRRRRRRRRRRRRRRR
    # def style_button_row(self, clicked_button_ix, n_buttons):
    #     def get_button_indices(button_ix):
    #         return {
    #             'nth_child': button_ix,
    #             'nth_last_child': n_buttons - button_ix + 1
    #         }

    #     clicked_style = """
    #     div[data-testid*="stHorizontalBlock"] > div:nth-child(%(nth_child)s):nth-last-child(%(nth_last_child)s) button {
    #         border-color: rgb(255, 75, 75);
    #         color: rgb(255, 75, 75);
    #         box-shadow: rgba(255, 75, 75, 0.5) 0px 0px 0px 0.2rem;
    #         outline: currentcolor none medium;
    #     }
    #     """
    #     unclicked_style = """
    #     div[data-testid*="stHorizontalBlock"] > div:nth-child(%(nth_child)s):nth-last-child(%(nth_last_child)s) button {
    #         pointer-events: none;
    #         cursor: not-allowed;
    #         opacity: 0.65;
    #         filter: alpha(opacity=65);
    #         -webkit-box-shadow: none;
    #         box-shadow: none;
    #     }
    #     """
    #     style = ""
    #     for ix in range(n_buttons):
    #         ix += 1
    #         if ix == clicked_button_ix:
    #             style += clicked_style % get_button_indices(ix)
    #         else:
    #             style += unclicked_style % get_button_indices(ix)
    #     st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)
    
    def side_bar(self):
        with st.sidebar:
            st.header("🎙️ Query input")
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
                whisper_botton = st.button("Whisper", icon=":material/record_voice_over:", disabled=False, width="stretch", )#on_click=self.style_button_row, args=(1, 2))
            with col2:
                speechmatics_botton = st.button("Speechmatics", icon=":material/record_voice_over:", disabled=False, width="stretch", )#on_click=self.style_button_row, args=(2, 2))
            
            if whisper_botton:
                st.session_state.selected_model = "Whisper"
            if speechmatics_botton:
                st.session_state.selected_model = "Speechmatics"
            
            st.markdown("**Status**")
            st.info(f"Model: **{st.session_state.selected_model}**")

            st.divider()
            
            
            if st.session_state.audio_bytes:
                st.success(":material/done_outline: Audio captured")
                st.audio(st.session_state.audio_bytes, format="audio/wav")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶ Run", width="stretch", type="primary"):
                    self.fake_backend_pipeline(st.session_state.selected_model, audio_blob=audio)
            with col2:
                if st.button("✕ Clear", width="stretch"):
                    clear_toggle = True
                    for k, v in self.DEFAULTS.items():
                        st.session_state[k] = v
                    st.rerun()  


    
    def fake_backend_pipeline(self, model_name, audio_blob=None):
        st.session_state.transcript= "show me the games with rating greater than 8"
        import requests

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

        
        #Old Logic
        """
        Placeholder — replace each step with real backend calls:
        1. transcribe_audio(audio_bytes, model)
        2. refine_text(transcript)
        3. generate_sql(text, schema)
        4. execute_sql(query)
        """
        
        
        st.session_state.corrected_text = "Show me the games with rating greater than 8."
        st.session_state.generated_sql  = (
            "SELECT game_name, rating\n"
            "FROM games\n"
            "WHERE rating > 8\n"
            "ORDER BY rating DESC;"
        )
        st.session_state.query_result = pd.DataFrame({
            "game_name": ["The Witcher 3", "Portal 2", "Hades"],
            "rating":    [9.8, 9.4, 8.9],
        })
        st.session_state.selected_model = model_name
        st.session_state.page = "review"
        st.rerun()
    
    def home_page(self):
        self.display_header()

        col_db, col_info = st.columns([3, 0.8])

        with col_db:
            self.show_database()

        with col_info:
            st.subheader("Pipeline overview")
            st.markdown(
                "1. **Speech input**\n"
                "2. **ASR transcription**\n"
                "3. **Text → SQL with the selected model**\n"
                "4. ▶ **Query execution**\n"
                "5. **Results dashboard**"
            )

        self.side_bar()

    def review_page(self):
        self.display_header()
        st.subheader("Review pipeline output")

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**ASR transcript**")
            st.info(st.session_state.transcript or "_No transcript yet._")

            st.markdown("**Selected model**")
            st.markdown(f"`{st.session_state.selected_model}`")

        with col_right:
            st.markdown("**Generated SQL**")
            st.code(st.session_state.generated_sql, language="sql")

        st.divider()
        col_ok, col_back = st.columns(2)
        with col_ok:
            if st.button("▶ Run query", width="stretch", type="primary"):
                st.session_state.page = "results"
                st.rerun()
        with col_back:
            if st.button("🔄 Re-record", width="stretch"):
                st.session_state.page = "home"
                st.rerun()

    def results_page(self):
        self.display_header()
        st.subheader("Query results")

        col_sql, col_data = st.columns([1, 2])

        with col_sql:
            st.markdown("**Executed SQL**")
            st.code(st.session_state.generated_sql, language="sql")

            st.divider()
            if st.button("⬅ New query", width="stretch"):
                st.session_state.page = "home"
                st.rerun()

        with col_data:
            st.markdown("**Returned rows**")
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



