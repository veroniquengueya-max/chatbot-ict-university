import streamlit as st
from deep_translator import GoogleTranslator
from infos_ecole import infos_ecole

st.set_page_config(page_title= "ICT University App")

def traduire(texte, langue_cible):
    if texte.strip()== "":
        return texte
    return GoogleTranslator(source='auto', target = langue_cible).translate(texte)

def detect_langue(texte):
    from langdetect import detect

    texte_lower = texte.lower()
    mots_fr_evidents = ["bonjour", "salut", "merci", "s'il vous plait", "s'il te plait"]
    mots_en_evidents = ["hello", "hi", "thank", "please"]

    if any(mot in texte_lower for mot in mots_fr_evidents):
        return "fr"
    if any(mot in texte_lower for mot in mots_en_evidents):
        return "en"
    
    try:
        langue = detect(texte)
    except:
        langue = "en"
    if langue != "fr":
            langue = "en"
    return langue
        
def chercher_reponse(question_fr, langue):
    if any(mot in question_fr for mot in ["réglement","reglement","règle","regle","rule"]):
        return infos_ecole["reglement"][langue]
    elif any(mot in question_fr for mot in ["frais","scolarité","tuition"]):
        return infos_ecole["frais_scolarite"][langue]
    elif any(mot in question_fr for mot in ["bus","transport"]):
        return infos_ecole["frais_transport"][langue]
    elif any(mot in question_fr for mot in["annonces","announcements", "communiquer"]):
        return infos_ecole["annonces"][langue]
    elif any(mot in question_fr for mot in["activité","activities","club"]):
        return infos_ecole["activites"][langue]
    elif any(mot in question_fr for mot in["licence","master","niveau","bachelor"]):
        return infos_ecole["activities"][langue]
    elif "semestre" in question_fr:
        return "Bonjour! Comment puis-je vous aidez ?" if langue == "fr" else "Hello! How can I help you ?"
    else:
        return "Desole, je ne comprends pas votre question." if langue == "fr" else "Soory, I don't understand your question."

st.sidebar.title("ICT University")
page = st.sidebar.radio("Navigation", ["Chatbot", "QR Codes", "Notes et Statistiques"])

if page == "Chatbot":
    st.title("Chatbot ICT University")
    st.write("Posez vos question/Ask your question (FR/EN)")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Tapez votre question ici....")

    if question:
        st.session_state.messages.append({"role": "user",  "content": question})
        with st.chat_message("user"):
            st.write(question)
        langue = detect_langue(question)
        question_fr = question.lower() if langue == "fr" else traduire(question, "fr").lower()
        reponse = chercher_reponse(question_fr, langue)

        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"):
            st.write(reponse)
            
elif page == "QR Codes":
    st.title("Generation de QR Codes")

    type_qr = st.radio("Type of QR Code", ["Admission", "Paiement"])

    if type_qr == "Admission":
        st.subheader("QR Code d'admission")
        matricule = st.text_input("Matricule de l'etudiant")
        nom_etudiant = st.text_input("Nom de l'etudiant")
        lien_drive = st.text_input("Lien Google Drive (lettre d'admission)")

        if st.button("Generer le QR code d'admission"):
            if matricule and nom_etudiant and lien_drive:
                import qrcode
                import uuid
                import csv
                import os

                identifiant = str(uuid.uuid4())
                dossiar_sortie = "qr codes"
                if not os.path.exists(dossier_sortie):
                    os.makedirs(dossier_sortie)

                fichier_existe = os.path.isfile("correspondance.csv")
                with open("correspondances.csv", mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not fichier_existe:
                        writer.writerow(["identifiant, matricule, nom_etudiant, lien_drive"])
                    writer.writerow([identifiant, matricule, nom_etudiant, lien_drive])
                nom_fichier = f"{dossier_sortie}/qr_{identifiant}.png"
                qr = qrcode.make(lien_drive)
                qr.save(nom_fichier)

                st.success(f"QR code cree pour {nom_etudiant}")
                st.image(nom_fichier, width=250)
            else:
                st.warning("Merci de replir tous les champs")

    elif type_qr == "paiement":
        st.subheader("QR Code de Paiement (lien fixe)")
        matricule_p = st.text_input("Matricule de l'etudiant", key="matricule_paiement")
        nom_eleve = st.text_input("Nom de l'etudiant", key="nom_paiement")
        lien_document = st.text_input("Lien du documentde paiement (Google Doc)")

        if st.button("Generer le QR code de paiement"):
            if matricule_p and nom_eleve and lien_document:
                import qrcode
                import uuid
                import csv
                import os

                identifiant = str(uuid.uuid4())
                dossier_sortie = "qrcodes_paiement"
                if not os.path.exists(dossier_sortie):
                    os.makedirs(dossier_sortie)
                fichier_existe = os.path.isfile("registre_paiements.csv")
                with open("registre_paiements.csv", mode="a",newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not fichier_existe:
                        writer.writer(["identifiant", "matricule", "nom", "lien_document"])
                    writer.writerow([identifiant, matricule_p, nom_eleve, lien_document])
                nom_fichier = f"{dossier_sortie}/paiement_{identifiant}.png"
                qr = qrcode.make(lien_document)
                qr.save(nom_fichier)

                st.success(f"QR code de paiement cree pour {nom_eleve}")
                st.image(nom_fichier, width= 250)
            else:
                st.warning("Merci de remplir tous les champs")
elif page == "Notes et Statistiques":
    st.title("Notes et Statistiques")

    import csv
    import os
    from collections import defaultdict

    def convertir_note(score):
        score = float(score)
        if score >= 80: return "A", 4.0
        elif score >= 70: return "B+", 3.5
        elif score >= 60: return "B", 3.0
        elif score >= 55: return "C+", 2.5
        elif score >= 50: return "C", 2.0
        elif score >= 45: return "D+", 1.5
        elif score >= 40: return "D", 1.0
        else: return "F", 0.0
    onglet = st.radio("Action", ["Saisir une note", "Voir le classement des matieres", "Verifier les ecarts"])

    if onglet == "Saisir une note":
        st.subheader("Ajouter une note(system officiel)")
        etudiant = st.text_input("Nom de l'etudiant")
        matiere = st.text_input("Matiere")
        score = st.text_input("Note (sur 100)")

        if st.button("Enregistrer la note"):
            if etudiant and matiere and score:
                lettre, gpa = convertir_note(score)
                fichier_existe = os.path.isfile("notes.csv")
                with open("notes.csv", mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not fichier_existe:
                        writer.writerow(["etudiant", "matiere", "score", "lettre", "gpa"])
                    writer.writerow([etudiant, matiere, score, lettre, gpa])
                st.success(f"Note enregistree: {etudiant} - {matiere} - {score}/100 ({lettre})")
            else:
                st.warning("Merci de remplir tous les champs")
elif onglet == "Voir le classement des matieres":
    st.subheader("Classement des matieres")
    if os.path.isfile("notes.csv"):
        notes_par_matiere = defaultdict(list)
        with open("notes.csv", mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for ligne in reader:
                try:
                    s = float(ligne["score"])
                    notes_par_matiere[ligne["matiere"]].append(s)
                except ValueError:
                    continue
        if notes_par_matiere:
            moyennes = {m: sum(s)/len(s) for m, s in notes_par_matiere.items()}
            for matiere, moyenne in sorted(moyennes.items(), key=lambda x: x[1], reverse=True):
                st.write(f"{mztiere} : {moyenne:.1f}/100")
            st.bar_chart(moyennes)
        else:
            st.info("Aucune note enregistree pour le moment")
    else:
        st.info("Aucune note enregistree pour le mmoment")

elif onglett == "Verifier les ecarts":
    st.subheader("Ecarts entre professeur et system offiviel")
    if os .path.isfile("notes_professeurs.csv") and os.path.isfile("notes.csv"):
        notes_profs = {}
        with open("notes_professeurs.csv", mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for ligne in reader:
                cle = (lgne["etudiant"], ligne["matiere"])
                notes_profs[cle] = ligne["score"].strip()
        notes_systeme = {}
        with open("notes.csv", mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for ligne in reader:
                cle = (ligne["etudiant"], ligne["matiere"])
                notes_systeme[cle] = ligne["score"].strip()

        ecarts = []
        for cle, note_prof in notes_profs.items():
            note_systeme = notes_systeme.get(cle)
            if note_systeme is None:
                ecarts.append(f"{cle[0]} - {cle[1]}: absent du systeme officiel")
            elif note_prof != note_systeme:
                ecarts.append(f"{cle[0]} - {cle[1]}: Prof a donne {note_prof}, systeme affiche {note_systeme}")

        if ecarts:
            for e in ecarts:
                st.warning(e)
        else:
            st.success("Aucun ecart detecte, tout correspond")
else:
    st.info("Fichiers de notes manquants pour effecuerla verification")
                    
                    





















