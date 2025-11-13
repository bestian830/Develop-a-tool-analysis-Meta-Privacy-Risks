"""
数据库配置和初始化
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path

# 数据库路径
BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / 'data' / 'policy_analysis.db'
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# 创建数据库引擎，确保UTF-8编码
engine = create_engine(
    f'sqlite:///{DATABASE_PATH}', 
    echo=False,
    connect_args={'check_same_thread': False}
)

# 创建会话
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """初始化数据库"""
    from models import PolicyAnalysis, PolicyComparison
    Base.metadata.create_all(bind=engine)

