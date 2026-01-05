import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authService: AuthService
    @State private var email = ""
    @State private var password = ""
    @State private var fullName = ""
    @State private var isRegistering = false
    @State private var showAlert = false
    @State private var errorMessage = ""
    
    var body: some View {
        NavigationView {
            VStack {
                Spacer()
                
                Image(systemName: "fork.knife.circle.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.appPrimary)
                    .padding(.bottom, 20)
                
                Text("Ultimate Kitchen Compendium")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .multilineTextAlignment(.center)
                    .padding(.bottom, 40)
                
                VStack(spacing: 16) {
                    if isRegistering {
                        TextField("Full Name", text: $fullName)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .autocapitalization(.words)
                            .disableAutocorrection(true)
                    }
                    
                    TextField("Email", text: $email)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .autocapitalization(.none)
                        .keyboardType(.emailAddress)
                        .disableAutocorrection(true)
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                .padding(.horizontal, 30)
                .padding(.bottom, 30)
                
                Button(action: handleSubmit) {
                    if authService.isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                            .frame(height: 44)
                    } else {
                        Text(isRegistering ? "Create Account" : "Sign In")
                            .frame(maxWidth: .infinity)
                            .frame(height: 44)
                    }
                }
                .buttonStyle(.borderedProminent)
                .tint(.appPrimary)
                .padding(.horizontal, 30)
                .disabled(!isFormValid || authService.isLoading)
                
                Button(action: { isRegistering.toggle() }) {
                    Text(isRegistering ? "Already have an account? Sign In" : "Don't have an account? Create one")
                        .font(.subheadline)
                        .foregroundColor(.appPrimary)
                }
                .padding(.top, 20)
                
                Spacer()
            }
            .background(Color(.systemBackground))
            .alert("Error", isPresented: $showAlert) {
                Button("OK", role: .cancel) { }
            } message: {
                Text(errorMessage)
            }
        }
    }
    
    private var isFormValid: Bool {
        if isRegistering {
            return !email.isEmpty && !password.isEmpty && !fullName.isEmpty && email.isValidEmail && password.isValidPassword
        } else {
            return !email.isEmpty && !password.isEmpty && email.isValidEmail
        }
    }
    
    private func handleSubmit() {
        if isRegistering {
            authService.register(email: email, password: password, fullName: fullName)
                .sink(
                    receiveCompletion: { completion in
                        if case .failure(let error) = completion {
                            errorMessage = error.localizedDescription
                            showAlert = true
                        }
                    },
                    receiveValue: { _ in }
                )
                .store(in: &authService.cancellables)
        } else {
            authService.login(email: email, password: password)
                .sink(
                    receiveCompletion: { completion in
                        if case .failure(let error) = completion {
                            errorMessage = error.localizedDescription
                            showAlert = true
                        }
                    },
                    receiveValue: { _ in }
                )
                .store(in: &authService.cancellables)
        }
    }
}

struct LoginView_Previews: PreviewProvider {
    static var previews: some View {
        LoginView()
            .environmentObject(AuthService.shared)
    }
}