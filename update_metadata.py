#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArXiv Deep Reader - Metadata Auto-Updater

This script automatically scans the AI directory for paper folders,
extracts metadata from HTML files, and updates the paperMetadata
object in index.html.

Usage: python update_metadata.py
"""

import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime

class MetadataExtractor:
    def __init__(self, ai_dir: str = "AI"):
        self.ai_dir = Path(ai_dir)
        self.paper_metadata = {}
        
    def extract_paper_id(self, folder_name: str) -> Optional[str]:
        """Extract paper ID from folder name (e.g., '2412.19255v2' -> '2412.19255')"""
        match = re.search(r'(\d{4}\.\d{5})', folder_name)
        return match.group(1) if match else None
    
    def extract_url(self, html_path: Path, soup: BeautifulSoup) -> Optional[str]:
        """Extract URL from paper ID or HTML content"""
        # First, try to extract ArXiv URL from folder/file name
        folder_name = html_path.parent.name
        paper_id = self.extract_paper_id(folder_name)
        
        if paper_id:
            # Generate ArXiv URL from paper ID
            return f"https://arxiv.org/abs/{paper_id}"
        
        # If no paper ID, try to find URLs in HTML content
        # Look for ArXiv links
        arxiv_links = soup.find_all('a', href=re.compile(r'arxiv\.org'))
        if arxiv_links:
            return arxiv_links[0]['href']
        
        # Look for other academic paper URLs
        academic_patterns = [
            r'https?://arxiv\.org/abs/[\d\.]+',
            r'https?://.*\.pdf',
            r'https?://github\.com/[^/]+/[^/]+',
            r'https?://huggingface\.co/[^/]+/[^/]+'
        ]
        
        content_text = soup.get_text()
        for pattern in academic_patterns:
            match = re.search(pattern, content_text)
            if match:
                return match.group(0)
        
        # Look for meta tags with URLs
        meta_url = soup.find('meta', attrs={'property': 'og:url'})
        if meta_url and meta_url.get('content'):
            return meta_url['content']
        
        # Return placeholder if no URL found
        return None
    
    def extract_html_metadata(self, html_path: Path) -> Dict:
        """Extract metadata from HTML file"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('title')
            title = title_elem.get_text().strip() if title_elem else ""
            
            # Try to extract from h1 if title is generic
            if not title or 'ArXiv' in title:
                h1_elem = soup.find('h1')
                if h1_elem:
                    title = h1_elem.get_text().strip()
            
            # Extract description from meta description or first paragraph
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description = meta_desc['content'].strip()
            else:
                # Try to find description in content
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50 and not text.startswith('©'):
                        description = text[:200] + '...' if len(text) > 200 else text
                        break
            
            # Extract URL - try multiple methods
            url = self.extract_url(html_path, soup)
            
            # Determine category and tags based on content
            content_text = soup.get_text().lower()
            category, category_color, tags, tag_colors, gradient = self.categorize_content(content_text, title)
            
            metadata = {
                'title': title,
                'description': description,
                'category': category,
                'categoryColor': category_color,
                'tags': tags,
                'tagColors': tag_colors,
                'gradient': gradient
            }
            
            # Add URL if found
            if url:
                if 'arxiv.org' in url:
                    metadata['arxivUrl'] = url
                else:
                    metadata['url'] = url
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting metadata from {html_path}: {e}")
            return self.get_default_metadata()
    
    def categorize_content(self, content_text: str, title: str) -> tuple:
        """Categorize paper based on content analysis"""
        content_lower = content_text.lower()
        title_lower = title.lower()
        
        # KV Cache related
        if any(keyword in content_lower for keyword in ['kv cache', 'kv缓存', 'cache', '缓存', 'memory', 'attention']):
            return ('KV缓存优化', 'blue', ['架构创新', '内存优化', '性能提升'], ['purple', 'green', 'orange'], 'from-blue-600 to-purple-600')
        
        # Multi-token prediction
        elif any(keyword in content_lower for keyword in ['multi-token', '多令牌', 'prediction', '预测', 'parallel', '并行']):
            return ('推理加速', 'emerald', ['并行计算', '推测解码', '效率优化'], ['blue', 'red', 'yellow'], 'from-emerald-600 to-teal-600')
        
        # Training and fine-tuning
        elif any(keyword in content_lower for keyword in ['training', '训练', 'fine-tuning', '微调', 'lora', 'peft']):
            return ('模型训练', 'purple', ['训练优化', '参数高效', '微调技术'], ['blue', 'green', 'purple'], 'from-purple-600 to-indigo-600')
        
        # Reasoning and logic
        elif any(keyword in content_lower for keyword in ['reasoning', '推理', 'logic', '逻辑', 'chain of thought', 'cot']):
            return ('推理能力', 'orange', ['逻辑推理', '思维链', '问题解决'], ['red', 'orange', 'yellow'], 'from-orange-600 to-red-600')
        
        # Multimodal
        elif any(keyword in content_lower for keyword in ['multimodal', '多模态', 'vision', '视觉', 'image', '图像']):
            return ('多模态', 'pink', ['视觉理解', '多模态融合', '跨模态'], ['pink', 'purple', 'blue'], 'from-pink-600 to-purple-600')
        
        # Architecture and model design
        elif any(keyword in content_lower for keyword in ['architecture', '架构', 'transformer', 'attention', 'model']):
            return ('模型架构', 'indigo', ['架构设计', '注意力机制', '模型创新'], ['indigo', 'blue', 'purple'], 'from-indigo-600 to-blue-600')
        
        # Default category
        else:
            return ('AI研究', 'gray', ['机器学习', 'AI技术'], ['blue', 'green'], 'from-gray-600 to-gray-700')
    
    def get_default_metadata(self) -> Dict:
        """Return default metadata for papers without extractable info"""
        return {
            'title': '未知论文',
            'description': '这是一篇关于AI技术的研究论文，包含了最新的研究成果和技术创新。',
            'category': 'AI研究',
            'categoryColor': 'gray',
            'tags': ['机器学习', 'AI技术'],
            'tagColors': ['blue', 'green'],
            'gradient': 'from-gray-600 to-gray-700',
            'url': None  # Placeholder for URL
        }
    
    def scan_papers(self) -> Dict:
        """Scan AI directory and extract metadata for all papers"""
        if not self.ai_dir.exists():
            print(f"AI directory '{self.ai_dir}' not found!")
            return {}
        
        paper_metadata = {}
        
        for folder in self.ai_dir.iterdir():
            if not folder.is_dir():
                continue
                
            paper_id = self.extract_paper_id(folder.name)
            if not paper_id:
                print(f"Skipping folder '{folder.name}' - no valid paper ID found")
                continue
            
            # Look for HTML file
            html_files = list(folder.glob('*.html'))
            if not html_files:
                print(f"No HTML file found in '{folder.name}'")
                paper_metadata[paper_id] = self.get_default_metadata()
                continue
            
            # Use the first HTML file found
            html_file = html_files[0]
            print(f"Processing {paper_id} from {html_file.name}...")
            
            metadata = self.extract_html_metadata(html_file)
            paper_metadata[paper_id] = metadata
        
        return paper_metadata
    
    def escape_js_string(self, text: str) -> str:
        """Properly escape string for JavaScript"""
        # Replace problematic characters
        text = text.replace('\\', '\\\\')
        text = text.replace("'", "\\'") 
        text = text.replace('"', '\\"')
        text = text.replace('\n', '\\n')
        text = text.replace('\r', '\\r')
        text = text.replace('\t', '\\t')
        return text
    
    def categorize_file_detailed(self, filename: str) -> Dict:
        """Detailed file categorization with complete information"""
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        name_lower = filename.lower()
        
        if ext == 'html':
            if 'step3-model-analysis' in name_lower:
                return {"type": "model_analysis", "priority": 2, "icon": "🧠", "label": "模型分析"}
            else:
                return {"type": "analysis", "priority": 1, "icon": "📖", "label": "深度解析"}
        elif 'report' in name_lower or '报告' in name_lower:
            return {"type": "report", "priority": 2, "icon": "📊", "label": "研究报告"}
        elif 'analysis' in name_lower or '分析' in name_lower:
            return {"type": "analysis_pdf", "priority": 2, "icon": "📊", "label": "分析报告"}
        elif 'mfa' in name_lower and 'kr' in name_lower:
            return {"type": "mfa_analysis", "priority": 3, "icon": "🔍", "label": "MFA-KR解析"}
        elif 'step3-sys-model' in name_lower:
            return {"type": "sys_model", "priority": 3, "icon": "⚙️", "label": "系统模型"}
        elif 'step' in name_lower or 'model' in name_lower or 'sys' in name_lower:
            return {"type": "tech", "priority": 3, "icon": "🔧", "label": "技术报告"}
        elif ext == 'pdf' and any(x in name_lower for x in ['v1', 'v2', 'v3']):
            return {"type": "original", "priority": 2, "icon": "📄", "label": "原文PDF"}
        elif ext == 'pdf':
            return {"type": "document", "priority": 3, "icon": "📄", "label": "PDF文档"}
        else:
            return {"type": "other", "priority": 4, "icon": "📎", "label": "其他文件"}
    
    def get_tag_colors(self, tags: List[str]) -> List[str]:
        """Assign colors to tags"""
        colors = ['purple', 'green', 'orange', 'blue', 'red', 'yellow', 'pink', 'cyan']
        return [colors[i % len(colors)] for i in range(len(tags))]
    
    def update_meta_json(self, metadata: Dict, meta_path: str = "meta.json") -> bool:
        """Update meta.json file with extracted metadata"""
        try:
            # Read existing meta.json or create new structure
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
            else:
                meta_data = {
                    "papers": {},
                    "statistics": {"totalPapers": 0, "totalDocuments": 0},
                    "lastUpdated": "",
                    "version": "1.0.0"
                }
            
            # Update papers data
            meta_data["papers"] = {}
            total_documents = 0
            
            for paper_id, data in metadata.items():
                # Find the actual folder (might have version suffix)
                folder_name = None
                for item in self.ai_dir.iterdir():
                    if item.is_dir() and paper_id in item.name:
                        folder_name = item.name
                        break
                
                if not folder_name:
                    folder_name = paper_id  # fallback
                
                folder_path = self.ai_dir / folder_name
                files_info = []
                
                if folder_path.exists():
                    # Recursively scan all files including subdirectories
                    for file_path in folder_path.rglob('*'):
                        if file_path.is_file():
                            # Get relative path for display
                            relative_path = file_path.relative_to(folder_path)
                            file_info = self.categorize_file_detailed(file_path.name)
                            files_info.append({
                                "name": str(relative_path),
                                "type": file_info["type"],
                                "priority": file_info["priority"],
                                "icon": file_info["icon"],
                                "label": file_info["label"]
                            })
                            total_documents += 1
                
                # Sort files by priority
                files_info.sort(key=lambda x: x["priority"])
                
                paper_entry = {
                    "title": data["title"],
                    "description": data["description"],
                    "category": data["category"],
                    "categoryColor": data["categoryColor"],
                    "tags": data["tags"],
                    "tagColors": data["tagColors"],
                    "gradient": data["gradient"],
                    "folder": folder_name,
                    "files": files_info
                }
                
                # Add URL fields if they exist
                if "arxivUrl" in data and data["arxivUrl"]:
                    paper_entry["arxivUrl"] = data["arxivUrl"]
                elif "url" in data and data["url"]:
                    paper_entry["url"] = data["url"]
                
                meta_data["papers"][paper_id] = paper_entry
            
            # Update statistics
            meta_data["statistics"] = {
                "totalPapers": len(metadata),
                "totalDocuments": total_documents
            }
            meta_data["lastUpdated"] = datetime.now().isoformat() + "Z"
            
            # Write to file
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=2)
            
            print(f"Successfully updated {meta_path} with {len(metadata)} papers")
            return True
            
        except Exception as e:
            print(f"Error updating meta.json: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function"""
    print("ArXiv Deep Reader - Metadata Auto-Updater")
    print("==========================================")
    
    extractor = MetadataExtractor()
    
    # Scan for papers
    print("\n1. Scanning AI directory for papers...")
    metadata = extractor.scan_papers()
    
    if not metadata:
        print("No papers found to process.")
        return
    
    print(f"Found {len(metadata)} papers:")
    for paper_id, data in metadata.items():
        print(f"  - {paper_id}: {data['title'][:50]}...")
    
    # Update meta.json
    print("\n2. Updating meta.json...")
    success = extractor.update_meta_json(metadata)
    
    if success:
        print("\n✅ Metadata update completed successfully!")
        print("\nYou can now refresh your browser to see the updated paper information.")
    else:
        print("\n❌ Failed to update metadata.")

if __name__ == "__main__":
    main()