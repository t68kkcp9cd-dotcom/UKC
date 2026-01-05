import SwiftUI

extension Color {
    static let appPrimary = Color("AppPrimary")
    static let appSecondary = Color("AppSecondary")
    static let appAccent = Color("AppAccent")
}

extension UIColor {
    static let appPrimary = UIColor(named: "AppPrimary") ?? UIColor.systemBlue
    static let appSecondary = UIColor(named: "AppSecondary") ?? UIColor.systemGreen
    static let appAccent = UIColor(named: "AppAccent") ?? UIColor.systemOrange
}

struct AppColors {
    static let primary = Color(red: 0.2, green: 0.4, blue: 0.8)
    static let secondary = Color(red: 0.3, green: 0.7, blue: 0.4)
    static let accent = Color(red: 1.0, green: 0.6, blue: 0.2)
    static let background = Color(.systemBackground)
    static let surface = Color(.secondarySystemBackground)
    static let text = Color(.label)
    static let textSecondary = Color(.secondaryLabel)
    static let success = Color.green
    static let warning = Color.orange
    static let error = Color.red
    static let info = Color.blue
}