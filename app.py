import os
import streamlit as st
import hashlib
from typing import Optional

# Authentication configuration
AUTH_USERNAME = os.getenv('AUTH_USERNAME', 'admin')
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD', 'changeme')
ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'true').lower() == 'true'

def check_password():
    """Returns True if user entered correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (st.session_state["username"] == AUTH_USERNAME and 
            st.session_state["password"] == AUTH_PASSWORD):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
            del st.session_state["username"]  # Don't store username
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Benutzername", on_change=password_entered, key="username")
        st.text_input(
            "Passwort", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Benutzername", on_change=password_entered, key="username")
        st.text_input(
            "Passwort", type="password", on_change=password_entered, key="password"
        )
        st.error("Benutzername oder Passwort falsch")
        return False
    else:
        # Password correct.
        return True

def get_api_keys():
    """Load API keys from environment variables."""
    api_keys = {}
    
    # Load available API keys from environment
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
        st.markdown("# ProMoAI - Enterprise Edition")
        st.markdown("Bitte melden Sie sich an, um fortzufahren.")
        return
    
    # Get available API keys
    available_keys = get_api_keys()
    
    if not available_keys:
        st.error("⚠️ Keine API Keys konfiguriert! Bitte Administrator kontaktieren.")
        st.info("Die folgenden Umgebungsvariablen müssen gesetzt werden: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, oder COHERE_API_KEY")
        return
    
    # Import ProMoAI components (assuming they exist)
    try:
        import promoai
    except ImportError:
        st.error("ProMoAI Module nicht gefunden. Bitte Installation prüfen.")
        return
    
    # Main ProMoAI interface
    st.markdown("# ProMoAI - Process Modeling with AI")
    st.markdown("*Enterprise Edition - Automatische BPMN-Generierung aus natürlicher Sprache*")
    
    # Sidebar for provider selection
    with st.sidebar:
        st.markdown("### AI Provider Configuration")
        
        # Provider selection based on available keys
        provider_options = list(available_keys.keys())
        default_provider = provider_options[0] if provider_options else "OpenAI"
        
        selected_provider = st.selectbox(
            "AI Provider:", 
            provider_options,
            index=0 if default_provider in provider_options else 0
        )
        
        # Model selection based on provider
        if selected_provider == "OpenAI":
            model_options = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
            default_model = "gpt-4"
        elif selected_provider == "Anthropic":
            model_options = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            default_model = "claude-3-sonnet-20240229"
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
        
        # Display current configuration
        st.markdown("---")
        st.markdown("**Aktuelle Konfiguration:**")
        st.markdown(f"Provider: {selected_provider}")
        st.markdown(f"Model: {selected_model}")
        st.markdown(f"API Key: {'✓ Verfügbar' if selected_provider in available_keys else '✗ Nicht verfügbar'}")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📝 Text zu BPMN", "📊 Event Log", "🔄 Model Verbesserung"])
    
    with tab1:
        st.markdown("### Prozessbeschreibung eingeben")
        process_description = st.text_area(
            "Beschreiben Sie Ihren Geschäftsprozess in natürlicher Sprache:",
            placeholder="Beispiel: Ein Kunde stellt einen Antrag. Der Antrag wird geprüft. Bei Genehmigung wird die Bestellung bearbeitet...",
            height=150
        )
        
        if st.button("BPMN Diagramm generieren", type="primary"):
            if process_description:
                with st.spinner("Generiere BPMN Diagramm..."):
                    try:
                        # Here you would call the actual ProMoAI functions
                        # For now, showing placeholder
                        st.success("✅ BPMN Diagramm erfolgreich generiert!")
                        st.info("🚧 ProMoAI Integration wird geladen...")
                        
                        # Placeholder for BPMN visualization
                        st.markdown("### Generiertes BPMN Diagramm")
                        st.info("Das generierte BPMN Diagramm wird hier angezeigt...")
                        
                    except Exception as e:
                        st.error(f"Fehler bei der Generierung: {str(e)}")
            else:
                st.warning("Bitte eine Prozessbeschreibung eingeben.")
    
    with tab2:
        st.markdown("### Event Log hochladen")
        uploaded_file = st.file_uploader(
            "Wählen Sie eine Event Log Datei (.csv, .xes):",
            type=['csv', 'xes']
        )
        
        if uploaded_file:
            st.success(f"✅ Datei '{uploaded_file.name}' hochgeladen")
            
            if st.button("Prozessmodell aus Event Log generieren", type="primary"):
                with st.spinner("Analysiere Event Log..."):
                    try:
                        st.info("🚧 Event Log Analyse wird implementiert...")
                    except Exception as e:
                        st.error(f"Fehler bei der Analyse: {str(e)}")
    
    with tab3:
        st.markdown("### Existierendes Model verbessern")
        
        model_file = st.file_uploader(
            "Wählen Sie eine BPMN oder Petri Net Datei:",
            type=['bpmn', 'pnml', 'xml']
        )
        
        improvement_request = st.text_area(
            "Beschreiben Sie gewünschte Verbesserungen:",
            placeholder="Beispiel: Fügen Sie Parallelverarbeitung hinzu, optimieren Sie für bessere Performance...",
            height=100
        )
        
        if model_file and improvement_request:
            if st.button("Model verbessern", type="primary"):
                with st.spinner("Verbessere Prozessmodell..."):
                    try:
                        st.info("🚧 Model Verbesserung wird implementiert...")
                    except Exception as e:
                        st.error(f"Fehler bei der Verbesserung: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("*ProMoAI Enterprise Edition - Entwickelt für interne Unternehmensnutzung*")

if __name__ == "__main__":
    main()