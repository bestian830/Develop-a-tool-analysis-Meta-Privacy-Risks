"""
Flask API for Privacy Policy Analyzer
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import json

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, db_session
from models import PolicyAnalysis
from services import PolicyService

app = Flask(__name__)
# 配置CORS，允许所有来源和所有方法
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 确保JSON编码正确
app.config['JSON_AS_ASCII'] = False  # 允许非ASCII字符
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# 初始化数据库
init_db()

# 初始化服务
policy_service = PolicyService()


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "message": "API is running"})


@app.route('/api/analyze', methods=['POST'])
def analyze_policy():
    """
    分析隐私政策
    
    请求体:
    {
        "url": "https://example.com/privacy-policy"
    }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # 爬取并分析
        result = policy_service.analyze_policy_from_url(url)
        
        # 确保返回的JSON编码正确
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error in analyze_policy: {error_msg}")
        print(traceback.format_exc())
        return jsonify({"error": error_msg}), 500


@app.route('/api/reports', methods=['GET'])
def get_reports():
    """获取所有分析报告列表"""
    try:
        reports = policy_service.get_all_reports()
        response = jsonify({"reports": reports})
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """获取单个分析报告"""
    try:
        report = policy_service.get_report_by_id(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404
        # 确保返回的JSON编码正确
        response = jsonify(report)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """删除分析报告"""
    try:
        success = policy_service.delete_report(report_id)
        if not success:
            return jsonify({"error": "Report not found"}), 404
        return jsonify({"message": "Report deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/compare', methods=['POST', 'OPTIONS'])
def compare_policies():
    """
    对比两个版本的隐私政策
    
    请求体:
    {
        "old_url": "https://example.com/privacy-policy-v1",
        "new_url": "https://example.com/privacy-policy-v2",
        "save": true  // 可选，是否保存结果
    }
    或
    {
        "old_text": "旧版本文本内容...",
        "new_text": "新版本文本内容...",
        "save": true  // 可选，是否保存结果
    }
    """
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200
    
    try:
        data = request.get_json()
        save_result = data.get('save', False)  # 默认不保存
        
        # 检查是URL对比还是文本对比
        if 'old_url' in data and 'new_url' in data:
            # URL对比
            old_url = data.get('old_url')
            new_url = data.get('new_url')
            
            if not old_url or not new_url:
                return jsonify({"error": "Both old_url and new_url are required"}), 400
            
            result = policy_service.compare_policy_versions(old_url, new_url)
            comparison_result = result['comparison_result']
            
            # 如果需要保存
            if save_result:
                saved = policy_service.save_comparison(
                    old_url=old_url,
                    new_url=new_url,
                    comparison_result=comparison_result
                )
                result['saved_id'] = saved['id']
                
        elif 'old_text' in data and 'new_text' in data:
            # 文本对比
            old_text = data.get('old_text')
            new_text = data.get('new_text')
            
            if not old_text or not new_text:
                return jsonify({"error": "Both old_text and new_text are required"}), 400
            
            result = policy_service.compare_policy_texts(old_text, new_text)
            comparison_result = result['comparison_result']
            
            # 如果需要保存
            if save_result:
                saved = policy_service.save_comparison(
                    comparison_result=comparison_result
                )
                result['saved_id'] = saved['id']
        else:
            return jsonify({"error": "Either (old_url, new_url) or (old_text, new_text) must be provided"}), 400
        
        # 确保返回的JSON编码正确
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error in compare_policies: {error_msg}")
        print(traceback.format_exc())
        response = jsonify({"error": error_msg})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


@app.route('/api/comparisons', methods=['GET'])
def get_comparisons():
    """获取所有对比报告列表"""
    try:
        comparisons = policy_service.get_all_comparisons()
        response = jsonify({"comparisons": comparisons})
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


@app.route('/api/comparisons/<int:comparison_id>', methods=['GET'])
def get_comparison(comparison_id):
    """获取单个对比报告"""
    try:
        comparison = policy_service.get_comparison_by_id(comparison_id)
        if not comparison:
            response = jsonify({"error": "Comparison not found"})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 404
        response = jsonify(comparison)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


@app.route('/api/comparisons/<int:comparison_id>', methods=['DELETE'])
def delete_comparison(comparison_id):
    """删除对比报告"""
    try:
        success = policy_service.delete_comparison(comparison_id)
        if not success:
            response = jsonify({"error": "Comparison not found"})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 404
        response = jsonify({"message": "Comparison deleted successfully"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


@app.teardown_appcontext
def shutdown_session(exception=None):
    """关闭数据库会话"""
    db_session.remove()



