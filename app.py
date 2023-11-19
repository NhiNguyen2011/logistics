import streamlit as st
import subprocess
import os

def run_script(input_text):
    with open("temp_input.txt","w") as temp_file:
        temp_file.write(input_text)

    result = subprocess.run(["python", "country_matching.py","temp_input.txt"], capture_output=True, text=True)

    os.remove("temp_input.txt")

    output = result.stdout.replace('\n', '<br>')

    return output, result.stderr   

def main():
    st.title("Prüfung von Ländern")

    user_input = st.text_area("Text hier eingeben:")

    if st.button("Länder prüfen"):
        output, error = run_script(user_input)

        st.subheader("Ergebnis:")
        if output:
            st.markdown(output, unsafe_allow_html=True)
        if error:
            st.error(error)

if __name__ == "__main__":
    main()