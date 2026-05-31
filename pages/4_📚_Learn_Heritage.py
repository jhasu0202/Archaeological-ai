import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.ui_utils import apply_custom_css

st.set_page_config(page_title="Learn Heritage - HeritageLens AI", page_icon="📚", layout="wide")
apply_custom_css()

st.markdown("""
<style>
.page-header { background: #3B2A1A; border-radius: 12px; padding: 2rem; text-align: center; margin-bottom: 1.5rem; }
.page-header h1 { color: #F5E6C8; font-size: 2rem; font-weight: 600; margin-bottom: 0.3rem; }
.page-header p  { color: #C9A97A; font-size: 1rem; }
.info-card { background: #FFFDF9; border: 1px solid #E8D8C0; border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; }
.info-card h3, .info-card h4 { color: #5C3A1E; margin-bottom: 0.4rem; }
.info-card p, .info-card li, .info-card ol li { color: #3D2410; line-height: 1.7; }
.class-header { background: #5C3A1E; border-radius: 10px 10px 0 0; padding: 1rem 1.4rem; margin-bottom: 0; }
.class-header h2 { color: #F5E6C8; font-size: 1.3rem; font-weight: 600; margin: 0; }
.class-body { background: #FFFDF9; border: 1px solid #E8D8C0; border-top: none; border-radius: 0 0 10px 10px; padding: 1.2rem 1.4rem; margin-bottom: 1.5rem; }
.class-body p { color: #3D2410; line-height: 1.7; }
.section-heading { color: #3B2A1A; font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 0.7rem; padding-bottom: 0.3rem; border-bottom: 2px solid #C9A97A; }
.footer { text-align: center; color: #9B7B5B; padding: 2rem 0 1rem; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h1>📚 Learn About Heritage</h1>
    <p>Discover the cultural significance and characteristics of heritage objects</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-card">
    <h3>🏛️ Understanding Heritage Through AI</h3>
    <p>HeritageLens AI recognises and classifies different types of cultural heritage and archaeological
    elements. Each class represents a distinct category with unique characteristics, historical
    significance, and cultural value. Understanding these classifications helps us appreciate the
    diversity and richness of our shared heritage.</p>
</div>
""", unsafe_allow_html=True)

heritage_classes = [
    {
        "name": "Stones / Stone Pillars / Stone Structures",
        "icon": "🗿",
        "description": "Ancient stone constructions and architectural elements that represent humanity's earliest and most enduring building achievements.",
        "characteristics": ["Carved or shaped stone blocks", "Ancient construction techniques", "Weathering and erosion patterns", "Geometric or decorative patterns", "Structural integrity indicators"],
        "significance": "Stone structures tell stories of civilisations that mastered working with stone. They served as religious centres, defensive structures, or territorial markers. Construction techniques, materials, and placement in the landscape reveal technological capabilities and cultural values of past societies.",
        "examples": ["Ancient megaliths and standing stones", "Temple pillars and columns", "Stone walls and fortifications", "Carved stone monuments", "Ancient stone foundations"],
        "preservation": ["Document structural condition regularly", "Monitor for erosion and weathering", "Protect from vandalism and theft", "Maintain proper drainage around structures", "Use non-invasive conservation methods"]
    },
    {
        "name": "Crops / Farmland",
        "icon": "🌾",
        "description": "Agricultural landscapes representing humanity's relationship with the land and the development of sustainable food production systems.",
        "characteristics": ["Cultivated fields and terraces", "Irrigation systems and channels", "Agricultural tools and equipment", "Seasonal planting patterns", "Traditional farming methods"],
        "significance": "These areas contain evidence of ancient farming techniques, irrigation systems, and land management practices that sustained civilisations for millennia. Traditional agricultural practices passed down through generations represent intangible cultural heritage increasingly at risk in the modern world.",
        "examples": ["Ancient terraced fields", "Traditional irrigation systems", "Historic agricultural tools", "Ancient crop storage facilities", "Traditional farming villages"],
        "preservation": ["Maintain traditional farming practices", "Preserve native crop varieties", "Document traditional knowledge", "Protect agricultural landscapes from development", "Support sustainable farming communities"]
    },
    {
        "name": "Non-archaeological (deserts, water, mountains)",
        "icon": "🏔️",
        "description": "Natural landscapes and geographical features that form the backdrop for human activity and cultural development.",
        "characteristics": ["Natural geological formations", "Water bodies and hydrological features", "Desert landscapes and sand dunes", "Mountain ranges and valleys", "Natural vegetation patterns"],
        "significance": "These landscapes provide context for understanding how ancient civilisations adapted to their environments, chose settlement locations, and developed trade routes. Natural features often influenced religious beliefs, architectural styles, and cultural practices of the people who lived nearby.",
        "examples": ["Sacred mountains and hills", "Ancient trade route landscapes", "Natural water sources for settlements", "Desert oases and caravan routes", "Coastal areas with historical significance"],
        "preservation": ["Protect natural landscapes from pollution", "Maintain ecological balance", "Preserve traditional land use practices", "Document cultural associations with natural features", "Support sustainable tourism practices"]
    },
    {
        "name": "Heritage Sites (temples, palaces, forts, museums)",
        "icon": "🏛️",
        "description": "Major cultural and historical monuments representing the pinnacle of human cultural achievement and tangible connections to our past.",
        "characteristics": ["Architectural complexity and design", "Historical and cultural significance", "Artistic and decorative elements", "Structural engineering achievements", "Cultural and religious importance"],
        "significance": "These structures served as centres of worship, seats of power, defensive structures, or repositories of knowledge and art. They reflect the technological capabilities, artistic sensibilities, and cultural values of the societies that created them. Many continue to serve as active cultural and religious centres today.",
        "examples": ["Ancient temples and religious complexes", "Royal palaces and administrative buildings", "Fortresses and defensive structures", "Museums and cultural institutions", "Archaeological sites and ruins"],
        "preservation": ["Implement comprehensive conservation plans", "Monitor structural stability regularly", "Control visitor impact and access", "Maintain appropriate environmental conditions", "Document associated intangible heritage"]
    }
]

for cls in heritage_classes:
    st.markdown(f"""
    <div class="class-header"><h2>{cls['icon']} {cls['name']}</h2></div>
    <div class="class-body"><p>{cls['description']}</p></div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Characteristics", "🏛️ Cultural Significance", "📋 Examples", "🛡️ Preservation"])
    with tab1:
        for item in cls['characteristics']:
            st.markdown(f"- {item}")
    with tab2:
        st.markdown(f"<div style='color:#3D2410; line-height:1.7;'>{cls['significance']}</div>", unsafe_allow_html=True)
    with tab3:
        for item in cls['examples']:
            st.markdown(f"- {item}")
    with tab4:
        for item in cls['preservation']:
            st.markdown(f"- {item}")

    st.markdown("---")

st.markdown('<div class="section-heading">🎓 Additional Resources</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-card">
    <h3>🤖 AI in Heritage Preservation</h3>
    <p>Artificial Intelligence is revolutionising heritage preservation and archaeology. Technologies like HeritageLens AI enable:</p>
    <ul>
        <li><strong>Automated detection</strong> — quickly identify heritage objects in large datasets</li>
        <li><strong>Documentation</strong> — create comprehensive records of archaeological sites</li>
        <li><strong>Monitoring</strong> — track changes and deterioration over time</li>
        <li><strong>Accessibility</strong> — make heritage discovery accessible to everyone</li>
        <li><strong>Research</strong> — support academic and professional study</li>
    </ul>
</div>

<div class="info-card">
    <h3>📋 Best Practices for Documentation</h3>
    <ol>
        <li><strong>Respect local regulations</strong> — obtain proper permissions before documenting sites</li>
        <li><strong>Follow ethical guidelines</strong> — respect cultural sensitivities and local communities</li>
        <li><strong>Document context</strong> — record not just objects but their environmental context</li>
        <li><strong>Share knowledge</strong> — contribute findings to academic and preservation communities</li>
        <li><strong>Support conservation</strong> — use documentation to support preservation efforts</li>
    </ol>
</div>

<div class="info-card">
    <h3>🔬 The Technology</h3>
    <p>HeritageLens AI uses advanced deep learning:</p>
    <ul>
        <li><strong>YOLOv11 model</strong> — state-of-the-art object detection</li>
        <li><strong>Custom training</strong> — fine-tuned on heritage and archaeological data</li>
        <li><strong>Real-time processing</strong> — fast analysis of images and videos</li>
        <li><strong>High accuracy</strong> — reliable detection of heritage objects</li>
    </ul>
</div>

<div class="info-card">
    <h3>🌟 Get Involved</h3>
    <p>Heritage preservation is a collective responsibility. You can contribute by:</p>
    <ul>
        <li>Using HeritageLens AI to document local heritage sites</li>
        <li>Sharing discoveries with heritage organisations</li>
        <li>Supporting local preservation efforts</li>
        <li>Educating others about the importance of conservation</li>
        <li>Participating in citizen science projects</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">📚 Knowledge is the foundation of preservation — learn, document, and protect our shared heritage</div>', unsafe_allow_html=True)
