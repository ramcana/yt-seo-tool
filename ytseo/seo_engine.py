from __future__ import annotations

import re
from typing import Dict, List, Optional

from .llm_client import get_llm_client
from .ai_ewg_bridge import get_episode_by_id


def generate_title(context: Dict) -> str:
    """
    Generate SEO-optimized title for Canadian news content.
    Max 100 characters, non-clickbait, includes show/host when available.
    """
    original_title = context.get("title_original", "")
    episode_data = _get_episode_context(context)
    
    # Build context for LLM
    show_name = episode_data.get("show_name", "The News Forum")
    topics = episode_data.get("topics", [])
    guests = episode_data.get("guest_names", [])
    
    topics_str = ", ".join(topics[:3]) if topics else ""
    guests_str = ", ".join(guests[:2]) if guests else ""
    
    system_prompt = """You are an SEO expert for Canadian news content. 
Generate YouTube titles that are:
- Professional and non-clickbait
- SEO-optimized for Canadian audience
- Max 100 characters
- Include show name when relevant
- Clear and descriptive"""
    
    user_prompt = f"""Original title: {original_title}
Show: {show_name}
Topics: {topics_str or 'N/A'}
Guests: {guests_str or 'N/A'}

Generate an improved YouTube title that is SEO-friendly, professional, and appeals to Canadian news viewers. Return ONLY the title, no explanation."""
    
    try:
        llm = get_llm_client()
        generated = llm.generate(user_prompt, system_prompt, max_tokens=100, temperature=0.7)
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
    Includes summary, key segments, and CTA.
    """
    original_desc = context.get("description_original", "")
    episode_data = _get_episode_context(context)
    
    show_name = episode_data.get("show_name", "The News Forum")
    summary = episode_data.get("summary", "")
    topics = episode_data.get("topics", [])
    guests = episode_data.get("guest_names", [])
    key_moments = episode_data.get("key_moments", [])
    
    topics_str = ", ".join(topics) if topics else "N/A"
    guests_str = ", ".join(guests) if guests else "N/A"
    moments_str = "\n".join([f"- {m.get('title', '')}" for m in key_moments[:5]]) if key_moments else ""
    
    system_prompt = """You are an SEO expert for Canadian news content.
Generate YouTube descriptions that are:
- 200-300 words
- Professional Canadian tone
- Include episode summary
- Mention key segments/topics
- End with clear CTA (subscribe, follow)
- SEO-optimized with relevant keywords"""
    
    user_prompt = f"""Show: {show_name}
Original description: {original_desc[:200]}
Summary: {summary or 'N/A'}
Topics: {topics_str}
Guests: {guests_str}
Key moments:
{moments_str or 'N/A'}

Generate a compelling YouTube description (200-300 words) that summarizes the content, highlights key topics, and encourages viewers to subscribe. Use a professional Canadian news tone."""
    
    try:
        llm = get_llm_client()
        description = llm.generate(user_prompt, system_prompt, max_tokens=500, temperature=0.7)
        
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
    
    system_prompt = """You are an SEO expert for Canadian news content.
Generate YouTube tags that:
- Are relevant to Canadian news audience
- Include broad and specific terms
- Total 20-30 tags
- Mix of single words and short phrases
- Include location, topic, and entity tags"""
    
    user_prompt = f"""Content topics: {topics_str or 'Canadian news'}
Entities: {entities_str or 'N/A'}
Show: {show_name}
Existing tags: {', '.join(original_tags[:10])}

Generate 20-30 YouTube tags as a comma-separated list. Focus on Canadian news, politics, and the specific topics mentioned. Return ONLY the comma-separated tags."""
    
    try:
        llm = get_llm_client()
        generated = llm.generate(user_prompt, system_prompt, max_tokens=300, temperature=0.6)
        
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
    
    system_prompt = """Generate 5-10 YouTube hashtags for Canadian news content.
Hashtags should be:
- Relevant and trending
- Mix of broad (#CanadianNews) and specific
- Proper capitalization
- No spaces"""
    
    user_prompt = f"""Topics: {', '.join(topics) if topics else 'Canadian news'}

Generate 5-10 hashtags as a comma-separated list. Return ONLY the hashtags with # prefix."""
    
    try:
        llm = get_llm_client()
        generated = llm.generate(user_prompt, system_prompt, max_tokens=100, temperature=0.6)
        
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
    
    system_prompt = """Generate thumbnail text for Canadian news videos.
Text should be:
- 3-5 options
- Very short (3-7 words max)
- Punchy and attention-grabbing
- Professional, not clickbait
- Readable on small screens"""
    
    user_prompt = f"""Video title: {original_title}
Topics: {', '.join(topics[:3]) if topics else 'N/A'}

Generate 3-5 short thumbnail text options (3-7 words each). Return as a numbered list."""
    
    try:
        llm = get_llm_client()
        generated = llm.generate(user_prompt, system_prompt, max_tokens=150, temperature=0.8)
        
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
    
    system_prompt = """Generate a pinned comment for Canadian news videos.
Comment should:
- Be polite and welcoming (Canadian tone)
- Include clear CTA (subscribe, like, comment)
- Be 2-3 sentences
- Encourage engagement
- Professional but friendly"""
    
    user_prompt = f"""Show: {show_name}
Video: {original_title}

Generate a pinned comment that thanks viewers, encourages them to subscribe, and invites discussion. Use a warm, professional Canadian tone."""
    
    try:
        llm = get_llm_client()
        comment = llm.generate(user_prompt, system_prompt, max_tokens=150, temperature=0.7)
        return comment.strip() if comment else f"Thanks for watching! Subscribe to {show_name} for more Canadian news and analysis."
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
