    def estimate_cost(self, provider_name: str, units: float) -> float:
        """Estimate cost for given provider and units.
        Оценка стоимости для заданного поставщика и количества единиц.

        Args:
            provider_name (str): Provider identifier.
            units (float): Number of units.

        Returns:
            float: Estimated cost, or 0.0 if provider not found.
        """
        if provider_name not in self.rates:
            return 0.0
        rate = self.rates.get(provider_name, 0.0)
        return rate * units
    
    def get_rate(self, provider_name: str) -> float:
        """Get rate for a provider.
        
        Args:
            provider_name: Provider name.
        
        Returns:
            float: Rate per unit, or 0.0 if not found.
        """
        return self.rates.get(provider_name, 0.0)
    
    def has_provider(self, provider_name: str) -> bool:
        """Check if provider exists.
        
        Args:
            provider_name: Provider name.
        
        Returns:
            bool: True if provider exists.
        """
        return provider_name in self.rates
    
    def get_all_rates(self):
        """Get all registered rates.
        
        Returns:
            dict: All provider rates.
        """
        return self.rates.copy()