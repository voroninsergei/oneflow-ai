"""
OneFlow.AI - Database Module
Модуль базы данных OneFlow.AI

This module provides database integration using SQLAlchemy ORM.
Supports both SQLite (development) and PostgreSQL (production).

Этот модуль обеспечивает интеграцию с базой данных через SQLAlchemy ORM.
Поддерживает SQLite (разработка) и PostgreSQL (продакшн).
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import os

# Create base class for declarative models
Base = declarative_base()

# Database Models / Модели базы данных

class User(Base):
    """
    User model for multi-user support.
    Модель пользователя для поддержки множества пользователей.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    api_key = Column(String(64), unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', balance={self.balance})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'balance': self.balance,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Request(Base):
    """
    AI request history model.
    Модель истории AI запросов.
    """
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)  # Foreign key to users
    provider = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    cost = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # success, error, budget_exceeded, etc.
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional data as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Request(id={self.id}, provider='{self.provider}', cost={self.cost}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
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
            'created_at': self.created_at.isoformat()
        }


class Transaction(Base):
    """
    Wallet transaction history.
    История транзакций кошелька.
    """
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    type = Column(String(20), nullable=False)  # add, deduct, refund
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    description = Column(String(200), nullable=True)
    request_id = Column(Integer, nullable=True)  # Link to request if applicable
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.type}', amount={self.amount})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'amount': self.amount,
            'balance_before': self.balance_before,
            'balance_after': self.balance_after,
            'description': self.description,
            'request_id': self.request_id,
            'created_at': self.created_at.isoformat()
        }


class BudgetConfig(Base):
    """
    Budget configuration storage.
    Хранение конфигурации бюджетов.
    """
    __tablename__ = 'budget_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    period = Column(String(20), nullable=False)  # daily, weekly, monthly, total
    limit_amount = Column(Float, nullable=True)  # NULL means no limit
    spent_amount = Column(Float, default=0.0)
    reset_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<BudgetConfig(period='{self.period}', limit={self.limit_amount}, spent={self.spent_amount})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'period': self.period,
            'limit_amount': self.limit_amount,
            'spent_amount': self.spent_amount,
            'reset_at': self.reset_at.isoformat() if self.reset_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ProviderConfig(Base):
    """
    Provider configuration and rates.
    Конфигурация и тарифы провайдеров.
    """
    __tablename__ = 'provider_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    rate_per_unit = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    budget_limit = Column(Float, nullable=True)
    spent_amount = Column(Float, default=0.0)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProviderConfig(provider='{self.provider_name}', rate={self.rate_per_unit})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'provider_name': self.provider_name,
            'rate_per_unit': self.rate_per_unit,
            'is_active': self.is_active,
            'budget_limit': self.budget_limit,
            'spent_amount': self.spent_amount,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# Database Manager Class

class DatabaseManager:
    """
    Database manager for OneFlow.AI.
    Менеджер базы данных для OneFlow.AI.
    """
    
    def __init__(self, database_url: str = None):
        """
        Initialize database manager.
        Инициализировать менеджер базы данных.
        
        Args:
            database_url: Database connection URL.
                         If None, uses SQLite with default path.
        """
        if database_url is None:
            # Default to SQLite in data directory
            db_path = os.path.join(os.getcwd(), 'data', 'oneflow.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            database_url = f'sqlite:///{db_path}'
        
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True  # Verify connections before using
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create all tables
        self.create_tables()
    
    def create_tables(self):
        """
        Create all database tables.
        Создать все таблицы базы данных.
        """
        Base.metadata.create_all(bind=self.engine)
        print("✓ Database tables created successfully")
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        Получить новую сессию базы данных.
        
        Returns:
            Database session.
        """
        return self.SessionLocal()
    
    def drop_all_tables(self):
        """
        Drop all tables (use with caution!).
        Удалить все таблицы (используйте осторожно!).
        """
        Base.metadata.drop_all(bind=self.engine)
        print("✓ All tables dropped")
    
    # User Management / Управление пользователями
    
    def create_user(self, username: str, email: str, initial_balance: float = 100.0) -> User:
        """
        Create a new user.
        Создать нового пользователя.
        """
        import secrets
        session = self.get_session()
        try:
            user = User(
                username=username,
                email=email,
                api_key=secrets.token_hex(32),
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
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()
    
    def update_user_balance(self, user_id: int, new_balance: float) -> bool:
        """Update user balance."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.balance = new_balance
                user.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    # Request Management / Управление запросами
    
    def create_request(self, user_id: Optional[int], provider: str, model: str,
                      prompt: str, response: str, cost: float, status: str,
                      error_message: str = None, metadata: Dict = None) -> Request:
        """
        Create a new request record.
        Создать новую запись запроса.
        """
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
        """Get request history."""
        session = self.get_session()
        try:
            query = session.query(Request)
            if user_id:
                query = query.filter(Request.user_id == user_id)
            return query.order_by(Request.created_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_requests_by_provider(self, provider: str, user_id: Optional[int] = None) -> List[Request]:
        """Get requests for specific provider."""
        session = self.get_session()
        try:
            query = session.query(Request).filter(Request.provider == provider)
            if user_id:
                query = query.filter(Request.user_id == user_id)
            return query.order_by(Request.created_at.desc()).all()
        finally:
            session.close()
    
    # Transaction Management / Управление транзакциями
    
    def create_transaction(self, user_id: Optional[int], type: str, amount: float,
                          balance_before: float, balance_after: float,
                          description: str = None, request_id: int = None) -> Transaction:
        """
        Create a new transaction record.
        Создать новую запись транзакции.
        """
        session = self.get_session()
        try:
            transaction = Transaction(
                user_id=user_id,
                type=type,
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
        """Get transaction history."""
        session = self.get_session()
        try:
            query = session.query(Transaction)
            if user_id:
                query = query.filter(Transaction.user_id == user_id)
            return query.order_by(Transaction.created_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    # Provider Configuration / Конфигурация провайдеров
    
    def create_or_update_provider(self, provider_name: str, rate_per_unit: float,
                                  is_active: bool = True, budget_limit: float = None) -> ProviderConfig:
        """
        Create or update provider configuration.
        Создать или обновить конфигурацию провайдера.
        """
        session = self.get_session()
        try:
            provider = session.query(ProviderConfig).filter(
                ProviderConfig.provider_name == provider_name
            ).first()
            
            if provider:
                provider.rate_per_unit = rate_per_unit
                provider.is_active = is_active
                provider.budget_limit = budget_limit
                provider.updated_at = datetime.utcnow()
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
    
    # Analytics / Аналитика
    
    def get_total_cost(self, user_id: Optional[int] = None) -> float:
        """Get total cost of all requests."""
        session = self.get_session()
        try:
            query = session.query(Request)
            if user_id:
                query = query.filter(Request.user_id == user_id)
            
            total = sum(r.cost for r in query.all())
            return total
        finally:
            session.close()
    
    def get_request_count(self, user_id: Optional[int] = None) -> int:
        """Get total number of requests."""
        session = self.get_session()
        try:
            query = session.query(Request)
            if user_id:
                query = query.filter(Request.user_id == user_id)
            return query.count()
        finally:
            session.close()
    
    def get_provider_stats(self, user_id: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each provider.
        Получить статистику по каждому провайдеру.
        """
        session = self.get_session()
        try:
            query = session.query(Request)
            if user_id:
                query = query.filter(Request.user_id == user_id)
            
            requests = query.all()
            stats = {}
            
            for request in requests:
                provider = request.provider
                if provider not in stats:
                    stats[provider] = {
                        'count': 0,
                        'total_cost': 0.0,
                        'success_count': 0,
                        'error_count': 0
                    }
                
                stats[provider]['count'] += 1
                stats[provider]['total_cost'] += request.cost
                
                if request.status == 'success':
                    stats[provider]['success_count'] += 1
                else:
                    stats[provider]['error_count'] += 1
            
            return stats
        finally:
            session.close()


# Singleton instance
_db_manager = None


def get_db_manager(database_url: str = None) -> DatabaseManager:
    """
    Get global database manager instance.
    Получить глобальный экземпляр менеджера БД.
    
    Args:
        database_url: Database connection URL.
    
    Returns:
        DatabaseManager instance.
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager


def reset_db_manager():
    """
    Reset global database manager.
    Сбросить глобальный менеджер БД.
    """
    global _db_manager
    _db_manager = None


# Example usage
if __name__ == '__main__':
    print("=" * 60)
    print("OneFlow.AI Database Module - Demo")
    print("=" * 60)
    
    # Initialize database
    db = get_db_manager()
    
    # Create a test user
    print("\n1. Creating test user...")
    user = db.create_user("testuser", "test@example.com", initial_balance=100.0)
    print(f"✓ Created user: {user.username} (ID: {user.id}, Balance: {user.balance})")
    
    # Create provider configurations
    print("\n2. Creating provider configurations...")
    db.create_or_update_provider("gpt", 1.0, is_active=True)
    db.create_or_update_provider("image", 10.0, is_active=True, budget_limit=100.0)
    print("✓ Providers configured")
    
    # Create test requests
    print("\n3. Creating test requests...")
    req1 = db.create_request(
        user_id=user.id,
        provider="gpt",
        model="gpt-3.5-turbo",
        prompt="Hello world",
        response="Hi there!",
        cost=2.0,
        status="success"
    )
    print(f"✓ Request created: {req1.id}")
    
    # Create transaction
    print("\n4. Creating transaction...")
    trans = db.create_transaction(
        user_id=user.id,
        type="deduct",
        amount=2.0,
        balance_before=100.0,
        balance_after=98.0,
        description="GPT request",
        request_id=req1.id
    )
    print(f"✓ Transaction created: {trans.id}")
    
    # Get analytics
    print("\n5. Getting analytics...")
    total_cost = db.get_total_cost(user_id=user.id)
    request_count = db.get_request_count(user_id=user.id)
    provider_stats = db.get_provider_stats(user_id=user.id)
    
    print(f"   Total cost: {total_cost} credits")
    print(f"   Total requests: {request_count}")
    print(f"   Provider stats: {provider_stats}")
    
    print("\n" + "=" * 60)
    print("✓ Database demo completed successfully!")
    print("=" * 60)
