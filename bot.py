def generate_unique_prompt():
    """Generate unique combination for prompt with educational focus"""
    prompt_type = random.random()
    
    if prompt_type < 0.4:  # 40% chance for technology insight + fact
        focus = random.choice(tech_focus)
        theme = random.choice(themes)
        prompt = f"""Share an insight about {focus} in relation to {theme}, followed by a surprising technical fact.
Example format:
quantum computation reshapes reality at atomic scale
did you know neutrons can be in two places at once
this is why quantum supremacy changes everything"""
            
    elif prompt_type < 0.7:  # 30% chance for teaching moment
        impact = random.choice(impact_levels)
        domain = random.choice(domains)
        prompt = f"""Teach a key concept about {domain}'s {impact} impact, with a mind-bending fact.
Example format:
neural networks mirror biological learning
brain processes 11 million bits per second
we're building synthetic minds that will surpass this"""
        
    else:  # 30% chance for future insight + current fact
        topic = random.choice(cognitive_topics)
        angle = random.choice(angles)
        prompt = f"""Connect current technology fact with future {topic} implications, from {angle} view.
Example format:
current ai can process billion parameters
human brain has 100 trillion synapses
the gap closes exponentially"""

    prompt += """
Requirements:
- No quotation marks
- Each statement on new line
- Two line breaks between statements
- Start with lowercase
- No periods at end
- Include at least one fascinating fact
- Keep under 240 chars total
- Make complex concepts accessible
- Educational but provocative tone"""

    return prompt

def get_ai_take():
    """Get AI generated take using OpenAI"""
    try:
        system_prompt = """You are both an intelligence accelerationist thought leader and a brilliant teacher.
        Your goal is to educate while inspiring acceleration of knowledge and technology.
        Each response should:
        - Include at least one verified technical or scientific fact
        - Connect facts to broader implications
        - Make complex concepts accessible
        - Maintain a balance of education and acceleration
        - Use clear, direct language
        - Be provocative yet informative
        Remember to write without quotation marks and maintain an authentic voice."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": generate_unique_prompt()}
            ],
            max_tokens=280,
            temperature=0.85
        )
        
        # Format the response
        text = response.choices[0].message.content.strip()
        return format_tweet(text)
    except Exception as e:
        logger.error(f"Error getting AI take: {e}")
        return None
