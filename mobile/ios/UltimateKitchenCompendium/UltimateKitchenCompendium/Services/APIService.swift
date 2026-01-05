import Foundation
import Combine

class APIService {
    static let shared = APIService()
    
    private let baseURL: String
    private let session: URLSession
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        self.baseURL = UserDefaults.standard.string(forKey: "serverURL") ?? "http://localhost:8000"
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        config.httpCookieStorage = nil
        config.httpShouldSetCookies = false
        
        self.session = URLSession(configuration: config)
    }
    
    func updateServerURL(_ url: String) {
        UserDefaults.standard.set(url, forKey: "serverURL")
        self.baseURL = url
    }
    
    private func makeRequest<T: Codable>(
        _ endpoint: String,
        method: HTTPMethod = .get,
        parameters: [String: Any]? = nil,
        requiresAuth: Bool = true
    ) -> AnyPublisher<T, APIError> {
        guard let url = URL(string: "\(baseURL)/api/v1\(endpoint)") else {
            return Fail(error: APIError.networkError("Invalid URL"))
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        if requiresAuth, let token = AuthService.shared.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        if let parameters = parameters {
            do {
                request.httpBody = try JSONSerialization.data(withJSONObject: parameters)
            } catch {
                return Fail(error: APIError.networkError("Failed to encode parameters"))
                    .eraseToAnyPublisher()
            }
        }
        
        return session.dataTaskPublisher(for: request)
            .mapError { error in
                APIError.networkError(error.localizedDescription)
            }
            .flatMap { data, response -> AnyPublisher<T, APIError> in
                guard let httpResponse = response as? HTTPURLResponse else {
                    return Fail(error: APIError.networkError("Invalid response"))
                        .eraseToAnyPublisher()
                }
                
                if (200...299).contains(httpResponse.statusCode) {
                    return Just(data)
                        .decode(type: T.self, decoder: JSONDecoder())
                        .mapError { error in
                            APIError.decodingError(error.localizedDescription)
                        }
                        .eraseToAnyPublisher()
                } else if httpResponse.statusCode == 401 {
                    AuthService.shared.clearTokens()
                    return Fail(error: APIError.unauthorized)
                        .eraseToAnyPublisher()
                } else {
                    do {
                        let errorResponse = try JSONDecoder().decode(APIErrorResponse.self, from: data)
                        return Fail(error: APIError.serverError(errorResponse.detail))
                            .eraseToAnyPublisher()
                    } catch {
                        return Fail(error: APIError.httpError(httpResponse.statusCode))
                            .eraseToAnyPublisher()
                    }
                }
            }
            .eraseToAnyPublisher()
    }
    
    func get<T: Codable>(_ endpoint: String, parameters: [String: Any]? = nil) -> AnyPublisher<T, APIError> {
        return makeRequest(endpoint, method: .get, parameters: parameters)
    }
    
    func post<T: Codable>(_ endpoint: String, parameters: [String: Any]) -> AnyPublisher<T, APIError> {
        return makeRequest(endpoint, method: .post, parameters: parameters)
    }
    
    func put<T: Codable>(_ endpoint: String, parameters: [String: Any]) -> AnyPublisher<T, APIError> {
        return makeRequest(endpoint, method: .put, parameters: parameters)
    }
    
    func delete<T: Codable>(_ endpoint: String) -> AnyPublisher<T, APIError> {
        return makeRequest(endpoint, method: .delete)
    }
}

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
    case patch = "PATCH"
}

enum APIError: Error, LocalizedError {
    case networkError(String)
    case decodingError(String)
    case serverError(String)
    case unauthorized
    case httpError(Int)
    case validationError([String: String])
    
    var errorDescription: String? {
        switch self {
        case .networkError(let message):
            return "Network error: \(message)"
        case .decodingError(let message):
            return "Data format error: \(message)"
        case .serverError(let message):
            return "Server error: \(message)"
        case .unauthorized:
            return "Session expired. Please log in again."
        case .httpError(let code):
            return "HTTP error \(code)"
        case .validationError(let errors):
            return errors.values.joined(separator: "\n")
        }
    }
}

struct APIErrorResponse: Codable {
    let detail: String
    let code: String?
}

struct ValidationErrorResponse: Codable {
    let detail: [String: String]
}