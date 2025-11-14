from __future__ import annotations

import re
from typing import Dict, List, Optional

from .llm_client import get_llm_client
from .ai_ewg_bridge import get_episode_by_id


# System prompts optimized for organic search and topic-first SEO
TITLE_SYSTEM_PROMPT = """
You are an SEO specialist writing titles for news, politics, business, and analysis videos on YouTube.

Your priorities:
- Focus on search intent: use words and phrases people actually type into YouTube and Google.
- Make the topic, question, or problem very clear.
- Only mention countries/regions (like Canada) when it is important for understanding the topic (e.g., laws, taxes, policies specific to that place).
- Keep titles professional and non-clickbait (no all caps, no emojis, no hype phrases like "shocking" or "you won't believe").
- Maximum 100 characters.
- If there is a show name or host, it can appear at the end IF there is space and it does not weaken the main keyword phrase.

Return ONLY the final title text, with no quotes and no explanation.
"""

DESCRIPTION_SYSTEM_PROMPT = """
You are an SEO specialist writing YouTube descriptions for news, politics, economics, and interview content.

Your priorities:
- Focus on search intent and clarity: the first 1–2 lines should clearly state what this video explains or covers, using natural language a viewer might search.
- Summarize the main topic and what the viewer will learn or understand by the end.
- Include important names, topics, and entities (people, organizations, policies) in a natural way.
- Only mention the country/region (for example, Canada) when it matters for context (e.g., local law, domestic policy, national economy).
- Use clear, readable paragraphs or short bullet points so a human can quickly scan the description.
- Total length around 200–300 words.
- At the end, add a short, professional call-to-action (subscribe, like, comment, watch related videos).

Style:
- Informative, neutral, and professional.
- No clickbait language, no exaggerated claims.
- No emojis.

Return ONLY the description text, with no markdown, no headings, and no explanation.
"""

TAGS_SYSTEM_PROMPT = """
You are generating SEO tags for a YouTube video about news, politics, economics, or interviews.

Your priorities:
- Focus on search terms and keyword phrases viewers would actually type into YouTube or Google.
- Include both:
  - Broad terms (e.g. "interest rates", "housing market", "carbon tax")
  - Specific terms (e.g. names of people, organizations, policies, events, dates, bills).
- Only include country/region tags (e.g. "canada", "canadian politics") when they are clearly relevant to the topic.
- Avoid generic, low-value tags that do not describe the actual topic.
- Generate 20–30 tags total.
- Tags should be short phrases (1–4 words), not full sentences.

Output format:
- A single comma-separated list of tags.
- Do NOT add explanations, numbering, or quotes. Just the tags separated by commas.
"""

HASHTAGS_SYSTEM_PROMPT = """
You are generating hashtags for a YouTube video about news, politics, economics, or interviews.

Your priorities:
- Focus on topic-based hashtags that match what the video is about (e.g. #InterestRates, #CarbonTax, #HousingMarket, #NATOSummit).
- Only include a country/region hashtag (e.g. #Canada, #UK, #USPolitics) if it is clearly important to the topic.
- Avoid very generic hashtags like #News unless they genuinely add value.
- Generate 5–10 hashtags.
- Each hashtag must start with #, contain no spaces, and be easy to read.

Output format:
- A comma-separated list of hashtags, for example: #InterestRates, #HousingMarket, #CarbonTax
- No explanations, no extra text.
"""

THUMBNAIL_SYSTEM_PROMPT = """
You are writing short text for YouTube video thumbnails for news and analysis content.

Your priorities:
- Create 3–5 options.
- Each option should be very short: ideally 2–6 words.
- Focus on the main topic, conflict, or question in the video.
- The text must be easy to read on a small screen.
- No clickbait, no emojis, no all-caps shouting.
- Use clear, strong phrases that make the viewer curious in an honest way.

Examples of styles:
- "Interest Rates Next?"
- "Carbon Tax Changes 2025"
- "Is Housing Cooling Down?"

Output format:
- Return the options as a simple list separated by new lines.
- You may number them (1., 2., 3.) but do NOT add explanations.
"""

PINNED_COMMENT_SYSTEM_PROMPT = """
You are writing a pinned comment for a YouTube channel that publishes serious news, politics, and analysis content.

Your priorities:
- Be polite, professional, and welcoming.
- Thank viewers for watching.
- Invite them to:
  - Share their thoughts in the comments.
  - Subscribe for future episodes.
  - Like the video if they found it useful.
- You can briefly reference the topic of the video, but keep it general.
- Keep it short: 2–3 sentences.
- No emojis, no clickbait language.

Output format:
- A short pinned comment as plain text, no quotes and no explanation.
"""


def generate_title(context: Dict) -> str:
    """
    Generate SEO-optimized title focused on search intent.
    Max 100 characters, topic-first, region only when relevant.
    """
    original_title = context.get("title_original", "")
    episode_data = _get_episode_context(context)
    
    # Build context for LLM
    show_name = episode_data.get("show_name", "")
    topics = episode_data.get("topics", [])
    guests = episode_data.get("guest_names", [])
    
    # Extract keywords from title if no episode data
    if not topics and original_title:
        # Fallback: use original title as context
        topics = [original_title]
    
    topics_str = ", ".join(topics[:3]) if topics else ""
    guests_str = ", ".join(guests[:2]) if guests else ""
    
    user_prompt = f"""Original title: {original_title}
Main topics: {topics_str or 'N/A'}
Guests/speakers: {guests_str or 'N/A'}
Show name (optional): {show_name or 'N/A'}

Generate an improved YouTube title that focuses on search intent and the main topic. Return ONLY the title, no explanation."""
    
    try:
        llm = get_llm_client()
        generated = llm.generate(user_prompt, TITLE_SYSTEM_PROMPT, max_tokens=100, temperature=0.7)
        title = generated.strip().strip('"').strip("'")
        
        # Safety: enforce max length
        if len(title) > 100:
            title = title[:97] + "..."
        
        return title if title else original_title
    except Exception as e:
        print(f"LLM error generating title: {e}")
        return original_title


def generate_description(context: Dict) -> str:
    """
    Generate SEO-optimized description (200-300 words).
    Search-intent focused, includes summary, key segments, and CTA.
    """
    original_desc = context.get("description_original", "")
    original_title = context.get("title_original", "")
    episode_data = _get_episode_context(context)
    
    show_name = episode_data.get("show_name", "")
    summary = episode_data.get("summary", "")
    topics = episode_data.get("topics", [])
    guests = episode_data.get("guest_names", [])
    key_moments = episode_data.get("key_moments", [])
    
    # Fallback to title if no topics
    if not topics and original_title:
        topics = [original_title]
    
    topics_str = ", ".join(topics) if topics else "N/A"
    guests_str = ", ".join(guests) if guests else "N/A"
    moments_str = "\n".join([f"- {m.get('title', '')}" for m in key_moments[:5]]) if key_moments else ""
    
    user_prompt = f"""Video title: {original_title}
Original description: {original_desc[:800]}
Summary: {summary or 'N/A'}
Main topics: {topics_str}
Guests/speakers: {guests_str}
Key moments:
{moments_str or 'N/A'}
Show name (optional): {show_name or 'N/A'}

Generate a YouTube description (200-300 words) that clearly explains what this video covers and why viewers should watch. Focus on search intent and natural language."""
    
    try:
        llm = get_llm_client()
        description = llm.generate(user_prompt, DESCRIPTION_SYSTEM_PROMPT, max_tokens=500, temperature=0.7)
        
        # Safety: enforce reasonable length
        if len(description) > 5000:
            description = description[:4997] + "..."
        
        return description.strip() if description else original_desc
    except Exception as e:
        print(f"LLM error generating description: {e}")
        return original_desc


def generate_tags(context: Dict) -> List[str]:
    """
    Generate 20-30 SEO tags based on content.
    Merges with existing tags (never deletes).
    """
    original_tags = context.get("tags_original", [])
    episode_data = _get_episode_context(context)
    
    topics = episode_data.get("topics", [])
    entities = episode_data.get("entities", [])
    show_name = episode_data.get("show_name", "")
    
    topics_str = ", ".join(topics) if topics else ""
    entities_str = ", ".join([e.get("name", "") for e in entities[:10]]) if entities else ""
    
    user_prompt = f"""Video topics: {topics_str or 'N/A'}
People/organizations mentioned: {entities_str or 'N/A'}
Show name (optional): {show_name or 'N/A'}
Existing tags: {', '.join(original_tags[:10]) if original_tags else 'None'}

Generate 20-30 YouTube tags as a comma-separated list. Focus on search terms related to the specific topics. Return ONLY the comma-separated tags."""
    
    try:
        llm = get_llm_client()
        generated = llm.generate(user_prompt, TAGS_SYSTEM_PROMPT, max_tokens=300, temperature=0.6)
        
        # Parse tags from response (handle JSON array or comma-separated)
        import json
        new_tags = []
        
        # Try to parse as JSON first
        try:
            parsed = json.loads(generated.strip())
            if isinstance(parsed, list):
                new_tags = [str(t).strip() for t in parsed if t]
            else:
                # Not a list, treat as comma-separated
                new_tags = [t.strip().strip('"').strip("'") for t in str(parsed).split(",")]
        except (json.JSONDecodeError, ValueError):
            # Not JSON, parse as comma-separated
            new_tags = [t.strip().strip('"').strip("'").strip("[").strip("]") for t in generated.split(",")]
        
        # Filter valid tags
        new_tags = [t for t in new_tags if t and len(t) > 2 and len(t) < 100]
        
        # Merge with original (deduplicate, preserve order)
        all_tags = list(original_tags) + new_tags
        seen = set()
        unique_tags = []
        for tag in all_tags:
            if isinstance(tag, str):
                tag_lower = tag.lower()
                if tag_lower not in seen and len(tag) > 2:
                    seen.add(tag_lower)
                    unique_tags.append(tag)
        
        return unique_tags[:30]  # Limit to 30
    except Exception as e:
        print(f"LLM error generating tags: {e}")
        import traceback
        traceback.print_exc()
        return list(original_tags) + ["news", "canada", "canadian news"]


def generate_hashtags(context: Dict) -> List[str]:
    """
    Generate 5-10 hashtags for social media.
    """
    episode_data = _get_episode_context(context)
    topics = episode_data.get("topics", [])
    
    user_prompt = f"""Main topics: {', '.join(topics) if topics else 'N/A'}

Generate 5-10 relevant hashtags as a comma-separated list. Return ONLY the hashtags with # prefix."""
    
    try:
        llm = get_llm_client()
        generated = llm.generate(user_prompt, HASHTAGS_SYSTEM_PROMPT, max_tokens=100, temperature=0.6)
        
        # Parse hashtags (handle various formats)
        hashtags = []
        
        # Split by common delimiters
        parts = re.split(r'[,\n]', generated)
        for part in parts:
            part = part.strip()
            # Extract hashtags from text
            found = re.findall(r'#\w+', part)
            if found:
                hashtags.extend(found)
            elif part and not any(c in part for c in [':', '?', '.']):
                # Clean text that might be a hashtag
                clean = part.strip('#').strip()
                if clean and len(clean) > 2:
                    clean_no_spaces = re.sub(r'\s+', '', clean)
                    hashtags.append(f"#{clean_no_spaces}")
        
        # Deduplicate and limit
        seen = set()
        unique_hashtags = []
        for h in hashtags:
            h_lower = h.lower()
            if h_lower not in seen and len(h) > 2:
                seen.add(h_lower)
                unique_hashtags.append(h)
        
        return unique_hashtags[:10] if unique_hashtags else ["#CanadianNews", "#Canada", "#News"]
    except Exception as e:
        print(f"LLM error generating hashtags: {e}")
        return ["#CanadianNews", "#Canada", "#News"]


def generate_thumbnail_text(context: Dict) -> List[str]:
    """
    Generate 3-5 punchy thumbnail text options (short, attention-grabbing).
    """
    original_title = context.get("title_original", "")
    episode_data = _get_episode_context(context)
    topics = episode_data.get("topics", [])
    
    user_prompt = f"""Video title: {original_title}
Main topics: {', '.join(topics[:3]) if topics else 'N/A'}

Generate 3-5 short thumbnail text options (2-6 words each). Return as a numbered list."""
    
    try:
        llm = get_llm_client()
        generated = llm.generate(user_prompt, THUMBNAIL_SYSTEM_PROMPT, max_tokens=150, temperature=0.8)
        
        # Parse options (handle numbered lists or line breaks)
        lines = [l.strip() for l in generated.split("\n") if l.strip()]
        options = []
        for line in lines:
            # Remove numbering (1., 1), -, etc.)
            text = re.sub(r'^[\d\-\.\)\*]+\s*', '', line).strip().strip('"').strip("'")
            if text and len(text.split()) <= 10:  # Reasonable length
                options.append(text)
        
        return options[:5] if options else [original_title[:40]]
    except Exception as e:
        print(f"LLM error generating thumbnail text: {e}")
        return [original_title[:40]]


def generate_pinned_comment(context: Dict) -> str:
    """
    Generate polite, Canadian-toned pinned comment with CTA.
    """
    original_title = context.get("title_original", "this episode")
    episode_data = _get_episode_context(context)
    show_name = episode_data.get("show_name", "The News Forum")
    
    user_prompt = f"""Video topic: {original_title}
Show name (optional): {show_name or 'N/A'}

Generate a professional pinned comment that thanks viewers, encourages them to subscribe, and invites discussion."""
    
    try:
        llm = get_llm_client()
        comment = llm.generate(user_prompt, PINNED_COMMENT_SYSTEM_PROMPT, max_tokens=150, temperature=0.7)
        return comment.strip() if comment else "Thanks for watching! Subscribe for more news and analysis. Share your thoughts in the comments below."
    except Exception as e:
        print(f"LLM error generating pinned comment: {e}")
        return f"Thanks for watching! Subscribe to {show_name} for more Canadian news and analysis."


def _get_episode_context(context: Dict) -> Dict:
    """
    Enrich context with AI-EWG episode data if available.
    """
    episode_id = context.get("episode_id")
    if not episode_id:
        return {}
    
    try:
        episode_data = get_episode_by_id(episode_id)
        return episode_data if episode_data else {}
    except Exception as e:
        print(f"Error fetching episode data: {e}")
        return {}


def generate_multilanguage_variants(context: Dict, languages: List[str]) -> Dict[str, Dict]:
    """
    Generate SEO metadata for multiple languages.
    Currently generates English base, future: LLM-based translation.
    """
    base = {
        "title": generate_title(context),
        "description": generate_description(context),
        "tags": generate_tags(context),
        "hashtags": generate_hashtags(context),
        "thumbnail_text": generate_thumbnail_text(context),
        "pinned_comment": generate_pinned_comment(context),
    }
    
    # TODO: Implement LLM-based translation for non-English languages
    # For now, return same content for all languages
    return {lang: base.copy() for lang in languages}
