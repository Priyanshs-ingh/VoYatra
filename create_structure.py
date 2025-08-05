import os
import shutil

# VoYatra folder already exists, so we'll create the structure inside it
# Create the VoYatra project structure with scraping subdirectory
project_structure = {
    "data-ingestion/": {
        "README.md": "",
        ".env.example": "",
        "requirements.txt": "",
        "docker-compose.yml": "",
        "config/": {
            "hdfs_config.py": "",
            "kafka_config.py": "",
            "redis_config.py": "",
            "scraping_settings.py": ""
        },
        "scrapers/": {
            "travel_scrapers/": {
                "__init__.py": "",
                "settings.py": "",
                "items.py": "",
                "middlewares.py": "",
                "pipelines.py": "",
                "spiders/": {
                    "__init__.py": "",
                    "news_spider.py": "",
                    "flights_spider.py": "",
                    "hotels_spider.py": "",
                    "weather_spider.py": ""
                }
            },
            "scrapy.cfg": ""
        },
        "data/": {
            "raw/": {
                "news/": {},
                "flights/": {},
                "hotels/": {},
                "weather/": {}
            },
            "hdfs_staging/": {}
        },
        "logs/": {
            "scrapy/": {},
            "kafka/": {},
            "hdfs/": {}
        },
        "scripts/": {
            "start_scraping.py": "",
            "hdfs_uploader.py": "",
            "kafka_producer.py": "",
            "setup_env.sh": ""
        },
        "monitoring/": {
            "prometheus/": {
                "config/": {}
            }
        }
    },
    "data-processing/": {
        "README.md": "# Data Processing Module\n\nThis module will handle Spark processing, analytics, and ML pipelines.\n\n*To be implemented in future phases*"
    },
    "data-visualization/": {
        "README.md": "# Data Visualization Module\n\nThis module will handle dashboards and reporting.\n\n*To be implemented in future phases*"
    },
    "data-storage/": {
        "README.md": "# Data Storage Module\n\nThis module will handle HDFS, Hive, and Delta Lake configurations.\n\n*To be implemented in future phases*"
    },
    "README.md": "# VoYatra - Travel Data Platform\n\nA comprehensive data platform for travel-related information including news, flights, hotels, and weather data.\n\n## Project Structure\n\n- **data-ingestion/**: Data scraping and ingestion components\n- **data-processing/**: Spark processing and ML pipelines (future)\n- **data-visualization/**: Dashboards and reporting (future)\n- **data-storage/**: HDFS, Hive, and Delta Lake configurations (future)\n",
    ".gitignore": "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\nPYPATH\n\n# Environment variables\n.env\n.venv\nenv/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n*~\n\n# Logs\n*.log\nlogs/\n\n# Data files\n*.csv\n*.json\n*.xml\ndata/raw/\ndata/processed/\n\n# Docker\n.dockerignore\ndocker-compose.override.yml\n\n# OS\n.DS_Store\nThumbs.db\n\n# Scrapy\n.scrapy\n\n# Jupyter Notebook\n.ipynb_checkpoints\n\n# Kafka\n*.kafka\n\n# HDFS\n*.hdfs\n"
}

def create_directory_structure(base_path, structure):
    """Recursively create directory structure"""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if name.endswith('/'):  # It's a directory
            os.makedirs(path, exist_ok=True)
            print(f"📁 Created directory: {path}")
            if isinstance(content, dict):
                create_directory_structure(path, content)
        else:  # It's a file
            # Create the file
            with open(path, 'w', encoding='utf-8') as f:
                if content:
                    f.write(content)
            print(f"📄 Created file: {path}")

# Create the project structure in the current VoYatra directory
base_path = "."
create_directory_structure(base_path, project_structure)

print("\n🎉 VoYatra project structure created successfully!")
print("\n📊 VoYatra Project Overview:")
print("=" * 50)
print("📁 data-ingestion/")
print("  ├── config/           - Configuration files")
print("  ├── scrapers/         - Scrapy spiders and settings")
print("  ├── data/             - Raw and staging data")
print("  ├── logs/             - Application logs")
print("  ├── scripts/          - Utility scripts")
print("  └── monitoring/       - Monitoring configs")
print("📁 data-processing/     - Future: Spark & ML")
print("📁 data-visualization/ - Future: Dashboards")
print("📁 data-storage/       - Future: HDFS & Delta Lake")
print("📄 README.md           - Project documentation")
print("📄 .gitignore          - Git ignore rules")
