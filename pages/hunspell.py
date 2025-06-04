# import streamlit as st
# from hunspell import Hunspell

# h = Hunspell()

# st.title("Hunspell Spellchecker Demo")
# user_input = st.text_area("Enter text:", height=150)
# if st.button("Spellcheck"):
#     words = user_input.split()
#     corrected = []
#     for word in words:
#         if not h.spell(word):
#             suggestions = h.suggest(word)
#             corrected.append(suggestions[0] if suggestions else word)
#         else:
#             corrected.append(word)
#     st.subheader("Corrected Text")
#     st.write(' '.join(corrected))
