from PyQt6.QtCore import QThread, pyqtSignal
import threading # Added for asynchronous LLM calls
import speech_recognition as sr
import subprocess
import time

# Historique de la conversation
import json
import os

HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except Exception as e:
        print(f"Erreur sauvegarde historique: {e}")

conversation_history = load_history()

class AudioWorker(QThread):
    # ... (signaux) ...
    signal_listening = pyqtSignal()
    signal_recognized = pyqtSignal(str)
    signal_processing = pyqtSignal(str)
    signal_finished = pyqtSignal(str)
    signal_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_llm_process = None # Pour stocker le processus Claude en cours
        self.is_processing_llm = False

    def run(self):
        print("Worker thread démarré")
        self.listen_and_process()

    def run_claude_async(self, full_prompt, command_part):
        """Exécute Claude dans un thread séparé pour ne pas bloquer l'écoute."""
        global conversation_history # Ensure global access
        self.is_processing_llm = True
        try:
            self.current_llm_process = subprocess.Popen(
                ["claude", "-p", "--dangerously-skip-permissions", full_prompt], 
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                bufsize=1
            )
            
            response = ""
            # Lecture ligne par ligne (permet de tuer le process proprement si besoin)
            for line in self.current_llm_process.stdout:
                print(line, end='')
                response += line
                
            self.current_llm_process.wait()
            
            if self.current_llm_process.returncode == 0:
                clean_response = response.strip()
                
                # --- PARSING ET EXÉCUTION DES COMMANDES LLM ---
                if "[EXEC:" in clean_response:
                    import re
                    # Regex pour capturer [EXEC: commande]
                    commands = re.findall(r"\[EXEC:\s*(.*?)\]", clean_response)
                    for cmd in commands:
                        print(f"Exécution commande LLM : {cmd}")
                        # On utilise hyprctl dispatch exec pour garantir l'ouverture sur le workspace actif
                        try:
                            subprocess.Popen(["hyprctl", "dispatch", "exec", cmd])
                        except Exception as e:
                            print(f"Erreur exécution LLM: {e}")
                    
                    # On nettoie la réponse pour l'affichage (optionnel, on peut laisser le texte explicatif)
                    # clean_response = re.sub(r"\[EXEC:.*?\]", "", clean_response).strip()

                conversation_history.append(("Utilisateur", command_part))
                conversation_history.append(("Claude", clean_response))
                save_history(conversation_history)
                self.signal_finished.emit(clean_response)
            else:
                # Si tué ou erreur
                print("Processus Claude terminé avec code", self.current_llm_process.returncode)
                # If it was terminated by user, we already emitted "Annulé."
                if self.current_llm_process.returncode != -9: # -9 is SIGKILL
                    self.signal_error.emit(f"Claude a terminé avec une erreur: {self.current_llm_process.returncode}")


        except Exception as e:
            print(f"Erreur thread Claude: {e}")
            self.signal_error.emit(str(e))
        finally:
            self.is_processing_llm = False
            self.current_llm_process = None

    def process_command(self, command_part):
        global conversation_history
        self.signal_processing.emit(command_part)
        
        # --- FAST TRACK (Exécution Immédiate sans LLM) ---
        cmd_lower = command_part.lower()
        
        # ... (Fast Track code inchangé) ...
        # Pour les actions d'ouverture, on ferme la fenêtre après (keep_open=False)
        if "ouvre" in cmd_lower or "lance" in cmd_lower:
            if "firefox" in cmd_lower:
                subprocess.Popen(["firefox"])
                self.signal_finished.emit("Firefox lancé")
                return "Firefox lancé", False
            elif "code" in cmd_lower or "vs code" in cmd_lower:
                subprocess.Popen(["code"])
                self.signal_finished.emit("VS Code lancé")
                return "VS Code lancé", False
            elif "terminal" in cmd_lower or "console" in cmd_lower:
                subprocess.Popen(["kitty"]) 
                self.signal_finished.emit("Terminal lancé")
                return "Terminal lancé", False
            elif "fichiers" in cmd_lower or "nautilus" in cmd_lower or "dossier" in cmd_lower:
                subprocess.Popen(["nautilus"])
                self.signal_finished.emit("Fichiers lancé")
                return "Fichiers lancé", False
            
            # --- Sites Web Courants (Fast Track) ---
            elif "youtube" in cmd_lower:
                subprocess.Popen(["firefox", "https://youtube.com"])
                self.signal_finished.emit("YouTube ouvert")
                return "YouTube ouvert", False
            elif "google" in cmd_lower:
                subprocess.Popen(["firefox", "https://google.com"])
                self.signal_finished.emit("Google ouvert")
                return "Google ouvert", False
            elif "github" in cmd_lower:
                subprocess.Popen(["firefox", "https://github.com"])
                self.signal_finished.emit("GitHub ouvert")
                return "GitHub ouvert", False
            elif "chatgpt" in cmd_lower or "openai" in cmd_lower:
                subprocess.Popen(["firefox", "https://chat.openai.com"])
                self.signal_finished.emit("ChatGPT ouvert")
                return "ChatGPT ouvert", False
            elif "amazon" in cmd_lower:
                subprocess.Popen(["firefox", "https://amazon.fr"])
                self.signal_finished.emit("Amazon ouvert")
                return "Amazon ouvert", False
            elif "wikipedia" in cmd_lower:
                subprocess.Popen(["firefox", "https://fr.wikipedia.org"])
                self.signal_finished.emit("Wikipedia ouvert")
                return "Wikipedia ouvert", False
            
            # --- Tentative générique de site web ---
            elif ".com" in cmd_lower or ".fr" in cmd_lower or ".org" in cmd_lower or ".net" in cmd_lower:
                words = cmd_lower.split()
                for w in words:
                    if "." in w and len(w) > 4:
                        url = w if w.startswith("http") else f"https://{w}"
                        subprocess.Popen(["firefox", url])
                        self.signal_finished.emit(f"Site {w} ouvert")
                        return f"Site {w} ouvert", False

            # --- Recherche de Projet (Fast Track) ---
            elif "ouvre le projet" in cmd_lower or "ouvre le dossier" in cmd_lower:
                # Extraction du nom (tout ce qui est après "projet" ou "dossier")
                keyword = ""
                if "projet" in cmd_lower:
                    keyword = cmd_lower.split("projet")[-1].strip()
                elif "dossier" in cmd_lower:
                    keyword = cmd_lower.split("dossier")[-1].strip()
                
                if keyword:
                    self.signal_processing.emit(f"Recherche de '{keyword}'...")
                    # Recherche dans le home directory (max depth 4 pour rapidité)
                    # On cherche un DOSSIER qui contient le mot clé
                    find_cmd = ["find", "/home/yusua", "-maxdepth", "4", "-type", "d", "-iname", f"*{keyword}*", "-print", "-quit"]
                    try:
                        result = subprocess.run(find_cmd, capture_output=True, text=True)
                        path = result.stdout.strip()
                        if path:
                            subprocess.Popen(["code", path])
                            self.signal_finished.emit(f"Projet {keyword} ouvert")
                            return f"Projet {keyword} ouvert", False
                        else:
                            # Si pas trouvé, on laisse Claude gérer ou on le dit
                            pass 
                    except Exception as e:
                        print(f"Erreur find: {e}")
        # -------------------------------------------------
        
        # Construction du prompt avec historique
        history_text = ""
        if conversation_history:
            history_text = "Historique de la conversation :\n"
            for role, msg in conversation_history[-20:]: 
                history_text += f"{role}: {msg}\n"
            history_text += "\n"
        
        system_prompt = (
            "Tu es Claude, un assistant vocal sur Linux. "
            "Réponds de manière concise. "
            "Tu as accès à l'historique de la conversation ci-dessus. "
            "Si l'utilisateur te demande d'ouvrir une application ou un site web que tu ne peux pas faire directement, "
            "réponds avec le format EXACT : [EXEC: commande_linux]. "
            "Exemple : Pour ouvrir Firefox, écris [EXEC: firefox]. "
            "Exemple : Pour ouvrir un site, écris [EXEC: firefox https://site.com]."
        )
        
        full_prompt = f"{system_prompt}\n\n{history_text}Utilisateur: {command_part}"
        print(f"[PROMPT]: {full_prompt}")
        
        # Lancement ASYNCHRONE
        t = threading.Thread(target=self.run_claude_async, args=(full_prompt, command_part))
        t.start()
        
        return "Traitement en cours...", False # On sort de la boucle d'écoute

    def listen_and_process(self):
        # Initialisation de Vosk pour le mot-clé (LOCAL et RAPIDE)
        from vosk import Model, KaldiRecognizer
        import json
        import pyaudio
        import whisper
        import soundfile as sf
        import numpy as np
        import tempfile
        import os
        import wave
        
        print("Chargement du modèle Vosk (Wake Word)...")
        try:
            model = Model("models/fr")
            rec = KaldiRecognizer(model, 16000)
        except Exception as e:
            self.signal_error.emit(f"Erreur modèle Vosk: {e}")
            return

        print("Chargement du modèle Whisper (Transcription)...")
        try:
            # On utilise le modèle 'base' qui est un bon compromis vitesse/précision
            # 'small' est mieux mais plus lent. 'tiny' est très rapide mais moins précis.
            whisper_model = whisper.load_model("base")
        except Exception as e:
            self.signal_error.emit(f"Erreur modèle Whisper: {e}")
            return

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
        
        print("Prêt (Vosk + Whisper) !")
        
        while True:
            print("En attente du mot clé 'Claude' (Local)...")
            
            # 1. ATTENTE DU WAKE WORD (Toujours avec Vosk pour la rapidité)
            while True:
                data = stream.read(2000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    rec.Result() # IMPORTANT: Vider le buffer pour éviter saturation mémoire
                else:
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text and "claude" in partial_text.lower():
                        print(f"Wake Word: {partial_text}")
                        rec.Reset()
                        break
            
            # 2. BOUCLE DE CONVERSATION
            in_conversation = True
            command_buffer = "" # Buffer pour accumuler le texte (Mode Dictée)
            
            while in_conversation:
                # IMPORTANT : On signale qu'on écoute à chaque tour de boucle
                # SAUF si on est en train de traiter une réponse LLM
                if not self.is_processing_llm:
                    self.signal_listening.emit()
                
                print("Écoute de la commande (Conversation)...")
                
                command_text = ""
                start_listen_time = time.time()
                last_partial = ""
                last_change_time = time.time()
                
                # Buffer audio pour Whisper
                audio_frames = []
                
                rec.Reset()
                
                while True:
                    data = stream.read(1000, exception_on_overflow=False)
                    audio_frames.append(data) # On enregistre tout
                    
                    # On utilise Vosk UNIQUEMENT pour le VAD (Détection de parole/silence)
                    # et pour les interruptions rapides (Merci/Stop)
                    if rec.AcceptWaveform(data):
                        # On ignore le résultat final de Vosk, on veut juste savoir que c'est fini
                        pass
                    else:
                        partial_json = json.loads(rec.PartialResult())
                        partial = partial_json.get("partial", "")
                        
                        if partial:
                            if partial != last_partial:
                                last_partial = partial
                                last_change_time = time.time()
                                # print(f"Partiel Vosk (VAD): {partial}")
                                
                                # INTERRUPTION PENDANT LE TRAITEMENT (Priorité Absolue)
                                if self.is_processing_llm:
                                    check_interrupt = partial.lower()
                                    if "merci" in check_interrupt or "arrête" in check_interrupt or "stop" in check_interrupt or "ok claude" in check_interrupt:
                                        print("INTERRUPTION DÉTECTÉE !")
                                        if self.current_llm_process:
                                            self.current_llm_process.terminate()
                                            self.current_llm_process = None
                                        self.is_processing_llm = False
                                        self.signal_finished.emit("Annulé.")
                                        time.sleep(0.5)
                                        if "merci" in check_interrupt or "arrête" in check_interrupt:
                                            in_conversation = False
                                            self.signal_error.emit("STOP_OVERLAY")
                                            break
                                        rec.Reset()
                                        last_partial = ""
                                        audio_frames = [] # Reset audio
                                        continue

                            else:
                                # VAD: 1.2s de silence = fin de phrase
                                if time.time() - last_change_time > 1.2:
                                    print("Fin VAD (Silence détecté)")
                                    break
                    
                    # Timeout: 20s max
                    if time.time() - start_listen_time > 20:
                        print("Timeout écoute")
                        break
                
                # Si on a cassé la boucle à cause d'une interruption "Merci", on sort
                if not in_conversation:
                    break

                # TRANSCRIPTION WHISPER
                if audio_frames:
                    print("Transcription Whisper en cours...")
                    # Sauvegarde temporaire du WAV
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                        temp_wav_path = temp_wav.name
                    
                    try:
                        # Écriture du fichier WAV
                        wf = wave.open(temp_wav_path, 'wb')
                        wf.setnchannels(1)
                        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                        wf.setframerate(16000)
                        wf.writeframes(b''.join(audio_frames))
                        wf.close()
                        
                        # Transcription
                        result = whisper_model.transcribe(temp_wav_path, fp16=False, language='fr') # On peut forcer 'fr' ou laisser auto
                        # Note: fp16=False pour éviter warning CPU
                        
                        command_text = result["text"].strip()
                        print(f"Whisper a entendu : {command_text}")
                        
                    except Exception as e:
                        print(f"Erreur Transcription Whisper: {e}")
                    finally:
                        if os.path.exists(temp_wav_path):
                            os.remove(temp_wav_path)

                if command_text:
                    cmd_lower = command_text.lower()
                    
                    # Si traitement en cours, on ignore (sauf interruption déjà gérée)
                    if self.is_processing_llm:
                        continue

                    # 1. GESTION DES COMMANDES D'ARRÊT IMMÉDIAT
                    if "arrête" in cmd_lower or "stop" in cmd_lower or "ferme" in cmd_lower or "merci" in cmd_lower:
                        print("Commande d'arrêt détectée.")
                        self.signal_finished.emit("Au revoir !")
                        time.sleep(1.5)
                        in_conversation = False
                        self.signal_error.emit("STOP_OVERLAY")
                        break
                    
                    # 2. MODE DICTÉE STRICT : On attend TOUJOURS le trigger
                    
                    # Vérification du TRIGGER "Fin Claude" (Prioritaire)
                    # Whisper est plus précis, donc on peut être plus strict sur les triggers
                    has_trigger = "fin claude" in cmd_lower or "c'est tout" in cmd_lower or "envoyer" in cmd_lower or "terminé" in cmd_lower
                    
                    # On ajoute le texte au buffer
                    if command_buffer:
                        command_buffer += " " + command_text
                    else:
                        command_buffer = command_text
                    
                    # On met à jour l'UI
                    self.signal_recognized.emit(command_buffer + "...")
                    
                    if has_trigger:
                        # On nettoie le trigger
                        final_command = command_buffer
                        # Nettoyage un peu plus smart avec regex pour Whisper qui met de la ponctuation
                        import re
                        triggers = ["fin claude", "c'est tout", "envoyer", "terminé"]
                        for t in triggers:
                            final_command = re.sub(t, "", final_command, flags=re.IGNORECASE)
                        
                        final_command = final_command.strip()
                        # Nettoyage ponctuation finale
                        final_command = final_command.rstrip(".,!?")
                        
                        if not final_command:
                            pass 
                        
                        print(f"Commande validée (Trigger) : {final_command}")
                        self.signal_recognized.emit(final_command)
                        
                        response_text, keep_open = self.process_command(final_command)
                        command_buffer = "" 
                        
                        # MÊME LOGIQUE DE SORTIE
                        if not keep_open:
                            if response_text == "Traitement en cours...":
                                print("LLM lancé, on sort de la boucle d'écoute")
                                in_conversation = False
                                break
                            else:
                                time.sleep(2.0)
                                in_conversation = False
                                self.signal_error.emit("STOP_OVERLAY")
                                break
                        
                        in_conversation = False
                        break
                    else:
                        print(f"Mode Dictée : Accumulation ({len(command_buffer.split())} mots)...")
                        # On continue d'écouter TANT QUE pas de trigger
                        
                else:
                    # Timeout (Rien entendu)
                    if not self.is_processing_llm:
                        if not command_buffer:
                            print("Timeout conversation (Buffer vide).")
                            in_conversation = False
                            self.signal_error.emit("STOP_OVERLAY")
                        else:
                            print("Timeout mais buffer non vide, on attend encore...")
            
            # Fin de conversation, on reset tout pour le prochain Wake Word
            rec.Reset()
