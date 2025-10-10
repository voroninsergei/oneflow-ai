"""
Database module for OneFlow.AI.
Модуль базы данных для OneFlow.AI.

Provides SQLAlchemy ORM models and database management.
Предоставляет модели SQLAlchemy ORM и управление базой данных.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

Base = declarative_base()


# Database Models

class User(Base):
    """User model."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    api_key = Column(String(64), unique=True)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'balance': self.balance,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Request(Base):
    """Request history model."""
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    provider = Column(String(50), nullable=False)
    model = Column(String(50))
    prompt = Column(Text, nullable=False)
    response = Column(Text)
    cost = Column(Float, nullable=False)
    status = Column(String(20), default='success')
    error_message = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider': self.provider,
            'model': self.model,
            'prompt': self.prompt,
            'response': self.response,
            'cost': self.cost,
            'status': self.status,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Transaction(Base):
    """Transaction history model."""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    type = Column(String(20), nullable=False)  # add, deduct, refund
    amount = Column(Float, nullable=False)
    balance_before = Column(Float)
    balance_after = Column(Float)
    description = Column(String(200))
    request_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'amount': self.amount,
            'balance_before': self.balance_before,
            'balance_after': self.balance_after,
            'description': self.description,
            'request_id': self.request_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProviderConfig(Base):
    """Provider configuration model."""
    __tablename__ = 'provider_configs'
    
    id = Column(Integer, primary_key=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    rate_per_unit = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    budget_limit = Column(Float)
    spent_amount = Column(Float, default=0.0)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_name': self.provider_name,
            'rate_per_unit': self.rate_per_unit,
            'is_active': self.is_active,
            'budget_limit': self.budget_limit,
            'spent_amount': self.spent_amount,
            'metadata': self.metadata
        }


class BudgetConfig(Base):
    """Budget configuration model."""
    __tablename__ = 'budget_configs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    period = Column(String(20), nullable=False)  # daily, weekly, monthly, total
    limit_amount = Column(Float)
    spent_amount = Column(Float, default=0.0)
    reset_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'period': self.period,
            'limit_amount': self.limit_amount,
            'spent_amount': self.spent_amount,
            'reset_at': self.reset_at.isoformat() if self.reset_at else None
        }


# Database Manager

class DatabaseManager:
    """
    Database management class.
    Класс управления базой данных.
    """
    
    def __init__(self, database_url: str = 'sqlite:///data/oneflow.db'):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL.
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create all tables."""
        # Ensure data directory exists
        if 'sqlite:///' in str(self.engine.url):
            db_path = str(self.engine.url).replace('sqlite:///', '')
            os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        
        Base.metadata.create_all(self.engine)
    
    def drop_all_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(self.engine)
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    # User operations
    
    def create_user(self, username: str, email: str, initial_balance: float = 100.0) -> User:
        """Create a new user."""
        session = self.get_session()
        try:
            user = User(
                username=username,
                email=email,
                balance=initial_balance
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()
    
    def update_user_balance(self, user_id: int, new_balance: float):
        """Update user balance."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.balance = new_balance
                session.commit()
        finally:
            session.close()
    
    # Request operations
    
    def create_request(
        self,
        user_id: Optional[int],
        provider: str,
        model: str,
        prompt: str,
        response: str,
        cost: float,
        status: str = 'success',
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Request:
        """Create a new request record."""
        session = self.get_session()
        try:
            request = Request(
                user_id=user_id,
                provider=provider,
                model=model,
                prompt=prompt,
                response=response,
                cost=cost,
                status=status,
                error_message=error_message,
                metadata=metadata
            )
            session.add(request)
            session.commit()
            session.refresh(request)
            return request
        finally:
            session.close()
    
    def get_requests(self, user_id: Optional[int] = None, limit: int = 100) -> List[Request]:
        """Get requests with optional user filter."""
        session = self.get_session()
        try:
            query = session.query(Request)
            if user_id is not None:
                query = query.filter(Request.user_id == user_id)
            return query.order_by(Request.created_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_requests_by_provider(self, provider: str) -> List[Request]:
        """Get all requests for a specific provider."""
        session = self.get_session()
        try:
            return session.query(Request).filter(Request.provider == provider).all()
        finally:
            session.close()
    
    # Transaction operations
    
    def create_transaction(
        self,
        user_id: Optional[int],
        trans_type: str,
        amount: float,
        balance_before: float,
        balance_after: float,
        description: Optional[str] = None,
        request_id: Optional[int] = None
    ) -> Transaction:
        """Create a new transaction record."""
        session = self.get_session()
        try:
            transaction = Transaction(
                user_id=user_id,
                type=trans_type,
                amount=amount,
                balance_before=balance_before,
                balance_after=balance_after,
                description=description,
                request_id=request_id
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return transaction
        finally:
            session.close()
    
    def get_transactions(self, user_id: Optional[int] = None, limit: int = 100) -> List[Transaction]:
        """Get transactions with optional user filter."""
        session = self.get_session()
        try:
            query = session.query(Transaction)
            if user_id is not None:
                query = query.filter(Transaction.user_id == user_id)
            return query.order_by(Transaction.created_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    # Provider operations
    
    def create_or_update_provider(
        self,
        provider_name: str,
        rate_per_unit: float,
        is_active: bool = True,
        budget_limit: Optional[float] = None
    ) -> ProviderConfig:
        """Create or update provider configuration."""
        session = self.get_session()
        try:
            provider = session.query(ProviderConfig).filter(
                ProviderConfig.provider_name == provider_name
            ).first()
            
            if provider:
                provider.rate_per_unit = rate_per_unit
                provider.is_active = is_active
                provider.budget_limit = budget_limit
            else:
                provider = ProviderConfig(
                    provider_name=provider_name,
                    rate_per_unit=rate_per_unit,
                    is_active=is_active,
                    budget_limit=budget_limit
                )
                session.add(provider)
            
            session.commit()
            session.refresh(provider)
            return provider
        finally:
            session.close()
    
    def get_provider(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get provider configuration."""
        session = self.get_session()
        try:
            return session.query(ProviderConfig).filter(
                ProviderConfig.provider_name == provider_name
            ).first()
        finally:
            session.close()
    
    def get_all_providers(self) -> List[ProviderConfig]:
        """Get all provider configurations."""
        session = self.get_session()
        try:
            return session.query(ProviderConfig).all()
        finally:
            session.close()
    
    # Analytics operations
    
    def get_total_cost(self, user_id: Optional[int] = None) -> float:
        """Get total cost of all requests."""
        session = self.get_session()
        try:
            query = session.query(Request)
            if user_id is not None:
                query = query.filter(Request.user_id == user_id)
            
            total = sum(req.cost for req in query.all())
            return total
        finally:
            session.close()
    
    def get_request_count(self, user_id: Optional[int] = None) -> int:
        """Get total number of requests."""
        session = self.get_session()
        try:
            query = session.query(Request)
            if user_id is not None:
                query = query.filter(Request.user_id == user_id)
            return query.count()
        finally:
            session.close()
    
    def get_provider_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get statistics by provider."""
        session = self.get_session()
        try:
            query = session.query(Request)
            if user_id is not None:
                query = query.filter(Request.user_id == user_id)
            
            requests = query.all()
            stats = {}
            
            for req in requests:
                provider = req.provider
                if provider not in stats:
                    stats[provider] = {
                        'count': 0,
                        'total_cost': 0.0,
                        'success_count': 0,
                        'error_count': 0
                    }
                
                stats[provider]['count'] += 1
                stats[provider]['total_cost'] += req.cost
                
                if req.status == 'success':
                    stats[provider]['success_count'] += 1
                else:
                    stats[provider]['error_count'] += 1
            
            return stats
        finally:
            session.close()


# Global instance

_db_manager = None


def get_db_manager(database_url: str = 'sqlite:///data/oneflow.db') -> DatabaseManager:
    """
    Get global database manager instance.
    
    Args:
        database_url: Database connection URL.
    
    Returns:
        DatabaseManager: Global database manager.
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager


def engine(db_path="sqlite:///data/oneflow.db"):
    """Helper function for compatibility."""
    from sqlalchemy import create_engine as sqlalchemy_create_engine
    return sqlalchemy_create_engine(db_path, future=True)
