"""
ProMoAI Core Module - Process Modeling with AI
Based on original work by Humam Kourani and Alessandro Berti
"""

import os
import json
import requests
import tempfile
from typing import Optional, Dict, Any
import streamlit as st

# Import AI libraries conditionally
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import cohere
except ImportError:
    cohere = None

# Import process mining libraries
try:
    import pm4py
    from pm4py.objects.bpmn.obj import BPMN
    from pm4py.objects.petri_net.obj import PetriNet, Marking
    from pm4py.objects.petri_net.utils import petri_utils
except ImportError:
    pm4py = None
    BPMN = None
    PetriNet = None
    Marking = None
    petri_utils = None


class ProMoAI:
    """Main ProMoAI class for process model generation"""
    
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate AI client based on provider"""
        if self.provider == "OpenAI" and openai:
            openai.api_key = self.api_key
            return openai.OpenAI(api_key=self.api_key)
        elif self.provider == "Anthropic" and anthropic:
            return anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == "Google" and genai:
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model)
        elif self.provider == "Cohere" and cohere:
            return cohere.Client(self.api_key)
        else:
            raise ValueError(f"Provider {self.provider} not supported or library not installed")
    
    def generate_bpmn_from_text(self, description: str, custom_instructions: str = "") -> Dict[str, Any]:
        """Generate BPMN model from text description"""
        
        # Create prompt for BPMN generation
        base_prompt = f"""
        Convert the following process description into a BPMN 2.0 XML format:
        
        {description}
        
        Please provide a valid BPMN 2.0 XML that includes:
        - Start and end events
        - Tasks/activities
        - Gateways (if needed)
        - Sequence flows
        """
        
        # Add custom instructions if provided
        if custom_instructions:
            prompt = base_prompt + f"""
        
        Additional instructions:
        {custom_instructions}
        
        Return only the XML code without any explanation.
        """
        else:
            prompt = base_prompt + """
        
        Return only the XML code without any explanation.
        """
        
        # Get response from AI
        bpmn_xml = self._get_ai_response(prompt)
        
        # Clean the response
        bpmn_xml = self._clean_xml_response(bpmn_xml)
        
        return {
            "bpmn_xml": bpmn_xml,
            "status": "success",
            "message": "BPMN model generated successfully"
        }
    
    def generate_petri_net_from_text(self, description: str) -> Dict[str, Any]:
        """Generate Petri Net from text description"""
        
        prompt = f"""
        Convert the following process description into a Petri Net structure:
        
        {description}
        
        Provide the Petri Net as a structured JSON with:
        - places: list of place names
        - transitions: list of transition names
        - arcs: list of arcs with source and target
        
        Return only valid JSON without any explanation.
        """
        
        petri_json = self._get_ai_response(prompt)
        
        try:
            petri_data = json.loads(petri_json)
            return {
                "petri_data": petri_data,
                "status": "success",
                "message": "Petri Net generated successfully"
            }
        except json.JSONDecodeError:
            return {
                "petri_data": None,
                "status": "error",
                "message": "Failed to parse Petri Net JSON"
            }
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get response from the AI provider"""
        try:
            if self.provider == "OpenAI" and openai:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a process modeling expert that converts text descriptions into formal process models."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            elif self.provider == "Anthropic" and anthropic:
                response = self.client.messages.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                return response.content[0].text
            
            elif self.provider == "Google" and genai:
                response = self.client.generate_content(prompt)
                return response.text
            
            elif self.provider == "Cohere" and cohere:
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=0.3
                )
                return response.generations[0].text
            
            else:
                return "Provider not properly configured"
                
        except Exception as e:
            st.error(f"Error getting AI response: {str(e)}")
            return ""
    
    def _clean_xml_response(self, xml_text: str) -> str:
        """Clean XML response from AI"""
        # Remove markdown code blocks if present
        if "```xml" in xml_text:
            xml_text = xml_text.split("```xml")[1].split("```")[0]
        elif "```" in xml_text:
            xml_text = xml_text.split("```")[1].split("```")[0]
        
        # Remove any leading/trailing whitespace
        xml_text = xml_text.strip()
        
        # Ensure it starts with <?xml
        if not xml_text.startswith("<?xml"):
            xml_text = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_text
        
        return xml_text
    
    def visualize_bpmn(self, bpmn_xml: str):
        """Visualize BPMN model using pm4py"""
        if not pm4py:
            st.error("pm4py library not installed. Cannot visualize BPMN.")
            return None
        
        try:
            # Save XML to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bpmn', delete=False) as f:
                f.write(bpmn_xml)
                temp_path = f.name
            
            # Import BPMN using pm4py
            bpmn_graph = pm4py.read_bpmn(temp_path)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return bpmn_graph
            
        except Exception as e:
            st.error(f"Error visualizing BPMN: {str(e)}")
            return None
    
    def export_bpmn(self, bpmn_xml: str, filename: str = "process_model.bpmn"):
        """Export BPMN model to file"""
        return bpmn_xml.encode('utf-8')


def analyze_event_log(file_path: str) -> Dict[str, Any]:
    """Analyze event log and extract process information"""
    if not pm4py:
        return {
            "status": "error",
            "message": "pm4py library not installed"
        }
    
    try:
        # Read event log
        if file_path.endswith('.xes'):
            log = pm4py.read_xes(file_path)
        elif file_path.endswith('.csv'):
            log = pm4py.read_csv(file_path)
        else:
            return {
                "status": "error",
                "message": "Unsupported file format"
            }
        
        # Get basic statistics
        num_traces = len(log)
        num_events = sum(len(trace) for trace in log)
        
        # Discover process model
        process_tree = pm4py.discover_process_tree_inductive(log)
        bpmn_model = pm4py.convert_to_bpmn(process_tree)
        
        return {
            "status": "success",
            "num_traces": num_traces,
            "num_events": num_events,
            "bpmn_model": bpmn_model,
            "message": "Event log analyzed successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error analyzing event log: {str(e)}"
        }