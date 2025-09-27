/**
 * API Client Utility
 * 백엔드 API와의 통신을 담당하는 유틸리티 (TypeScript)
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT) || 10000;

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = API_TIMEOUT;
  }

  /**
   * HTTP 요청을 보내는 기본 메서드
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // 타임아웃 설정
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    config.signal = controller.signal;

    try {
      const response = await fetch(url, config);
      clearTimeout(timeoutId);

      // 응답 상태 확인
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: 'Unknown error occurred' };
        }
        
        throw new ApiError(
          errorData.message || `HTTP ${response.status}`,
          response.status,
          errorData
        );
      }

      // JSON 응답 파싱
      const data = await response.json();
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408);
      }
      
      if (error instanceof ApiError) {
        throw error;
      }
      
      // 네트워크 오류 등
      throw new ApiError('Network error', 0, { originalError: error });
    }
  }

  /**
   * GET 요청
   */
  async get(endpoint, params = {}) {
    const searchParams = new URLSearchParams(params);
    const url = searchParams.toString() ? `${endpoint}?${searchParams}` : endpoint;
    
    return this.request(url, {
      method: 'GET',
    });
  }

  /**
   * POST 요청
   */
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * PUT 요청
   */
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * DELETE 요청
   */
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  // === 특화된 API 메서드들 ===

  /**
   * 서버 상태 확인
   */
  async checkHealth() {
    return this.get('/health');
  }

  /**
   * 클라이언트 설정 정보 가져오기
   */
  async getConfig() {
    return this.get('/api/config');
  }

  /**
   * 주식 데이터 조회
   */
  async getStockData(symbol) {
    return this.get(`/api/stocks/${symbol.toUpperCase()}`);
  }

  /**
   * 주식 분석 요청
   */
  async analyzeStock(symbol, options = {}) {
    return this.post(`/api/analysis/${symbol.toUpperCase()}`, options);
  }

  /**
   * 포트폴리오 분석
   */
  async analyzePortfolio(symbols) {
    return this.post('/api/portfolio/analyze', { symbols });
  }

  /**
   * 거래 내역 조회
   */
  async getTransactions(params = {}) {
    return this.get('/api/transactions', params);
  }

  /**
   * 새 거래 생성
   */
  async createTransaction(transaction) {
    return this.post('/api/transactions', transaction);
  }
}

// 전역 API 클라이언트 인스턴스
const apiClient = new ApiClient();

// React Hook을 위한 유틸리티 함수들
export const useApiCall = (apiFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction(...args);
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, dependencies);

  return { data, loading, error, execute };
};

// 에러 처리 유틸리티
export const handleApiError = (error) => {
  console.error('API Error:', error);
  
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        return 'Authentication required';
      case 403:
        return 'Access denied';
      case 404:
        return 'Resource not found';
      case 408:
        return 'Request timeout';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Server error. Please try again later.';
      case 503:
        return 'Service unavailable. Please try again later.';
      default:
        return error.message || 'An unexpected error occurred';
    }
  }
  
  return 'Network error. Please check your connection.';
};

// 기본 내보내기
export default apiClient;
export { ApiError, ApiClient };
