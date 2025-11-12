"""
Scanner Update Parser
Parses markdown files from the _posts directory and extracts incident data.
"""

import os
import re
import yaml
from datetime import datetime
from typing import List, Dict, Optional


class ScannerParser:
    def __init__(self, posts_directory: str):
        self.posts_directory = posts_directory
        self.incidents = []
        self.load_all_posts()

    def load_all_posts(self):
        """Load and parse all scanner update markdown files."""
        self.incidents = []

        if not os.path.exists(self.posts_directory):
            print(f"Warning: Posts directory not found: {self.posts_directory}")
            return

        for filename in os.listdir(self.posts_directory):
            if filename.endswith('.md') and 'scanner-update' in filename:
                filepath = os.path.join(self.posts_directory, filename)
                post_data = self.parse_post(filepath)
                if post_data:
                    self.incidents.append(post_data)

        # Sort by date, most recent first
        self.incidents.sort(key=lambda x: x['date'], reverse=True)
        print(f"Loaded {len(self.incidents)} scanner updates")

    def parse_post(self, filepath: str) -> Optional[Dict]:
        """Parse a single markdown post file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split front matter and content
            parts = content.split('---')
            if len(parts) < 3:
                return None

            # Parse YAML front matter
            front_matter = yaml.safe_load(parts[1])
            markdown_content = parts[2].strip()

            # Extract incidents from markdown content
            incidents = self.extract_incidents_from_content(markdown_content)

            # Ensure date is a datetime object for consistent sorting
            date_value = front_matter.get('date')
            if isinstance(date_value, str):
                # Parse string to datetime
                try:
                    date_value = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # Try alternative format
                    try:
                        date_value = datetime.strptime(date_value, '%Y-%m-%d')
                    except ValueError:
                        date_value = datetime.now()
            elif not isinstance(date_value, datetime):
                date_value = datetime.now()

            return {
                'filename': os.path.basename(filepath),
                'title': front_matter.get('title', ''),
                'date': date_value,
                'categories': front_matter.get('categories', []),
                'tags': front_matter.get('tags', []),
                'status': front_matter.get('status', 'Unknown'),
                'content': markdown_content,
                'incidents': incidents
            }
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None

    def extract_incidents_from_content(self, content: str) -> List[Dict]:
        """Extract individual incidents from markdown content."""
        incidents = []

        # Pattern to match incident entries like: 🚔 **Title** – Location – time
        pattern = r'([🚔🚒🚑🚨🔥💊⚠️🏥🚗🚙]+)\s*\*\*([^*]+)\*\*\s*[–-]\s*([^–\n]+?)(?:\s*[–-]\s*([^–\n]+?))?(?:\n|$)'

        matches = re.finditer(pattern, content)
        for match in matches:
            emoji = match.group(1)
            title = match.group(2).strip()
            location = match.group(3).strip()
            time_info = match.group(4).strip() if match.group(4) else ""

            # Determine incident type from emoji
            incident_type = self.get_incident_type_from_emoji(emoji)

            incidents.append({
                'type': incident_type,
                'title': title,
                'location': location,
                'time': time_info,
                'emoji': emoji
            })

        return incidents

    def get_incident_type_from_emoji(self, emoji: str) -> str:
        """Determine incident type from emoji."""
        if '🚔' in emoji or '🚨' in emoji:
            return 'police'
        elif '🚒' in emoji or '🔥' in emoji:
            return 'fire'
        elif '🚑' in emoji or '🏥' in emoji or '💊' in emoji:
            return 'medical'
        elif '🚗' in emoji or '🚙' in emoji:
            return 'traffic'
        else:
            return 'other'

    def search_by_location(self, location_query: str, limit: int = 10) -> List[Dict]:
        """Search for incidents by location."""
        location_query = location_query.lower()
        results = []

        for post in self.incidents:
            # Search in main content
            if location_query in post['content'].lower():
                results.append(post)
                continue

            # Search in individual incidents
            for incident in post.get('incidents', []):
                if location_query in incident['location'].lower():
                    results.append(post)
                    break

        return results[:limit]

    def search_by_route(self, start_location: str, end_location: str, limit: int = 10) -> List[Dict]:
        """Search for traffic incidents along a route (simplified - searches both locations)."""
        start_query = start_location.lower()
        end_query = end_location.lower()
        results = []

        for post in self.incidents:
            # Only look at traffic-related incidents
            categories = post.get('categories', [])
            tags = post.get('tags', [])

            content_lower = post['content'].lower()

            # Check if either location is mentioned and it's traffic-related
            if (start_query in content_lower or end_query in content_lower):
                if 'traffic' in categories or 'traffic' in tags or any(
                    kw in content_lower for kw in ['traffic', 'accident', 'crash', 'collision', 'road', 'highway']
                ):
                    results.append(post)

        return results[:limit]

    def get_recent_incidents(self, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent incidents, optionally filtered by category."""
        if category:
            filtered = [
                post for post in self.incidents
                if category.lower() in [c.lower() for c in post.get('categories', [])]
                or category.lower() in [t.lower() for t in post.get('tags', [])]
            ]
            return filtered[:limit]

        return self.incidents[:limit]

    def get_all_data_for_ai(self) -> str:
        """Get formatted data for AI context."""
        # Limit to most recent 50 posts to keep context manageable
        recent_posts = self.incidents[:50]

        formatted = "# Recent Scanner Updates from Derby City Watch (Louisville, KY)\n\n"

        for post in recent_posts:
            formatted += f"## Update from {post['date']}\n"
            formatted += f"Status: {post['status']}\n"
            formatted += f"Categories: {', '.join(post['categories'])}\n\n"
            formatted += post['content']
            formatted += "\n\n---\n\n"

        return formatted
