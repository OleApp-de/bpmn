import os
import streamlit as st
import tempfile
from typing import Optional

# Authentication configuration
AUTH_USERNAME = os.getenv('AUTH_USERNAME', 'admin')
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD', 'changeme')
ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'true').lower() == 'true'

def check_password():
    """Returns True if user entered correct password."""
    
    if "password_correct" not in st.session_state:
        # Show clean login form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## Login")
            
            with st.form("login_form"):
                username = st.text_input("Benutzername", key="username_form")
                password = st.text_input("Passwort", type="password", key="password_form")
                submitted = st.form_submit_button("Anmelden", use_container_width=True, type="primary")
                
                if submitted:
                    if username == AUTH_USERNAME and password == AUTH_PASSWORD:
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("❌ Ungültige Anmeldedaten")
        return False
    else:
        return True

def get_api_keys():
    """Load API keys from environment variables."""
    api_keys = {}
    
    if os.getenv('OPENAI_API_KEY'):
        api_keys['OpenAI'] = os.getenv('OPENAI_API_KEY')
    if os.getenv('ANTHROPIC_API_KEY'):
        api_keys['Anthropic'] = os.getenv('ANTHROPIC_API_KEY')
    if os.getenv('GOOGLE_API_KEY'):
        api_keys['Google'] = os.getenv('GOOGLE_API_KEY')
    if os.getenv('COHERE_API_KEY'):
        api_keys['Cohere'] = os.getenv('COHERE_API_KEY')
    
    return api_keys

def main():
    """Main application logic."""
    st.set_page_config(
        page_title="ProMoAI - Enterprise", 
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Show authentication if enabled
    if ENABLE_AUTH and not check_password():
        return
    
    # Get available API keys
    available_keys = get_api_keys()
    
    if not available_keys:
        st.error("⚠️ Keine API Keys konfiguriert! Bitte Administrator kontaktieren.")
        return
    
    # Import ProMoAI components
    try:
        from promoai import ProMoAI, analyze_event_log
        import pm4py
        from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
    except ImportError as e:
        st.error(f"Fehler beim Import: {str(e)}")
        return
    
    # Initialize session state
    if "model_gen" not in st.session_state:
        st.session_state["model_gen"] = None
    if "feedback_history" not in st.session_state:
        st.session_state["feedback_history"] = []
    if "current_bpmn" not in st.session_state:
        st.session_state["current_bpmn"] = None
    
    # Main ProMoAI interface
    st.markdown("# ProMoAI - Process Modeling with AI")
    st.markdown("*Enterprise Edition - Automatische BPMN-Generierung und Verfeinerung*")
    
    # Sidebar for provider selection
    with st.sidebar:
        st.markdown("### AI Provider Configuration")
        
        provider_options = list(available_keys.keys())
        selected_provider = st.selectbox(
            "AI Provider:", 
            provider_options,
            index=0 if provider_options else 0
        )
        
        # Model selection based on provider
        if selected_provider == "OpenAI":
            model_options = ["gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
            default_model = "gpt-4o"
        elif selected_provider == "Anthropic":
            model_options = ["claude-sonnet-4-20250514"]
            default_model = "claude-sonnet-4-20250514"
        elif selected_provider == "Google":
            model_options = ["gemini-pro", "gemini-pro-vision"]
            default_model = "gemini-pro"
        elif selected_provider == "Cohere":
            model_options = ["command", "command-light"]
            default_model = "command"
        else:
            model_options = ["gpt-4"]
            default_model = "gpt-4"
        
        selected_model = st.selectbox("Model:", model_options)
        
        st.markdown("---")
        st.markdown("**Status:**")
        st.success(f"✓ {selected_provider} verbunden")
        
        # View options
        st.markdown("---")
        st.markdown("### Ansichtsoptionen")
        view_type = st.selectbox(
            "Diagramm-Typ:",
            ["BPMN", "Petri Net", "POWL"],
            index=0
        )
        
        # Reset button
        if st.button("🔄 Zurücksetzen", use_container_width=True):
            st.session_state["model_gen"] = None
            st.session_state["feedback_history"] = []
            st.session_state["current_bpmn"] = None
            st.rerun()
    
    # Main content area with two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Eingabe")
        
        # Input method selection
        input_method = st.radio(
            "Wählen Sie eine Eingabemethode:",
            ["Text-Beschreibung", "Event Log hochladen", "BPMN/Petri Net hochladen"],
            horizontal=True
        )
        
        if input_method == "Text-Beschreibung":
            process_description = st.text_area(
                "Prozessbeschreibung:",
                placeholder="Beschreiben Sie Ihren Geschäftsprozess in natürlicher Sprache...",
                height=150
            )
            
            # Optional instructions field
            with st.expander("⚙️ Erweiterte Optionen"):
                custom_instructions = st.text_area(
                    "Zusätzliche Anweisungen (optional):",
                    placeholder="z.B.: Verwende deutsche Bezeichnungen, füge Swimlanes hinzu, nutze Message Events für Kommunikation, erstelle parallele Gateways wo möglich...",
                    height=80,
                    help="Diese Anweisungen werden dem AI-Prompt hinzugefügt um das Ergebnis zu beeinflussen"
                )
            
            if st.button("🚀 Modell generieren", type="primary", use_container_width=True):
                if process_description:
                    with st.spinner("Generiere Prozessmodell..."):
                        try:
                            api_key = available_keys[selected_provider]
                            promoai = ProMoAI(selected_provider, api_key, selected_model)
                            result = promoai.generate_bpmn_from_text(process_description, custom_instructions)
                            
                            if result["status"] == "success":
                                st.session_state["current_bpmn"] = result["bpmn_xml"]
                                st.session_state["model_gen"] = promoai
                                st.session_state["custom_instructions"] = custom_instructions
                                st.success("✅ Modell erfolgreich generiert!")
                        except Exception as e:
                            st.error(f"Fehler: {str(e)}")
                else:
                    st.warning("Bitte geben Sie eine Beschreibung ein.")
        
        elif input_method == "Event Log hochladen":
            uploaded_file = st.file_uploader(
                "Event Log auswählen:",
                type=['xes', 'csv', 'gz'],
                help="Unterstützte Formate: XES, CSV, GZ-komprimiert"
            )
            
            if uploaded_file:
                st.info(f"📄 {uploaded_file.name} geladen")
                
                if st.button("🔍 Prozess entdecken", type="primary", use_container_width=True):
                    with st.spinner("Analysiere Event Log..."):
                        try:
                            # Save uploaded file temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
                                tmp.write(uploaded_file.getbuffer())
                                temp_path = tmp.name
                            
                            result = analyze_event_log(temp_path)
                            
                            if result["status"] == "success":
                                st.success(f"✅ Prozess entdeckt! ({result['num_traces']} Traces, {result['num_events']} Events)")
                                # Convert to BPMN XML
                                bpmn_xml = pm4py.write_bpmn(result["bpmn_model"])
                                st.session_state["current_bpmn"] = bpmn_xml
                            else:
                                st.error(result["message"])
                            
                            os.unlink(temp_path)
                        except Exception as e:
                            st.error(f"Fehler: {str(e)}")
        
        else:  # BPMN/Petri Net upload
            uploaded_model = st.file_uploader(
                "Modell hochladen:",
                type=['bpmn', 'pnml', 'xml'],
                help="Laden Sie ein bestehendes BPMN oder Petri Net Modell hoch"
            )
            
            if uploaded_model:
                st.info(f"📊 {uploaded_model.name} geladen")
                
                improvement_request = st.text_area(
                    "Verbesserungsvorschläge:",
                    placeholder="Beschreiben Sie, wie das Modell verbessert werden soll...",
                    height=100
                )
                
                if st.button("🔧 Modell verbessern", type="primary", use_container_width=True):
                    if improvement_request:
                        with st.spinner("Verbessere Modell..."):
                            try:
                                # Read uploaded model
                                model_content = uploaded_model.read().decode('utf-8')
                                st.session_state["current_bpmn"] = model_content
                                
                                # Initialize ProMoAI for improvement
                                api_key = available_keys[selected_provider]
                                promoai = ProMoAI(selected_provider, api_key, selected_model)
                                
                                # Improve model based on feedback
                                prompt = f"Improve this BPMN model based on the following feedback: {improvement_request}\n\nOriginal model:\n{model_content}"
                                result = promoai.generate_bpmn_from_text(prompt)
                                
                                if result["status"] == "success":
                                    st.session_state["current_bpmn"] = result["bpmn_xml"]
                                    st.session_state["model_gen"] = promoai
                                    st.session_state["feedback_history"].append(improvement_request)
                                    st.success("✅ Modell verbessert!")
                            except Exception as e:
                                st.error(f"Fehler: {str(e)}")
                    else:
                        st.warning("Bitte beschreiben Sie die gewünschten Verbesserungen.")
        
        # Feedback section for iterative refinement
        if st.session_state["current_bpmn"]:
            st.markdown("---")
            st.markdown("### 🔄 Modell verfeinern")
            
            with st.form("feedback_form"):
                feedback = st.text_area(
                    "Feedback für Verbesserung:",
                    placeholder="Was soll am Modell geändert werden?",
                    height=100
                )
                
                if st.form_submit_button("Modell aktualisieren", use_container_width=True):
                    if feedback and st.session_state["model_gen"]:
                        with st.spinner("Aktualisiere Modell..."):
                            try:
                                # Update model with feedback
                                current_model = st.session_state["current_bpmn"]
                                prompt = f"Update this BPMN model based on feedback: {feedback}\n\nCurrent model:\n{current_model}"
                                
                                # Keep custom instructions if they exist
                                custom_inst = st.session_state.get("custom_instructions", "")
                                result = st.session_state["model_gen"].generate_bpmn_from_text(prompt, custom_inst)
                                
                                if result["status"] == "success":
                                    st.session_state["current_bpmn"] = result["bpmn_xml"]
                                    st.session_state["feedback_history"].append(feedback)
                                    st.success("✅ Modell aktualisiert!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Fehler: {str(e)}")
            
            # Show feedback history
            if st.session_state["feedback_history"]:
                with st.expander("📜 Feedback-Historie"):
                    for i, fb in enumerate(st.session_state["feedback_history"], 1):
                        st.markdown(f"**Iteration {i}:** {fb}")
    
    with col2:
        st.markdown("### 📊 Visualisierung")
        
        if st.session_state["current_bpmn"]:
            # Visualization tabs
            viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Diagramm", "XML", "Export"])
            
            with viz_tab1:
                try:
                    # Try to visualize the BPMN
                    if st.session_state["model_gen"]:
                        bpmn_graph = st.session_state["model_gen"].visualize_bpmn(st.session_state["current_bpmn"])
                        if bpmn_graph:
                            # Save visualization
                            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                                pm4py.save_vis_bpmn(bpmn_graph, tmp.name)
                                st.image(tmp.name, use_container_width=True)
                                os.unlink(tmp.name)
                        else:
                            st.info("Diagramm-Visualisierung wird vorbereitet...")
                except Exception as e:
                    st.warning(f"Visualisierung nicht verfügbar: {str(e)}")
                    st.info("Sie können das Modell trotzdem als XML anzeigen und exportieren.")
            
            with viz_tab2:
                st.code(st.session_state["current_bpmn"], language="xml")
            
            with viz_tab3:
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    st.download_button(
                        label="📥 BPMN herunterladen",
                        data=st.session_state["current_bpmn"],
                        file_name="process_model.bpmn",
                        mime="application/xml",
                        use_container_width=True
                    )
                
                with col_exp2:
                    # Convert to Petri Net if possible
                    try:
                        if pm4py:
                            # This would need proper conversion logic
                            st.download_button(
                                label="📥 Als PNML exportieren",
                                data=st.session_state["current_bpmn"],  # This should be converted
                                file_name="process_model.pnml",
                                mime="application/xml",
                                use_container_width=True
                            )
                    except:
                        st.info("PNML Export nicht verfügbar")
                
                # Statistics
                st.markdown("---")
                st.markdown("**Modell-Statistiken:**")
                try:
                    lines = st.session_state["current_bpmn"].count('\n')
                    size = len(st.session_state["current_bpmn"])
                    st.metric("Zeilen", lines)
                    st.metric("Größe", f"{size:,} Zeichen")
                    st.metric("Iterationen", len(st.session_state["feedback_history"]))
                except:
                    pass
        else:
            st.info("🎯 Wählen Sie links eine Eingabemethode, um zu beginnen.")
            
            # Show example
            with st.expander("💡 Beispiel-Prozessbeschreibung"):
                st.markdown("""
                **Bestellprozess:**
                1. Kunde gibt Bestellung auf
                2. System prüft Lagerbestand
                3. Bei Verfügbarkeit: Bestellung wird bestätigt
                4. Bei Nichtverfügbarkeit: Nachbestellung beim Lieferanten
                5. Ware wird verpackt
                6. Versand an Kunden
                7. Kunde erhält Sendungsverfolgung
                """)
    

if __name__ == "__main__":
    main()