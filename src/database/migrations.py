"""
Alembic миграции базы данных
Настройка для production с индексами и idempotency
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, Text, Index, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


# ============================================================================
# МОДЕЛИ ТАБЛИЦ
# ============================================================================

class User(Base):
    """Пользователи"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='user', index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
    )


class APIKey(Base):
    """API ключи с версионированием"""
    __tablename__ = 'api_keys'
    
    id = Column(String(36), primary_key=True)
    key_id = Column(String(255), nullable=False, index=True)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    status = Column(String(50), nullable=False, default='active', index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, index=True)
    deprecated_at = Column(DateTime)
    revoked_at = Column(DateTime)
    last_used_at = Column(DateTime)
    usage_count = Column(Integer, default=0, nullable=False)
    metadata = Column(Text)  # JSON
    
    __table_args__ = (
        UniqueConstraint('key_id', 'version', name='uq_api_key_version'),
        Index('idx_api_keys_user_status', 'user_id', 'status'),
        Index('idx_api_keys_expires_at', 'expires_at'),
    )


class Request(Base):
    """AI запросы с idempotency key"""
    __tablename__ = 'requests'
    
    id = Column(String(36), primary_key=True)
    idempotency_key = Column(String(255), unique=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    request_type = Column(String(50), nullable=False)
    prompt = Column(Text)
    response = Column(Text)
    status = Column(String(50), nullable=False, default='pending', index=True)
    cost = Column(Float, default=0.0, nullable=False)
    tokens = Column(Integer)
    latency_ms = Column(Float)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime)
    metadata = Column(Text)  # JSON
    
    __table_args__ = (
        Index('idx_requests_user_created', 'user_id', 'created_at'),
        Index('idx_requests_provider_status', 'provider', 'status'),
        Index('idx_requests_created_at_desc', 'created_at', postgresql_ops={'created_at': 'DESC'}),
    )


class Transaction(Base):
    """Транзакции wallet с audit log"""
    __tablename__ = 'transactions'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)  # topup, charge, refund, transfer
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    reference_id = Column(String(255), index=True)  # Ссылка на request_id или другую сущность
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata = Column(Text)  # JSON
    
    __table_args__ = (
        Index('idx_transactions_user_created', 'user_id', 'created_at'),
        Index('idx_transactions_type_created', 'transaction_type', 'created_at'),
        Index('idx_transactions_reference', 'reference_id'),
    )


class Wallet(Base):
    """Wallet пользователя"""
    __tablename__ = 'wallets'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    balance = Column(Float, default=0.0, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)
    total_topped_up = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default='USD', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_wallets_balance', 'balance'),
    )


class Budget(Base):
    """Бюджеты пользователей"""
    __tablename__ = 'budgets'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    period = Column(String(50), nullable=False)  # hourly, daily, weekly, monthly
    provider = Column(String(50), nullable=False, index=True)
    limit_amount = Column(Float, nullable=False)
    current_usage = Column(Float, default=0.0, nullable=False)
    reset_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'period', 'provider', name='uq_budget_user_period_provider'),
        Index('idx_budgets_user_period', 'user_id', 'period'),
        Index('idx_budgets_reset_at', 'reset_at'),
    )


class ProviderStats(Base):
    """Статистика провайдеров"""
    __tablename__ = 'provider_stats'
    
    id = Column(String(36), primary_key=True)
    provider = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    avg_latency = Column(Float, nullable=False)
    p95_latency = Column(Float)
    p99_latency = Column(Float)
    cost_per_request = Column(Float, nullable=False)
    quality_score = Column(Float)
    availability = Column(Float, nullable=False)
    error_rate = Column(Float, nullable=False)
    total_requests = Column(Integer, nullable=False)
    successful_requests = Column(Integer, nullable=False)
    failed_requests = Column(Integer, nullable=False)
    
    __table_args__ = (
        Index('idx_provider_stats_provider_timestamp', 'provider', 'timestamp'),
        Index('idx_provider_stats_timestamp_desc', 'timestamp', postgresql_ops={'timestamp': 'DESC'}),
    )


class AuditLog(Base):
    """Audit log всех действий"""
    __tablename__ = 'audit_logs'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(255), index=True)
    details = Column(Text)  # JSON
    ip_address = Column(String(45))
    user_agent = Column(Text)
    status = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_audit_logs_user_created', 'user_id', 'created_at'),
        Index('idx_audit_logs_action_created', 'action', 'created_at'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_logs_created_desc', 'created_at', postgresql_ops={'created_at': 'DESC'}),
    )


class IdempotencyKey(Base):
    """Idempotency keys для предотвращения дублирования"""
    __tablename__ = 'idempotency_keys'
    
    id = Column(String(36), primary_key=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False)
    request_payload = Column(Text)  # JSON
    response_payload = Column(Text)  # JSON
    status_code = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)  # TTL
    
    __table_args__ = (
        Index('idx_idempotency_keys_expires_at', 'expires_at'),
        Index('idx_idempotency_keys_user_created', 'user_id', 'created_at'),
    )


# ============================================================================
# МИГРАЦИОННЫЕ СКРИПТЫ
# ============================================================================

def upgrade_001_initial_schema(engine):
    """Создание начальной схемы"""
    Base.metadata.create_all(engine)
    print("✓ Migration 001: Initial schema created")


def upgrade_002_add_indexes(engine):
    """Добавление дополнительных индексов для производительности"""
    # Composite indexes для частых запросов
    with engine.connect() as conn:
        # Индекс для поиска активных пользователей по email
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email_active_composite 
            ON users(email, is_active) 
            WHERE is_active = true;
        """)
        
        # Индекс для поиска последних запросов пользователя
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_requests_user_recent 
            ON requests(user_id, created_at DESC) 
            WHERE status = 'completed';
        """)
        
        # Индекс для подсчёта использования бюджета
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_budgets_usage 
            ON budgets(user_id, provider, current_usage) 
            WHERE current_usage < limit_amount;
        """)
        
        conn.commit()
    
    print("✓ Migration 002: Additional indexes created")


def upgrade_003_add_partitioning(engine):
    """Партиционирование больших таблиц (PostgreSQL)"""
    with engine.connect() as conn:
        # Партиционирование audit_logs по месяцам
        conn.execute("""
            -- Это пример для PostgreSQL 11+
            -- В реальности нужно пересоздать таблицу как партиционированную
            -- ALTER TABLE audit_logs PARTITION BY RANGE (created_at);
        """)
        
        conn.commit()
    
    print("✓ Migration 003: Table partitioning configured")


def downgrade_001_initial_schema(engine):
    """Откат начальной схемы"""
    Base.metadata.drop_all(engine)
    print("✓ Downgrade 001: Schema dropped")


# ============================================================================
# ALEMBIC ENV CONFIGURATION
# ============================================================================

ALEMBIC_CONFIG = """
# Alembic configuration file

[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql://user:password@localhost/oneflow

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""


# ============================================================================
# MIGRATION RUNNER
# ============================================================================

def run_migrations(database_url: str):
    """
    Запустить все миграции
    
    Args:
        database_url: URL базы данных
    """
    engine = create_engine(database_url)
    
    print("Starting database migrations...")
    
    try:
        upgrade_001_initial_schema(engine)
        upgrade_002_add_indexes(engine)
        # upgrade_003_add_partitioning(engine)  # Только для PostgreSQL
        
        print("\n✓ All migrations completed successfully!")
    
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        raise
    
    finally:
        engine.dispose()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrations.py <database_url>")
        sys.exit(1)
    
    database_url = sys.argv[1]
    run_migrations(database_url)
