"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.sql import func
from database import Base


class PolicyAnalysis(Base):
    """隐私政策分析结果模型"""
    __tablename__ = 'policy_analyses'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False, index=True)
    policy_content = Column(Text, nullable=False)  # 爬取的原始内容（不展示）
    analysis_result = Column(JSON, nullable=False)  # 分析结果JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 摘要字段（方便查询）
    total_segments = Column(Integer)
    average_risk_score = Column(Float)
    total_data_types = Column(Integer)
    total_third_parties = Column(Integer)
    
    def to_dict(self):
        """转换为字典"""
        import json
        # 确保analysis_result是字典格式（如果存储时是JSON字符串则解析）
        analysis_result = self.analysis_result
        if isinstance(analysis_result, str):
            try:
                analysis_result = json.loads(analysis_result)
            except:
                pass
        
        # 清理文本内容，确保UTF-8编码
        if isinstance(analysis_result, dict):
            analysis_result = self._clean_text_in_dict(analysis_result)
        
        return {
            'id': self.id,
            'url': self.url,
            'analysis_result': analysis_result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'summary': {
                'total_segments': self.total_segments,
                'average_risk_score': self.average_risk_score,
                'total_data_types': self.total_data_types,
                'total_third_parties': self.total_third_parties
            },
            'type': 'analysis'
        }
    
    def _clean_text_in_dict(self, obj):
        """递归清理字典中的文本，确保UTF-8编码"""
        if isinstance(obj, dict):
            return {k: self._clean_text_in_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_text_in_dict(item) for item in obj]
        elif isinstance(obj, str):
            # 只做最基本的清理：移除控制字符
            # 不要过度清理，避免破坏正常文本
            import re
            # 移除控制字符（但保留Unicode字符）
            cleaned = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', obj)
            return cleaned
        else:
            return obj


class PolicyComparison(Base):
    """隐私政策版本对比结果模型"""
    __tablename__ = 'policy_comparisons'
    
    id = Column(Integer, primary_key=True)
    old_url = Column(String(500), nullable=True)  # 旧版本URL（如果通过URL对比）
    new_url = Column(String(500), nullable=True)  # 新版本URL（如果通过URL对比）
    comparison_result = Column(JSON, nullable=False)  # 对比结果JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 摘要字段（方便查询）
    risk_change = Column(Float)  # 风险变化值
    old_average_risk = Column(Float)  # 旧版本平均风险
    new_average_risk = Column(Float)  # 新版本平均风险
    
    def to_dict(self):
        """转换为字典"""
        import json
        # 确保comparison_result是字典格式
        comparison_result = self.comparison_result
        if isinstance(comparison_result, str):
            try:
                comparison_result = json.loads(comparison_result)
            except:
                pass
        
        # 清理文本内容
        if isinstance(comparison_result, dict):
            comparison_result = self._clean_text_in_dict(comparison_result)
        
        return {
            'id': self.id,
            'old_url': self.old_url,
            'new_url': self.new_url,
            'comparison_result': comparison_result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'summary': {
                'risk_change': self.risk_change,
                'old_average_risk': self.old_average_risk,
                'new_average_risk': self.new_average_risk
            },
            'type': 'comparison'
        }
    
    def _clean_text_in_dict(self, obj):
        """递归清理字典中的文本，确保UTF-8编码"""
        if isinstance(obj, dict):
            return {k: self._clean_text_in_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_text_in_dict(item) for item in obj]
        elif isinstance(obj, str):
            import re
            cleaned = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', obj)
            return cleaned
        else:
            return obj

