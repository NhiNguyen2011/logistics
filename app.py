import streamlit as st
import subprocess
import os
import sys

def run_script(input_text, selected_option):
    with open("temp_input.txt","w") as temp_file:
        temp_file.write(input_text)

    result = subprocess.run([f"{sys.executable}", "country_matching.py", "temp_input.txt", selected_option], capture_output=True, text=True)

    os.remove("temp_input.txt")

    output = result.stdout.replace('\n', '<br>')

    return output, result.stderr  

def clear_text():
    st.session_state["input"] = ""


def main():
    st.title("Prüfung von Ländern")

    user_input = st.text_area("Text hier eingeben:", height=300, key="input")
    
    col1, col2 = st.columns([3, 1])

    selected_option = st.selectbox(
        "Wählen Sie Ihren gewünschten Kunden.", 
        ["Allgemein ohne Wirtschaftszonen", "Clariant Gruppe + Heubach", "Avient Color", "Avient Luxembourg"],
        index=None,
        placeholder="Kunden auswählen ...",
        )

    if st.button("Länder prüfen"):
        output, error = run_script(user_input, selected_option)

        st.subheader("Ergebnis:")
        if output:
            st.markdown(output, unsafe_allow_html=True)
        if error:
            st.error(error)
    


    with col2:
        st.button("Texteingabe löschen", on_click=clear_text)    
    

if __name__ == "__main__":
    main()