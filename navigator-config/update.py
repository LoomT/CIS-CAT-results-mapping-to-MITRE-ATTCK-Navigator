import requests
import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MitreAttackDownloader:
    def __init__(self, base_dir="mitre_attack_data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create base subdirectories
        self.config_dir = self.base_dir / "config"
        self.data_dir = self.base_dir / "data"
        
        for dir_path in [self.config_dir, self.data_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Track created collection directories
        self.collection_dirs = {}

    def download_file_with_retry(self, url, local_path, max_retries=3, delay=1):
        """Download a file with retry logic and error handling."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Downloading {url} (attempt {attempt + 1}/{max_retries})")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Ensure parent directory exists
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save the file
                with open(local_path, 'w', encoding='utf-8') as f:
                    if url.endswith('.json'):
                        # Pretty print JSON for readability
                        json.dump(response.json(), f, ensure_ascii=False)
                    else:
                        f.write(response.text)
                
                logger.info(f"Successfully downloaded to {local_path}")
                return True
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)  # Exponential backoff
                else:
                    logger.error(f"Failed to download {url} after {max_retries} attempts")
                    return False
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in response from {url}: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error downloading {url}: {e}")
                return False

    def fetch_config(self, config_url="https://mitre-attack.github.io/attack-navigator/assets/config.json"):
        """Fetch the MITRE ATT&CK Navigator configuration."""
        try:
            logger.info(f"Fetching config from: {config_url}")
            response = requests.get(config_url, timeout=30)
            response.raise_for_status()
            config = response.json()

            # Maybe save this original config in the future
            #             
            # config_path = self.config_dir / "config.json"
            # with open(config_path, 'w', encoding='utf-8') as f:
            #     json.dump(config, f, indent=2, ensure_ascii=False)
            
            # logger.info(f"Config saved to {config_path}")
            return config
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch config from {config_url}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config response: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching config: {e}")
            raise

    def fetch_collection_index(self, config):
        """Fetch the collection index from the config."""
        try:
            if "collection_index_url" not in config:
                raise KeyError("collection_index_url not found in config")
            
            collection_index_url = config["collection_index_url"]
            logger.info(f"Loading collection index from: {collection_index_url}")
            
            response = requests.get(collection_index_url, timeout=30)
            response.raise_for_status()
            collection_index = response.json()
            
            # Maybe save this original index in the future
            # index_path = self.config_dir / "index.json"
            # with open(index_path, 'w', encoding='utf-8') as f:
            #     json.dump(collection_index, f, indent=2, ensure_ascii=False)
            
            # logger.info(f"Collection index saved to {index_path}")
            return collection_index
            
        except KeyError as e:
            logger.error(f"Missing key in config: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch collection index: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in collection index response: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching collection index: {e}")
            raise

    def normalize_collection_name(self, collection_name):
        """Convert collection name to a directory-friendly format."""
        if not collection_name:
            return "unknown"
        
        # Convert to lowercase
        normalized = collection_name.lower()
        # Remove common prefixes/suffixes and normalize
        normalized = normalized.replace("att&ck", "attack")
        normalized = normalized.replace("&", "and")
        
        # Replace spaces and special characters with hyphens
        import re
        normalized = re.sub(r'[^\w\s-]', '', normalized)
        normalized = re.sub(r'[-\s]+', '-', normalized)

        # Remove leading/trailing hyphens
        normalized = normalized.strip('-')
        
        return normalized or "unknown"

    def get_local_path_for_collection(self, collection_name, filename):
        """Get the appropriate local directory for a collection, creating it if needed."""
        # Normalize collection name to create directory
        dir_name = self.normalize_collection_name(collection_name)
        
        # Cache the directory path
        if dir_name not in self.collection_dirs:
            collection_dir = self.data_dir / dir_name
            collection_dir.mkdir(exist_ok=True)
            self.collection_dirs[dir_name] = collection_dir
            logger.info(f"Created directory for collection '{collection_name}': {collection_dir}")
        
        return self.collection_dirs[dir_name] / filename

    def download_all_collections(self, collection_index):
        """Download all collection files and update URLs to local paths."""
        try:
            if "collections" not in collection_index:
                raise KeyError("collections not found in collection index")
            
            updated_collections = []
            total_files = 0
            downloaded_files = 0
            failed_files = []
            
            # Count total files first
            for collection in collection_index["collections"]:
                if "versions" in collection:
                    total_files += len(collection["versions"])
            
            logger.info(f"Found {total_files} files to download across {len(collection_index['collections'])} collections")
            
            for collection in collection_index["collections"]:
                logger.info(f"Processing collection: {collection.get('name', 'Unknown')}")
                
                updated_collection = collection.copy()
                updated_versions = []
                
                if "versions" not in collection:
                    logger.warning(f"No versions found in collection {collection.get('name', 'Unknown')}")
                    updated_collections.append(updated_collection)
                    continue
                
                for version in collection["versions"]:
                    if "url" not in version:
                        logger.warning(f"No URL found in version {version.get('version', 'Unknown')}")
                        updated_versions.append(version)
                        continue
                    
                    # Extract filename from URL
                    url = version["url"]
                    parsed_url = urlparse(url)
                    filename = os.path.basename(parsed_url.path)
                    
                    # Determine local path based on collection type
                    local_path = self.get_local_path_for_collection(collection.get('name', ''), filename)
                    
                    # Download the file
                    if self.download_file_with_retry(url, local_path):
                        downloaded_files += 1
                        # Update the version with local path
                        updated_version = version.copy()
                        updated_version["url"] = local_path.as_posix()
                        updated_versions.append(updated_version)
                    else:
                        failed_files.append(url)
                        # Keep original URL if download failed
                        updated_versions.append(version)
                
                updated_collection["versions"] = updated_versions
                updated_collections.append(updated_collection)
            
            # Update the collection index with new local paths
            updated_collection_index = collection_index.copy()
            updated_collection_index["collections"] = updated_collections
            
            # Save updated collection index
            self.updated_index_path = self.config_dir / "index_local.json"
            with open(self.updated_index_path, 'w', encoding='utf-8') as f:
                json.dump(updated_collection_index, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated collection index saved to {self.updated_index_path}")
            logger.info(f"Download summary: {downloaded_files}/{total_files} files downloaded successfully")
            
            if failed_files:
                logger.warning(f"Failed to download {len(failed_files)} files:")
                for failed_url in failed_files:
                    logger.warning(f"  - {failed_url}")
            
            return updated_collection_index
            
        except Exception as e:
            logger.error(f"Error downloading collections: {e}")
            raise

    def update_config_for_local_use(self, config):
        """Update config to use local collection index."""
        updated_config = config.copy()
        updated_config["collection_index_url"] = self.updated_index_path.as_posix()
        
        # Save updated config
        self.updated_config_path = self.config_dir / "config_local.json"
        with open(self.updated_config_path, 'w', encoding='utf-8') as f:
            json.dump(updated_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated config saved to {self.updated_config_path}")
        return updated_config

    def run(self):
        """Main method to download all MITRE ATT&CK data."""
        try:
            logger.info("Starting MITRE ATT&CK data download process")
            
            # Step 1: Fetch config
            config = self.fetch_config()
            
            # Step 2: Fetch collection index
            collection_index = self.fetch_collection_index(config)
            
            # Step 3: Download all collection files
            updated_collection_index = self.download_all_collections(collection_index)
            
            # Step 4: Update config for local use
            updated_config = self.update_config_for_local_use(config)
            
            logger.info("MITRE ATT&CK data download process completed successfully")
            logger.info(f"All data saved to: {self.base_dir.absolute()}")
            logger.info(f"Use local config: {self.updated_config_path}")
            logger.info(f"Use local index: {self.updated_index_path}")
            
            return {
                "config": updated_config,
                "collection_index": updated_collection_index,
                "base_dir": str(self.base_dir.absolute())
            }
            
        except Exception as e:
            logger.error(f"Failed to complete download process: {e}")
            raise


def main():
    """Example usage of the MitreAttackDownloader."""
    try:
        downloader = MitreAttackDownloader("mitre_attack_local")
        result = downloader.run()
        
        print(f"Data location: {result['base_dir']}")
        print(f"Collections downloaded: {len(result['collection_index']['collections'])}")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()