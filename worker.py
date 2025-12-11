from PyQt6.QtCore import QThread, pyqtSignal
import threading # Added for asynchronous LLM calls
import speech_recognition as sr
import subprocess
import time

# Conversation history
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
        print(f"Error saving history: {e}")

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
        self.current_llm_process = None # To store the current Claude process
        self.is_processing_llm = False

    def run(self):
        print("Worker thread started")
        self.listen_and_process()

    def run_claude_async(self, full_prompt, command_part):
        """Runs Claude in a separate thread to avoid blocking listening."""
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
            # Read line by line (allows killing the process cleanly if needed)
            for line in self.current_llm_process.stdout:
                print(line, end='')
                response += line
                
            self.current_llm_process.wait()
            
            if self.current_llm_process.returncode == 0:
                clean_response = response.strip()
                
                # --- LLM COMMAND PARSING AND EXECUTION ---
                if "[EXEC:" in clean_response:
                    import re
                    # Regex to capture [EXEC: command]
                    commands = re.findall(r"\[EXEC:\s*(.*?)\]", clean_response)
                    for cmd in commands:
                        print(f"Executing LLM command: {cmd}")
                        # Use hyprctl dispatch exec to ensure opening on the active workspace
                        try:
                            subprocess.Popen(["hyprctl", "dispatch", "exec", cmd])
                        except Exception as e:
                            print(f"LLM execution error: {e}")
                    
                    # Clean the response for display (optional, we can leave the explanatory text)
                    # clean_response = re.sub(r"\[EXEC:.*?\]", "", clean_response).strip()

                conversation_history.append(("User", command_part))
                conversation_history.append(("Claude", clean_response))
                save_history(conversation_history)
                self.signal_finished.emit(clean_response)
            else:
                # If killed or error
                print("Claude process terminated with code", self.current_llm_process.returncode)
                # If it was terminated by user, we already emitted "Cancelled."
                if self.current_llm_process.returncode != -9: # -9 is SIGKILL
                    self.signal_error.emit(f"Claude terminated with an error: {self.current_llm_process.returncode}")


        except Exception as e:
            print(f"Claude thread error: {e}")
            self.signal_error.emit(str(e))
        finally:
            self.is_processing_llm = False
            self.current_llm_process = None

    def process_command(self, command_part):
        global conversation_history
        self.signal_processing.emit(command_part)
        
        # --- FAST TRACK (Immediate Execution without LLM) ---
        cmd_lower = command_part.lower()
        
        # ... (Fast Track code unchanged) ...
        # For opening actions, we close the window after (keep_open=False)
        if "open" in cmd_lower or "launch" in cmd_lower:
            if "firefox" in cmd_lower:
                subprocess.Popen(["firefox"])
                self.signal_finished.emit("Firefox launched")
                return "Firefox launched", False
            elif "code" in cmd_lower or "vs code" in cmd_lower:
                subprocess.Popen(["code"])
                self.signal_finished.emit("VS Code launched")
                return "VS Code launched", False
            elif "terminal" in cmd_lower or "console" in cmd_lower:
                subprocess.Popen(["kitty"]) 
                self.signal_finished.emit("Terminal launched")
                return "Terminal launched", False
            elif "files" in cmd_lower or "nautilus" in cmd_lower or "folder" in cmd_lower:
                subprocess.Popen(["nautilus"])
                self.signal_finished.emit("Files launched")
                return "Files launched", False
            
            # --- Common Websites (Fast Track) ---
            elif "youtube" in cmd_lower:
                subprocess.Popen(["firefox", "https://youtube.com"])
                self.signal_finished.emit("YouTube opened")
                return "YouTube opened", False
            elif "google" in cmd_lower:
                subprocess.Popen(["firefox", "https://google.com"])
                self.signal_finished.emit("Google opened")
                return "Google opened", False
            elif "github" in cmd_lower:
                subprocess.Popen(["firefox", "https://github.com"])
                self.signal_finished.emit("GitHub opened")
                return "GitHub opened", False
            elif "chatgpt" in cmd_lower or "openai" in cmd_lower:
                subprocess.Popen(["firefox", "https://chat.openai.com"])
                self.signal_finished.emit("ChatGPT opened")
                return "ChatGPT opened", False
            elif "amazon" in cmd_lower:
                subprocess.Popen(["firefox", "https://amazon.fr"])
                self.signal_finished.emit("Amazon opened")
                return "Amazon opened", False
            elif "wikipedia" in cmd_lower:
                subprocess.Popen(["firefox", "https://fr.wikipedia.org"])
                self.signal_finished.emit("Wikipedia opened")
                return "Wikipedia opened", False
            
            # --- Generic website attempt ---
            elif ".com" in cmd_lower or ".fr" in cmd_lower or ".org" in cmd_lower or ".net" in cmd_lower:
                words = cmd_lower.split()
                for w in words:
                    if "." in w and len(w) > 4:
                        url = w if w.startswith("http") else f"https://{w}"
                        subprocess.Popen(["firefox", url])
                        self.signal_finished.emit(f"Site {w} opened")
                        return f"Site {w} opened", False

            # --- Project Search (Fast Track) ---
            elif "open the project" in cmd_lower or "open the folder" in cmd_lower:
                # Extract the name (everything after "project" or "folder")
                keyword = ""
                if "project" in cmd_lower:
                    keyword = cmd_lower.split("project")[-1].strip()
                elif "folder" in cmd_lower:
                    keyword = cmd_lower.split("folder")[-1].strip()
                
                if keyword:
                    self.signal_processing.emit(f"Searching for '{keyword}'...")
                    # Search in the home directory (max depth 4 for speed)
                    # We search for a FOLDER that contains the keyword
                    find_cmd = ["find", "/home/yusua", "-maxdepth", "4", "-type", "d", "-iname", f"*{keyword}*", "-print", "-quit"]
                    try:
                        result = subprocess.run(find_cmd, capture_output=True, text=True)
                        path = result.stdout.strip()
                        if path:
                            subprocess.Popen(["code", path])
                            self.signal_finished.emit(f"Project {keyword} opened")
                            return f"Project {keyword} opened", False
                        else:
                            # If not found, let Claude handle it or state it
                            pass 
                    except Exception as e:
                        print(f"Find error: {e}")
        # -------------------------------------------------
        
        # Build prompt with history
        history_text = ""
        if conversation_history:
            history_text = "Conversation history:\n"
            for role, msg in conversation_history[-20:]: 
                history_text += f"{role}: {msg}\n"
            history_text += "\n"
        
        system_prompt = (
            "You are Claude, a voice assistant on Linux. "
            "Respond concisely. "
            "You have access to the conversation history above. "
            "If the user asks you to open an application or website that you can't do directly, "
            "respond with the EXACT format: [EXEC: linux_command]. "
            "Example: To open Firefox, write [EXEC: firefox]. "
            "Example: To open a site, write [EXEC: firefox https://site.com]."
        )
        
        full_prompt = f"{system_prompt}\n\n{history_text}User: {command_part}"
        print(f"[PROMPT]: {full_prompt}")
        
        # ASYNCHRONOUS launch
        t = threading.Thread(target=self.run_claude_async, args=(full_prompt, command_part))
        t.start()
        
        return "Processing...", False # Exit the listening loop

    def listen_and_process(self):
        # Initialize Vosk for the keyword (LOCAL and FAST)
        from vosk import Model, KaldiRecognizer
        import json
        import pyaudio
        import whisper
        import soundfile as sf
        import numpy as np
        import tempfile
        import os
        import wave
        
        print("Loading Vosk model (Wake Word)...")
        try:
            model = Model("models/fr")
            rec = KaldiRecognizer(model, 16000)
        except Exception as e:
            self.signal_error.emit(f"Vosk model error: {e}")
            return

        print("Loading Whisper model (Transcription)...")
        try:
            # We use the 'base' model which is a good speed/accuracy compromise
            # 'small' is better but slower. 'tiny' is very fast but less accurate.
            whisper_model = whisper.load_model("base")
        except Exception as e:
            self.signal_error.emit(f"Whisper model error: {e}")
            return

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
        
        print("Ready (Vosk + Whisper)!")
        
        while True:
            print("Waiting for wake word 'Claude' (Local)...")
            
            # 1. WAITING FOR WAKE WORD (Always with Vosk for speed)
            while True:
                data = stream.read(2000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    rec.Result() # IMPORTANT: Empty the buffer to avoid memory saturation
                else:
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text and "claude" in partial_text.lower():
                        print(f"Wake Word: {partial_text}")
                        rec.Reset()
                        break
            
            # 2. CONVERSATION LOOP
            in_conversation = True
            command_buffer = "" # Buffer to accumulate text (Dictation Mode)
            
            while in_conversation:
                # IMPORTANT: Signal that we're listening at each loop iteration
                # EXCEPT if we're processing an LLM response
                if not self.is_processing_llm:
                    self.signal_listening.emit()
                
                print("Listening for command (Conversation)...")
                
                command_text = ""
                start_listen_time = time.time()
                last_partial = ""
                last_change_time = time.time()
                
                # Audio buffer for Whisper
                audio_frames = []
                
                rec.Reset()
                
                while True:
                    data = stream.read(1000, exception_on_overflow=False)
                    audio_frames.append(data) # Record everything
                    
                    # Use Vosk ONLY for VAD (Voice Activity Detection)
                    # and for quick interruptions (Thanks/Stop)
                    if rec.AcceptWaveform(data):
                        # Ignore Vosk final result, we just want to know it's finished
                        pass
                    else:
                        partial_json = json.loads(rec.PartialResult())
                        partial = partial_json.get("partial", "")
                        
                        if partial:
                            if partial != last_partial:
                                last_partial = partial
                                last_change_time = time.time()
                                # print(f"Vosk partial (VAD): {partial}")
                                
                                # INTERRUPTION DURING PROCESSING (Absolute Priority)
                                if self.is_processing_llm:
                                    check_interrupt = partial.lower()
                                    if "thanks" in check_interrupt or "stop" in check_interrupt or "ok claude" in check_interrupt:
                                        print("INTERRUPTION DETECTED!")
                                        if self.current_llm_process:
                                            self.current_llm_process.terminate()
                                            self.current_llm_process = None
                                        self.is_processing_llm = False
                                        self.signal_finished.emit("Cancelled.")
                                        time.sleep(0.5)
                                        if "thanks" in check_interrupt or "stop" in check_interrupt:
                                            in_conversation = False
                                            self.signal_error.emit("STOP_OVERLAY")
                                            break
                                        rec.Reset()
                                        last_partial = ""
                                        audio_frames = [] # Reset audio
                                        continue

                            else:
                                # VAD: 1.2s of silence = end of sentence
                                if time.time() - last_change_time > 1.2:
                                    print("VAD end (Silence detected)")
                                    break
                    
                    # Timeout: 20s max
                    if time.time() - start_listen_time > 20:
                        print("Listening timeout")
                        break
                
                # If we broke the loop due to a "Thanks" interruption, exit
                if not in_conversation:
                    break

                # WHISPER TRANSCRIPTION
                if audio_frames:
                    print("Whisper transcription in progress...")
                    # Temporary WAV save
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                        temp_wav_path = temp_wav.name
                    
                    try:
                        # Write WAV file
                        wf = wave.open(temp_wav_path, 'wb')
                        wf.setnchannels(1)
                        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                        wf.setframerate(16000)
                        wf.writeframes(b''.join(audio_frames))
                        wf.close()
                        
                        # Transcription
                        result = whisper_model.transcribe(temp_wav_path, fp16=False, language='en') # Can force 'en' or leave auto
                        # Note: fp16=False to avoid CPU warning
                        
                        command_text = result["text"].strip()
                        print(f"Whisper heard: {command_text}")
                        
                    except Exception as e:
                        print(f"Whisper Transcription Error: {e}")
                    finally:
                        if os.path.exists(temp_wav_path):
                            os.remove(temp_wav_path)

                if command_text:
                    cmd_lower = command_text.lower()
                    
                    # If processing in progress, ignore (except interruption already handled)
                    if self.is_processing_llm:
                        continue

                    # 1. IMMEDIATE STOP COMMAND HANDLING
                    if "stop" in cmd_lower or "close" in cmd_lower or "thanks" in cmd_lower:
                        print("Stop command detected.")
                        self.signal_finished.emit("Goodbye!")
                        time.sleep(1.5)
                        in_conversation = False
                        self.signal_error.emit("STOP_OVERLAY")
                        break
                    
                    # 2. STRICT DICTATION MODE: Always wait for trigger
                    
                    # Check for TRIGGER "End Claude" (Priority)
                    # Whisper is more accurate, so we can be stricter on triggers
                    has_trigger = "end claude" in cmd_lower or "that's all" in cmd_lower or "send" in cmd_lower or "done" in cmd_lower
                    
                    # Add text to buffer
                    if command_buffer:
                        command_buffer += " " + command_text
                    else:
                        command_buffer = command_text
                    
                    # Update the UI
                    self.signal_recognized.emit(command_buffer + "...")
                    
                    if has_trigger:
                        # Clean the trigger
                        final_command = command_buffer
                        # Smarter cleaning with regex for Whisper which adds punctuation
                        import re
                        triggers = ["end claude", "that's all", "send", "done"]
                        for t in triggers:
                            final_command = re.sub(t, "", final_command, flags=re.IGNORECASE)
                        
                        final_command = final_command.strip()
                        # Clean final punctuation
                        final_command = final_command.rstrip(".,!?")
                        
                        if not final_command:
                            pass 
                        
                        print(f"Command validated (Trigger): {final_command}")
                        self.signal_recognized.emit(final_command)
                        
                        response_text, keep_open = self.process_command(final_command)
                        command_buffer = "" 
                        
                        # SAME EXIT LOGIC
                        if not keep_open:
                            if response_text == "Processing...":
                                print("LLM launched, exiting listening loop")
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
                        print(f"Dictation Mode: Accumulating ({len(command_buffer.split())} words)...")
                        # Continue listening AS LONG AS no trigger
                        
                else:
                    # Timeout (Nothing heard)
                    if not self.is_processing_llm:
                        if not command_buffer:
                            print("Conversation timeout (Empty buffer).")
                            in_conversation = False
                            self.signal_error.emit("STOP_OVERLAY")
                        else:
                            print("Timeout but buffer not empty, waiting more...")
            
            # End of conversation, reset everything for the next Wake Word
            rec.Reset()
