import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

// 调试：显示当前使用的 API URL
console.log('API Base URL:', API_BASE_URL);

// 如果使用 ngrok，检测并提示用户
if (API_BASE_URL.includes('ngrok')) {
    console.warn('Using ngrok URL. If you see ngrok warning pages, please visit the ngrok URL in browser first and click "Visit Site"');
}

// 如果使用 cloudflared，显示提示
if (API_BASE_URL.includes('trycloudflare')) {
    console.log('Using cloudflared URL for backend API');
}

export interface AnalysisResult {
  id: number;
  url: string;
  analysis_result: {
    summary: {
      total_segments: number;
      average_risk_score: number;
      category_distribution: Record<string, number>;
      total_data_types: string[];
      total_third_parties: string[];
      total_purposes: string[];
      data_collection_by_activity?: Record<string, {
        data_types: string[];
        description: string;
        segment_count: number;
        segments: Array<{
          segment_id: number;
          text_preview: string;
          risk_score: number;
        }>;
      }>;
    };
    segment_analyses: Array<{
      text: string;
      category: string;
      category_cn: string;
      parameters: {
        data_types: string[];
        purposes: string[];
        third_parties: string[];
        retention_period: string | null;
        user_rights: string[];
        security_measures: string[];
      };
      risk_score: number;
      explanation: string;
    }>;
  };
  created_at: string;
}

export interface ReportSummary {
  id: number;
  url: string;
  created_at: string;
  summary: {
    total_segments: number;
    average_risk_score: number;
    total_data_types: number;
    total_third_parties: number;
  };
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加请求拦截器用于调试
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// 添加响应拦截器用于调试
api.interceptors.response.use(
  (response) => {
    // 检查是否是 ngrok 警告页面
    if (typeof response.data === 'string' && response.data.includes('ERR_NGROK')) {
      console.error('ngrok warning page detected. Please click "Visit Site" button on ngrok page first.');
      throw new Error('ngrok warning page: Please visit the ngrok URL in browser first and click "Visit Site"');
    }
    console.log('API Response:', response.config.url, response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.config?.url, error.response?.status, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const analyzePolicy = async (url: string): Promise<AnalysisResult> => {
  const response = await api.post('/analyze', { url });
  return response.data;
};

export const getAllReports = async (): Promise<ReportSummary[]> => {
  const response = await api.get('/reports');
  return response.data.reports;
};

export const getReportById = async (id: number): Promise<AnalysisResult> => {
  const response = await api.get(`/reports/${id}`);
  return response.data;
};

export const deleteReport = async (id: number): Promise<void> => {
  await api.delete(`/reports/${id}`);
};

export interface ComparisonResult {
  id?: number;
  old_url?: string;
  new_url?: string;
  saved_id?: number;
  created_at?: string;
  comparison_result: {
    summary_changes: {
      data_types: {
        added: string[];
        removed: string[];
        unchanged: string[];
        has_changes: boolean;
      };
      third_parties: {
        added: string[];
        removed: string[];
        unchanged: string[];
        has_changes: boolean;
      };
      user_rights: {
        added: string[];
        removed: string[];
        unchanged: string[];
        has_changes: boolean;
      };
      security_measures: {
        added: string[];
        removed: string[];
        unchanged: string[];
        has_changes: boolean;
      };
      purposes: {
        added: string[];
        removed: string[];
        unchanged: string[];
        has_changes: boolean;
      };
    };
    category_changes: Record<string, {
      old_count: number;
      new_count: number;
      count_change: number;
      matched_segments: number;
      added_segments: Array<{
        text: string;
        parameters: any;
        risk_score: number;
      }>;
      removed_segments: Array<{
        text: string;
        parameters: any;
        risk_score: number;
      }>;
      modified_segments: Array<{
        old_text: string;
        new_text: string;
        similarity: number;
        is_modified: boolean;
        parameter_changes: any;
        old_risk: number;
        new_risk: number;
        risk_change: number;
      }>;
    }>;
    risk_change: {
      old_average_risk: number;
      new_average_risk: number;
      risk_change: number;
      risk_increased: boolean;
    };
  };
}

export const comparePolicies = async (
  oldUrl?: string,
  newUrl?: string,
  oldText?: string,
  newText?: string,
  save: boolean = false
): Promise<ComparisonResult> => {
  const payload: any = { save };
  if (oldUrl && newUrl) {
    payload.old_url = oldUrl;
    payload.new_url = newUrl;
  } else if (oldText && newText) {
    payload.old_text = oldText;
    payload.new_text = newText;
  } else {
    throw new Error('Either URLs or texts must be provided');
  }
  
  const response = await api.post('/compare', payload);
  return response.data;
};

export const getAllComparisons = async (): Promise<ComparisonSummary[]> => {
  const response = await api.get('/comparisons');
  return response.data.comparisons;
};

export const getComparisonById = async (id: number): Promise<ComparisonResult> => {
  const response = await api.get(`/comparisons/${id}`);
  return response.data;
};

export const deleteComparison = async (id: number): Promise<void> => {
  await api.delete(`/comparisons/${id}`);
};

export interface ComparisonSummary {
  id: number;
  old_url?: string;
  new_url?: string;
  created_at: string;
  summary: {
    risk_change: number;
    old_average_risk: number;
    new_average_risk: number;
  };
  type: 'comparison';
}

export default api;

