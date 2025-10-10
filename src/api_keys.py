    def _load_keys(self) -> None:
        """
        Load API keys from file or environment variables.
        Загрузить API ключи из файла или переменных окружения.
        """
        # Try to load from file first
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_data = json.load(f)
                    # Handle both flat and nested structures
                    for provider, value in file_data.items():
                        if isinstance(value, dict) and 'api_key' in value:
                            self.keys[provider] = value['api_key']
                        elif isinstance(value, str):
                            self.keys[provider] = value
            except Exception as e:
                print(f"Warning: Could not load API keys from file: {e}")
        
        # Override with environment variables if present
        env_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'stability': os.getenv('STABILITY_API_KEY'),
            'elevenlabs': os.getenv('ELEVENLABS_API_KEY'),
            'runway': os.getenv('RUNWAY_API_KEY'),
        }
        
        for provider, key in env_keys.items():
            if key:
                self.keys[provider] = key