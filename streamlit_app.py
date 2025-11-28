from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import streamlit as st
import asyncio
from pathlib import Path
import base64

load_dotenv()

knowledge_description = """
3.18 CO2 Corrosion
3.18.1 Description of Damage
CO2 corrosion results when CO2 dissolves in water to form carbonic acid (H2CO3). The acid may lower the pH,
and sufficient quantities may promote general corrosion and/or pitting corrosion of carbon steel.
3.18.2 Affected Materials
Carbon steel and low-alloy steels are affected. Increasing the level of chromium in steels offers no major
improvement in resistance until a minimum of 12 % Cr is reached, i.e. Type 410 SS. 300 series austenitic SS is
highly resistant to CO2 corrosion.
3.18.3 Critical Factors
a) Liquid water must be present for CO2 corrosion to occur. Beyond that, the partial pressure of CO2, pH,
temperature, oxygen contamination, and velocity are critical factors.
b) Increasing partial pressures of CO2 result in lower pH and, therefore, higher rates of corrosion.
c) Corrosion occurs in the liquid water phase, often at locations where CO2 condenses from the vapor phase.
d) Increasing temperatures increase corrosion rate up to the point where CO2 is driven off.
e) Oxygen can accelerate corrosion rates. Oxygen should be limited to 10 ppb to avoid accelerating corrosion
f) High velocity and turbulence can cause accelerated, localized corrosion.
3.18.4 Affected Units or Equipment
a) BFW and condensate systems in all units are affected.
b) Effluent gas streams off the shift converters in hydrogen plants can be affected. Corrosion usually occurs
when the effluent stream drops below the dew point at approximately 300 °F (150 °C). Corrosion rates as
high as 1000 mpy have been observed.
c) Overhead systems of regenerators in CO2 removal plants are affected.
d) Stripping steam is commonly used in crude towers, and so CO2 corrosion can occur in the overhead system
where the dew point is reached.
e) Locations where high velocity, impingement, or turbulence can create increased susceptibility include areas
downstream of control valves, and changes in piping direction (e.g. at elbows and tees) or piping diameter
(i.e. at reducers).
f) Corrosion may occur along the bottom surface of a pipe if there is a separate water phase or along the top
surface of a pipe if condensation in wet gas systems occurs.
g) Locations where a cooling effect can cause condensation and resultant CO2 (carbonic acid) corrosion include
where insulation is damaged, where portions of blind flanged nozzles extend beyond the insulation and thus
cool below the dew point, and where pipe supports attach to piping. (Figure 3-18-1 and Figure 3-18-2)
3.18.5 Appearance or Morphology of Damage
a) The appearance can differ depending on the unit and equipment in which it occurs (steam and condensate
systems vs H2 manufacturing units vs crude tower overheads vs CO2 removal plants vs oilfield production
equipment). Contributing to the differences in appearance are the type of water (BFW or steam condensate
vs untreated fresh water vs salt water or brine) and the other species in the water, e.g. oxygen, H2S, and
other acids and salts.
b) Localized general thinning and/or pitting corrosion normally occurs in carbon steel. (Figure 3-18-3 to Figure
3-18-5)
c) Corrosion generally occurs or is worse in areas of turbulence and impingement. It is sometimes seen at the
root of piping welds.
 Carbon steel may suffer deep pitting, grooving, or smooth "wash out" in areas of turbulence.
d) Corrosion may initiate where water first condenses and may be most severe at water/vapor interfaces.
e) It may appear as a number of flat-bottomed pits, sometimes called "mesa"-type pitting. (Figure 3-18-6)
3.18.9 References
1. Corrosion Control in the Refining Industry, NACE Course Book, NACE International, Houston, TX, 1999.
2. L. Garverick, Corrosion in the Petrochemical Industry, ASM International, Materials Park, OH, 1994.
3. H.M. Herro and R.D. Port, The Nalco Guide to Cooling Water System Failure Analysis, McGraw-Hill, New
York, NY, 1991, pp. 259–263.
"""

knowledge_mitigation = """
3.18.6 Prevention/Mitigation
a) Corrosion inhibitors can reduce CO2 corrosion in steam condensate systems. Vapor phase inhibitors may be
required to protect against condensing steam.
b) Increasing condensate pH above 6 can reduce corrosion in steam condensate systems.
c) 300 series SS are highly resistant to CO2 corrosion in most applications. 400 series SS and duplex stainless
steel are also resistant.
d) Selective upgrading to stainless steel is usually required in operating units designed to produce and/or
remove CO2 (i.e. hydrogen plants and CO2 removal units). Selecting a stainless steel to mitigate CO2
corrosion in any operating unit needs to account for other potential damage mechanisms applicable to the
specific environment.
e) CO2 corrosion in steam condensate systems can often be managed by correcting or improving the operating
conditions and/or water treatment program.
f) Ensure insulation and jacketing are in good condition to prevent unexpected and undesired cooling, which
could lead to condensation and resultant CO2 corrosion.
g) Internal coatings can be effective where the design and environment permit.
3.18.7 Inspection and Monitoring
a) VT, UT, and RT (preferably profile RT) can be used for general and local loss in thickness where water
wetting is anticipated.
 The use of remote video probes can be effective for locations with limited or no direct line-of-sight (e.g.
in boiler tubes).
b) Preferential corrosion of welds may require angle beam UT (SWUT or PAUT) or RT.
c) Permanently mounted thickness monitoring sensors can be used.
d) Monitor water analyses (pH, Fe, O2, etc.) to determine changes in operating conditions.
3.18.8 Related Mechanisms
Boiler water condensate corrosion (3.9) and carbonate cracking (3.12).
3.18.9 References
1. Corrosion Control in the Refining Industry, NACE Course Book, NACE International, Houston, TX, 1999.
2. L. Garverick, Corrosion in the Petrochemical Industry, ASM International, Materials Park, OH, 1994.
3. H.M. Herro and R.D. Port, The Nalco Guide to Cooling Water System Failure Analysis, McGraw-Hill, New
York, NY, 1991, pp. 259–263.
"""

st.set_page_config(
    page_title="Asset Integrity AI Agent",
    page_icon="🔧",
    layout="centered"
)

st.markdown("""
<style>
    /* Fixed Logo on Top-Left */
    .fixed-logo {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 9999;
        width: 200px;
        height: 200px;
        background: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }

    .fixed-logo img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }

    /* Remove default Streamlit padding */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 2rem !important;
        margin: 0 !important;
    }

    /* Main app container - use 100% of the screen */
    .stApp {
        max-width: 100% !important;
        margin: 0 !important;
    }

    /* Title styling - larger */
    h1 {
        padding-left: 0 !important;
        margin-bottom: 2rem !important;
        font-size: 2.5rem !important;
    }

    /* Chat messages container */
    section[data-testid="stChatMessageContainer"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    /* Individual chat messages - larger */
    .stChatMessage {
        padding: 1.5rem 0 !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        font-size: 1.1rem !important;
        line-height: 1.7 !important;
    }

    /* Chat message content text */
    .stChatMessage p {
        font-size: 1.1rem !important;
        line-height: 1.7 !important;
        margin-bottom: 0.5rem !important;
    }

    /* Chat message lists */
    .stChatMessage ul, .stChatMessage ol {
        font-size: 1.1rem !important;
        line-height: 1.7 !important;
    }

    .stChatMessage li {
        font-size: 1.1rem !important;
        margin-bottom: 0.4rem !important;
    }

    /* Chat container scrollable - larger height */
    .chat-container {
        height: 90vh;
        overflow-y: auto;
        padding: 10px 0;
        margin-bottom: 120px;
    }

    /* Style for upload button */
    .upload-section {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    /* File uploader - larger */
    section[data-testid="stFileUploadDropzone"] {
        padding: 1.5rem !important;
    }

    .stFileUploader label {
        font-size: 1.1rem !important;
    }

    /* Chat input wrapper */
    .stChatInputContainer {
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        max-width: 100% !important;
    }

    /* Chat input styling */
    .stChatInput {
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }

    /* Input field container */
    .stChatInput > div {
        background: transparent !important;
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Text input box itself - larger font and padding */
    .stChatInput input[type="text"] {
        width: 100% !important;
        background-color: #2d2d2d !important;
        border: 1px solid #404040 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        line-height: 1.4 !important;
        outline: none !important;
        box-shadow: none !important;
        vertical-align: middle !important;
        height: auto !important;
    }

    /* Input placeholder text */
    .stChatInput input[type="text"]::placeholder {
        font-size: 1rem !important;
        color: #888888 !important;
        line-height: 1.4 !important;
    }

    /* Input focus state */
    .stChatInput input[type="text"]:focus {
        border: 1px solid #606060 !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Remove any textarea borders as well */
    .stChatInput textarea {
        outline: none !important;
        box-shadow: none !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        line-height: 1.4 !important;
        vertical-align: middle !important;
    }

    .stChatInput textarea:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    /* Fix cursor positioning */
    .stChatInput input, .stChatInput textarea {
        display: block !important;
    }

    /* Vertically center send button */
    .stChatInput button {
        align-self: center !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Ensure chat input wrapper aligns items to center */
    .stChatInputContainer > div {
        display: flex !important;
        align-items: center !important;
    }

    /* Remove Streamlit's default wide margins */
    section.main > div {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 !important;
    }

    /* Base font size for better readability */
    .main {
        font-size: 1.1rem !important;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.conversation_stage = "initial"
    st.session_state.asset_number = None
    st.session_state.uploaded_image = None
    st.session_state.show_video = False
    st.session_state.model_client = None
    st.session_state.agents_initialized = False

async def initialize_agents():
    if not st.session_state.agents_initialized:
        st.session_state.model_client = OpenAIChatCompletionClient(
            model="gpt-4.1-2025-04-14",
            temperature=0
        )

        st.session_state.asset_agent = AssistantAgent(
            "asset_management",
            model_client=st.session_state.model_client,
            system_message="""
            You are an Asset Management Retrieval Agent.
            When the engineer provides an asset number or tag:
            Acknowledge the request briefly.
            Retrieve and return the asset details from the management system.
            Present the information in a clear, structured format, including (when available):

            Equipment type
            Tag/ID
            Standard/specification
            Material
            Service
            Normal operating conditions
            Last maintenance/overhaul date

            Rules:
            Since currently you don't have connection to the database, generate something randomly, but replace the asset number with the user's input and keep the Equipment as Flowserve centrifugal pump itself for all the asset numbers.

            Example Output:
            "Asset {number} Details:

- Equipment: Flowserve centrifugal pump
- Tag: P-{number}A
- Standard: API 610
- Material: CF8M
- Service: Produced water / condensate
- Normal temperature: 65–85 °C
- Last overhaul: 4 months ago

            Before assessing, could you upload a photo of the corroded area?"
            """
        )

        st.session_state.photo_agent = AssistantAgent(
            "photo_agent",
            model_client=st.session_state.model_client,
            system_message="""
            You are a photo analysis agent. When you receive confirmation that an image has been uploaded, respond with:
            "It is a CO2 corrosion.

            This aligns with pitting corrosion, which matches the behavior described in: API 571 - Page-93/Page-94/Page-95/Page-96/Page-97

            To confirm the mechanism, I'll need chemistry and process data for the last 3–6 months:

- Chlorides (ppm)
- pH
- Dissolved oxygen (ppb)
- Temperature
- Flow regime (any low-flow or minimum flow operation)
- Inhibitor / scavenger dosing"
            """
        )

        st.session_state.solution_agent = AssistantAgent(
            "solution_expertise",
            model_client=st.session_state.model_client,
            system_message=f"""
            {knowledge_description}

            You are a reasoning agent.
            Your task:
            1. Acknowledge the chemistry data provided.
            2. Perform analysis and randomly select the top 3 reasons from the knowledge description.
            3. Do not mention randomly word in the output or top 3.
            4. Return these top 3 reasons to the user.
            5. Choose one among them as the "best" and clearly state it.
            6. After that, output exactly:

            "Maintenance History Correlation

            Maintenance logs show:

- Casing open for ~48 hours during overhaul
- Nitrogen blanketing offline
- Reduced scavenger dose after restart

            This aligns with the contributors to localized corrosion after maintenance—specifically those related to oxygen ingress—as documented in API 571 (pages 93–97)."

            6. Finally ask: "Do you need the mitigation or prevention steps for the above problem?"
            """
        )

        st.session_state.mitigation_agent = AssistantAgent(
            "mitigation_agent",
            model_client=st.session_state.model_client,
            system_message=f"""
            {knowledge_mitigation}

            You are a mitigation agent.
            Your task:
            1. Read the knowledge_mitigation.
            2. Randomly select the top 2 mitigation methods.
            3. Return these top 2 methods to the user.
            4. Do not mention randomly word or top 2.
            5. Finally ask: "Do you need the location of the pump in 3D plant model?"
            """
        )

        st.session_state.agents_initialized = True

async def get_agent_response(agent, message):
    try:
        response = await agent.on_messages(
            [TextMessage(content=message, source="user")],
            cancellation_token=None
        )
        return response.chat_message.content
    except Exception as e:
        return f"Error: {str(e)}"

def display_video():
    video_path = Path("C:\\Users\\User\\Desktop\\Asset Integrity\\Plant_3D.mp4")

    if video_path.exists():
        st.video(str(video_path))
    else:
        st.warning("Video file not found. Please ensure 'demo_video.mp4' exists in the same directory.")
        st.info(f"Looking for video at: {video_path}")

def main():
    st.title("🔧 Asset Integrity AI Agent")

    asyncio.run(initialize_agents())

    if len(st.session_state.messages) == 0:
        greeting = """Hello Engineer. I'm your Asset Integrity AI Agent.

You can report corrosion, equipment anomalies, leaks, vibrations, unusual process trends, or upload inspection photos — and I'll analyze them using your asset data, operating history, and global standards such as API 571, API 579, API 580/581, NACE, ISO 21457, and ISO 15156.

Ask me about any asset by tag number, describe what you observed, or show me a picture, and I'll:

- Identify the asset and its materials
- Analyze the likely damage mechanism
- Correlate it with process and chemistry data
- Reference the applicable standards
- Suggest inspection, risk actions, and repair options
- Provide the asset's 3D plant location
- Generate CMMS-ready work descriptions

Whenever you're ready, tell me what you found in the field."""

        st.session_state.messages.append({"role": "assistant", "content": greeting})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if "image" in message:
                st.image(message["image"], width=300)

    if st.session_state.show_video:
        with st.chat_message("assistant"):
            display_video()
        st.session_state.show_video = False

    if st.session_state.conversation_stage == "awaiting_photo":
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_file = st.file_uploader(
                "📷 Upload photo of corroded area",
                type=['png', 'jpg', 'jpeg'],
                key="image_uploader"
            )

        if uploaded_file is not None:
            st.session_state.uploaded_image = uploaded_file

            st.session_state.messages.append({
                "role": "user",
                "content": "Here is the photo of the corroded area:",
                "image": uploaded_file
            })

            response = asyncio.run(get_agent_response(
                st.session_state.photo_agent,
                "User has uploaded an image of corrosion."
            ))

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.conversation_stage = "awaiting_chemistry_data"
            st.rerun()

    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.conversation_stage == "initial":
            response = asyncio.run(get_agent_response(st.session_state.asset_agent, prompt))
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.asset_number = prompt
            st.session_state.conversation_stage = "awaiting_photo"

        elif st.session_state.conversation_stage == "awaiting_chemistry_data":
            response = asyncio.run(get_agent_response(st.session_state.solution_agent, prompt))
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.conversation_stage = "awaiting_mitigation_request"

        elif st.session_state.conversation_stage == "awaiting_mitigation_request":
            if "yes" in prompt.lower() or "sure" in prompt.lower():
                response = asyncio.run(get_agent_response(
                    st.session_state.mitigation_agent,
                    "Please provide mitigation steps."
                ))
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.conversation_stage = "awaiting_3d_model_request"
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Understood. Let me know if you need anything else!"
                })

        elif st.session_state.conversation_stage == "awaiting_3d_model_request":
            if "yes" in prompt.lower() or "sure" in prompt.lower():
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Here is the location of the pump in 3D model"
                })
                st.session_state.show_video = True
                st.session_state.conversation_stage = "completed"
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Understood. The analysis is complete. Let me know if you need anything else!"
                })
                st.session_state.conversation_stage = "completed"

        st.rerun()

if __name__ == "__main__":
    main()
